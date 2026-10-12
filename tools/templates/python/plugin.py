#!/usr/bin/env python3
import sys
from pathlib import Path

# Installed packages use the local SDK; source development uses the checkout.
local_sdk = Path(__file__).resolve().parent / "sdk"
sdk = local_sdk if local_sdk.is_dir() else Path(__file__).resolve().parents[2] / "sdk" / "python"
sys.path.insert(0, str(sdk))
from decksdk import DeckPlugin, run

PLUGIN_ID = __ID_JSON__

class Plugin(DeckPlugin):
    def catalog(self):
        return [{"id": "hello.say", "title": "Say hello", "action": "hello",
                 "plugin_id": PLUGIN_ID, "icon_key": "plugins", "columns": 1,
                 "rows": 1, "editor": {"tap": True}}]

    def invoke(self, typ, action, body, payload):
        if action != "hello":
            raise ValueError(f"unknown action: {action}")
        print("Hello from AirDeck!", file=sys.stderr)

if __name__ == "__main__":
    run(Plugin())
