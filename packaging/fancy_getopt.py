"""Command line parsing machinery.

The FancyGetopt class is a Wrapper around the getopt module that
provides the following additional features:
  * short and long options are tied together
  * options have help strings, so fancy_getopt could potentially
    create a complete usage summary
  * options set attributes of a passed-in object.

It is used under the hood by the command classes.  Do not use directly.
"""

import getopt
import re
import sys
import textwrap

from packaging.errors import PackagingGetoptError, PackagingArgError

# Much like command_re in packaging.core, this is close to but not quite
# the same as a Python NAME -- except, in the spirit of most GNU
# utilities, we use '-' in place of '_'.  (The spirit of LISP lives on!)
# The similarities to NAME are again not a coincidence...
longopt_pat = r'[a-zA-Z](?:[a-zA-Z0-9-]*)'
longopt_re = re.compile(r'^%s$' % longopt_pat)

# For recognizing "negative alias" options, eg. "quiet=!verbose"
neg_alias_re = re.compile("^(%s)=!(%s)$" % (longopt_pat, longopt_pat))


class FancyGetopt:
    """Wrapper around the standard 'getopt()' module that provides some
    handy extra functionality:
      * short and long options are tied together
      * options have help strings, and help text can be assembled
        from them
      * options set attributes of a passed-in object
      * boolean options can have "negative aliases" -- eg. if
        --quiet is the "negative alias" of --verbose, then "--quiet"
        on the command line sets 'verbose' to false
    """

    def __init__(self, option_table=None):

        # The option table is (currently) a list of tuples.  The
        # tuples may have 3 or four values:
        #   (long_option, short_option, help_string [, repeatable])
        # if an option takes an argument, its long_option should have '='
        # appended; short_option should just be a single character, no ':'
        # in any case.  If a long_option doesn't have a corresponding
        # short_option, short_option should be None.  All option tuples
        # must have long options.
        self.option_table = option_table

        # 'option_index' maps long option names to entries in the option
        # table (ie. those 3-tuples).
        self.option_index = {}
        if self.option_table:
            self._build_index()

        # 'alias' records (duh) alias options; {'foo': 'bar'} means
        # --foo is an alias for --bar
        self.alias = {}

        # 'negative_alias' keeps track of options that are the boolean
        # opposite of some other option
        self.negative_alias = {}

        # These keep track of the information in the option table.  We
        # don't actually populate these structures until we're ready to
        # parse the command line, since the 'option_table' passed in here
        # isn't necessarily the final word.
        self.short_opts = []
        self.long_opts = []
        self.short2long = {}
        self.attr_name = {}
        self.takes_arg = {}

        # And 'option_order' is filled up in 'getopt()'; it records the
        # original order of options (and their values) on the command line,
        # but expands short options, converts aliases, etc.
        self.option_order = []

    def _build_index(self):
        self.option_index.clear()
        for option in self.option_table:
            self.option_index[option[0]] = option

    def set_option_table(self, option_table):
        self.option_table = option_table
        self._build_index()

    def add_option(self, long_option, short_option=None, help_string=None):
        if long_option in self.option_index:
            raise PackagingGetoptError(
                  "option conflict: already an option '%s'" % long_option)
        else:
            option = (long_option, short_option, help_string)
            self.option_table.append(option)
            self.option_index[long_option] = option

    def has_option(self, long_option):
        """Return true if the option table for this parser has an
        option with long name 'long_option'."""
        return long_option in self.option_index

    def _check_alias_dict(self, aliases, what):
        assert isinstance(aliases, dict)
        for alias, opt in aliases.items():
            if alias not in self.option_index:
                raise PackagingGetoptError(
                      ("invalid %s '%s': "
                       "option '%s' not defined") % (what, alias, alias))
            if opt not in self.option_index:
                raise PackagingGetoptError(
                      ("invalid %s '%s': "
                       "aliased option '%s' not defined") % (what, alias, opt))

    def set_aliases(self, alias):
        """Set the aliases for this option parser."""
        self._check_alias_dict(alias, "alias")
        self.alias = alias

    def set_negative_aliases(self, negative_alias):
        """Set the negative aliases for this option parser.
        'negative_alias' should be a dictionary mapping option names to
        option names, both the key and value must already be defined
        in the option table."""
        self._check_alias_dict(negative_alias, "negative alias")
        self.negative_alias = negative_alias

    def _grok_option_table(self):
        """Populate the various data structures that keep tabs on the
        option table.  Called by 'getopt()' before it can do anything
        worthwhile.
        """
        self.long_opts = []
        self.short_opts = []
        self.short2long.clear()
        self.repeat = {}

        for option in self.option_table:
            if len(option) == 3:
                longopt, short, help = option
                repeat = 0
            elif len(option) == 4:
                longopt, short, help, repeat = option
            else:
                # the option table is part of the code, so simply
                # assert that it is correct
                raise ValueError("invalid option tuple: %r" % option)

            # Type- and value-check the option names
            if not isinstance(longopt, str) or len(longopt) < 2:
                raise PackagingGetoptError(
                      ("invalid long option '%s': "
                       "must be a string of length >= 2") % longopt)

            if (not ((short is None) or
                     (isinstance(short, str) and len(short) == 1))):
                raise PackagingGetoptError(
                      ("invalid short option '%s': "
                       "must be a single character or None") % short)

            self.repeat[longopt] = repeat
            self.long_opts.append(longopt)

            if longopt[-1] == '=':             # option takes an argument?
                if short:
                    short = short + ':'
                longopt = longopt[0:-1]
                self.takes_arg[longopt] = 1
            else:

                # Is option is a "negative alias" for some other option (eg.
                # "quiet" == "!verbose")?
                alias_to = self.negative_alias.get(longopt)
                if alias_to is not None:
                    if self.takes_arg[alias_to]:
                        raise PackagingGetoptError(
                              ("invalid negative alias '%s': "
                               "aliased option '%s' takes a value") % \
                               (longopt, alias_to))

                    self.long_opts[-1] = longopt   # XXX redundant?!
                    self.takes_arg[longopt] = 0

                else:
                    self.takes_arg[longopt] = 0

            # If this is an alias option, make sure its "takes arg" flag is
            # the same as the option it's aliased to.
            alias_to = self.alias.get(longopt)
            if alias_to is not None:
                if self.takes_arg[longopt] != self.takes_arg[alias_to]:
                    raise PackagingGetoptError(
                          ("invalid alias '%s': inconsistent with "
                           "aliased option '%s' (one of them takes a value, "
                           "the other doesn't") % (longopt, alias_to))

            # Now enforce some bondage on the long option name, so we can
            # later translate it to an attribute name on some object.  Have
            # to do this a bit late to make sure we've removed any trailing
            # '='.
            if not longopt_re.match(longopt):
                raise PackagingGetoptError(
                      ("invalid long option name '%s' " +
                       "(must be letters, numbers, hyphens only") % longopt)

            self.attr_name[longopt] = longopt.replace('-', '_')
            if short:
                self.short_opts.append(short)
                self.short2long[short[0]] = longopt

    def getopt(self, args=None, object=None):
        """Parse command-line options in args. Store as attributes on object.

        If 'args' is None or not supplied, uses 'sys.argv[1:]'.  If
        'object' is None or not supplied, creates a new OptionDummy
        object, stores option values there, and returns a tuple (args,
        object).  If 'object' is supplied, it is modified in place and
        'getopt()' just returns 'args'; in both cases, the returned
        'args' is a modified copy of the passed-in 'args' list, which
        is left untouched.
        """
        if args is None:
            args = sys.argv[1:]
        if object is None:
            object = OptionDummy()
            created_object = 1
        else:
            created_object = 0

        self._grok_option_table()

        short_opts = ' '.join(self.short_opts)

        try:
            opts, args = getopt.getopt(args, short_opts, self.long_opts)
        except getopt.error as msg:
            raise PackagingArgError(msg)

        for opt, val in opts:
            if len(opt) == 2 and opt[0] == '-':   # it's a short option
                opt = self.short2long[opt[1]]
            else:
                assert len(opt) > 2 and opt[:2] == '--'
                opt = opt[2:]

            alias = self.alias.get(opt)
            if alias:
                opt = alias

            if not self.takes_arg[opt]:     # boolean option?
                assert val == '', "boolean option can't have value"
                alias = self.negative_alias.get(opt)
                if alias:
                    opt = alias
                    val = 0
                else:
                    val = 1

            attr = self.attr_name[opt]
            # The only repeating option at the moment is 'verbose'.
            # It has a negative option -q quiet, which should set verbose = 0.
            if val and self.repeat.get(attr) is not None:
                val = getattr(object, attr, 0) + 1
            setattr(object, attr, val)
            self.option_order.append((opt, val))

        # for opts
        if created_object:
            return args, object
        else:
            return args

    def get_option_order(self):
        """Returns the list of (option, value) tuples processed by the
        previous run of 'getopt()'.  Raises RuntimeError if
        'getopt()' hasn't been called yet.
        """
        if self.option_order is None:
            raise RuntimeError("'getopt()' hasn't been called yet")
        else:
            return self.option_order

        return self.option_order

    def generate_help(self, header=None):
        """Generate help text (a list of strings, one per suggested line of
        output) from the option table for this FancyGetopt object.
        """
        # Blithely assume the option table is good: probably wouldn't call
        # 'generate_help()' unless you've already called 'getopt()'.

        # First pass: determine maximum length of long option names
        max_opt = 0
        for option in self.option_table:
            longopt = option[0]
            short = option[1]
            l = len(longopt)
            if longopt[-1] == '=':
                l = l - 1
            if short is not None:
                l = l + 5                   # " (-x)" where short == 'x'
            if l > max_opt:
                max_opt = l

        opt_width = max_opt + 2 + 2 + 2     # room for indent + dashes + gutter

        # Typical help block looks like this:
        #   --foo       controls foonabulation
        # Help block for longest option looks like this:
        #   --flimflam  set the flim-flam level
        # and with wrapped text:
        #   --flimflam  set the flim-flam level (must be between
        #               0 and 100, except on Tuesdays)
        # Options with short names will have the short name shown (but
        # it doesn't contribute to max_opt):
        #   --foo (-f)  controls foonabulation
        # If adding the short option would make the left column too wide,
        # we push the explanation off to the next line
        #   --flimflam (-l)
        #               set the flim-flam level
        # Important parameters:
        #   - 2 spaces before option block start lines
        #   - 2 dashes for each long option name
        #   - min. 2 spaces between option and explanation (gutter)
        #   - 5 characters (incl. space) for short option name

        # Now generate lines of help text.  (If 80 columns were good enough
        # for Jesus, then 78 columns are good enough for me!)
        line_width = 78
        text_width = line_width - opt_width
        big_indent = ' ' * opt_width
        if header:
            lines = [header]
        else:
            lines = ['Option summary:']

        for option in self.option_table:
            longopt, short, help = option[:3]
            text = textwrap.wrap(help, text_width)

            # Case 1: no short option at all (makes life easy)
            if short is None:
                if text:
                    lines.append("  --%-*s  %s" % (max_opt, longopt, text[0]))
                else:
                    lines.append("  --%-*s  " % (max_opt, longopt))

            # Case 2: we have a short option, so we have to include it
            # just after the long option
            else:
                opt_names = "%s (-%s)" % (longopt, short)
                if text:
                    lines.append("  --%-*s  %s" %
                                 (max_opt, opt_names, text[0]))
                else:
                    lines.append("  --%-*s" % opt_names)

            for l in text[1:]:
                lines.append(big_indent + l)

        return lines

    def print_help(self, header=None, file=None):
        if file is None:
            file = sys.stdout
        for line in self.generate_help(header):
            file.write(line + "\n")


def fancy_getopt(options, negative_opt, object, args):
    parser = FancyGetopt(options)
    parser.set_negative_aliases(negative_opt)
    return parser.getopt(args, object)


class OptionDummy:
    """Dummy class just used as a place to hold command-line option
    values as instance attributes."""

    def __init__(self, options=[]):
        """Create a new OptionDummy instance.  The attributes listed in
        'options' will be initialized to None."""
        for opt in options:
            setattr(self, opt, None)
