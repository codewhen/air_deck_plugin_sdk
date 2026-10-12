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
class Motion:
    dx: float
    dy: float
    sensitivity: float
class ClickButton(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
@dataclass
class Click:
    button: ClickButton
    double_click: bool
    def __post_init__(self):
        self.button = ClickButton(self.button)
class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def move(self, request: Motion) -> Empty:
        return Empty(**self.transport.call("core.pointer", "move", asdict(request)))
    def scroll(self, request: Motion) -> Empty:
        return Empty(**self.transport.call("core.pointer", "scroll", asdict(request)))
    def click(self, request: Click) -> Empty:
        return Empty(**self.transport.call("core.pointer", "click", asdict(request)))
class Provider(Protocol):
    def move(self, request: Motion) -> Empty: ...
    def scroll(self, request: Motion) -> Empty: ...
    def click(self, request: Click) -> Empty: ...
def dispatch(provider: Provider, method: str, payload: dict) -> dict:
    if method == "move": return asdict(provider.move(Motion(**payload)))
    if method == "scroll": return asdict(provider.scroll(Motion(**payload)))
    if method == "click": return asdict(provider.click(Click(**payload)))
    raise ValueError("unknown capability method")
