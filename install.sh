#!/usr/bin/env bash
set -euo pipefail
dotfiles_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
exec python3 "$dotfiles_dir/install.py" "$@"
