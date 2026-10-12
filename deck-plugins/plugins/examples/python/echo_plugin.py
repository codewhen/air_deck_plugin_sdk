#!/usr/bin/env python3
"""Echo Beep — Python example plugin using the decksdk."""

from __future__ import annotations

import platform
import subprocess
import sys
from pathlib import Path

# Prefer the monorepo SDK without installing a package.
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "sdk" / "python"))

from decksdk import DeckPlugin, run  # noqa: E402

PLUGIN_ID = "com.example.echo"


class EchoPlugin(DeckPlugin):
    def catalog(self):
        return [
            {
                "id": "echo.beep",
                "title": "Echo Beep",
                "icon_key": "plugins",
                "columns": 1,
                "rows": 1,
                "action": "beep",
                "plugin_id": PLUGIN_ID,
                "editor": {"tap": True, "toggle": True},
            }
        ]

    def invoke(self, typ, action, body, payload):
        if action and action != "beep":
            raise ValueError(f"unknown action: {action}")
        beep()


def beep() -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            if subprocess.run(["afplay", "/System/Library/Sounds/Tink.aiff"]).returncode != 0:
                subprocess.run(["osascript", "-e", "beep"], check=False)
        elif system == "Windows":
            import winsound  # type: ignore

            winsound.Beep(880, 180)
        else:
            subprocess.run(
                ["paplay", "/usr/share/sounds/freedesktop/stereo/message.oga"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
    except Exception as exc:  # noqa: BLE001
        print(f"[echo] beep failed: {exc}", file=sys.stderr)


if __name__ == "__main__":
    run(EchoPlugin())
