# AirDeck PC plugins — API v2

Plugins contribute Stream Deck actions using the same public SDK whether bundled or community-authored. They may call permission-controlled capabilities and provide namespaced capabilities for other plugins. Dedicated mobile plugin layouts are not included yet.

```json
{
  "id": "com.example.media-tools",
  "name": "Media Tools",
  "version": "1.0.0",
  "api_version": 2,
  "entrypoint": "./media-tools",
  "permissions": ["core.media.playback.read", "core.media.playback.control"],
  "uses": [{"id": "core.media", "min_version": "1.0.0", "max_version": "2.0.0"}],
  "files": []
}
```

All declared permissions are required. Users approve before execution and can view/revoke them in Plugins. Adding permissions in an update requires approval. Bundled plugins can be removed or disabled and have no elevated permissions.

Go plugins implement the catalog/invoke interface and optional `Init(*decksdk.Host)`:

```go
func (p *plugin) Init(host *decksdk.Host) {
    p.media = media.NewClient(host)
}
// During an invocation:
_, err := p.media.TogglePlayback(ctx, media.Empty{})
```

Python plugins use `init(host)` and import `Client, Empty` from `airdeck_sdk.core.media`. Java plugins implement `PluginHost.Initializer`; C++ plugins override `init(Host&)`. Readers remain active during invocations. Only SDK JSON messages may go to stdout; diagnostics use stderr.

Providers declare `capability_schemas` paths in their source manifest. Packing validates and embeds those schemas into the packaged manifest's `capabilities`, adding schema resources to `files`. Capability IDs and permission IDs start with the provider's plugin ID. Use the public generator to produce provider/client code. Register generated dispatch using `host.Provide`, `host.provide`, or the equivalent API; publish declared topic values through `host.Publish`/`publish`.

Consumers declare both `dependencies` (plugin ID, `min_version`, optional exclusive `max_version`) and `uses` (capability ID, `provider`, compatible versions). Dependencies download only from the configured marketplace or bundled archives, with one approval flow for the resolved package set.

See `plugins/examples/capability-provider` and `capability-consumer` for a typed counter provider/consumer, and the Echo examples for basic plugins in Go, Python, Java and C++. Build and pack:

```sh
cd deck-plugins
./scripts/build_all.sh
# Individual package:
./scripts/pack_deckplugin.sh plugins/myplugin
```

The PC helper offers hotkey and launch packages. OBS is maintained outside this public repository; its implementation is private. Core mouse, keyboard, media and volume functionality is hosted in Go without sidecars. Legacy plugins must adopt API v2 and required permission declarations; see [architecture and migration](../docs/capability-architecture.md).

### Bundling into the PC Helper

The SDK build only writes plugin packages into `dist/`. The app build passes an explicit destination:

```sh
./scripts/build_all.sh --bundle-to /absolute/path/to/air_mouse/pc_app/assets/plugins
```
