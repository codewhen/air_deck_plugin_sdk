import importlib.util,json,pathlib,subprocess,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('generator',ROOT/'capabilities/tools/generate.py');generator=importlib.util.module_from_spec(spec);spec.loader.exec_module(generator)
class Contracts(unittest.TestCase):
 def test_reproducible(self):
  with tempfile.TemporaryDirectory() as tmp:
   subprocess.run(['python3',str(ROOT/'capabilities/tools/generate.py'),'--out',tmp],check=True)
   for f in (ROOT/'capabilities/generated').rglob('*'):
    if f.is_file() and '__pycache__' not in str(f):self.assertEqual(f.read_bytes(),(pathlib.Path(tmp)/f.relative_to(ROOT/'capabilities/generated')).read_bytes(),str(f))
 def test_missing_permissions_and_refs(self):
  s=json.loads((ROOT/'capabilities/schemas/core.media.json').read_text());s['methods']['pause']['permissions']=[]
  with self.assertRaises(AssertionError):generator.validate(s)
  s=json.loads((ROOT/'capabilities/schemas/core.media.json').read_text());s['topics']['track']['type']='Missing'
  with self.assertRaises(AssertionError):generator.validate(s)

 def test_breaking_contract_requires_major_version(self):
  old=json.loads((ROOT/'capabilities/schemas/core.media.json').read_text());new=json.loads(json.dumps(old));del new['methods']['pause']
  with self.assertRaises(AssertionError):generator.check_compatibility(new,old)
  new['version']='2.0.0';generator.check_compatibility(new,old)

 def test_app_catalog_array_contract_and_python_decoding(self):
  s=json.loads((ROOT/'capabilities/schemas/core.apps.json').read_text())
  generator.validate(s)
  s['types']['Applications']['properties']['apps']['items']['$ref']='Missing'
  with self.assertRaises(AssertionError):generator.validate(s)
  spec=importlib.util.spec_from_file_location('app_types',ROOT/'capabilities/generated/python/airdeck_sdk/core/apps.py')
  module=importlib.util.module_from_spec(spec)
  import sys
  sys.modules[spec.name]=module
  spec.loader.exec_module(module)
  result=module.Applications(apps=[{'id':'code','name':'Code','target':'/Applications/Code.app'}])
  self.assertIsInstance(result.apps[0],module.Application)
  self.assertEqual(result.apps[0].target,'/Applications/Code.app')
