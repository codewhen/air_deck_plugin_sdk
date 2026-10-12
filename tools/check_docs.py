#!/usr/bin/env python3
"""Validate hierarchical docs navigation, metadata, relative links and generated contracts."""
import json
from pathlib import Path
import re
from generate_reference_docs import generate

SDK=Path(__file__).resolve().parents[1]
ROOT=SDK/'docs/plugin-development'
pages={p.relative_to(ROOT).with_suffix('').as_posix():p for p in ROOT.rglob('*.mdx')}

def check_navigation(directory):
    meta=json.loads((directory/'meta.json').read_text())
    order=meta['pages']
    assert len(order)==len(set(order)), directory
    expected={p.stem for p in directory.glob('*.mdx')}|{p.name for p in directory.iterdir() if p.is_dir()}
    assert set(order)==expected, (directory,order,expected)
    for child in directory.iterdir():
        if child.is_dir():check_navigation(child)

check_navigation(ROOT)
for name,p in pages.items():
    text=p.read_text()
    assert text.startswith('---\n'), name
    metadata=text.split('---',2)[1]
    assert re.search(r'^title: .+',metadata,re.M) and re.search(r'^description: .+',metadata,re.M), name
    content=re.sub(r'```.*?```','',text,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if target.startswith('.'):
            path=target.split('#')[0].removesuffix('.mdx').removesuffix('.md')
            resolved=(p.parent/path).resolve()
            assert resolved.is_relative_to(ROOT.resolve()), (name,target)
            relative=resolved.relative_to(ROOT.resolve()).as_posix()
            assert relative in pages or relative+'/index' in pages, (name,target)
    assert 'air_mouse_workspace' not in text, 'Public docs must not link private source'
for language,filename in [('go','main.go'),('python','plugin.py'),('java','Plugin.java'),('cpp','main.cpp')]:
    template=(SDK/'tools/templates'/language/filename).read_text().replace('__ID_JSON__','\"com.yourname.hello\"').rstrip()
    assert template in (ROOT/'get-started'/(language+'.mdx')).read_text(), 'Tutorial source drift: '+language
for file in (SDK/'capabilities/schemas').glob('core.*.json'):
    contract=json.loads(file.read_text())
    actual=ROOT/'reference'/(contract['id'].replace('.','-')+'.mdx')
    assert actual.read_text()==generate(contract), 'Regenerate core reference docs: '+str(actual)
print(f'PASS: {len(pages)} developer pages, sections, metadata, internal links and generated contracts')
