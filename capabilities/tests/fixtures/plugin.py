import threading
from decksdk import DeckPlugin,run
from airdeck_sdk.core.media import Client,Empty,PlaybackStatus
class Plugin(DeckPlugin):
    def init(self,host): self.client=Client(host)
    def catalog(self): return []
    def invoke(self,t,action,*args):
        if action == 'subscribe':
            done=threading.Event(); values=[]
            def state(v): values.append(v);done.set()
            stop=self.client.subscribe_playback(state)
            try:
                assert done.wait(2)
                assert values[0].status is PlaybackStatus.PLAYING and values[0].available
            finally:stop()
            return
        state=self.client.get_playback(Empty())
        assert state.status is PlaybackStatus.PLAYING and state.available
run(Plugin())
