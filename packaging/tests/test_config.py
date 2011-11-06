"""Tests for packaging.config."""
import os
import sys

from packaging import command
from packaging.dist import Distribution
from packaging.errors import PackagingFileError, PackagingOptionError
from packaging.compiler import new_compiler, _COMPILERS
from packaging.command.sdist import sdist

from packaging.tests import unittest, support
from packaging.tests.support import requires_zlib


SETUP_CFG = """
[metadata]
name = RestingParrot
version = 0.6.4
author = Carl Meyer
author_email = carl@oddbird.net
maintainer = Éric Araujo
maintainer_email = merwok@netwok.org
summary = A sample project demonstrating packaging
description-file = %(description-file)s
keywords = packaging, sample project

classifier =
  Development Status :: 4 - Beta
  Environment :: Console (Text Based)
  Environment :: X11 Applications :: GTK; python_version < '3'
  License :: OSI Approved :: MIT License
  Programming Language :: Python
  Programming Language :: Python :: 2
  Programming Language :: Python :: 3

requires_python = >=2.4, <3.2

requires_dist =
  PetShoppe
  MichaelPalin (> 1.1)
  pywin32; sys.platform == 'win32'
  pysqlite2; python_version < '2.5'
  inotify (0.0.1); sys.platform == 'linux2'

requires_external = libxml2

provides_dist = packaging-sample-project (0.2)
                unittest2-sample-project

project_url =
  Main repository, http://bitbucket.org/carljm/sample-distutils2-project
  Fork in progress, http://bitbucket.org/Merwok/sample-distutils2-project

[files]
packages_root = src

packages = one
           two
           three

modules = haven

scripts =
  script1.py
  scripts/find-coconuts
  bin/taunt

package_data =
  cheese = data/templates/*

extra_files = %(extra-files)s

# Replaces MANIFEST.in
sdist_extra =
  include THANKS HACKING
  recursive-include examples *.txt *.py
  prune examples/sample?/build

resources=
  bm/ {b1,b2}.gif = {icon}
  Cf*/ *.CFG = {config}/baBar/
  init_script = {script}/JunGle/

[global]
commands =
    packaging.tests.test_config.FooBarBazTest

compilers =
    packaging.tests.test_config.DCompiler

setup_hooks = %(setup-hooks)s



[install_dist]
sub_commands = foo
"""

# Can not be merged with SETUP_CFG else install_dist
# command will fail when trying to compile C sources
# TODO use a DummyCommand to mock build_ext
EXT_SETUP_CFG = """
[files]
packages = one
           two
           parent.undeclared

[extension:one.speed_coconuts]
sources = c_src/speed_coconuts.c
extra_link_args = "`gcc -print-file-name=libgcc.a`" -shared
define_macros = HAVE_CAIRO HAVE_GTK2
libraries = gecodeint gecodekernel -- sys.platform != 'win32'
    GecodeInt GecodeKernel -- sys.platform == 'win32'

[extension: two.fast_taunt]
sources = cxx_src/utils_taunt.cxx
          cxx_src/python_module.cxx
include_dirs = /usr/include/gecode
    /usr/include/blitz
extra_compile_args = -fPIC -O2
    -DGECODE_VERSION=$(./gecode_version) -- sys.platform != 'win32'
    /DGECODE_VERSION='win32' -- sys.platform == 'win32'
language = cxx

# corner case: if the parent package of an extension is declared but
# not its grandparent, it's legal
[extension: parent.undeclared._speed]
sources = parent/undeclared/_speed.c
"""

EXT_SETUP_CFG_BUGGY_1 = """
[extension: realname]
name = crash_here
"""

EXT_SETUP_CFG_BUGGY_2 = """
[files]
packages = ham

[extension: spam.eggs]
"""

EXT_SETUP_CFG_BUGGY_3 = """
[files]
packages = ok
           ok.works

[extension: ok.works.breaks._ext]
"""

HOOKS_MODULE = """
import logging

logger = logging.getLogger('packaging')

def logging_hook(config):
    logger.warning('logging_hook called')
"""


class DCompiler:
    name = 'd'
    description = 'D Compiler'

    def __init__(self, *args):
        pass


def version_hook(config):
    config['metadata']['version'] += '.dev1'


def first_hook(config):
    config['files']['modules'] += '\n first'


def third_hook(config):
    config['files']['modules'] += '\n third'


class FooBarBazTest:

    def __init__(self, dist):
        self.distribution = dist
        self._record = []

    @classmethod
    def get_command_name(cls):
        return 'foo'

    def run(self):
        self._record.append('foo has run')

    def nothing(self):
        pass

    def get_source_files(self):
        return []

    ensure_finalized = finalize_options = initialize_options = nothing


class ConfigTestCase(support.TempdirManager,
                     support.EnvironRestorer,
                     support.LoggingCatcher,
                     unittest.TestCase):

    restore_environ = ['PLAT']

    def setUp(self):
        super(ConfigTestCase, self).setUp()
        tempdir = self.mkdtemp()
        self.working_dir = os.getcwd()
        os.chdir(tempdir)
        self.tempdir = tempdir

    def write_setup(self, kwargs=None):
        opts = {'description-file': 'README', 'extra-files': '',
                'setup-hooks': 'packaging.tests.test_config.version_hook'}
        if kwargs:
            opts.update(kwargs)
        self.write_file('setup.cfg', SETUP_CFG % opts, encoding='utf-8')

    def get_dist(self):
        dist = Distribution()
        dist.parse_config_files()
        return dist

    def test_config(self):
        self.write_setup()
        self.write_file('README', 'yeah')
        os.mkdir('bm')
        self.write_file(('bm', 'b1.gif'), '')
        self.write_file(('bm', 'b2.gif'), '')
        os.mkdir('Cfg')
        self.write_file(('Cfg', 'data.CFG'), '')
        self.write_file('init_script', '')

        # try to load the metadata now
        dist = self.get_dist()

        # check what was done
        self.assertEqual(dist.metadata['Author'], 'Carl Meyer')
        self.assertEqual(dist.metadata['Author-Email'], 'carl@oddbird.net')

        # the hook adds .dev1
        self.assertEqual(dist.metadata['Version'], '0.6.4.dev1')

        wanted = [
            'Development Status :: 4 - Beta',
            'Environment :: Console (Text Based)',
            "Environment :: X11 Applications :: GTK; python_version < '3'",
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 3']
        self.assertEqual(dist.metadata['Classifier'], wanted)

        wanted = ['packaging', 'sample project']
        self.assertEqual(dist.metadata['Keywords'], wanted)

        self.assertEqual(dist.metadata['Requires-Python'], '>=2.4, <3.2')

        wanted = ['PetShoppe',
                  'MichaelPalin (> 1.1)',
                  "pywin32; sys.platform == 'win32'",
                  "pysqlite2; python_version < '2.5'",
                  "inotify (0.0.1); sys.platform == 'linux2'"]

        self.assertEqual(dist.metadata['Requires-Dist'], wanted)
        urls = [('Main repository',
                 'http://bitbucket.org/carljm/sample-distutils2-project'),
                ('Fork in progress',
                 'http://bitbucket.org/Merwok/sample-distutils2-project')]
        self.assertEqual(dist.metadata['Project-Url'], urls)

        self.assertEqual(dist.packages, ['one', 'two', 'three'])
        self.assertEqual(dist.py_modules, ['haven'])
        self.assertEqual(dist.package_data, {'cheese': 'data/templates/*'})
        self.assertEqual(
            {'bm/b1.gif': '{icon}/b1.gif',
             'bm/b2.gif': '{icon}/b2.gif',
             'Cfg/data.CFG': '{config}/baBar/data.CFG',
             'init_script': '{script}/JunGle/init_script'},
             dist.data_files)

        self.assertEqual(dist.package_dir, 'src')

        # Make sure we get the foo command loaded.  We use a string comparison
        # instead of assertIsInstance because the class is not the same when
        # this test is run directly: foo is packaging.tests.test_config.Foo
        # because get_command_class uses the full name, but a bare "Foo" in
        # this file would be __main__.Foo when run as "python test_config.py".
        # The name FooBarBazTest should be unique enough to prevent
        # collisions.
        self.assertEqual('FooBarBazTest',
                         dist.get_command_obj('foo').__class__.__name__)

        # did the README got loaded ?
        self.assertEqual(dist.metadata['description'], 'yeah')

        # do we have the D Compiler enabled ?
        self.assertIn('d', _COMPILERS)
        d = new_compiler(compiler='d')
        self.assertEqual(d.description, 'D Compiler')

    def test_multiple_description_file(self):
        self.write_setup({'description-file': 'README  CHANGES'})
        self.write_file('README', 'yeah')
        self.write_file('CHANGES', 'changelog2')
        dist = self.get_dist()
        self.assertEqual(dist.metadata.requires_files, ['README', 'CHANGES'])

    def test_multiline_description_file(self):
        self.write_setup({'description-file': 'README\n  CHANGES'})
        self.write_file('README', 'yeah')
        self.write_file('CHANGES', 'changelog')
        dist = self.get_dist()
        self.assertEqual(dist.metadata['description'], 'yeah\nchangelog')
        self.assertEqual(dist.metadata.requires_files, ['README', 'CHANGES'])

    def test_parse_extensions_in_config(self):
        self.write_file('setup.cfg', EXT_SETUP_CFG)
        dist = self.get_dist()

        ext_modules = dict((mod.name, mod) for mod in dist.ext_modules)
        self.assertEqual(len(ext_modules), 3)
        ext = ext_modules.get('one.speed_coconuts')
        self.assertEqual(ext.sources, ['c_src/speed_coconuts.c'])
        self.assertEqual(ext.define_macros, ['HAVE_CAIRO', 'HAVE_GTK2'])
        libs = ['gecodeint', 'gecodekernel']
        if sys.platform == 'win32':
            libs = ['GecodeInt', 'GecodeKernel']
        self.assertEqual(ext.libraries, libs)
        self.assertEqual(ext.extra_link_args,
            ['`gcc -print-file-name=libgcc.a`', '-shared'])

        ext = ext_modules.get('two.fast_taunt')
        self.assertEqual(ext.sources,
            ['cxx_src/utils_taunt.cxx', 'cxx_src/python_module.cxx'])
        self.assertEqual(ext.include_dirs,
            ['/usr/include/gecode', '/usr/include/blitz'])
        cargs = ['-fPIC', '-O2']
        if sys.platform == 'win32':
            cargs.append("/DGECODE_VERSION=win32")
        else:
            cargs.append('-DGECODE_VERSION=$(./gecode_version)')
        self.assertEqual(ext.extra_compile_args, cargs)
        self.assertEqual(ext.language, 'cxx')

        self.write_file('setup.cfg', EXT_SETUP_CFG_BUGGY_1)
        self.assertRaises(PackagingOptionError, self.get_dist)

        self.write_file('setup.cfg', EXT_SETUP_CFG_BUGGY_2)
        self.assertRaises(PackagingOptionError, self.get_dist)

        self.write_file('setup.cfg', EXT_SETUP_CFG_BUGGY_3)
        self.assertRaises(PackagingOptionError, self.get_dist)

    def test_project_setup_hook_works(self):
        # Bug #11637: ensure the project directory is on sys.path to allow
        # project-specific hooks
        self.write_setup({'setup-hooks': 'hooks.logging_hook'})
        self.write_file('README', 'yeah')
        self.write_file('hooks.py', HOOKS_MODULE)
        self.get_dist()
        self.assertEqual(['logging_hook called'], self.get_logs())
        self.assertIn('hooks', sys.modules)

    def test_missing_setup_hook_warns(self):
        self.write_setup({'setup-hooks': 'does._not.exist'})
        self.write_file('README', 'yeah')
        self.get_dist()
        logs = self.get_logs()
        self.assertEqual(1, len(logs))
        self.assertIn('cannot find setup hook', logs[0])

    def test_multiple_setup_hooks(self):
        self.write_setup({
            'setup-hooks': '\n  packaging.tests.test_config.first_hook'
                           '\n  packaging.tests.test_config.missing_hook'
                           '\n  packaging.tests.test_config.third_hook',
        })
        self.write_file('README', 'yeah')
        dist = self.get_dist()

        self.assertEqual(['haven', 'first', 'third'], dist.py_modules)
        logs = self.get_logs()
        self.assertEqual(1, len(logs))
        self.assertIn('cannot find setup hook', logs[0])

    def test_metadata_requires_description_files_missing(self):
        self.write_setup({'description-file': 'README README2'})
        self.write_file('README', 'yeah')
        self.write_file('README2', 'yeah')
        os.mkdir('src')
        self.write_file(('src', 'haven.py'), '#')
        self.write_file('script1.py', '#')
        os.mkdir('scripts')
        self.write_file(('scripts', 'find-coconuts'), '#')
        os.mkdir('bin')
        self.write_file(('bin', 'taunt'), '#')

        for pkg in ('one', 'two', 'three'):
            pkg = os.path.join('src', pkg)
            os.mkdir(pkg)
            self.write_file((pkg, '__init__.py'), '#')

        dist = self.get_dist()
        cmd = sdist(dist)
        cmd.finalize_options()
        cmd.get_file_list()
        self.assertRaises(PackagingFileError, cmd.make_distribution)

    @requires_zlib
    def test_metadata_requires_description_files(self):
        # Create the following file structure:
        #   README
        #   README2
        #   script1.py
        #   scripts/
        #       find-coconuts
        #   bin/
        #       taunt
        #   src/
        #       haven.py
        #       one/__init__.py
        #       two/__init__.py
        #       three/__init__.py

        self.write_setup({'description-file': 'README\n  README2',
                          'extra-files': '\n  README3'})
        self.write_file('README', 'yeah 1')
        self.write_file('README2', 'yeah 2')
        self.write_file('README3', 'yeah 3')
        os.mkdir('src')
        self.write_file(('src', 'haven.py'), '#')
        self.write_file('script1.py', '#')
        os.mkdir('scripts')
        self.write_file(('scripts', 'find-coconuts'), '#')
        os.mkdir('bin')
        self.write_file(('bin', 'taunt'), '#')

        for pkg in ('one', 'two', 'three'):
            pkg = os.path.join('src', pkg)
            os.mkdir(pkg)
            self.write_file((pkg, '__init__.py'), '#')

        dist = self.get_dist()
        self.assertIn('yeah 1\nyeah 2', dist.metadata['description'])

        cmd = sdist(dist)
        cmd.finalize_options()
        cmd.get_file_list()
        self.assertRaises(PackagingFileError, cmd.make_distribution)

        self.write_setup({'description-file': 'README\n  README2',
                          'extra-files': '\n  README2\n    README'})
        dist = self.get_dist()
        cmd = sdist(dist)
        cmd.finalize_options()
        cmd.get_file_list()
        cmd.make_distribution()
        with open('MANIFEST') as fp:
            self.assertIn('README\nREADME2\n', fp.read())

    def test_sub_commands(self):
        self.write_setup()
        self.write_file('README', 'yeah')
        os.mkdir('src')
        self.write_file(('src', 'haven.py'), '#')
        self.write_file('script1.py', '#')
        os.mkdir('scripts')
        self.write_file(('scripts', 'find-coconuts'), '#')
        os.mkdir('bin')
        self.write_file(('bin', 'taunt'), '#')

        for pkg in ('one', 'two', 'three'):
            pkg = os.path.join('src', pkg)
            os.mkdir(pkg)
            self.write_file((pkg, '__init__.py'), '#')

        # try to run the install command to see if foo is called
        self.addCleanup(command._COMMANDS.__delitem__, 'foo')
        dist = self.get_dist()
        dist.run_command('install_dist')
        cmd = dist.get_command_obj('foo')
        self.assertEqual(cmd.__class__.__name__, 'FooBarBazTest')
        self.assertEqual(cmd._record, ['foo has run'])


def test_suite():
    return unittest.makeSuite(ConfigTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
