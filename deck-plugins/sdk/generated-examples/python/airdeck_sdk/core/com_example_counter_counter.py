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
class Count:
    value: int
class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def get_count(self, request: Empty) -> Count:
        return Count(**self.transport.call("com.example.counter.counter", "getCount", asdict(request)))
    def subscribe_count(self, callback: Callable[[Count], None]) -> Callable[[], None]:
        return self.transport.subscribe("com.example.counter.counter", "count", lambda data: callback(Count(**data)))
class Provider(Protocol):
    def get_count(self, request: Empty) -> Count: ...
def dispatch(provider: Provider, method: str, payload: dict) -> dict:
    if method == "getCount": return asdict(provider.get_count(Empty(**payload)))
    raise ValueError("unknown capability method")
