"""Tests for scripts in the Tools directory.

This file contains regression tests for some of the scripts found in the
Tools directory of a Python checkout or tarball, such as reindent.py.
"""

import os
import sys
import unittest
import sysconfig
from test import support
from test.script_helper import assert_python_ok

if not sysconfig.is_python_build():
    # XXX some installers do contain the tools, should we detect that
    # and run the tests in that case too?
    raise unittest.SkipTest('test irrelevant for an installed Python')

srcdir = sysconfig.get_config_var('projectbase')
basepath = os.path.join(os.getcwd(), srcdir, 'Tools')
scriptsdir = os.path.join(basepath, 'scripts')


class ReindentTests(unittest.TestCase):
    script = os.path.join(scriptsdir, 'reindent.py')

    def test_noargs(self):
        assert_python_ok(self.script)

    def test_help(self):
        rc, out, err = assert_python_ok(self.script, '-h')
        self.assertEqual(out, b'')
        self.assertGreater(err, b'')


class TestSundryScripts(unittest.TestCase):
    # At least make sure the rest don't have syntax errors.  When tests are
    # added for a script it should be added to the whitelist below.

    # scripts that have independent tests.
    whitelist = ['reindent.py']
    # scripts that can't be imported without running
    blacklist = ['make_ctype.py']
    # scripts that use windows-only modules
    windows_only = ['win_add2path.py']
    # blacklisted for other reasons
    other = ['analyze_dxp.py']

    skiplist = blacklist + whitelist + windows_only + other

    def setUp(self):
        cm = support.DirsOnSysPath(scriptsdir)
        cm.__enter__()
        self.addCleanup(cm.__exit__)

    def test_sundry(self):
        for fn in os.listdir(scriptsdir):
            if fn.endswith('.py') and fn not in self.skiplist:
                __import__(fn[:-3])

    @unittest.skipIf(sys.platform != "win32", "Windows-only test")
    def test_sundry_windows(self):
        for fn in self.windows_only:
            __import__(fn[:-3])

    def test_analyze_dxp_import(self):
        if hasattr(sys, 'getdxp'):
            import analyze_dxp
        else:
            with self.assertRaises(RuntimeError):
                import analyze_dxp


def test_main():
    support.run_unittest(*[obj for obj in globals().values()
                               if isinstance(obj, type)])


if __name__ == '__main__':
    unittest.main()
