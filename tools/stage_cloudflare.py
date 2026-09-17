"""Stage the reviewed public site, then add deterministic continuity modules.

The upstream dist/ stays untouched. Only the finalized artifacts/cloudflare/ is a
release candidate. No publishing, network calls, or private source copying occurs.
"""
from pathlib import Path
import shutil
import sys
import tempfile

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from continuity_publication import apply
from tools.verify_publication import verify
source = root / 'dist'
target = root / 'artifacts/cloudflare'
if target.resolve() != root.resolve() / 'artifacts/cloudflare' or target.is_symlink():
    raise SystemExit('Unexpected staging destination')
if not source.is_dir() or source.is_symlink() or any(p.is_symlink() for p in source.rglob('*')):
    raise SystemExit('Expected a real, symlink-free dist directory')
target.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='publication-', dir=target.parent) as temp:
    candidate = Path(temp) / 'site'
    shutil.copytree(source, candidate, ignore=shutil.ignore_patterns('_redirects'))
    result = apply(candidate, root)
    verify(candidate)
    if target.exists(): shutil.rmtree(target)
    shutil.move(str(candidate), target)
print(f'Cloudflare staging: {sum(p.is_file() for p in target.rglob("*"))} files; original dist preserved. {result}')
