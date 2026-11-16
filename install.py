#!/usr/bin/env python3
"""Preview by default; --apply installs with backups. Compatible with Python 3.6+."""
import argparse
import datetime
import os
from pathlib import Path
import shutil

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--target-home', type=Path, default=Path.home())
    args = parser.parse_args()
    root = Path(__file__).resolve().parent / 'home'
    target_home = args.target_home.expanduser().resolve()
    backup = target_home / '.local/state/dotfiles/backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    def save_existing(target, relative):
        if target.exists() or target.is_symlink():
            dest = backup / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            if target.is_dir() and not target.is_symlink():
                raise RuntimeError('Refusing to replace directory: ' + str(target))
            shutil.copy2(str(target), str(dest), follow_symlinks=False)
    changed = 0
    for source in sorted(root.rglob('*')):
        if not source.is_file():
            continue
        relative = source.relative_to(root)
        target = target_home / relative
        data = source.read_bytes()
        if b'\x00' not in data[:8192]:
            data = data.replace(b'/home/yong', str(target_home).encode('utf-8'))
        if target.is_file() and not target.is_symlink() and target.read_bytes() == data:
            continue
        print(('INSTALL ' if args.apply else 'WOULD INSTALL ') + str(relative))
        changed += 1
        if args.apply:
            save_existing(target, relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.is_symlink():
                target.unlink()
            target.write_bytes(data)
            target.chmod(source.stat().st_mode & 0o777)
    bashrc = target_home / '.bashrc'
    source_line = '[ -f "$HOME/.config/ysyx/bashrc.sh" ] && . "$HOME/.config/ysyx/bashrc.sh"'
    old = bashrc.read_text(encoding='utf-8') if bashrc.is_file() else ''
    if source_line not in old:
        print(('APPEND ' if args.apply else 'WOULD APPEND ') + 'ysyx setup to .bashrc')
        if args.apply:
            save_existing(bashrc, Path('.bashrc'))
            bashrc.write_text(old.rstrip() + '\n\n# Personal ysyx configuration\n' + source_line + '\n', encoding='utf-8')
    print('Changed files: {}'.format(changed))
    if args.apply:
        print('Previous files saved under ' + str(backup))
    else:
        print('Preview only. Run with --apply to install.')

if __name__ == '__main__':
    main()
