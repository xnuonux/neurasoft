"""Validate the FINAL publication stage and write an external byte manifest. Offline only."""
import argparse, hashlib, json, sys
from pathlib import Path
import xml.etree.ElementTree as ET


def verify(stage):
    if stage.is_symlink() or not stage.is_dir(): raise ValueError('real stage required')
    entries = list(stage.rglob('*'))
    if any(p.is_symlink() for p in entries): raise ValueError('no staged symlinks')
    for path in entries:
        if any(part.startswith('.') or part in ('company','private','tests','__pycache__') for part in path.relative_to(stage).parts):
            raise ValueError('non-public tree in stage')
        if path.is_file() and path.suffix in ('.py','.pyc','.zip','.md','.yml','.yaml','.patch'):
            raise ValueError('unexpected implementation artifact in stage')
    for required in ('index.html','luna/index.html','glossary/index.html','updates/index.html','assets/publication.json','feed.xml','llms.txt','sitemap.xml'):
        if not (stage/required).is_file(): raise ValueError('missing '+required)
    ET.fromstring((stage/'feed.xml').read_bytes());ET.fromstring((stage/'sitemap.xml').read_bytes())
    name='Locus of Unified Noetic Agency'
    for p in ('luna/index.html','glossary/index.html','llms.txt'):
        if name not in (stage/p).read_text(encoding='utf-8'):raise ValueError('missing canonical name')
    index=json.loads((stage/'assets/search-index.json').read_text(encoding='utf-8'))
    if not any(x.get('url')=='/luna/' and name in x.get('text','') for x in index):raise ValueError('name not searchable')
    if not any(x.get('url')=='/updates/' for x in index):raise ValueError('publication record not searchable')
    record=json.loads((stage/'assets/publication.json').read_text(encoding='utf-8'))
    return {'schema':'neurasoft.staged-publication-check/v1','passed':True,'deployment_verified':False,
            'edition':record['edition'],'files':{str(p.relative_to(stage)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(entries) if p.is_file()}}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('stage',nargs='?',default='artifacts/cloudflare');p.add_argument('--output',default='artifacts/publication-validation.json');args=p.parse_args()
    result=verify(Path(args.stage));out=Path(args.output)
    if out.resolve().is_relative_to(Path(args.stage).resolve()):raise SystemExit('manifest must remain outside public stage')
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps({'passed':True,'files':len(result['files']),'deployment_verified':False}))
