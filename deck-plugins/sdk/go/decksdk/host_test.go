package decksdk

import (
	"bufio"
	"context"
	"encoding/json"
	"io"
	"testing"
	"time"
)

type callingPlugin struct{ host *Host }

func (p *callingPlugin) Init(h *Host)      { p.host = h }
func (p *callingPlugin) Catalog() []Button { return nil }
func (p *callingPlugin) Invoke(string, string, json.RawMessage, json.RawMessage) error {
	var result struct{}
	return p.host.Call(context.Background(), "core.media", "pause", struct{}{}, &result)
}
func TestCapabilityCallInsideInvocation(t *testing.T) {
	inR, inW := io.Pipe()
	outR, outW := io.Pipe()
	h := NewHost(inR, outW)
	finished := make(chan struct{})
	go func() { RunWithHost(&callingPlugin{}, h); close(finished) }()
	defer inW.Close()
	defer outR.Close()
	encoder := json.NewEncoder(inW)
	_ = encoder.Encode(Request{Op: "invoke", IPCID: "invoke-1"})
	scanner := bufio.NewScanner(outR)
	line := make(chan Request, 1)
	go func() {
		for scanner.Scan() {
			var q Request
			_ = json.Unmarshal(scanner.Bytes(), &q)
			line <- q
		}
	}()
	select {
	case q := <-line:
		if q.Op != "capability.call" {
			t.Fatalf("unexpected %s", q.Op)
		}
		_ = encoder.Encode(Request{Op: "capability.result", IPCID: q.IPCID, Value: json.RawMessage(`{}`)})
	case <-time.After(time.Second):
		t.Fatal("nested call deadlocked")
	}
	select {
	case q := <-line:
		if q.Op != "ok" || q.IPCID != "invoke-1" {
			t.Fatalf("unexpected response %#v", q)
		}
	case <-time.After(time.Second):
		t.Fatal("invocation response deadlocked")
	}
	inW.Close()
	select {
	case <-finished:
	case <-time.After(time.Second):
		t.Fatal("reader did not stop")
	}
}
