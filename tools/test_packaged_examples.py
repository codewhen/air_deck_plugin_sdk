#!/usr/bin/env python3
"""Exercise installed example packages from a directory outside the SDK checkout."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import tempfile
import threading
import zipfile

def exercise(package):
    with tempfile.TemporaryDirectory(prefix='airdeck-installed-') as tmp:
        root = Path(tmp)
        with zipfile.ZipFile(package) as archive:
            archive.extractall(root)
        manifest = json.loads((root/'manifest.json').read_text())
        entry = root/manifest['entrypoint'].removeprefix('./')
        entry.chmod(0o755)
        env = dict(os.environ, PYTHONPATH='', CLASSPATH='')
        process = subprocess.Popen([str(entry)], cwd=root, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        messages = queue.Queue()
        def reader():
            for line in process.stdout: messages.put(line)
        threading.Thread(target=reader, daemon=True).start()
        try:
            for request in [
                {'op':'catalog','ipc_id':'catalog'},
                {'op':'invoke','ipc_id':'invoke','type':'plugin.command','action':'beep','payload':{},'body':{}},
                {'op':'invoke','ipc_id':'invalid','type':'plugin.command','action':'does-not-exist','payload':{},'body':{}},
            ]:
                process.stdin.write(json.dumps(request)+'\n'); process.stdin.flush()
                try: response = json.loads(messages.get(timeout=15))
                except queue.Empty: raise AssertionError(f'{package}: no correlated response; process exit={process.poll()}')
                assert response['ipc_id'] == request['ipc_id'], response
                assert response['op'] == ('error' if request['ipc_id']=='invalid' else 'ok'), response
                if request['ipc_id']=='catalog': assert response['buttons'][0]['action']=='beep', response
            print('PASS isolated package:', package)
        finally:
            process.stdin.close()
            try: process.wait(timeout=5)
            except subprocess.TimeoutExpired: process.kill(); process.wait()
            process.stdout.close(); process.stderr.close()

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packages', nargs='+', type=Path)
    for package in parser.parse_args().packages: exercise(package.resolve())
