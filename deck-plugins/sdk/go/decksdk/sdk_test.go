package decksdk

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"io"
	"testing"
)

func TestDecodeBody(t *testing.T) {
	for _, raw := range []json.RawMessage{nil, {}, json.RawMessage(`{}`), json.RawMessage(`{"name":"Deck"}`)} {
		var got struct {
			Name string `json:"name"`
		}
		if err := DecodeBody(raw, &got); err != nil {
			t.Fatal(err)
		}
		if len(raw) > 2 && got.Name != "Deck" {
			t.Fatalf("lost field: %+v", got)
		}
	}
	for _, raw := range []string{`{`, `[]`, `"text"`} {
		var got struct{}
		if DecodeBody(json.RawMessage(raw), &got) == nil {
			t.Fatalf("accepted %s", raw)
		}
	}
}
func TestWantsAck(t *testing.T) {
	yes, no := true, false
	for _, c := range []struct {
		ack  *bool
		want bool
	}{{nil, true}, {&yes, true}, {&no, false}} {
		if wantsAck(Request{Ack: c.ack}) != c.want {
			t.Fatal("wrong ack default")
		}
	}
}

type failingWriter struct{}

func (failingWriter) Write([]byte) (int, error) { return 0, io.ErrClosedPipe }
func TestExchangeCleansPendingOnSendFailure(t *testing.T) {
	h := NewHost(bytes.NewReader(nil), failingWriter{})
	_, err := h.exchange(context.Background(), Request{Op: "capability.call"})
	if !errors.Is(err, io.ErrClosedPipe) {
		t.Fatalf("got %v", err)
	}
	if len(h.pending) != 0 {
		t.Fatal("pending request leaked")
	}
}
func TestCanceledExchangeSendsCancellationAndCleansPending(t *testing.T) {
	var output bytes.Buffer
	h := NewHost(bytes.NewReader(nil), &output)
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	_, err := h.exchange(ctx, Request{Op: "capability.call", IPCID: "test-1"})
	var ce *CapabilityError
	if !errors.As(err, &ce) || ce.Code != "timeout" {
		t.Fatalf("got %v", err)
	}
	if len(h.pending) != 0 {
		t.Fatal("pending request leaked")
	}
	decoder := json.NewDecoder(&output)
	var call, cancellation Request
	if err := decoder.Decode(&call); err != nil {
		t.Fatal(err)
	}
	if err := decoder.Decode(&cancellation); err != nil {
		t.Fatal(err)
	}
	if call.IPCID != "test-1" || cancellation.Op != "capability.cancel" || cancellation.Action != call.IPCID {
		t.Fatalf("wrong cancellation %+v", cancellation)
	}
}
func TestDisconnectedExchangeCleansPending(t *testing.T) {
	h := NewHost(bytes.NewReader(nil), io.Discard)
	close(h.done)
	_, err := h.exchange(context.Background(), Request{Op: "capability.call"})
	var ce *CapabilityError
	if !errors.As(err, &ce) || ce.Code != "provider_failed" {
		t.Fatalf("got %v", err)
	}
	if len(h.pending) != 0 {
		t.Fatal("pending request leaked")
	}
}
