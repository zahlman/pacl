"""Tests for packaging.command.install_data."""
import os
import sys
import imp

from packaging.tests import unittest, support
from packaging.command.install_lib import install_lib
from packaging.compiler.extension import Extension
from packaging.errors import PackagingOptionError


class InstallLibTestCase(support.TempdirManager,
                         support.LoggingCatcher,
                         support.EnvironRestorer,
                         unittest.TestCase):

    restore_environ = ['PYTHONPATH']

    def test_finalize_options(self):
        pkg_dir, dist = self.create_dist()
        cmd = install_lib(dist)

        cmd.finalize_options()
        self.assertTrue(cmd.compile)
        self.assertEqual(cmd.optimize, 0)

        # optimize must be 0, 1, or 2
        cmd.optimize = 'foo'
        self.assertRaises(PackagingOptionError, cmd.finalize_options)
        cmd.optimize = '4'
        self.assertRaises(PackagingOptionError, cmd.finalize_options)

        cmd.optimize = '2'
        cmd.finalize_options()
        self.assertEqual(cmd.optimize, 2)

    @unittest.skipIf(sys.dont_write_bytecode, 'byte-compile disabled')
    def test_byte_compile(self):
        pkg_dir, dist = self.create_dist()
        os.chdir(pkg_dir)
        cmd = install_lib(dist)
        cmd.compile = True
        cmd.optimize = 1

        f = os.path.join(pkg_dir, 'foo.py')
        self.write_file(f, '# python file')
        cmd.byte_compile([f])
        pyc_file = imp.cache_from_source('foo.py')
        pyo_file = imp.cache_from_source('foo.py', debug_override=False)
        self.assertTrue(os.path.exists(pyc_file))
        self.assertTrue(os.path.exists(pyo_file))

    def test_get_outputs(self):
        pkg_dir, dist = self.create_dist()
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = True
        cmd.optimize = 1
        cmd.install_dir = pkg_dir
        f = os.path.join(pkg_dir, '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = [pkg_dir]

        # make sure the build_lib is set the temp dir
        build_dir = os.path.split(pkg_dir)[0]
        cmd.get_finalized_command('build_py').build_lib = build_dir

        # get_output should return 4 elements
        self.assertEqual(len(cmd.get_outputs()), 4)

    def test_get_inputs(self):
        pkg_dir, dist = self.create_dist()
        cmd = install_lib(dist)

        # setting up a dist environment
        cmd.compile = True
        cmd.optimize = 1
        cmd.install_dir = pkg_dir
        f = os.path.join(pkg_dir, '__init__.py')
        self.write_file(f, '# python package')
        cmd.distribution.ext_modules = [Extension('foo', ['xxx'])]
        cmd.distribution.packages = [pkg_dir]

        # get_input should return 2 elements
        self.assertEqual(len(cmd.get_inputs()), 2)

    def test_dont_write_bytecode(self):
        # makes sure byte_compile is not used
        pkg_dir, dist = self.create_dist()
        cmd = install_lib(dist)
        cmd.compile = True
        cmd.optimize = 1

        self.addCleanup(setattr, sys, 'dont_write_bytecode',
                        sys.dont_write_bytecode)
        sys.dont_write_bytecode = True
        cmd.byte_compile([])

        self.assertIn('byte-compiling is disabled', self.get_logs()[0])


def test_suite():
    return unittest.makeSuite(InstallLibTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
