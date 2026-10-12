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
class PlaybackStatus(str, Enum):
    PLAYING = 'playing'
    PAUSED = 'paused'
    STOPPED = 'stopped'
    UNKNOWN = 'unknown'
@dataclass
class Playback:
    status: PlaybackStatus
    available: bool
    def __post_init__(self):
        self.status = PlaybackStatus(self.status)
@dataclass
class Track:
    title: str
    artist: str
    album: str
    app: str
    available: bool
@dataclass
class Volume:
    level: float
    muted: bool
    available: bool
@dataclass
class SetVolume:
    level: float
@dataclass
class AdjustVolume:
    delta: float
@dataclass
class Mute:
    muted: bool
class Client:
    def __init__(self, transport: Transport): self.transport = transport
    def get_playback(self, request: Empty) -> Playback:
        return Playback(**self.transport.call("core.media", "getPlayback", asdict(request)))
    def get_track(self, request: Empty) -> Track:
        return Track(**self.transport.call("core.media", "getTrack", asdict(request)))
    def get_volume(self, request: Empty) -> Volume:
        return Volume(**self.transport.call("core.media", "getVolume", asdict(request)))
    def toggle_playback(self, request: Empty) -> Empty:
        return Empty(**self.transport.call("core.media", "togglePlayback", asdict(request)))
    def play(self, request: Empty) -> Empty:
        return Empty(**self.transport.call("core.media", "play", asdict(request)))
    def pause(self, request: Empty) -> Empty:
        return Empty(**self.transport.call("core.media", "pause", asdict(request)))
    def next(self, request: Empty) -> Empty:
        return Empty(**self.transport.call("core.media", "next", asdict(request)))
    def previous(self, request: Empty) -> Empty:
        return Empty(**self.transport.call("core.media", "previous", asdict(request)))
    def set_volume(self, request: SetVolume) -> Empty:
        return Empty(**self.transport.call("core.media", "setVolume", asdict(request)))
    def adjust_volume(self, request: AdjustVolume) -> Empty:
        return Empty(**self.transport.call("core.media", "adjustVolume", asdict(request)))
    def set_mute(self, request: Mute) -> Empty:
        return Empty(**self.transport.call("core.media", "setMute", asdict(request)))
    def subscribe_playback(self, callback: Callable[[Playback], None]) -> Callable[[], None]:
        return self.transport.subscribe("core.media", "playback", lambda data: callback(Playback(**data)))
    def subscribe_track(self, callback: Callable[[Track], None]) -> Callable[[], None]:
        return self.transport.subscribe("core.media", "track", lambda data: callback(Track(**data)))
    def subscribe_volume(self, callback: Callable[[Volume], None]) -> Callable[[], None]:
        return self.transport.subscribe("core.media", "volume", lambda data: callback(Volume(**data)))
class Provider(Protocol):
    def get_playback(self, request: Empty) -> Playback: ...
    def get_track(self, request: Empty) -> Track: ...
    def get_volume(self, request: Empty) -> Volume: ...
    def toggle_playback(self, request: Empty) -> Empty: ...
    def play(self, request: Empty) -> Empty: ...
    def pause(self, request: Empty) -> Empty: ...
    def next(self, request: Empty) -> Empty: ...
    def previous(self, request: Empty) -> Empty: ...
    def set_volume(self, request: SetVolume) -> Empty: ...
    def adjust_volume(self, request: AdjustVolume) -> Empty: ...
    def set_mute(self, request: Mute) -> Empty: ...
def dispatch(provider: Provider, method: str, payload: dict) -> dict:
    if method == "getPlayback": return asdict(provider.get_playback(Empty(**payload)))
    if method == "getTrack": return asdict(provider.get_track(Empty(**payload)))
    if method == "getVolume": return asdict(provider.get_volume(Empty(**payload)))
    if method == "togglePlayback": return asdict(provider.toggle_playback(Empty(**payload)))
    if method == "play": return asdict(provider.play(Empty(**payload)))
    if method == "pause": return asdict(provider.pause(Empty(**payload)))
    if method == "next": return asdict(provider.next(Empty(**payload)))
    if method == "previous": return asdict(provider.previous(Empty(**payload)))
    if method == "setVolume": return asdict(provider.set_volume(SetVolume(**payload)))
    if method == "adjustVolume": return asdict(provider.adjust_volume(AdjustVolume(**payload)))
    if method == "setMute": return asdict(provider.set_mute(Mute(**payload)))
    raise ValueError("unknown capability method")
