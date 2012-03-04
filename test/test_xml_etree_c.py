# xml.etree test for cElementTree

from test import support
from test.support import import_fresh_module
import unittest

cET = import_fresh_module('xml.etree.ElementTree', fresh=['_elementtree'])
cET_alias = import_fresh_module('xml.etree.cElementTree', fresh=['_elementtree', 'xml.etree'])


# cElementTree specific tests

def sanity():
    r"""
    Import sanity.

    Issue #6697.

    >>> cElementTree = cET
    >>> e = cElementTree.Element('a')
    >>> getattr(e, '\uD800')           # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    UnicodeEncodeError: ...

    >>> p = cElementTree.XMLParser()
    >>> p.version.split()[0]
    'Expat'
    >>> getattr(p, '\uD800')
    Traceback (most recent call last):
     ...
    AttributeError: 'XMLParser' object has no attribute '\ud800'
    """


class MiscTests(unittest.TestCase):
    # Issue #8651.
    @support.bigmemtest(size=support._2G + 100, memuse=1)
    def test_length_overflow(self, size):
        if size < support._2G + 100:
            self.skipTest("not enough free memory, need at least 2 GB")
        data = b'x' * size
        parser = cET.XMLParser()
        try:
            self.assertRaises(OverflowError, parser.feed, data)
        finally:
            data = None

@unittest.skipUnless(cET, 'requires _elementtree')
class TestAliasWorking(unittest.TestCase):
    # Test that the cET alias module is alive
    def test_alias_working(self):
        e = cET_alias.Element('foo')
        self.assertEqual(e.tag, 'foo')
        

@unittest.skipUnless(cET, 'requires _elementtree')
class TestAcceleratorImported(unittest.TestCase):
    # Test that the C accelerator was imported, as expected
    def test_correct_import_cET(self):
        self.assertEqual(cET.SubElement.__module__, '_elementtree')

    def test_correct_import_cET_alias(self):
        self.assertEqual(cET_alias.SubElement.__module__, '_elementtree')


def test_main():
    from test import test_xml_etree, test_xml_etree_c

    # Run the tests specific to the C implementation
    support.run_doctest(test_xml_etree_c, verbosity=True)
    support.run_unittest(
        MiscTests,
        TestAliasWorking,
        TestAcceleratorImported
        )

    # Run the same test suite as the Python module
    test_xml_etree.test_main(module=cET)


if __name__ == '__main__':
    test_main()
