#!/usr/bin/env python3
"""Generate complete core capability references from the public schema contracts."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'docs/plugin-development/reference'
NOTES={
 'core.media': ('Media capability','Playback, track metadata, system volume and mute.', '''Playback/track availability depends on the operating system and media application. Inspect `available`; an unknown or unavailable snapshot is not a playing/paused guarantee. A successful next/previous command does not prove the prepared player has another track.

Volume `level` is normalized from 0 to 1: 0.5 means 50%. An adjustment `delta` of 0.1 represents ten percentage points. Volume and mute are separate values. Use `setMute` for mute state rather than assuming a zero volume is equivalent. Respect the numeric ranges below. Subscribe to playback/track/volume topics when a UI needs current state.'''),
 'core.keyboard': ('Keyboard capability','Supported key presses and hotkey combinations.', '''The current core key-press implementation accepts the lowercase keys `up`, `down`, `left`, `right` and `enter`. The string schema is not a promise that every possible key name is supported. Unsupported names return `invalid_arguments`.

Use `hotkey` for a supported combination and test its platform-specific parsing and effect. Avoid leaving keys pressed or assuming a keyboard layout is identical on every machine.'''),
 'core.pointer': ('Pointer capability','Pointer motion and clicks through the helper broker.', '''Motion uses relative deltas. Keep sensitivity within the declared range; test real cursor behavior on the target desktop. The schema defines accepted fields, while the OS adapter determines the actual effect.

Clicks use the declared left/right button values and an explicit double-click boolean. Request pointer permission before making a broker call. Do not describe an unverified compiled binary as a real pointer-control test.'''),
 'core.apps': ('Applications capability','List applications and launch a selected target.', '''Use the application catalog's returned target for launch where possible. A target is an OS-specific identifier/path understood by the helper, not a portable path you can invent once for every system.

Catalog availability and application names can vary by computer. Validate a selected target, handle launch failure and keep a saved action meaningful when an app is moved or uninstalled.'''),
}

def shape(field):
    if field['type']=='array': return [f"{field['items']['$ref']}[]",f"maximum {field.get('maxItems','unspecified')} items"]
    constraints=[]
    for k in ('minimum','maximum','minLength','maxLength','maxItems'):
        if k in field: constraints.append(f"{k}={field[k]}")
    if field.get('enum'): constraints.append('one of '+', '.join('`'+str(v)+'`' for v in field['enum']))
    return [field['type'], '; '.join(constraints) or 'No additional schema constraint']

def value(field):
    if field.get('enum'): return field['enum'][0]
    typ=field['type']
    if typ=='string': return 'example'
    if typ=='boolean': return False
    if typ=='array': return []
    lo=field.get('minimum',0);hi=field.get('maximum',100)
    return int(lo) if typ=='integer' else (0.5 if lo<=0.5<=hi else 1 if lo<=1<=hi else lo)

def sample(contract,typename):
    result = {name:value(field) for name,field in contract['types'][typename]['properties'].items()}
    if result.get('available') is False and 'status' in result: result['status']='unknown'
    return result

def generate(contract):
    cap=contract['id'];title,description,notes=NOTES[cap]
    text=f'''---
title: {json.dumps(title)}
description: {json.dumps(description)}
---

This page is generated from `{cap}.json`. Contract version: **{contract['version']}**. Edit the public schema and run `python3 tools/generate_reference_docs.py` to update the tables and payload shapes.

## Before calling this capability

Declare the permissions needed by your selected methods/topics and a compatible `uses` range for `{cap}`. Construct the generated client from the SDK host during initialization. Handle denied permissions, incompatible contracts and operational failures.

{notes}

## Permission IDs

| ID | User-facing purpose |
| --- | --- |
'''
    for name,desc in contract['permissions'].items(): text+=f'| `{name}` | {desc} |\n'
    text+='\n## Methods\n\nThe method names below are the contract/wire names. Generated clients expose language-appropriate names; use those clients rather than manually inventing JSON fields.\n\n'
    for name,method in contract['methods'].items():
        text+=f"### `{name}`\n\nRequest: `{method['request']}`. Result: `{method['result']}`.\n\nRequired permissions: "+', '.join('`'+p+'`' for p in method['permissions'])+'.\n\n'
        payload=sample(contract,method['request'])
        if cap=='core.keyboard' and name=='press': payload['key']='enter'
        if cap=='core.keyboard' and name=='hotkey': payload['combo']='ctrl+c'
        text+='Example request payload shape:\n\n```json\n'+json.dumps(payload,indent=2)+'\n```\n\n'
        if any(v=='example' for v in payload.values()):text+='Replace `example` with a real value valid on your target computer. This is a shape example, not a verified external application target.\n\n'
        if method['result']=='Empty':text+='A successful method returns an empty result object. Inspect the error path when the operation cannot complete.\n\n'
        else:text+=f"Read the `{method['result']}` type below for the returned fields.\n\n"
    text+='## Topics\n\n'
    if not contract['topics']:text+='This contract declares no state topics.\n\n'
    for name,topic in contract['topics'].items():
        text+=f"### `{name}`\n\nValue type: `{topic['type']}`. Required permissions: "+', '.join('`'+p+'`' for p in topic['permissions'])+'.\n\nSubscribe with the generated client. Store and eventually call the unsubscribe function. Treat the value as observed state rather than acknowledgement of a particular command.\n\n'
    text+='## Types\n\nThese objects are closed: their schema does not allow additional properties. Every listed property is required in this version.\n\n'
    for name,typ in contract['types'].items():
        text+=f'### `{name}`\n\n'
        if not typ['properties']:text+='An empty object: `{}`.\n\n';continue
        text+='| Field | Type | Constraints |\n| --- | --- | --- |\n'
        for namefield,field in typ['properties'].items():
            kind,constraints=shape(field);text+=f'| `{namefield}` | `{kind}` | {constraints} |\n'
        text+='\nExample value shape:\n\n```json\n'+json.dumps(sample(contract,name),indent=2)+'\n```\n\n'
    text+='## Permission groups\n\n'
    if not contract.get('groups'):text+='No permission groups are declared by this contract.\n\n'
    for group,permissions in contract.get('groups',{}).items(): text+=f"- `{group}`: "+', '.join('`'+p+'`' for p in permissions)+'.\n'
    text+='\n## Verification checklist\n\nTest a valid operation, invalid input, missing/revoked permission, unsupported OS/application behavior and incompatible contract version. For topics, test initial/current state, later updates and unsubscribe. A packaged protocol test alone cannot verify this native operation.\n'
    return text

if __name__=='__main__':
    OUT.mkdir(parents=True,exist_ok=True)
    for file in sorted((ROOT/'capabilities/schemas').glob('core.*.json')):
        contract=json.loads(file.read_text());(OUT/(contract['id'].replace('.','-')+'.mdx')).write_text(generate(contract))
    print('Generated four core capability references')
