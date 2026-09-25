"""Create a portable GB package from already-built, public article artifacts."""
import json
import shutil
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT=Path(__file__).resolve().parents[1]
slug=sys.argv[1]
if not slug or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in slug):
    raise SystemExit('Expected an article slug')
source=ROOT/'dist/articles'/slug
packet=json.loads((source/'grok-packet.json').read_text(encoding='utf-8'))
out=ROOT/'artifacts/editorial-packets'/packet['id']
out.mkdir(parents=True,exist_ok=True)
shutil.copy2(source/'grok-packet.json',out/'grok-packet.json')
shutil.copy2(source/'article.md',out/'article.md')
for image in packet['images']:
    shutil.copy2(ROOT/'dist/assets/articles'/slug/image['file'],out/image['file'])
(out/'x-post.txt').write_text(packet['x_post']+'\n',encoding='utf-8')
(out/'linkedin-post.txt').write_text(packet['linkedin_post']+'\n',encoding='utf-8')
(out/'README.md').write_text('# Ready for Grok Bot\n\n'+packet['title']+'\n\n'+packet['instructions']+'\n\nCanonical: '+packet['canonical_url']+'\n\nFull text: article.md. Image order, captions and alt text: grok-packet.json.\n\nPrepared does not mean socially published. Record post URLs after publication.\n',encoding='utf-8')
archive=out.with_suffix('.zip')
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
    for p in sorted(out.iterdir()):
        if p.is_file(): z.write(p,p.name)
print(archive)
