# Public capability contracts and SDK generation

See [architecture](../docs/capability-architecture.md) and [plugin authoring](../deck-plugins/README.md).

Generate SDK contracts with `python3 capabilities/tools/generate.py`. To also regenerate app integration assets, pass `--host-root /path/to/air_mouse`. The SDK generator does not write into app directories by default.
For community providers, put schemas in a dedicated directory and pass `--schemas <directory> --out <output>`. Generated clients share a language-wide transport interface so new capabilities work with the existing plugin runtime. Generated Go interfaces include `Provider`, `Dispatch`, and `DispatchTyped`; Python, Java and C++ have equivalent provider dispatch bindings.

Go module: `github.com/codewhen/airdeck-plugin-sdk/capabilities`; clients are under `generated/go/<capability>`.
Python: install `deck-plugins/sdk/python`, then import `airdeck_sdk.core.media`.
Java: compile generated sources and the SDK with Gson 2.10+ and include Gson at runtime.
C++17: include the SDK and its `vendor` directory. Vendored nlohmann JSON 3.12.0 retains its upstream MIT license in the header.
Kotlin: generated serializers and clients are included in the Android application.

All SDKs provide typed methods/results/enums. Serialization occurs only at process/network boundaries; authorization is always enforced by the host.

`core.apps` 1.1 adds a bounded, typed installed-app catalog (`list`) protected by
`core.apps.read`, independently from `core.apps.launch`. Catalog entries carry
an ID, display name and exact launch target. Arrays reference named object types
with `items.$ref` and declare `maxItems`; generated clients decode their items.
Android caches each PC catalog by its paired certificate identity and searches
names locally. macOS discovery scans application bundles, while Windows scans
user and system Start Menu shortcuts. Custom launch targets remain supported.
Existing paired phones must approve the expanded read permission before use.
