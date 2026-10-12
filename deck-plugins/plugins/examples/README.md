# Example plugins — Echo Beep

Minimal working `.deckPlugin` in four languages. Each plays a short system beep when tapped from the Stream Deck **Plugins** library.

Pick one language, copy the folder to `plugins/myplugin`, change `id` / name / logic, pack, install.

## Protocol (all languages)

Host ↔ plugin = **correlated API v2 JSON lines** on stdin/stdout. Every request and response carries `ipc_id`; use the SDK to handle correlation.

| Host → plugin | Plugin → host |
|---------------|---------------|
| `{"op":"catalog"}` | `{"op":"ok","buttons":[...]}` |
| `{"op":"invoke","type":"...","action":"beep",...}` | `{"op":"ok"}` or `{"op":"error","error":"..."}` |

Use the SDK in `../../sdk/` so you do not reimplement framing. Log diagnostics to **stderr** only.

## Go (recommended)

```bash
cd deck-plugins
go build -o plugins/examples/go/echo-plugin ./plugins/examples/go
./scripts/pack_deckplugin.sh plugins/examples/go
# → dist/com.example.echo.deckPlugin
```

Uses `sdk/go/decksdk`. Typed capability examples: `capability-provider` and `capability-consumer`.

## Python

```bash
chmod +x plugins/examples/python/echo_plugin.py
./scripts/pack_deckplugin.sh plugins/examples/python
```

The script adds `sdk/python` to `sys.path` so `decksdk` imports without install.

## Java

```bash
cd plugins/examples/java
javac -cp "$GSON_JAR" -d build \
  ../../../sdk/java/com/airdeck/decksdk/*.java \
  ../../../../capabilities/generated/java/com/airdeck/capabilities/*.java \
  EchoPlugin.java
jar cfe echo-plugin.jar com.example.echo.EchoPlugin \
  -C build .
chmod +x echo-plugin
cd ../../..
./scripts/pack_deckplugin.sh plugins/examples/java
```

Manifest entrypoint is the `echo-plugin` shell launcher (Windows: `echo-plugin.bat`); `echo-plugin.jar` is listed in `files`.

## C++

```bash
c++ -std=c++17 -O2 -I sdk/cpp -I sdk/cpp/vendor -o plugins/examples/cpp/echo-plugin plugins/examples/cpp/main.cpp
# or: cmake -S plugins/examples/cpp -B plugins/examples/cpp/build && cmake --build plugins/examples/cpp/build
./scripts/pack_deckplugin.sh plugins/examples/cpp
```

## Install & test

1. PC Helper → **Plugins** → **Add Plugin** → pick `com.example.echo.deckPlugin`
2. Restart the bridge if it was already running
3. On the phone Stream Deck library → **Plugins** → **Echo Beep**

## Manifest checklist

- `id` unique (e.g. `com.you.name`)
- `entrypoint` exists and is executable after pack
- `types` empty for invoke-only plugins (Echo); fill in for targeted wire types
- Never set `builtin: true` for third-party plugins
- Optional `config: "./config.json"` — packed automatically; PC Helper **Edit config** opens it with the OS default app (existing user config kept on reinstall)
- Optional catalog `editor: { "tap": true, "toggle": true }` to show the action in the Button Editor (Action Type → Plugin)

Java packaging must include Gson and generated capability classes in the plugin JAR or classpath. See the API v2 SDK integration fixtures under `capabilities/tests/fixtures`.
