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
class Launch:
    target: str
@dataclass
class Application:
    id: str
    name: str
    target: str
@dataclass
class Applications:
    apps: list[Application]
    def __post_init__(self):
        self.apps = [v if isinstance(v, Application) else Application(**v) for v in self.apps]
class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def launch(self, request: Launch) -> Empty:
        return Empty(**self.transport.call("core.apps", "launch", asdict(request)))
    def list(self, request: Empty) -> Applications:
        return Applications(**self.transport.call("core.apps", "list", asdict(request)))
class Provider(Protocol):
    def launch(self, request: Launch) -> Empty: ...
    def list(self, request: Empty) -> Applications: ...
def dispatch(provider: Provider, method: str, payload: dict) -> dict:
    if method == "launch": return asdict(provider.launch(Launch(**payload)))
    if method == "list": return asdict(provider.list(Empty(**payload)))
    raise ValueError("unknown capability method")
