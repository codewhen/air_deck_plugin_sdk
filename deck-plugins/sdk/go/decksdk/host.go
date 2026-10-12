package decksdk

import (
	"bufio"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"sync"
	"sync/atomic"
	"time"
)

type CapabilityError struct {
	Code    string
	Message string
}

func (e *CapabilityError) Error() string { return e.Code + ": " + e.Message }

type Initializer interface{ Init(*Host) }
type Provider func(context.Context, string, json.RawMessage) (any, error)
type Host struct {
	input         io.Reader
	output        io.Writer
	mu            sync.Mutex
	writeMu       sync.Mutex
	pending       map[string]chan Request
	subscriptions map[string]chan json.RawMessage
	providers     map[string]Provider
	seq           atomic.Uint64
	done          chan struct{}
}

func NewHost(in io.Reader, out io.Writer) *Host {
	return &Host{input: in, output: out, pending: map[string]chan Request{}, subscriptions: map[string]chan json.RawMessage{}, providers: map[string]Provider{}, done: make(chan struct{})}
}
func (h *Host) send(v any) error {
	h.writeMu.Lock()
	defer h.writeMu.Unlock()
	return json.NewEncoder(h.output).Encode(v)
}
func (h *Host) exchange(ctx context.Context, q Request) (Request, error) {
	ctx, cancel := context.WithTimeout(ctx, 4*time.Second)
	defer cancel()
	if q.IPCID == "" {
		q.IPCID = fmt.Sprintf("plugin-%d", h.seq.Add(1))
	}
	ch := make(chan Request, 1)
	h.mu.Lock()
	h.pending[q.IPCID] = ch
	h.mu.Unlock()
	defer func() { h.mu.Lock(); delete(h.pending, q.IPCID); h.mu.Unlock() }()
	if err := h.send(q); err != nil {
		return Request{}, err
	}
	select {
	case r := <-ch:
		if r.Error != "" {
			return r, &CapabilityError{r.Code, r.Error}
		}
		return r, nil
	case <-ctx.Done():
		_ = h.send(Request{Op: "capability.cancel", Action: q.IPCID})
		return Request{}, &CapabilityError{"timeout", ctx.Err().Error()}
	case <-h.done:
		return Request{}, &CapabilityError{"provider_failed", "host disconnected"}
	}
}
func (h *Host) Call(ctx context.Context, cap, method string, q, r any) error {
	raw, err := json.Marshal(q)
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(ctx, 3*time.Second)
	defer cancel()
	reply, err := h.exchange(ctx, Request{Op: "capability.call", Capability: cap, Action: method, Payload: raw})
	if err != nil {
		return err
	}
	return json.Unmarshal(reply.Value, r)
}
func (h *Host) Subscribe(ctx context.Context, cap, topic string, fn func(json.RawMessage)) (func(), error) {
	id := fmt.Sprintf("subscription-%d", h.seq.Add(1))
	h.mu.Lock()
	queue := make(chan json.RawMessage, 1)
	stopped := make(chan struct{})
	var once sync.Once
	h.subscriptions[id] = queue
	go func() {
		for {
			select {
			case value := <-queue:
				fn(value)
			case <-stopped:
				return
			case <-h.done:
				return
			}
		}
	}()
	h.mu.Unlock()
	_, err := h.exchange(ctx, Request{Op: "capability.subscribe", IPCID: id, Capability: cap, Topic: topic})
	stop := func() {
		once.Do(func() { close(stopped) })
		h.mu.Lock()
		delete(h.subscriptions, id)
		h.mu.Unlock()
		_ = h.send(Request{Op: "capability.unsubscribe", Action: id})
	}
	if err != nil {
		stop()
		return nil, err
	}
	return stop, nil
}
func (h *Host) Provide(id string, p Provider) { h.mu.Lock(); h.providers[id] = p; h.mu.Unlock() }
func (h *Host) Publish(ctx context.Context, cap, topic string, value any) error {
	raw, err := json.Marshal(value)
	if err != nil {
		return err
	}
	_, err = h.exchange(ctx, Request{Op: "capability.publish", Capability: cap, Topic: topic, Value: raw})
	return err
}
func RunWithHost(p Plugin, h *Host) {
	if p == nil {
		panic("nil plugin")
	}
	scanner := bufio.NewScanner(h.input)
	scanner.Buffer(make([]byte, 65536), 1024*1024)
	// Initialization runs after the reader is active, so it may make capability calls.
	initialized := make(chan struct{})
	go func() {
		if init, ok := p.(Initializer); ok {
			init.Init(h)
		}
		close(initialized)
	}()
	defer close(h.done)
	for scanner.Scan() {
		var req Request
		if json.Unmarshal(scanner.Bytes(), &req) != nil {
			continue
		}
		h.mu.Lock()
		pending := h.pending[req.IPCID]
		callback := h.subscriptions[req.IPCID]
		h.mu.Unlock()
		if req.Op == "capability.result" {
			if pending != nil {
				select {
				case pending <- req:
				default:
				}
			}
			continue
		}
		if req.Op == "capability.state" {
			if callback != nil {
				var state struct {
					Value json.RawMessage `json:"value"`
				}
				if json.Unmarshal(req.Value, &state) == nil {
					select {
					case callback <- state.Value:
					default:
						select {
						case <-callback:
						default:
						}
						select {
						case callback <- state.Value:
						default:
						}
					}
				}
			}
			continue
		}
		go func(req Request) {
			<-initialized
			reply := Response{Op: "ok", IPCID: req.IPCID}
			var err error
			switch req.Op {
			case "catalog":
				reply.Buttons = p.Catalog()
				if reply.Buttons == nil {
					reply.Buttons = []Button{}
				}
			case "invoke":
				err = p.Invoke(req.Type, req.Action, req.Body, req.Payload)
			case "poll":
				if poll, ok := p.(Poller); ok {
					err = poll.Poll()
				}
			case "capability.invoke":
				h.mu.Lock()
				provider := h.providers[req.Capability]
				h.mu.Unlock()
				if provider == nil {
					err = &CapabilityError{"capability_unavailable", req.Capability}
				} else {
					ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
					reply.Value, err = provider(ctx, req.Action, req.Payload)
					cancel()
				}
			default:
				err = &CapabilityError{"invalid_arguments", "unknown op"}
			}
			if err != nil {
				reply.Op = "error"
				reply.Error = err.Error()
				reply.Code = "provider_failed"
				if e, ok := err.(*CapabilityError); ok {
					reply.Code = e.Code
				}
			}
			if req.Op == "catalog" || wantsAck(req) {
				_ = h.send(reply)
			}
		}(req)
	}
}
