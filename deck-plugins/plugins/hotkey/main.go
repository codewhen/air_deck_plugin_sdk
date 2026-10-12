package main

import (
	"context"
	"encoding/json"
	coreapi "github.com/codewhen/air_deck_plugin_sdk/capabilities/generated/go/keyboard"

	"github.com/codewhen/air_deck_plugin_sdk/deck-plugins/sdk/go/decksdk"
)

type plugin struct{ client *coreapi.Client }

func (p *plugin) Init(host *decksdk.Host) { p.client = coreapi.NewClient(host) }

func (p *plugin) Catalog() []decksdk.Button {
	return []decksdk.Button{{
		ID: "hotkey.combo", Title: "Keyboard Shortcut", IconKey: "keyboard",
		Action: "combo", PluginID: "com.airdeck.hotkey",
		Editor: &decksdk.EditorOpts{Tap: true},
	}}
}

func (p *plugin) Invoke(typ, action string, body, payload json.RawMessage) error {
	var b struct {
		Combo  string `json:"combo"`
		Target string `json:"target"`
	}
	_ = decksdk.DecodeBody(body, &b)
	if b.Combo == "" {
		_ = decksdk.DecodeBody(payload, &b)
	}
	combo := b.Combo
	if combo == "" {
		combo = b.Target
	}
	if combo == "" {
		combo = action
	}
	_, err := p.client.Hotkey(context.Background(), coreapi.Combo{Combo: combo})
	return err
}

func main() { decksdk.Run(&plugin{}) }
