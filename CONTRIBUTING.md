# Contributing

Open an issue describing your proposal or bug, then submit a focused pull request with relevant tests. Run the SDK tests described in README.md before submitting.

Keep protocol and permission changes backward compatible within a major version. Breaking capability contract changes require a major version increase and updated fixtures. Generated files come from capability schemas; update schemas and regenerate rather than editing generated clients manually.

Keep diagnostics on stderr and protocol messages on stdout. Do not commit credentials, personal OBS configuration, built executables or plugin archives. Contributions are accepted under the project's Apache-2.0 license.
