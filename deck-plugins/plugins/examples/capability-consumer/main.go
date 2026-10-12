package main

import (
	"context"
	"encoding/json"
	"fmt"
	counter "github.com/codewhen/airdeck-plugin-sdk/deck-plugins/sdk/generated-examples/go/com_example_counter_counter"
	"github.com/codewhen/airdeck-plugin-sdk/deck-plugins/sdk/go/decksdk"
	"os"
)

type plugin struct{ client *counter.Client }

func (p *plugin) Init(h *decksdk.Host) { p.client = counter.NewClient(h) }
func (p *plugin) Catalog() []decksdk.Button {
	return []decksdk.Button{{ID: "counter.read", Title: "Read Counter", Action: "read", Editor: &decksdk.EditorOpts{Tap: true}}}
}
func (p *plugin) Invoke(string, string, json.RawMessage, json.RawMessage) error {
	v, e := p.client.GetCount(context.Background(), counter.Empty{})
	if e == nil {
		fmt.Fprintln(os.Stderr, "Counter:", v.Value)
	}
	return e
}
func main() { decksdk.Run(&plugin{}) }
