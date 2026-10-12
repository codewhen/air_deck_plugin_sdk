package main

import (
	"encoding/json"
	"fmt"
	"os/exec"
	"runtime"

	"github.com/codewhen/air_deck_plugin_sdk/deck-plugins/sdk/go/decksdk"
)

const pluginID = "com.example.echo"

type plugin struct{}

func (p *plugin) Catalog() []decksdk.Button {
	return []decksdk.Button{{
		ID: "echo.beep", Title: "Echo Beep", IconKey: "plugins",
		Columns: 1, Rows: 1, Action: "beep", PluginID: pluginID,
		Editor: &decksdk.EditorOpts{Tap: true, Toggle: true},
	}}
}

func (p *plugin) Invoke(typ, action string, body, payload json.RawMessage) error {
	if action != "" && action != "beep" {
		return fmt.Errorf("unknown action: %s", action)
	}
	beep()
	return nil
}

func beep() {
	switch runtime.GOOS {
	case "darwin":
		if exec.Command("afplay", "/System/Library/Sounds/Tink.aiff").Run() != nil {
			_ = exec.Command("osascript", "-e", "beep").Run()
		}
	case "windows":
		_ = exec.Command("powershell", "-NoProfile", "-Command", "[console]::beep(880,180)").Run()
	default:
		_ = exec.Command("paplay", "/usr/share/sounds/freedesktop/stereo/message.oga").Run()
	}
}

func main() { decksdk.Run(&plugin{}) }
