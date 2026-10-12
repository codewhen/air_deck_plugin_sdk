#!/usr/bin/env python3
"""Pack a v2 executable plugin, embedding validated capability contracts."""
import argparse,json,pathlib,zipfile
from generate import validate

def safe(root,name):
    name=name.removeprefix('./');p=pathlib.PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name or not name:raise ValueError('unsafe package path: '+name)
    file=root/name
    if not file.is_file() or not file.resolve().is_relative_to(root.resolve()):raise ValueError('missing or escaping file: '+name)
    return name,file

def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=pathlib.Path);ap.add_argument('output',type=pathlib.Path);a=ap.parse_args();root=a.directory.resolve();m=json.loads((root/'manifest.json').read_text());assert m.get('api_version')==2 and isinstance(m.get('permissions'),list),'plugin API v2 and permissions required'
    assert m['id'] and '/' not in m['id'] and '\\' not in m['id'] and '..' not in m['id'],'invalid plugin id'
    schemas=m.get('capability_schemas',[])
    if schemas:m['capabilities']=[json.loads(safe(root,f)[1].read_text()) for f in schemas]
    for c in m.get('capabilities',[]):validate(c);assert c['id'].startswith(m['id']+'.'),'invalid provider namespace'
    files=list(dict.fromkeys(m.get('files',[])+schemas));m['files']=files
    entry=m['entrypoint'].removeprefix('./');actual=entry
    if not (root/entry).is_file() and (root/(entry+'.exe')).is_file():actual=entry+'.exe'
    m['entrypoint']='./'+actual
    resources=[actual]+files+([m['config']] if m.get('config') else [])
    a.output.mkdir(parents=True,exist_ok=True);out=a.output/(m['id']+'.deckPlugin')
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('manifest.json',json.dumps(m,indent=2)+'\n')
        for name in dict.fromkeys(resources):relative,file=safe(root,name);z.write(file,relative)
    print('packed '+str(out))
if __name__=='__main__':main()
