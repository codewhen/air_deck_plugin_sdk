#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$ROOT/capabilities/tools/pack_plugin.py" "${1:?usage: pack_deckplugin.sh <plugin-dir> [out_dir]}" "${2:-$ROOT/deck-plugins/dist}"
