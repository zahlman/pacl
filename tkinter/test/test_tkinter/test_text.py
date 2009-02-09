import unittest
import tkinter
from test.support import requires, run_unittest
from tkinter.ttk import setup_master

requires('gui')

class TextTest(unittest.TestCase):

    def setUp(self):
        self.root = setup_master()
        self.text = tkinter.Text(self.root)

    def tearDown(self):
        self.text.destroy()


    def test_search(self):
        text = self.text

        # pattern and index are obligatory arguments.
        self.failUnlessRaises(tkinter.TclError, text.search, None, '1.0')
        self.failUnlessRaises(tkinter.TclError, text.search, 'a', None)
        self.failUnlessRaises(tkinter.TclError, text.search, None, None)

        # Invalid text index.
        self.failUnlessRaises(tkinter.TclError, text.search, '', 0)

        # Check if we are getting the indices as strings -- you are likely
        # to get Tcl_Obj under Tk 8.5 if Tkinter doesn't convert it.
        text.insert('1.0', 'hi-test')
        self.failUnlessEqual(text.search('-test', '1.0', 'end'), '1.2')
        self.failUnlessEqual(text.search('test', '1.0', 'end'), '1.3')


tests_gui = (TextTest, )

if __name__ == "__main__":
    run_unittest(*tests_gui)
