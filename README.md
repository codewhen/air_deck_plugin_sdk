# AirDeck Plugin SDK

Open-source SDK, capability contracts and examples for community AirDeck plugins.

- [Plugin authoring and protocol](deck-plugins/README.md)
- [Examples](deck-plugins/plugins/examples/README.md)
- [Capability architecture](docs/capability-architecture.md)
- [Capability generator](capabilities/README.md)

## Build and test

Install Go matching `deck-plugins/go.mod` and Python 3.11 or newer.

```sh
cd deck-plugins
go test ./...
./scripts/build_all.sh
cd ..
python3 -m unittest discover -s deck-plugins/sdk/python/tests -v
python3 -m unittest discover -s capabilities/tests -p test_contracts.py -v
```

Packages are written to `deck-plugins/dist/`. Install `.deckPlugin` packages using the released PC Helper's Plugins interface. The Android and PC Helper sources are not required to author plugins.

Cross-language integration checks additionally require a C++17 compiler, a JDK and Gson; set `GSON_JAR` to your Gson jar, then run:

```sh
python3 -m unittest discover -s capabilities/tests -v
```

Regenerate SDK contracts with `python3 capabilities/tools/generate.py`. Private host asset generation is opt-in through `--host-root /path/to/app`.

## License

Project code is licensed under Apache-2.0. Vendored third-party files retain their own licenses; see THIRD_PARTY_NOTICES.md.

## Community plugin development

This public repository provides SDK source, capability contracts, examples and packaging tools for creating independent community plugins. Developers may build and include the SDK in their own plugin executables under its license. Their plugins may be open source or closed source, free or paid. AirDeck-owned private plugin implementations are maintained outside this repository and may be distributed as binary packages. The SDK is a library/toolkit; it does not require bundling a separate SDK executable.
