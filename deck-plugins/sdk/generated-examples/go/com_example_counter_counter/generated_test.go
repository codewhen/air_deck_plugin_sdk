package com_example_counter_counter

import (
	"context"
	"encoding/json"
	"errors"
	"testing"
)

type testTransport struct {
	t         *testing.T
	err       error
	event     func(json.RawMessage)
	cancelled bool
}

func (tr *testTransport) Call(ctx context.Context, capability, method string, request, result any) error {
	if capability != "com.example.counter.counter" || method != "getCount" {
		tr.t.Fatalf("incorrect routing: %s/%s", capability, method)
	}
	if _, ok := request.(Empty); !ok {
		tr.t.Fatalf("incorrect request type: %T", request)
	}
	if tr.err != nil {
		return tr.err
	}
	*result.(*Count) = Count{Value: 42}
	return nil
}
func (tr *testTransport) Subscribe(ctx context.Context, capability, topic string, fn func(json.RawMessage)) (func(), error) {
	if capability != "com.example.counter.counter" || topic != "count" {
		tr.t.Fatalf("incorrect subscription: %s/%s", capability, topic)
	}
	if tr.err != nil {
		return nil, tr.err
	}
	tr.event = fn
	return func() { tr.cancelled = true }, nil
}
func TestClientCallsAndSubscription(t *testing.T) {
	tr := &testTransport{t: t}
	client := NewClient(tr)
	value, err := client.GetCount(context.Background(), Empty{})
	if err != nil || value.Value != 42 {
		t.Fatalf("count: %+v, %v", value, err)
	}
	var received []Count
	cancel, err := client.SubscribeCount(context.Background(), func(v Count) { received = append(received, v) })
	if err != nil {
		t.Fatal(err)
	}
	tr.event(json.RawMessage(`{"value":17}`))
	tr.event(json.RawMessage(`invalid`))
	if len(received) != 1 || received[0].Value != 17 {
		t.Fatalf("events: %+v", received)
	}
	cancel()
	if !tr.cancelled {
		t.Fatal("subscription not cancelled")
	}
	tr.err = errors.New("permission denied")
	if _, err = client.GetCount(context.Background(), Empty{}); !errors.Is(err, tr.err) {
		t.Fatalf("call error: %v", err)
	}
	if _, err = client.SubscribeCount(context.Background(), func(Count) {}); !errors.Is(err, tr.err) {
		t.Fatalf("subscription error: %v", err)
	}
}

type testProvider struct{ err error }

func (p testProvider) GetCount(context.Context, Empty) (Count, error) { return Count{Value: 42}, p.err }
func TestProviderDispatchValidation(t *testing.T) {
	ctx := context.Background()
	for _, typed := range []bool{false, true} {
		dispatch := func(p testProvider, method string, request any) (any, error) {
			if typed {
				return DispatchTyped(ctx, p, method, request)
			}
			return Dispatch(ctx, p, method, request.(json.RawMessage))
		}
		var valid, invalid any = json.RawMessage(`{}`), json.RawMessage(`broken`)
		if typed {
			valid = Empty{}
			invalid = Count{}
		}
		v, err := dispatch(testProvider{}, "getCount", valid)
		if err != nil || v.(Count).Value != 42 {
			t.Fatalf("dispatch: %v %v", v, err)
		}
		if _, err = dispatch(testProvider{}, "getCount", invalid); err == nil {
			t.Fatal("invalid request accepted")
		} else if typed {
			var invalidRequest *InvalidRequest
			if !errors.As(err, &invalidRequest) || err.Error() != "invalid request type: getCount" {
				t.Fatalf("invalid type error: %v", err)
			}
		}
		if _, err = dispatch(testProvider{}, "missing", valid); err == nil {
			t.Fatal("unknown method accepted")
		} else {
			var unknown *UnknownMethod
			if !errors.As(err, &unknown) || err.Error() != "unknown method: missing" {
				t.Fatalf("unknown method error: %v", err)
			}
		}
		want := errors.New("provider unavailable")
		if _, err = dispatch(testProvider{err: want}, "getCount", valid); !errors.Is(err, want) {
			t.Fatalf("provider error lost: %v", err)
		}
	}
}
