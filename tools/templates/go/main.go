package main

import (
    "encoding/json"
    "fmt"
    "os"
    "github.com/codewhen/air_deck_plugin_sdk/deck-plugins/sdk/go/decksdk"
)

const pluginID = __ID_JSON__
type plugin struct{}

func (p *plugin) Catalog() []decksdk.Button {
    return []decksdk.Button{{
        ID: "hello.say", Title: "Say hello", Action: "hello", PluginID: pluginID,
        IconKey: "plugins", Columns: 1, Rows: 1,
        Editor: &decksdk.EditorOpts{Tap: true},
    }}
}

func (p *plugin) Invoke(typ, action string, body, payload json.RawMessage) error {
    if action != "hello" { return fmt.Errorf("unknown action: %s", action) }
    fmt.Fprintln(os.Stderr, "Hello from AirDeck!")
    return nil
}

func main() { decksdk.Run(&plugin{}) }
