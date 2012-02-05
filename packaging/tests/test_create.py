"""Tests for packaging.create."""
import os
import sys
import sysconfig
from textwrap import dedent
from packaging import create
from packaging.create import MainProgram, ask_yn, ask, main

from packaging.tests import support, unittest
from packaging.tests.support import Inputs


class CreateTestCase(support.TempdirManager,
                     support.EnvironRestorer,
                     support.LoggingCatcher,
                     unittest.TestCase):

    maxDiff = None
    restore_environ = ['PLAT']

    def setUp(self):
        super(CreateTestCase, self).setUp()
        self.wdir = self.mkdtemp()
        os.chdir(self.wdir)
        # patch sysconfig
        self._old_get_paths = sysconfig.get_paths
        sysconfig.get_paths = lambda *args, **kwargs: {
            'man': sys.prefix + '/share/man',
            'doc': sys.prefix + '/share/doc/pyxfoil', }

    def tearDown(self):
        sysconfig.get_paths = self._old_get_paths
        if hasattr(create, 'input'):
            del create.input
        super(CreateTestCase, self).tearDown()

    def test_ask_yn(self):
        create.input = Inputs('y')
        self.assertEqual('y', ask_yn('is this a test'))

    def test_ask(self):
        create.input = Inputs('a', 'b')
        self.assertEqual('a', ask('is this a test'))
        self.assertEqual('b', ask(str(list(range(0, 70))), default='c',
                                  lengthy=True))

    def test_set_multi(self):
        mainprogram = MainProgram()
        create.input = Inputs('aaaaa')
        mainprogram.data['author'] = []
        mainprogram._set_multi('_set_multi test', 'author')
        self.assertEqual(['aaaaa'], mainprogram.data['author'])

    def test_find_files(self):
        # making sure we scan a project dir correctly
        mainprogram = MainProgram()

        # building the structure
        tempdir = self.wdir
        dirs = ['pkg1', 'data', 'pkg2', 'pkg2/sub']
        files = [
            'README',
            'data/data1',
            'foo.py',
            'pkg1/__init__.py',
            'pkg1/bar.py',
            'pkg2/__init__.py',
            'pkg2/sub/__init__.py',
        ]

        for dir_ in dirs:
            os.mkdir(os.path.join(tempdir, dir_))

        for file_ in files:
            self.write_file((tempdir, file_), 'xxx')

        mainprogram._find_files()
        mainprogram.data['packages'].sort()

        # do we have what we want?
        self.assertEqual(mainprogram.data['packages'],
                         ['pkg1', 'pkg2', 'pkg2.sub'])
        self.assertEqual(mainprogram.data['modules'], ['foo'])
        data_fn = os.path.join('data', 'data1')
        self.assertEqual(mainprogram.data['extra_files'],
                         ['README', data_fn])

    def test_convert_setup_py_to_cfg(self):
        self.write_file((self.wdir, 'setup.py'),
                        dedent("""
        # coding: utf-8
        from distutils.core import setup

        long_description = '''My super Death-scription
        barbar is now on the public domain,
        ho, baby !'''

        setup(name='pyxfoil',
              version='0.2',
              description='Python bindings for the Xfoil engine',
              long_description=long_description,
              maintainer='André Espaze',
              maintainer_email='andre.espaze@logilab.fr',
              url='http://www.python-science.org/project/pyxfoil',
              license='GPLv2',
              packages=['pyxfoil', 'babar', 'me'],
              data_files=[
                  ('share/doc/pyxfoil', ['README.rst']),
                  ('share/man', ['pyxfoil.1']),
                         ],
              py_modules=['my_lib', 'mymodule'],
              package_dir={
                  'babar': '',
                  'me': 'Martinique/Lamentin',
                          },
              package_data={
                  'babar': ['Pom', 'Flora', 'Alexander'],
                  'me': ['dady', 'mumy', 'sys', 'bro'],
                  'pyxfoil': ['fengine.so'],
                           },
              scripts=['my_script', 'bin/run'],
              )
        """), encoding='utf-8')
        create.input = Inputs('y')
        main()

        path = os.path.join(self.wdir, 'setup.cfg')
        with open(path, encoding='utf-8') as fp:
            contents = fp.read()

        self.assertEqual(contents, dedent("""\
            [metadata]
            name = pyxfoil
            version = 0.2
            summary = Python bindings for the Xfoil engine
            download_url = UNKNOWN
            home_page = http://www.python-science.org/project/pyxfoil
            maintainer = André Espaze
            maintainer_email = andre.espaze@logilab.fr
            description = My super Death-scription
                   |barbar is now on the public domain,
                   |ho, baby !

            [files]
            packages = pyxfoil
                babar
                me
            modules = my_lib
                mymodule
            scripts = my_script
                bin/run
            package_data =
                babar = Pom
                        Flora
                        Alexander
                me = dady
                     mumy
                     sys
                     bro
                pyxfoil = fengine.so

            resources =
                README.rst = {doc}
                pyxfoil.1 = {man}

            """))

    def test_convert_setup_py_to_cfg_with_description_in_readme(self):
        self.write_file((self.wdir, 'setup.py'),
                        dedent("""
        # coding: utf-8
        from distutils.core import setup
        with open('README.txt') as fp:
            long_description = fp.read()

        setup(name='pyxfoil',
              version='0.2',
              description='Python bindings for the Xfoil engine',
              long_description=long_description,
              maintainer='André Espaze',
              maintainer_email='andre.espaze@logilab.fr',
              url='http://www.python-science.org/project/pyxfoil',
              license='GPLv2',
              packages=['pyxfoil'],
              package_data={'pyxfoil': ['fengine.so', 'babar.so']},
              data_files=[
                ('share/doc/pyxfoil', ['README.rst']),
                ('share/man', ['pyxfoil.1']),
              ],
        )
        """), encoding='utf-8')
        self.write_file((self.wdir, 'README.txt'),
                        dedent('''
My super Death-scription
barbar is now in the public domain,
ho, baby!
                        '''))
        create.input = Inputs('y')
        main()

        path = os.path.join(self.wdir, 'setup.cfg')
        with open(path, encoding='utf-8') as fp:
            contents = fp.read()

        self.assertEqual(contents, dedent("""\
            [metadata]
            name = pyxfoil
            version = 0.2
            summary = Python bindings for the Xfoil engine
            download_url = UNKNOWN
            home_page = http://www.python-science.org/project/pyxfoil
            maintainer = André Espaze
            maintainer_email = andre.espaze@logilab.fr
            description-file = README.txt

            [files]
            packages = pyxfoil
            package_data =
                pyxfoil = fengine.so
                          babar.so

            resources =
                README.rst = {doc}
                pyxfoil.1 = {man}

            """))


def test_suite():
    return unittest.makeSuite(CreateTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
