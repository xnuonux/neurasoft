"""Verify the custom domain against the local build, tolerating Cloudflare's edge injection.

verify_release.py compares raw bytes, which fails on the proxied custom domain because Cloudflare
appends a Web Analytics beacon script at the edge. That injection is the edge's, not the build's.
So: compare bytes exactly, and when they differ, check whether the ONLY difference is a
cloudflareinsights beacon. Anything else is a real mismatch.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(r'C:\dev\neurasoft')
DIST = ROOT / 'dist'
origin = sys.argv[1].rstrip('/')

BEACON = re.compile(
    rb'<script[^>]*static\.cloudflareinsights\.com/beacon\.min\.js[^>]*></script>\s*', re.I)

rows = []
for path in sorted(DIST.rglob('*')):
    if not path.is_file():
        continue
    rel = path.relative_to(DIST).as_posix()
    if rel.startswith('_'):
        continue
    route = '/' + rel
    if rel.endswith('index.html'):
        route = route[:-10]
    out = subprocess.run(
        ['curl', '-sS', '-o', '-', '-w', '\n%{http_code}',
         '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0 Safari/537.36',
         '-H', 'Cache-Control: no-cache', origin + route],
        capture_output=True)
    body = out.stdout
    nl = body.rfind(b'\n')
    status = body[nl + 1:].decode(errors='replace').strip()
    body = body[:nl]
    want = path.read_bytes()
    exact = hashlib.sha256(body).digest() == hashlib.sha256(want).digest()
    beacon_only = False
    if not exact:
        stripped = BEACON.sub(b'', body)
        beacon_only = hashlib.sha256(stripped).digest() == hashlib.sha256(want).digest()
    rows.append({
        'route': route, 'status': status,
        'exact': exact, 'beacon_only_diff': beacon_only,
        'clean': exact or beacon_only,
        'live_bytes': len(body), 'local_bytes': len(want),
    })

bad = [r for r in rows if not r['clean']]
inj = [r for r in rows if r['beacon_only_diff']]
wrong_status = [r for r in rows if r['status'] not in ('200', '404')]

print(f"  origin            {origin}")
print(f"  files checked     {len(rows)}")
print(f"  byte-exact        {len([r for r in rows if r['exact']])}")
print(f"  beacon-only diff  {len(inj)}")
print(f"  REAL MISMATCH     {len(bad)}")
print(f"  bad status        {[(r['route'], r['status']) for r in wrong_status] or 'none'}")
if bad:
    print("\n  real mismatches:")
    for r in bad[:10]:
        print(f"    {r['route']}  live={r['live_bytes']} local={r['local_bytes']} status={r['status']}")
print(f"\n  VERDICT: {'content matches the build' if not bad else 'CONTENT DOES NOT MATCH'}"
      f"{'; Cloudflare beacon injected on ' + str(len(inj)) + ' HTML routes' if inj else ''}")
Path(sys.argv[2]).write_text(json.dumps(
    {'origin': origin, 'files': len(rows), 'byte_exact': len([r for r in rows if r['exact']]),
     'beacon_only': len(inj), 'real_mismatch': len(bad), 'rows': rows}, indent=1), encoding='utf-8')
raise SystemExit(0 if not bad else 1)
