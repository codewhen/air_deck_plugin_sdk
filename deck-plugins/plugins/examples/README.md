# Example plugins — Echo Beep

Four complete API v2 examples: Go, Python, Java and C++. Read the [developer documentation](../../../docs/plugin-development/index.mdx) for full tutorials.

From the SDK root, build standalone packages:

```sh
python3 tools/build_examples.py go
python3 tools/build_examples.py python
python3 tools/build_examples.py java --gson /absolute/path/to/gson.jar
python3 tools/build_examples.py cpp
```

Outputs are separated by language in `deck-plugins/dist/examples/`. Each Echo variant uses the same plugin ID; install one at a time. Python packages carry SDK runtime files. Java packages include Gson on the launcher's classpath. Python and Java still require their runtime on the user's computer. On Windows the builder uses Go at build time to create native runtime launchers; users do not need Go.

```sh
python3 tools/test_packaged_examples.py deck-plugins/dist/examples/python/com.example.echo.deckPlugin
```

This validates catalog, invoke and an invalid action after extraction to a directory outside the SDK checkout. Successful invokes play a short beep.

Use `--plugin-dir deck-plugins/plugins/my-plugin` with a copied/edited template to build your own plugin. Keep template filenames/class names for this builder and update manifest and catalog plugin IDs together. All diagnostics belong on stderr; SDK protocol messages belong on stdout.

Go typed provider/consumer examples remain in `capability-provider` and `capability-consumer`. Build those with `bash deck-plugins/scripts/build_all.sh`, then install the provider before the consumer.
