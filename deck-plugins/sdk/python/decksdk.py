"""AirDeck plugin API v2. Typed capability clients live in airdeck_sdk.core."""
from __future__ import annotations
import abc, json, sys, threading, uuid
from concurrent.futures import ThreadPoolExecutor, Future, TimeoutError
from typing import Any, Callable
class Button(dict): pass
class CapabilityError(Exception):
    def __init__(self, code: str, message: str): self.code=code; super().__init__(message)
class DeckPlugin(abc.ABC):
    @abc.abstractmethod
    def catalog(self) -> list[dict[str,Any]]: ...
    @abc.abstractmethod
    def invoke(self, typ:str, action:str, body:dict, payload:dict) -> None: ...
class Host:
    def __init__(self, input=None, output=None):
        self.input=input or sys.stdin; self.output=output or sys.stdout
        self.lock=threading.RLock(); self.write_lock=threading.Lock()
        self.pending:dict[str,Future]={}; self.subscriptions:dict[str,Callable]={}; self.providers:dict[str,Callable]={}
    def send(self, data:dict) -> None:
        with self.write_lock: self.output.write(json.dumps(data,separators=(',',':'))+'\n'); self.output.flush()
    def exchange(self, req:dict) -> dict:
        identifier=req.setdefault('ipc_id',str(uuid.uuid4())); future=Future()
        with self.lock: self.pending[identifier]=future
        try: self.send(req); return future.result(timeout=4)
        except TimeoutError:
            self.send({"op":"capability.cancel","action":identifier}); raise CapabilityError("timeout","Host request timed out")
        finally:
            with self.lock: self.pending.pop(identifier,None)
    def call(self, capability:str, method:str, payload:dict) -> dict:
        return self.exchange({'op':'capability.call','capability':capability,'action':method,'payload':payload}).get('value',{})
    def subscribe(self, capability:str, topic:str, callback:Callable[[dict],None]) -> Callable[[],None]:
        identifier=str(uuid.uuid4())
        with self.lock: self.subscriptions[identifier]=callback
        def stop():
            with self.lock: self.subscriptions.pop(identifier,None)
            self.send({'op':'capability.unsubscribe','action':identifier})
        try: self.exchange({'op':'capability.subscribe','ipc_id':identifier,'capability':capability,'topic':topic})
        except Exception: stop(); raise
        return stop
    def provide(self, capability:str, dispatch:Callable[[str,dict],dict]) -> None:
        with self.lock: self.providers[capability]=dispatch
    def publish(self, capability:str, topic:str, value:dict) -> None:
        self.exchange({'op':'capability.publish','capability':capability,'topic':topic,'value':value})
    def run(self, plugin:DeckPlugin) -> None:
        ready=threading.Event(); pool=ThreadPoolExecutor(max_workers=16)
        def initialize():
            try:
                if hasattr(plugin,'init'): plugin.init(self)
            finally: ready.set()
        pool.submit(initialize)
        def handle(req):
            ready.wait(); reply={'op':'ok','ipc_id':req.get('ipc_id','')}
            try:
                op=req['op']
                if op=='catalog': reply['buttons']=plugin.catalog() or []
                elif op=='invoke': plugin.invoke(req.get('type',''),req.get('action',''),req.get('body',{}),req.get('payload',{}))
                elif op=='capability.invoke': reply['value']=self.providers[req['capability']](req['action'],req.get('payload',{}))
                elif op=='poll': reply['states']=plugin.poll() if hasattr(plugin,'poll') else []
                else: raise CapabilityError('invalid_arguments','Unknown operation')
            except Exception as exc: reply.update(op='error',error=str(exc),code=getattr(exc,'code','provider_failed'))
            if req.get('ack',True): self.send(reply)
        try:
            for line in self.input:
                try: req=json.loads(line)
                except (ValueError,TypeError): continue
                if not isinstance(req,dict) or not isinstance(req.get('op'),str) or not isinstance(req.get('ipc_id',''),str): continue
                identifier=req.get('ipc_id','')
                if req.get('op')=='capability.result':
                    with self.lock: future=self.pending.get(identifier)
                    if future and not future.done():
                        if req.get('error'): future.set_exception(CapabilityError(req.get('code','provider_failed'),req['error']))
                        else: future.set_result(req)
                elif req.get('op')=='capability.state':
                    with self.lock: callback=self.subscriptions.get(identifier)
                    state=req.get('value')
                    if callback and isinstance(state,dict) and 'value' in state:
                        pool.submit(callback,state['value'])
                else: pool.submit(handle,req)
        finally:
            with self.lock:
                for future in self.pending.values():
                    if not future.done(): future.set_exception(CapabilityError('provider_failed','Host disconnected'))
                self.subscriptions.clear()
            pool.shutdown(wait=True)
def run(plugin:DeckPlugin) -> None: Host().run(plugin)
