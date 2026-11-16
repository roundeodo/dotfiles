#!/usr/bin/env python3
"""Restore recorded Vim plugin revisions; preview unless --apply is supplied."""
import argparse
import json
from pathlib import Path
import subprocess

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    for plugin in json.loads((base / 'reference/vim-plugins.json').read_text()):
        target = Path.home() / '.vim/plugged' / plugin['name']
        print(plugin['name'] + ' @ ' + plugin['head'])
        if not args.apply:
            continue
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            subprocess.check_call(['git', 'clone', plugin['origin'], str(target)])
        status = subprocess.check_output(['git', '-C', str(target), 'status', '--porcelain'])
        if status.strip():
            raise RuntimeError('Plugin has local changes: ' + str(target))
        subprocess.check_call(['git', '-C', str(target), 'fetch', 'origin', plugin['head']])
        subprocess.check_call(['git', '-C', str(target), 'checkout', '--detach', plugin['head']])

if __name__ == '__main__':
    main()
