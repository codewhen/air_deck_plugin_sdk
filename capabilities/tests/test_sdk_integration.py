"""All executable SDKs consume the same correlated request/result fixture."""
import json,os,pathlib,queue,threading,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]; FIX=ROOT/'capabilities/tests/fixtures'
class SDKIntegration(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();cls.out=pathlib.Path(cls.tmp.name);cls.env=dict(os.environ,GOCACHE='/private/tmp/airdeck-go-cache')
  subprocess.run(['go','build','-o',str(cls.out/'go-plugin'),str(FIX/'plugin.go')],cwd=ROOT/'deck-plugins',env=cls.env,check=True)
  subprocess.run(['c++','-std=c++17','-I',str(ROOT/'deck-plugins/sdk/cpp'),'-I',str(ROOT/'deck-plugins/sdk/cpp/vendor'),str(FIX/'plugin.cpp'),'-o',str(cls.out/'cpp-plugin')],check=True)
  subprocess.run(['c++','-std=c++17','-I',str(ROOT/'deck-plugins/sdk/cpp'),'-I',str(ROOT/'deck-plugins/sdk/cpp/vendor'),'-I',str(ROOT/'deck-plugins/sdk/generated-examples/cpp'),str(FIX/'provider.cpp'),'-o',str(cls.out/'cpp-provider')],check=True)
  cls.jar=pathlib.Path(os.environ['GSON_JAR']) if os.environ.get('GSON_JAR') else next(p for p in (pathlib.Path.home()/'.gradle/caches/modules-2/files-2.1/com.google.code.gson/gson').rglob('*.jar') if not p.name.endswith('-sources.jar'))
  sources=list((ROOT/'capabilities/generated/java').rglob('*.java'))+list((ROOT/'deck-plugins/sdk/java').rglob('*.java'))+[FIX/'TestPlugin.java']
  subprocess.run(['javac','-cp',str(cls.jar),'-d',str(cls.out),*map(str,sources)],check=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def exercise(self,command,env=None):
  p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
  def send(v):p.stdin.write(json.dumps(v)+'\n');p.stdin.flush()
  messages=queue.Queue()
  def read():
   for line in p.stdout:messages.put(line)
  reader=threading.Thread(target=read,daemon=True);reader.start()
  def receive():
   try:return json.loads(messages.get(timeout=6))
   except queue.Empty:self.fail('SDK deadlocked')
  try:
   p.stdin.write('not JSON\n[]\n{"op":[]}\n');p.stdin.flush()
   send({'op':'invoke','ipc_id':'invoke-1','action':'test','payload':{}});q=receive();self.assertEqual(q['op'],'capability.call');self.assertEqual(q['capability'],'core.media');self.assertEqual(q['action'],'getPlayback');self.assertEqual(q['payload'],{})
   send({'op':'capability.result','ipc_id':q['ipc_id'],'value':{'status':'playing','available':True}});r=receive();self.assertEqual(r['op'],'ok',r);self.assertEqual(r['ipc_id'],'invoke-1')
   send({'op':'invoke','ipc_id':'invoke-denied','action':'test','payload':{}});q=receive()
   send({'op':'capability.result','ipc_id':q['ipc_id'],'code':'permission_denied','error':'Not granted'});r=receive()
   if r['op']=='capability.cancel':r=receive()
   self.assertEqual(r['op'],'error',r);self.assertEqual(r['code'],'permission_denied');self.assertEqual(r['ipc_id'],'invoke-denied')
   send({'op':'invoke','ipc_id':'invoke-state','action':'subscribe','payload':{}});q=receive();self.assertEqual(q['op'],'capability.subscribe')
   send({'op':'capability.result','ipc_id':q['ipc_id'],'value':{}})
   send({'op':'capability.state','ipc_id':q['ipc_id'],'value':{'capability':'core.media','topic':'playback','value':{'status':'playing','available':True},'revision':1,'captured_at_ms':1}})
   r=receive()
   if r['op']=='capability.unsubscribe':r=receive()
   self.assertEqual(r['op'],'ok',r);self.assertEqual(r['ipc_id'],'invoke-state')

  finally:p.stdin.close();p.wait(timeout=6);reader.join(timeout=1);p.stdout.close();p.stderr.close()
 def test_go(self):self.exercise([str(self.out/'go-plugin')])
 def test_python(self):self.exercise(['python3',str(FIX/'plugin.py')],dict(self.env,PYTHONPATH=str(ROOT/'deck-plugins/sdk/python'),PYTHONDONTWRITEBYTECODE='1'))
 def test_java(self):self.exercise(['java','-cp',str(self.out)+os.pathsep+str(self.jar),'TestPlugin'])
 def test_cpp(self):self.exercise([str(self.out/'cpp-plugin')])
