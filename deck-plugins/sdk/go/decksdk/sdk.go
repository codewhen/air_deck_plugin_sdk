// Package decksdk is the required Go interface for Air Mouse .deckPlugin sidecars.
package decksdk

import (
	"encoding/json"
	"os"
)

// Button is a Stream Deck catalog entry.
type Button struct {
	ID       string `json:"id"`
	Title    string `json:"title"`
	IconKey  string `json:"icon_key,omitempty"`
	Columns  int    `json:"columns,omitempty"`
	Rows     int    `json:"rows,omitempty"`
	Action   string `json:"action"`
	PluginID string `json:"plugin_id"`
	// Editor controls Button Editor action-type visibility (tap / toggle).
	// Omit or leave both false to hide from the editor (library Plugins section still lists the action).
	Editor      *EditorOpts `json:"editor,omitempty"`
	ComponentID string      `json:"component_id,omitempty"`
}

// EditorOpts selects which button kinds may pick this action in the Button Editor.
type EditorOpts struct {
	Tap    bool `json:"tap,omitempty"`
	Toggle bool `json:"toggle,omitempty"`
}

// Request is one JSON line from the host.
type Request struct {
	IPCID      string          `json:"ipc_id,omitempty"`
	Capability string          `json:"capability,omitempty"`
	Topic      string          `json:"topic,omitempty"`
	Value      json.RawMessage `json:"value,omitempty"`
	Code       string          `json:"code,omitempty"`
	Error      string          `json:"error,omitempty"`
	Op         string          `json:"op"`
	Type       string          `json:"type,omitempty"`
	PluginID   string          `json:"plugin_id,omitempty"`
	Action     string          `json:"action,omitempty"`
	RequestID  string          `json:"request_id,omitempty"`
	Payload    json.RawMessage `json:"payload,omitempty"`
	Body       json.RawMessage `json:"body,omitempty"`
	// Ack is false when the host does not require an invocation result.
	Ack *bool `json:"ack,omitempty"`
}

// Response is one JSON line to the host.
type Response struct {
	IPCID   string          `json:"ipc_id,omitempty"`
	Value   any             `json:"value,omitempty"`
	Code    string          `json:"code,omitempty"`
	Op      string          `json:"op"`
	Buttons []Button        `json:"buttons,omitempty"`
	Error   string          `json:"error,omitempty"`
	Type    string          `json:"type,omitempty"`
	Body    json.RawMessage `json:"body,omitempty"`
}

// Poller is optional. The host calls it only when the plugin manifest declares
// poll_tier; plugin code must not create its own recurring timer.
// Poll refreshes native state and publishes it through Host.Publish.
type Poller interface{ Poll() error }

// Plugin is the required contract. Implement this or the binary is not a valid deck plugin.
type Plugin interface {
	// Catalog returns Stream Deck buttons (may be empty).
	Catalog() []Button
	// Invoke handles an authorized host message.
	// typ identifies the host message; action/payload describe the deck command.
	Invoke(typ, action string, body, payload json.RawMessage) error
}

// Run owns the stdin/stdout JSON-lines loop. Call from main.
func Run(p Plugin) { RunWithHost(p, NewHost(os.Stdin, os.Stdout)) }

func wantsAck(req Request) bool {
	if req.Ack == nil {
		return true
	}
	return *req.Ack
}

// DecodeBody unmarshals body JSON into dest.
func DecodeBody(raw json.RawMessage, dest any) error {
	if len(raw) == 0 {
		raw = json.RawMessage(`{}`)
	}
	return json.Unmarshal(raw, dest)
}
