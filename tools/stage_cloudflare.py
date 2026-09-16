"""Stage the identical site for Pages; its native 404.html replaces Netlify's rule."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
source = root / 'dist'
target = root / 'artifacts/cloudflare'
if target.resolve() != root.resolve() / 'artifacts/cloudflare' or target.is_symlink():
    raise SystemExit('Unexpected staging destination')
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target, ignore=shutil.ignore_patterns('_redirects'))
print(f'Cloudflare staging: {sum(p.is_file() for p in target.rglob("*"))} files; original dist preserved.')
