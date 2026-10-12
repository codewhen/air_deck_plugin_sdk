#!/usr/bin/env python3
"""Validate navigation, required metadata and relative developer-guide links."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]/'docs/plugin-development'
pages = {p.stem:p for p in ROOT.glob('*.mdx')}
order = json.loads((ROOT/'meta.json').read_text())['pages']
assert len(order)==len(set(order)) and set(order)==set(pages), 'Navigation must contain each page once'
for name,p in pages.items():
    text=p.read_text()
    assert text.startswith('---\n'), name
    metadata=text.split('---',2)[1]
    assert re.search(r'^title: .+',metadata,re.M) and re.search(r'^description: .+',metadata,re.M), name
    content=re.sub(r'```.*?```','',text,flags=re.S)
    for target in re.findall(r'\]\(([^)]+)\)',content):
        if target.startswith('./'):
            assert target[2:].split('#')[0] in pages, (name,target)
    assert 'air_mouse_workspace' not in text, 'Public docs must not link private source'
print(f'PASS: {len(pages)} developer pages, metadata and internal links')
