#!/usr/bin/env python3
"""Create, build and test a minimal Hello AirDeck starter in the public SDK."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
from build_examples import build
from test_packaged_examples import exercise

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = ('go','python','java','cpp')

def create(language, directory, plugin_id, name):
    if language not in LANGUAGES: raise ValueError('Unsupported language')
    if not re.fullmatch(r'[a-z][a-z0-9]*(?:\.[a-z][a-z0-9_-]*)+', plugin_id):
        raise ValueError('Use a dotted lowercase plugin ID, for example com.yourname.hello')
    if not name.strip() or any(ord(c)<32 for c in name): raise ValueError('Name must be nonempty and contain no control characters')
    if directory.exists(): raise ValueError('Destination already exists; choose a new folder name')
    templates = ROOT/'tools/templates'/language
    directory.mkdir(parents=True)
    for template in templates.iterdir():
        if template.is_file():
            (directory/template.name).write_text(template.read_text().replace('__ID_JSON__',json.dumps(plugin_id, ensure_ascii=False)))
    config = {'language':language, 'action':'hello', 'binary_name':'plugin'}
    if language=='python': config['python_entry']='plugin.py'
    if language=='java': config['java_main']='com.example.starter.Plugin'
    manifest = {'id':plugin_id,'name':name,'version':'1.0.0','api_version':2,'mode':'targeted','types':[],
                'entrypoint':'./plugin.py' if language=='python' else './plugin','permissions':[],'files':[]}
    (directory/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (directory/'airdeck.build.json').write_text(json.dumps(config,indent=2)+'\n')
    (directory/'README.md').write_text(f'# {name}\n\nCreated with the public AirDeck SDK.\n\nFrom the SDK root:\n\n```sh\npython3 tools/plugin.py build {directory.name}\npython3 tools/plugin.py test {directory.name}\n```\n\nFor Java pass --gson /path/to/gson.jar when building. Replace the hello action with your logic; keep logging on stderr.\n')
    return directory

def project(name):
    if not re.fullmatch(r'[A-Za-z0-9_-]+', name): raise ValueError('Project name must use letters, numbers, hyphens or underscores')
    return ROOT/'deck-plugins/plugins'/name

def package_path(directory, config, manifest):
    return ROOT/'deck-plugins/dist/starters'/directory.name/config['language']/(manifest['id']+'.deckPlugin')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    new=commands.add_parser('create',help='Create a new plugin; never overwrites a directory')
    new.add_argument('language',choices=LANGUAGES);new.add_argument('project')
    new.add_argument('--id',required=True);new.add_argument('--name',default='Hello AirDeck')
    compile_cmd=commands.add_parser('build',help='Build a standalone package for this computer')
    compile_cmd.add_argument('project');compile_cmd.add_argument('--gson',type=Path,default=Path(os.environ['GSON_JAR']) if os.environ.get('GSON_JAR') else None)
    check=commands.add_parser('test',help='Test the built package outside the source checkout')
    check.add_argument('project')
    args=parser.parse_args()
    try:
        directory=project(args.project)
        if args.command=='create':
            create(args.language,directory,args.id,args.name)
            print('Created:',directory)
            print(f'Next: python3 tools/plugin.py build {args.project}'+(' --gson /path/to/gson.jar' if args.language=='java' else ''))
        else:
            config=json.loads((directory/'airdeck.build.json').read_text());manifest=json.loads((directory/'manifest.json').read_text())
            if args.command=='build':
                build(config['language'], ROOT/'deck-plugins/dist/starters'/args.project, args.gson, directory,
                      config.get('python_entry','echo_plugin.py'), config.get('java_main','com.example.echo.EchoPlugin'), config.get('binary_name','plugin'))
                print('Install in AirDeck Helper:',package_path(directory,config,manifest))
            else: exercise(package_path(directory,config,manifest), config.get('action','hello'))
    except (ValueError, OSError) as error: parser.error(str(error))

if __name__=='__main__': main()
