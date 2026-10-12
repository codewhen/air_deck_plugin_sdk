"""Deterministic SDK protocol tests; no host process or OS actions required."""
import io
import json
from pathlib import Path
import sys
import unittest
from concurrent.futures import Future, TimeoutError
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from decksdk import CapabilityError, DeckPlugin, Host


class Plugin(DeckPlugin):
    def __init__(self):
        self.calls = []

    def catalog(self):
        return [{"id": "test", "action": "run"}]

    def invoke(self, typ, action, body, payload):
        if action == "fail":
            raise CapabilityError("permission_denied", "Not granted")
        self.calls.append((typ, action, body, payload))

    def poll(self):
        return [{"id": "test", "active": True}]


class HostTests(unittest.TestCase):
    def run_requests(self, requests, plugin=None, configure=None):
        output = io.StringIO()
        host = Host(io.StringIO("\n".join(requests)), output)
        if configure:
            configure(host)
        plugin = plugin or Plugin()
        host.run(plugin)
        return host, plugin, [json.loads(line) for line in output.getvalue().splitlines()]

    def test_dispatch_and_correlation(self):
        requests = [
            {"op": "catalog", "ipc_id": "catalog"},
            {"op": "invoke", "ipc_id": "invoke", "type": "deck", "action": "run", "body": {"a": 1}, "payload": {"b": 2}},
            {"op": "poll", "ipc_id": "poll"},
            {"op": "capability.invoke", "ipc_id": "provider", "capability": "test", "action": "add", "payload": {"n": 2}},
        ]
        _, plugin, replies = self.run_requests(map(json.dumps, requests), configure=lambda h: h.provide("test", lambda action, payload: {"action": action, "n": payload["n"] + 1}))
        replies = {r["ipc_id"]: r for r in replies}
        self.assertEqual(set(replies), {"catalog", "invoke", "poll", "provider"})
        self.assertTrue(all(r["op"] == "ok" for r in replies.values()))
        self.assertEqual(replies["catalog"]["buttons"], plugin.catalog())
        self.assertEqual(plugin.calls, [("deck", "run", {"a": 1}, {"b": 2})])
        self.assertEqual(replies["poll"]["states"], plugin.poll())
        self.assertEqual(replies["provider"]["value"], {"action": "add", "n": 3})

    def test_invalid_lines_are_ignored_and_ack_false_suppresses_reply(self):
        _, plugin, replies = self.run_requests([
            "not JSON", "[]", "null", '{"op":[]}', '{"op":"catalog","ipc_id":7}',
            '{"op":"invoke","action":"run","ack":false}',
            '{"op":"catalog","ipc_id":"valid"}',
        ])
        self.assertEqual(len(plugin.calls), 1)
        self.assertEqual([r["ipc_id"] for r in replies], ["valid"])

    def test_errors_keep_codes_and_request_ids(self):
        _, _, replies = self.run_requests([
            '{"op":"unknown","ipc_id":"unknown"}',
            '{"op":"invoke","ipc_id":"denied","action":"fail"}',
            '{"op":"capability.invoke","ipc_id":"missing","capability":"missing","action":"run"}',
        ])
        replies = {r["ipc_id"]: r for r in replies}
        self.assertEqual(replies["unknown"]["code"], "invalid_arguments")
        self.assertEqual(replies["denied"]["code"], "permission_denied")
        self.assertEqual(replies["missing"]["code"], "provider_failed")
        self.assertTrue(all(r["op"] == "error" and r["error"] for r in replies.values()))

    def test_optional_poll_and_empty_catalog(self):
        class Minimal(DeckPlugin):
            def catalog(self): return None
            def invoke(self, *args): pass
        _, _, replies = self.run_requests(['{"op":"catalog","ipc_id":"c"}', '{"op":"poll","ipc_id":"p"}'], Minimal())
        replies = {r["ipc_id"]: r for r in replies}
        self.assertEqual(replies["c"]["buttons"], [])
        self.assertEqual(replies["p"]["states"], [])

    def test_call_and_publish_envelopes(self):
        host = Host(io.StringIO(), io.StringIO())
        with patch.object(host, "exchange", return_value={"value": {"ok": True}}) as exchange:
            self.assertEqual(host.call("core.media", "pause", {}), {"ok": True})
            exchange.assert_called_with({"op": "capability.call", "capability": "core.media", "action": "pause", "payload": {}})
            host.publish("test", "state", {"n": 1})
            exchange.assert_called_with({"op": "capability.publish", "capability": "test", "topic": "state", "value": {"n": 1}})

    def test_subscription_stop_and_failed_subscription_cleanup(self):
        host = Host(io.StringIO(), io.StringIO())
        callback = lambda value: None
        with patch.object(host, "exchange", return_value={}):
            stop = host.subscribe("test", "state", callback)
        identifier = next(iter(host.subscriptions))
        self.assertIs(host.subscriptions[identifier], callback)
        stop()
        self.assertEqual(host.subscriptions, {})
        self.assertEqual(json.loads(host.output.getvalue()), {"op": "capability.unsubscribe", "action": identifier})
        with patch.object(host, "exchange", side_effect=CapabilityError("permission_denied", "denied")):
            with self.assertRaises(CapabilityError):
                host.subscribe("test", "state", callback)
        self.assertEqual(host.subscriptions, {})

    def test_exchange_success_error_timeout_and_send_failure_cleanup(self):
        for error in [None, CapabilityError("permission_denied", "denied"), TimeoutError()]:
            with self.subTest(error=error):
                host = Host(io.StringIO(), io.StringIO())
                future = Future()
                if error is None: future.set_result({"value": {"n": 1}})
                else: future.set_exception(error)
                with patch("decksdk.Future", return_value=future):
                    if error is None:
                        self.assertEqual(host.exchange({"op": "test", "ipc_id": "request"}), {"value": {"n": 1}})
                    else:
                        with self.assertRaises(CapabilityError) as caught:
                            host.exchange({"op": "test", "ipc_id": "request"})
                        self.assertEqual(caught.exception.code, "timeout" if isinstance(error, TimeoutError) else "permission_denied")
                self.assertEqual(host.pending, {})
                lines = [json.loads(line) for line in host.output.getvalue().splitlines()]
                if isinstance(error, TimeoutError):
                    self.assertEqual(lines[-1], {"op": "capability.cancel", "action": "request"})
        host = Host(io.StringIO(), io.StringIO())
        with patch.object(host, "send", side_effect=OSError("closed")):
            with self.assertRaises(OSError): host.exchange({"op": "test"})
        self.assertEqual(host.pending, {})

    def test_results_resolve_pending_future_and_disconnect_cleans_subscriptions(self):
        for result in [{"value": {"n": 1}}, {"code": "permission_denied", "error": "denied"}]:
            with self.subTest(result=result):
                future = Future()
                def configure(host):
                    host.pending["request"] = future
                    host.subscriptions["state"] = lambda value: None
                host, _, replies = self.run_requests([json.dumps({"op": "capability.result", "ipc_id": "request", **result})], configure=configure)
                self.assertEqual(replies, [])
                self.assertEqual(host.subscriptions, {})
                if "error" in result:
                    with self.assertRaises(CapabilityError) as caught: future.result()
                    self.assertEqual(caught.exception.code, "permission_denied")
                else: self.assertEqual(future.result()["value"], {"n": 1})
        future = Future()
        self.run_requests([], configure=lambda h: h.pending.update({"waiting": future}))
        with self.assertRaises(CapabilityError) as caught: future.result()
        self.assertEqual(caught.exception.code, "provider_failed")

    def test_subscription_state_routes_inner_value(self):
        received = []
        host, _, _ = self.run_requests(['{"op":"capability.state","ipc_id":"state","value":{"value":{"n":5}}}'],
            configure=lambda h: h.subscriptions.update({"state": received.append}))
        self.assertEqual(received, [{"n": 5}])
        self.assertEqual(host.subscriptions, {})

    def test_malformed_subscription_states_do_not_terminate_reader(self):
        received = []
        _, _, replies = self.run_requests([
            '{"op":"capability.state","ipc_id":"state"}',
            '{"op":"capability.state","ipc_id":"state","value":null}',
            '{"op":"capability.state","ipc_id":"state","value":[]}',
            '{"op":"capability.state","ipc_id":"state","value":{}}',
            '{"op":"catalog","ipc_id":"after-invalid"}',
        ], configure=lambda h: h.subscriptions.update({"state": received.append}))
        self.assertEqual(received, [])
        self.assertEqual([r["ipc_id"] for r in replies], ["after-invalid"])


if __name__ == "__main__":
    unittest.main()
