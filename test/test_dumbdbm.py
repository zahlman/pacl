#! /usr/bin/env python
"""Test script for the dumbdbm module
   Original by Roger E. Masse
"""

import os
import test_support
import unittest
import dumbdbm
import tempfile

class DumbDBMTestCase(unittest.TestCase):
    _fname = tempfile.mktemp()
    _dict = {'0': '',
             'a': 'Python:',
             'b': 'Programming',
             'c': 'the',
             'd': 'way',
             'f': 'Guido',
             'g': 'intended'
             }

    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self._dkeys = self._dict.keys()
        self._dkeys.sort()
        
    def test_dumbdbm_creation(self):
        for ext in [".dir", ".dat", ".bak"]:
            try: os.unlink(self._fname+ext)
            except OSError: pass

        f = dumbdbm.open(self._fname, 'c')
        self.assertEqual(f.keys(), [])
        for key in self._dict:
            f[key] = self._dict[key]
        self.read_helper(f)
        f.close()

    def test_dumbdbm_modification(self):
        f = dumbdbm.open(self._fname, 'w')
        self._dict['g'] = f['g'] = "indented"
        self.read_helper(f)
        f.close()

    def test_dumbdbm_read(self):
        f = dumbdbm.open(self._fname, 'r')
        self.read_helper(f)
        f.close()

    def test_dumbdbm_keys(self):
        f = dumbdbm.open(self._fname)
        keys = self.keys_helper(f)
        f.close()

    def read_helper(self, f):
        keys = self.keys_helper(f)
        for key in self._dict:
            self.assertEqual(self._dict[key], f[key])
        
    def keys_helper(self, f):
        keys = f.keys()
        keys.sort()
        self.assertEqual(keys, self._dkeys)
        return keys

def test_main():
    test_support.run_unittest(DumbDBMTestCase)


if __name__ == "__main__":
    test_main()
