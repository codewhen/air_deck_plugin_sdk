# Capabilities, plugins and Android resources

The Go runtime owns the capability gateway, providers, permission grants, state cache and scheduler. Flutter owns installation and approval UI. Android owns layouts and resource packs. A layout binds to a core capability or a plugin action; it never grants privileges.

## Core contracts

`capabilities/schemas/` is the public source of truth. Generate clients/types with:

```sh
python3 capabilities/tools/generate.py
# Optional compatibility check against previously released contracts:
python3 capabilities/tools/generate.py --baseline /path/to/released/schemas
```

Generated Go, Python, Java, C++ and Kotlin clients hide JSON routing. Each method and topic declares permissions; required permissions have descriptions in the contract. Contracts currently support closed objects containing strings/enums, booleans, integers and numbers with range constraints; fields are required in this schema version. Breaking existing types/methods/topics requires a new major contract version; additive operations can use the current major version.

Core providers are `core.pointer`, `core.keyboard`, `core.media` (playback, track, volume and mute), and `core.apps`. Native adapters live under `firmware/internal/core/native`. Hotkeys and launching remain removable plugins using core primitives. Mouse, keyboard, media and volume sidecars are retired. No plugin executable is needed for dedicated controls or media/volume deck tiles.

## Permissions and identity

The gateway takes a caller established by an authenticated phone session or plugin process, never one supplied in a message. It checks method/topic permissions, validates input/results, and dispatches through typed Go interfaces. Host code can use generated clients with `gateway.Local(caller)` to call in-process providers without JSON serialization; the same gateway checks permissions and values. Plugin permissions are all required. Approval grants the entire requested set; revocation disables the plugin and closes subscriptions. Permission groups expand to explicit grants at approval time; later additions are not inherited.

Plugin approvals live in `plugin-grants.json` beside the plugins directory. Their digest covers the manifest, executable and declared resources, excluding editable configuration. Community package replacement invalidates approval until approved through the installer. Every package, including one declaring `builtin: true`, requires host-owned approval for its exact digest and expanded permissions. Only synchronization of verified shipped asset bytes provisions bundled approvals. A running process still loses access if its package changes. Declared permissions and grants are separate. Plugin-provided capabilities cannot replace `core.*` or another provider's namespace.

Phone approval grants the dedicated pointer, keyboard-key, media and installed-app catalog read permission set. Existing phones without those grants must pair with manual approval again. The phone cannot directly use `core.apps` or keyboard hotkeys; those run through approved deck plugins.

These are capability gateway permissions, not an OS sandbox. Native plugin executables can still call OS APIs directly.

## State and lifecycle

Read/subscribe endpoints expose separate playback, track and volume payloads. Subscribers get a cached initial snapshot and changed values; slow consumers receive the newest state through bounded/coalescing queues. The runtime owns polling cadence and diagnostics. Core media has one refresh job, independent of subscriber count, and stops polling without consumers. Desktop commands refresh observed state; successful command completion is distinct from observed state.

Executable IPC uses correlated `ipc_id` values and separate readers/handlers, so a plugin may call another capability during an invocation. Timeouts discard late results; cancellation messages cancel host-side calls. Provider failure unregisters capabilities and deactivates dependent plugins; reload is the explicit recovery operation. Dedicated media and visible media deck controls own subscriptions and release them on leaving the screen.

## Providers and dependencies

Plugins declare required plugin IDs and version ranges, plus capability `uses` entries. Core uses do not need a plugin dependency. Plugin uses identify the exact provider and require a matching dependency. Minimum versions are inclusive; maximum versions are exclusive.

Installation resolves bundled packages or the configured marketplace by plugin ID. It rejects cycles, wrong identities and incompatible/missing providers before executing anything. The approval view shows every package being installed and its requested permissions. Staging/rollback preserves prior packages and configuration on commit failure. Removing or disabling a provider disables its dependent plugins while preserving their files.

Only hotkey and launch are bundled by default. The manifest `builtin` flag is display metadata and grants no trust; every user import or download requires explicit permission approval. Startup refreshes installed built-ins and installs them on first use, while recorded removals prevent automatic reinstalls. Existing community legacy packages retain configuration but need API v2 and approval before activation; shipped built-ins upgrade automatically.

## Compatibility and validation

Wire protocol 5 and component versions 1.4.0 ship together. Saved legacy media/volume/mouse/keyboard bindings translate to core bindings; hotkey, launch and community IDs remain intact. Missing plugins/icons preserve references.

Run Go tests in both modules, Flutter tests/analyzer, Android compilation/unit tests, and `python3 -m unittest discover -s capabilities/tests -v`. Java fixture tests need Gson (`GSON_JAR`, or a cached Gradle Gson jar). C++ includes the pinned MIT-licensed nlohmann JSON header.

Windows CI uses C++/WinRT SDK headers for track/playback observation. MinGW-only cross builds without those headers retain input, playback commands and volume state, but report track/playback observation unavailable. Test actual OS interaction on Windows and macOS before release; compilation does not substitute for a hardware smoke test.

## Implementation boundaries

`firmware/internal/core/core.go` is the composition root. Each capability has its own provider and narrow native dependency interfaces. Media owns snapshot freshness; a dispatch decorator applies the same refresh policy to typed and JSON calls. The gateway resolves permissions through one shared authorization path, and activation checks index contracts and permission ownership before starting plugins.

On Android, `CapabilityConnection` implements only the generated transport contract. `CoreCommands` translates saved deck actions into typed calls; `UdpSession` owns the authenticated connection. `IconPackRules` and `IconPackArchive` validate resources without Android APIs, `IconPacks` owns app-private storage, and Stream Deck presentation observes changes and decodes images off the UI thread.

PC plugin data models live under `data/models/plugin.dart`. Installation and grant storage stay in the repository layer. Installed-plugin scans share one grants snapshot while retaining package digest verification. Application startup refreshes verified shipped assets and records approvals for those bytes before starting the runtime, preserving configuration and disabled state. Removal markers prevent reinstalls until an explicit reinstall.

The former plugin broker registry and media wire messages are removed. Capability
subscriptions are the single state path; Android volume and saved mute controls
read the same typed media snapshot as the dedicated screen. The Go SDK's optional
`Poll() error` refreshes its source and publishes through `Host.Publish`; it does
not return broker states. API v1 packages remain inactive until upgraded.

Native adapters mirror the capability boundaries under
`firmware/internal/core/native`: `pointer` owns mouse injection, `keyboard` owns
keys and hotkey combinations, `apps` owns launching, and `media` owns playback,
metadata, output volume and mute. Volume and hotkeys are operations within those
capabilities, not separate native packages or plugins.

### Source organization

Contract definitions and value validation live in `capability/contract.go`;
`gateway.go` owns provider registration, grants and shared state. Typed local
transport remains in `local.go`. Contract validation does not depend on the
plugin loader or server.

The server separates plugin activation and dependency cleanup (`plugins.go`),
phone grant persistence (`phone_permissions.go`), capability wire requests
(`capabilities.go`), and subscriber-driven polling (`capability_polling.go`).
These files share server state; they do not introduce parallel runtimes.

The executable loader has a single API v2 correlated request path in
`sidecar.go`; capability consumer/provider handling lives in `capabilities.go`.
Legacy packages are rejected by the authorized loader, rather than supported
by a second IPC loop. Lifecycle fixtures use that same v2 protocol.

The PC installation repository keeps contract checks in `plugin_contracts.dart`
and uses one transitive dependency traversal for both impact reporting and
provider disablement. These are private parts of the repository library, not
additional public services.
