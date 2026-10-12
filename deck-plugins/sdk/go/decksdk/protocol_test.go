package decksdk

import (
	"bufio"
	"context"
	"encoding/json"
	"errors"
	"io"
	"sync/atomic"
	"testing"
	"time"
)

type protocolPlugin struct {
	fail  bool
	polls atomic.Int32
}

func (*protocolPlugin) Catalog() []Button {
	return []Button{{ID: "test", Title: "Test", Action: "run"}}
}
func (p *protocolPlugin) Invoke(string, string, json.RawMessage, json.RawMessage) error {
	if p.fail {
		return &CapabilityError{"permission_denied", "not granted"}
	}
	return nil
}
func (p *protocolPlugin) Poll() error { p.polls.Add(1); return nil }

type harness struct {
	host     *Host
	input    *io.PipeWriter
	messages chan []byte
}

func newHarness(t *testing.T, p Plugin) *harness {
	t.Helper()
	inR, inW := io.Pipe()
	outR, outW := io.Pipe()
	h := &harness{host: NewHost(inR, outW), input: inW, messages: make(chan []byte, 32)}
	done := make(chan struct{})
	go func() { RunWithHost(p, h.host); close(done) }()
	go func() {
		scanner := bufio.NewScanner(outR)
		for scanner.Scan() {
			h.messages <- append([]byte(nil), scanner.Bytes()...)
		}
	}()
	t.Cleanup(func() {
		inW.Close()
		outR.Close()
		outW.Close()
		inR.Close()
		select {
		case <-done:
		case <-time.After(time.Second):
			t.Error("host reader did not stop")
		}
	})
	return h
}
func (h *harness) send(t *testing.T, r Request) {
	t.Helper()
	if err := json.NewEncoder(h.input).Encode(r); err != nil {
		t.Fatal(err)
	}
}
func (h *harness) receive(t *testing.T) Response {
	t.Helper()
	select {
	case raw := <-h.messages:
		var r Response
		if err := json.Unmarshal(raw, &r); err != nil {
			t.Fatal(err)
		}
		return r
	case <-time.After(time.Second):
		t.Fatal("host response timed out")
		return Response{}
	}
}
func TestDispatchCatalogPollProviderAndErrors(t *testing.T) {
	p := &protocolPlugin{fail: true}
	h := newHarness(t, p)
	h.host.Provide("test", func(_ context.Context, method string, payload json.RawMessage) (any, error) {
		return map[string]string{"method": method}, nil
	})
	cases := []struct{ op, cap, code string }{{"catalog", "", ""}, {"poll", "", ""}, {"invoke", "", "permission_denied"}, {"capability.invoke", "test", ""}, {"capability.invoke", "missing", "capability_unavailable"}, {"unknown", "", "invalid_arguments"}}
	for _, c := range cases {
		t.Run(c.op+c.cap, func(t *testing.T) {
			h.send(t, Request{Op: c.op, Capability: c.cap, IPCID: "id", Action: "run"})
			r := h.receive(t)
			if r.IPCID != "id" || r.Code != c.code {
				t.Fatalf("wrong response %+v", r)
			}
			if c.code != "" && r.Op != "error" {
				t.Fatal("failure acknowledged as ok")
			}
			if c.op == "catalog" && len(r.Buttons) != 1 {
				t.Fatal("lost catalog")
			}
			if c.cap == "test" && r.Value.(map[string]any)["method"] != "run" {
				t.Fatal("provider arguments lost")
			}
		})
	}
	if p.polls.Load() != 1 {
		t.Fatal("poll not dispatched")
	}
}
func TestCallAndPublishRepliesAndMarshalFailures(t *testing.T) {
	h := newHarness(t, &protocolPlugin{})
	for _, failure := range []bool{false, true} {
		done := make(chan error, 1)
		go func() {
			var result map[string]int
			err := h.host.Call(context.Background(), "test", "get", map[string]int{"n": 1}, &result)
			if err == nil && result["n"] != 2 {
				err = errors.New("wrong result")
			}
			done <- err
		}()
		q := h.receiveRequest(t)
		if q.Op != "capability.call" || q.Capability != "test" || q.Action != "get" {
			t.Fatalf("wrong call %+v", q)
		}
		reply := Request{Op: "capability.result", IPCID: q.IPCID, Value: json.RawMessage(`{"n":2}`)}
		if failure {
			reply.Error = "denied"
			reply.Code = "permission_denied"
		}
		h.send(t, reply)
		err := <-done
		if failure {
			var ce *CapabilityError
			if !errors.As(err, &ce) || ce.Code != "permission_denied" {
				t.Fatalf("wrong error %v", err)
			}
		} else if err != nil {
			t.Fatal(err)
		}
	}
	done := make(chan error, 1)
	go func() { done <- h.host.Publish(context.Background(), "test", "state", map[string]int{"n": 3}) }()
	q := h.receiveRequest(t)
	if q.Op != "capability.publish" || q.Topic != "state" || string(q.Value) != `{"n":3}` {
		t.Fatalf("wrong publish %+v", q)
	}
	h.send(t, Request{Op: "capability.result", IPCID: q.IPCID, Value: json.RawMessage(`{}`)})
	if err := <-done; err != nil {
		t.Fatal(err)
	}
	if h.host.Call(context.Background(), "test", "get", make(chan int), nil) == nil || h.host.Publish(context.Background(), "test", "state", make(chan int)) == nil {
		t.Fatal("marshal failure ignored")
	}
}

func (h *harness) receiveRequest(t *testing.T) Request {
	t.Helper()
	select {
	case raw := <-h.messages:
		var q Request
		if err := json.Unmarshal(raw, &q); err != nil {
			t.Fatal(err)
		}
		return q
	case <-time.After(time.Second):
		t.Fatal("request timed out")
		return Request{}
	}
}
func TestSubscribeRoutesStateAndStopCleansCallback(t *testing.T) {
	for _, failure := range []bool{false, true} {
		t.Run(map[bool]string{false: "success", true: "denied"}[failure], func(t *testing.T) {
			h := newHarness(t, &protocolPlugin{})
			states := make(chan json.RawMessage, 1)
			type result struct {
				stop func()
				err  error
			}
			done := make(chan result, 1)
			go func() {
				stop, err := h.host.Subscribe(context.Background(), "test", "state", func(raw json.RawMessage) { states <- raw })
				done <- result{stop, err}
			}()
			q := h.receiveRequest(t)
			if q.Op != "capability.subscribe" || q.Topic != "state" {
				t.Fatalf("wrong subscription %+v", q)
			}
			reply := Request{Op: "capability.result", IPCID: q.IPCID, Value: json.RawMessage(`{}`)}
			if failure {
				reply.Code = "permission_denied"
				reply.Error = "denied"
			}
			h.send(t, reply)
			r := <-done
			if failure {
				if r.err == nil || r.stop != nil {
					t.Fatal("failed subscription returned active callback")
				}
			} else {
				if r.err != nil {
					t.Fatal(r.err)
				}
				h.send(t, Request{Op: "capability.state", IPCID: q.IPCID, Value: json.RawMessage(`{"value":{"n":5}}`)})
				select {
				case raw := <-states:
					if string(raw) != `{"n":5}` {
						t.Fatalf("wrong state %s", raw)
					}
				case <-time.After(time.Second):
					t.Fatal("state callback not invoked")
				}
				r.stop()
			}
			cancel := h.receiveRequest(t)
			if cancel.Op != "capability.unsubscribe" || cancel.Action != q.IPCID {
				t.Fatalf("wrong unsubscribe %+v", cancel)
			}
			h.host.mu.Lock()
			count := len(h.host.subscriptions)
			h.host.mu.Unlock()
			if count != 0 {
				t.Fatal("subscription leaked")
			}
		})
	}
}
func TestCallRejectsMalformedResultAndUnknownResultsAreIgnored(t *testing.T) {
	h := newHarness(t, &protocolPlugin{})
	h.send(t, Request{Op: "capability.result", IPCID: "unknown", Value: json.RawMessage(`{}`)})
	done := make(chan error, 1)
	go func() {
		var result struct{}
		done <- h.host.Call(context.Background(), "test", "get", struct{}{}, &result)
	}()
	q := h.receiveRequest(t)
	h.send(t, Request{Op: "capability.result", IPCID: q.IPCID, Value: json.RawMessage(`[]`)})
	if err := <-done; err == nil {
		t.Fatal("malformed result accepted")
	}
	h.host.mu.Lock()
	count := len(h.host.pending)
	h.host.mu.Unlock()
	if count != 0 {
		t.Fatal("pending call leaked")
	}
}
