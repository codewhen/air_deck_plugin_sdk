#!/usr/bin/env bash
# Build builtin Go plugins and pack .deckPlugin archives into dist/.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ASSETS=""
if [[ "$#" -gt 0 ]]; then
  if [[ "$#" -ne 2 || "$1" != "--bundle-to" ]]; then
    echo "Usage: $0 [--bundle-to PC_APP_ASSETS_DIRECTORY]" >&2
    exit 2
  fi
  ASSETS="$2"
fi
cd "$ROOT"
export GOMODCACHE="${GOMODCACHE:-$HOME/go/pkg/mod}"

build_one() {
  local name="$1"
  local bin="$2"
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*|Windows_NT)
      rm -f "plugins/$name/${bin}"
      bin="${bin}.exe"
      ;;
  esac
  echo "building $name..."
  ( cd "plugins/$name" && go build -o "$bin" . )
  ./scripts/pack_deckplugin.sh "plugins/$name" "$ROOT/dist"
}

mkdir -p dist
chmod +x scripts/pack_deckplugin.sh
build_one hotkey hotkey-plugin
build_one launch launch-plugin
build_one examples/go echo-plugin
build_one examples/capability-provider counter-plugin
build_one examples/capability-consumer counter-reader

# Exercise every plugin package so platform-specific adapters fail before
# packaging rather than at runtime.
go test ./...

# Ship builtins into PC Helper assets (firmware loads them after ensureBundledPlugins).
# Private plugins are built separately by the private app repository.
if [[ -n "$ASSETS" ]]; then
mkdir -p "$ASSETS"
BUILTINS=(
  com.airdeck.hotkey
  com.airdeck.launch
)
for id in "${BUILTINS[@]}"; do
  f="$ROOT/dist/${id}.deckPlugin"
  [[ -f "$f" ]] || continue
  cp "$f" "$ASSETS/"
  echo "bundled → $ASSETS/$(basename "$f")"
done

fi

echo "done → $ROOT/dist"
ls -la dist/
