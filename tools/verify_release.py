"""Check a named deployment against this exact static build, including error headers."""
import concurrent.futures
import hashlib
import json
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
origin = sys.argv[1].rstrip('/')
if urlparse(origin).scheme != 'https':
    raise SystemExit('Verification requires an HTTPS origin.')


def check(path):
    relative = path.relative_to(ROOT / 'dist').as_posix()
    if relative.startswith('_'):
        return None
    route = '/' + relative
    if relative.endswith('index.html'):
        route = route[:-10]
    request = Request(origin + route, headers={'Cache-Control': 'no-cache', 'User-Agent': 'Neurasoft-Release-Verification/1'})
    with urlopen(request, timeout=25) as response:
        data = response.read()
        return {
            'route': route,
            'status': response.status,
            'byte_match': hashlib.sha256(data).digest() == hashlib.sha256(path.read_bytes()).digest(),
            'csp_present': "default-src 'self'" in response.headers.get('Content-Security-Policy', ''),
            'nosniff': response.headers.get('X-Content-Type-Options') == 'nosniff',
        }


try:
    first = check(ROOT / 'dist/index.html')
except HTTPError as error:
    report = {'origin': origin, 'passed': False, 'preflight_status': error.code, 'files_checked': 1}
    if len(sys.argv) > 2:
        destination = Path(sys.argv[2])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report))
    raise SystemExit(1)

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    # Stop on an unavailable origin before requesting the rest of the publication.
    rows = []
    futures = [executor.submit(check, p) for p in sorted((ROOT / 'dist').rglob('*')) if p.is_file()]
    for future in futures:
        try:
            row = future.result()
        except HTTPError as error:
            # A hosting platform can correctly return 404 for the direct 404 document.
            row = {'route': error.url.removeprefix(origin), 'status': error.code, 'byte_match': error.read() == (ROOT/'dist/404.html').read_bytes(), 'csp_present': "default-src 'self'" in error.headers.get('Content-Security-Policy',''), 'nosniff': error.headers.get('X-Content-Type-Options') == 'nosniff'}
        if row:
            rows.append(row)

try:
    request = Request(origin + '/not-a-real-neurasoft-route-20260916/', headers={'Cache-Control': 'no-cache', 'User-Agent': 'Neurasoft-Release-Verification/1'})
    with urlopen(request, timeout=25) as response:
        missing = {'status': response.status, 'custom_404': False}
except HTTPError as error:
    missing = {'status': error.code, 'custom_404': error.read() == (ROOT/'dist/404.html').read_bytes()}

passed = all(r['byte_match'] and r['csp_present'] and r['nosniff'] and (r['status'] == 200 or (r['route'] == '/404.html' and r['status'] == 404)) for r in rows) and missing == {'status':404, 'custom_404':True}
report = {'origin': origin, 'files_checked': len(rows), 'passed': passed, 'unknown_route': missing, 'files': rows}
if len(sys.argv) > 2:
    destination = Path(sys.argv[2])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k!='files'}))
if not passed:
    print(json.dumps([row for row in rows if not row['byte_match'] or not row['csp_present'] or not row['nosniff']], indent=2))
raise SystemExit(0 if passed else 1)
