package main

import (
	"context"
	"encoding/json"
	"errors"
	coreapi "github.com/codewhen/airdeck-plugin-sdk/capabilities/generated/go/apps"
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
		{"path wins", "{\"path\":\"/body\",\"app\":\"body-app\"}", "{\"path\":\"/payload\"}", "fallback", "/body"},
		{"body app", "{\"app\":\"body-app\",\"target\":\"target\"}", "{}", "fallback", "body-app"},
		{"payload path", "{}", "{\"path\":\"/payload\"}", "fallback", "/payload"},
		{"payload app", "{}", "{\"app\":\"payload-app\"}", "fallback", "payload-app"},
		{"body target", "{\"target\":\"target\"}", "{}", "fallback", "target"},
		{"payload target", "{}", "{\"target\":\"payload-target\"}", "fallback", "payload-target"},
		{"action fallback", "{}", "{}", "fallback", "fallback"},
		{"malformed body", "{", "{\"path\":\"/payload\"}", "fallback", "/payload"},
		{"empty fallback", "", "", "", ""},
	}
	for _, c := range cases {
		t.Run(c.name, func(t *testing.T) {
			transport := &recordingTransport{}
			p := plugin{client: coreapi.NewClient(transport)}
			if err := p.Invoke("deck", c.action, json.RawMessage(c.body), json.RawMessage(c.payload)); err != nil {
				t.Fatal(err)
			}
			request, ok := transport.request.(coreapi.Launch)
			if !ok || request.Target != c.want || transport.capability != "core.apps" || transport.method != "launch" {
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
	if b.PluginID != "com.airdeck.launch" || b.Action != "launch" || b.ID == "" || b.Title == "" || b.Editor == nil || !b.Editor.Tap || b.Editor.Toggle {
		t.Fatalf("wrong catalog: %+v", b)
	}
}
