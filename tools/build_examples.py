#!/usr/bin/env python3
"""Build standalone API v2 tutorial packages using installed, local toolchains."""
import argparse
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def run(args, **kwargs):
    subprocess.run(list(map(str, args)), check=True, **kwargs)

def build(language, output, gson=None, plugin_dir=None, python_entry="echo_plugin.py", java_main="com.example.echo.EchoPlugin", binary_name="echo-plugin"):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", binary_name): raise ValueError("Invalid binary name")
    if not re.fullmatch(r"[A-Za-z0-9_-]+\.py", python_entry): raise ValueError("Invalid Python entry filename")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*", java_main): raise ValueError("Invalid Java main class")
    sdk = ROOT / 'deck-plugins'
    source = plugin_dir.resolve() if plugin_dir else sdk / 'plugins/examples' / language
    with tempfile.TemporaryDirectory(prefix='airdeck-example-') as tmp:
        stage = Path(tmp)
        manifest = json.loads((source / 'manifest.json').read_text())
        windows = sys.platform == 'win32'
        binary = binary_name + ('.exe' if windows else '')
        java_jar = binary_name + '.jar'
        if language == 'go':
            run(['go', 'build', '-o', stage / binary, './'+source.relative_to(sdk).as_posix()], cwd=sdk)
        elif language == 'cpp':
            run([os.environ.get('CXX', 'c++'), '-std=c++17', '-O2', '-I', sdk/'sdk/cpp', '-I', sdk/'sdk/cpp/vendor', source/'main.cpp', '-o', stage/binary])
        elif language == 'python':
            shutil.copy2(source/python_entry, stage/python_entry)
            shutil.copytree(sdk/'sdk/python', stage/'sdk', ignore=shutil.ignore_patterns('__pycache__', 'tests', '*.pyc'))
            if not windows:
                (stage/python_entry).chmod(0o755)
                binary = python_entry
        elif language == 'java':
            if not gson or not gson.is_file():
                raise ValueError('Java needs --gson /path/to/gson.jar (or GSON_JAR).')
            classes = stage/'classes'
            classes.mkdir()
            sources = [* (sdk/'sdk/java').rglob('*.java'), * (ROOT/'capabilities/generated/java').rglob('*.java'), *source.rglob('*.java')]
            run(['javac', '--release', '17', '-cp', gson, '-d', classes, *sources])
            run(['jar', '--create', '--file', stage/java_jar, '-C', classes, '.'])
            shutil.rmtree(classes)
            shutil.copy2(gson, stage/'gson.jar')
            if not windows:
                (stage/binary).write_text('#!/usr/bin/env sh\nDIR="$(cd -- "$(dirname -- "$0")" && pwd)"\nexec java -cp "$DIR/'+java_jar+':$DIR/gson.jar" '+java_main+'\n')
                (stage/binary).chmod(0o755)
        if windows and language in ('python', 'java'):
            run(['go', 'build', '-ldflags', f'-X main.language={language} -X main.pythonEntry={python_entry} -X main.javaMain={java_main} -X main.javaJar={java_jar}', '-o', stage/binary, ROOT/'tools/runtime-launcher/main.go'], cwd=sdk)
        manifest['entrypoint'] = './' + binary
        shutil.copy2(ROOT/'LICENSE', stage/'LICENSE.sdk')
        shutil.copy2(ROOT/'THIRD_PARTY_NOTICES.md', stage/'THIRD_PARTY_NOTICES.md')
        if language == 'cpp':
            shutil.copy2(sdk/'sdk/cpp/vendor/LICENSE.MIT', stage/'LICENSE.nlohmann-json')
        if language == 'java':
            (stage/'NOTICE.gson').write_text('Gson: Copyright 2008 Google Inc. Licensed under Apache-2.0; see LICENSE.sdk.\n')
        # Runtime files, excluding original implementation/build sources.
        manifest['files'] = [p.relative_to(stage).as_posix() for p in sorted(stage.rglob('*')) if p.is_file() and p.name not in (binary, 'manifest.json')]
        (stage/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
        run([sys.executable, ROOT/'capabilities/tools/pack_plugin.py', stage, output/language])
    return output/language/(manifest['id']+'.deckPlugin')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('language', choices=['go','python','java','cpp','all'])
    parser.add_argument('--out', type=Path, default=ROOT/'deck-plugins/dist/examples')
    parser.add_argument('--plugin-dir', type=Path, help='Custom template directory inside deck-plugins (one language only)')
    parser.add_argument('--gson', type=Path, default=Path(os.environ['GSON_JAR']) if os.environ.get('GSON_JAR') else None)
    args = parser.parse_args()
    if args.language == 'all' and args.plugin_dir: parser.error('--plugin-dir needs one language')
    languages = ['go','python','java','cpp'] if args.language == 'all' else [args.language]
    for language in languages: build(language, args.out.resolve(), args.gson, args.plugin_dir)

if __name__ == '__main__': main()
