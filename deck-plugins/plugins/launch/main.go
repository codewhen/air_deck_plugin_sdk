package main

import (
	"context"
	"encoding/json"
	coreapi "github.com/codewhen/air_deck_plugin_sdk/capabilities/generated/go/apps"

	"github.com/codewhen/air_deck_plugin_sdk/deck-plugins/sdk/go/decksdk"
)

type plugin struct{ client *coreapi.Client }

func (p *plugin) Init(host *decksdk.Host) { p.client = coreapi.NewClient(host) }

func (p *plugin) Catalog() []decksdk.Button {
	return []decksdk.Button{{
		ID: "launch.app", Title: "Launch Application", IconKey: "apps",
		Action: "launch", PluginID: "com.airdeck.launch",
		Editor: &decksdk.EditorOpts{Tap: true},
	}}
}

func (p *plugin) Invoke(typ, action string, body, payload json.RawMessage) error {
	var b struct {
		Path   string `json:"path"`
		App    string `json:"app"`
		Target string `json:"target"`
	}
	_ = decksdk.DecodeBody(body, &b)
	if b.Path == "" && b.App == "" {
		_ = decksdk.DecodeBody(payload, &b)
	}
	target := b.Path
	if target == "" {
		target = b.App
	}
	if target == "" {
		target = b.Target
	}
	if target == "" {
		target = action
	}
	_, err := p.client.Launch(context.Background(), coreapi.Launch{Target: target})
	return err
}

func main() { decksdk.Run(&plugin{}) }
