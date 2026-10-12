#!/usr/bin/env python3
"""Build all four generated starters, then test isolated packages and identities."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from plugin import ROOT, create
from build_examples import build
from test_packaged_examples import exercise

class Starters(unittest.TestCase):
    def test_rejects_invalid_identity_and_existing_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            destination = Path(tmp)/'hello'
            with self.assertRaises(ValueError): create('go',destination,'../bad','Hello')
            self.assertFalse(destination.exists())
            create('go',destination,'com.example.hello','Hello')
            before=(destination/'main.go').read_bytes()
            with self.assertRaises(ValueError): create('go',destination,'com.example.hello','New name')
            self.assertEqual(before,(destination/'main.go').read_bytes())

    def test_all_starters_build_and_run_without_the_checkout(self):
        gson = Path(os.environ.get('GSON_JAR',''))
        self.assertTrue(gson.is_file(), 'Set GSON_JAR to the local Gson jar before running all-language tests')
        with tempfile.TemporaryDirectory(prefix='_starter-tests-',dir=ROOT/'deck-plugins/plugins') as tmp, tempfile.TemporaryDirectory() as out:
            for language in ('go','python','java','cpp'):
                with self.subTest(language=language):
                    directory=Path(tmp)/language
                    create(language,directory,f'com.example.hello_{language}','Hello AirDeck')
                    package=build(language,Path(out),gson,directory,'plugin.py','com.example.starter.Plugin','plugin')
                    exercise(package,'hello')
                    self.assertEqual(json.loads((directory/'manifest.json').read_text())['permissions'], [])

if __name__=='__main__': unittest.main()
