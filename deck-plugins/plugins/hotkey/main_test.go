package main

import (
	"context"
	"encoding/json"
	"errors"
	coreapi "github.com/codewhen/airdeck-plugin-sdk/capabilities/generated/go/keyboard"
	"testing"
)

type recordingTransport struct {
	capability, method string
	request            any
	err                error
}

func (r *recordingTransport) Call(_ context.Context, cap, method string, request, result any) error {
	r.capability = cap
	r.method = method
	r.request = request
	return r.err
}
func (*recordingTransport) Subscribe(context.Context, string, string, func(json.RawMessage)) (func(), error) {
	panic("unexpected subscription")
}
func TestInvokeArgumentPrecedence(t *testing.T) {
	cases := []struct{ name, body, payload, action, want string }{
		{"body wins", "{\"combo\":\"Ctrl+A\"}", "{\"combo\":\"Ctrl+B\"}", "Ctrl+C", "Ctrl+A"},
		{"payload combo", "{}", "{\"combo\":\"Alt+B\"}", "Ctrl+C", "Alt+B"},
		{"body target", "{\"target\":\"Cmd+D\"}", "{}", "Ctrl+C", "Cmd+D"},
		{"payload target", "{}", "{\"target\":\"Shift+E\"}", "Ctrl+C", "Shift+E"},
		{"action fallback", "{}", "{}", "F12", "F12"},
		{"malformed body", "{", "{\"combo\":\"Ctrl+F\"}", "Ctrl+C", "Ctrl+F"},
		{"empty fallback", "", "", "", ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			transport := &recordingTransport{}
			p := plugin{client: coreapi.NewClient(transport)}
			if err := p.Invoke("deck", c.action, json.RawMessage(c.body), json.RawMessage(c.payload)); err != nil {
				t.Fatal(err)
			}
			request, ok := transport.request.(coreapi.Combo)
			if !ok || request.Combo != c.want || transport.capability != "core.keyboard" || transport.method != "hotkey" {
				t.Fatalf("wrong dispatch: %+v", transport)
			}
		})
	}
}
func TestInvokePropagatesCapabilityError(t *testing.T) {
	denied := errors.New("permission denied")
	p := plugin{client: coreapi.NewClient(&recordingTransport{err: denied})}
	if err := p.Invoke("deck", "run", nil, nil); !errors.Is(err, denied) {
		t.Fatalf("got %v", err)
	}
}
func TestCatalogActionIdentity(t *testing.T) {
	p := plugin{}
	buttons := p.Catalog()
	if len(buttons) != 1 {
		t.Fatalf("got %d buttons", len(buttons))
	}
	b := buttons[0]
	if b.PluginID != "com.airdeck.hotkey" || b.Action != "combo" || b.ID == "" || b.Title == "" || b.Editor == nil || !b.Editor.Tap || b.Editor.Toggle {
		t.Fatalf("wrong catalog: %+v", b)
	}
}
