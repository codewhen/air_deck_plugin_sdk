# Generated; do not edit.
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Callable, Protocol, Any, Literal
class Transport(Protocol):
    def call(self, capability: str, method: str, payload: dict) -> dict: ...
    def subscribe(self, capability: str, topic: str, callback: Callable[[dict], None]) -> Callable[[], None]: ...
@dataclass
class Empty:
    pass
@dataclass
class Key:
    key: str
@dataclass
class Combo:
    combo: str
class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def press(self, request: Key) -> Empty:
        return Empty(**self.transport.call("core.keyboard", "press", asdict(request)))
    def hotkey(self, request: Combo) -> Empty:
        return Empty(**self.transport.call("core.keyboard", "hotkey", asdict(request)))
class Provider(Protocol):
    def press(self, request: Key) -> Empty: ...
    def hotkey(self, request: Combo) -> Empty: ...
def dispatch(provider: Provider, method: str, payload: dict) -> dict:
    if method == "press": return asdict(provider.press(Key(**payload)))
    if method == "hotkey": return asdict(provider.hotkey(Combo(**payload)))
    raise ValueError("unknown capability method")
