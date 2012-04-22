from . import util as source_util

from importlib import _bootstrap
import imp
import unittest


class PathHookTest(unittest.TestCase):

    """Test the path hook for source."""

    def path_hook(self):
        return _bootstrap.FileFinder.path_hook((_bootstrap.SourceFileLoader,
            _bootstrap._suffix_list(imp.PY_SOURCE), True))

    def test_success(self):
        with source_util.create_modules('dummy') as mapping:
            self.assertTrue(hasattr(self.path_hook()(mapping['.root']),
                                 'find_module'))

    def test_empty_string(self):
        # The empty string represents the cwd.
        self.assertTrue(hasattr(self.path_hook()(''), 'find_module'))


def test_main():
    from test.support import run_unittest
    run_unittest(PathHookTest)


if __name__ == '__main__':
    test_main()
