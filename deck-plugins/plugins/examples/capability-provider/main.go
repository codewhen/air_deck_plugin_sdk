package main

import (
	"context"
	"encoding/json"
	counter "github.com/codewhen/airdeck-plugin-sdk/deck-plugins/sdk/generated-examples/go/com_example_counter_counter"
	"github.com/codewhen/airdeck-plugin-sdk/deck-plugins/sdk/go/decksdk"
)

type plugin struct{}

func (p *plugin) Init(h *decksdk.Host) {
	h.Provide("com.example.counter.counter", func(ctx context.Context, m string, q json.RawMessage) (any, error) {
		return counter.Dispatch(ctx, p, m, q)
	})
 _ = h.Publish(context.Background(),"com.example.counter.counter","count",counter.Count{Value:42})
}
func (p *plugin) GetCount(context.Context, counter.Empty) (counter.Count, error) {
	return counter.Count{Value: 42}, nil
}
func (p *plugin) Catalog() []decksdk.Button                                     { return nil }
func (p *plugin) Invoke(string, string, json.RawMessage, json.RawMessage) error { return nil }
func main()                                                                     { decksdk.Run(&plugin{}) }
