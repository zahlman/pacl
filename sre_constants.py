#
# Secret Labs' Regular Expression Engine
# $Id$
#
# various symbols used by the regular expression engine.
# run this script to update the _sre include files!
#
# Copyright (c) 1998-2000 by Secret Labs AB.  All rights reserved.
#
# This code can only be used for 1.6 alpha testing.  All other use
# require explicit permission from Secret Labs AB.
#
# Portions of this engine have been developed in cooperation with
# CNRI.  Hewlett-Packard provided funding for 1.6 integration and
# other compatibility work.
#

# should this really be here?

class error(Exception):
    pass

# operators

FAILURE = "failure"
SUCCESS = "success"

ANY = "any"
ASSERT = "assert"
AT = "at"
BRANCH = "branch"
CALL = "call"
CATEGORY = "category"
GROUP = "group"
GROUP_IGNORE = "group_ignore"
IN = "in"
IN_IGNORE = "in_ignore"
INFO = "info"
JUMP = "jump"
LITERAL = "literal"
LITERAL_IGNORE = "literal_ignore"
MARK = "mark"
MAX_REPEAT = "max_repeat"
MAX_REPEAT_ONE = "max_repeat_one"
MIN_REPEAT = "min_repeat"
NEGATE = "negate"
NOT_LITERAL = "not_literal"
NOT_LITERAL_IGNORE = "not_literal_ignore"
RANGE = "range"
REPEAT = "repeat"
REPEAT_ONE = "repeat_one"
SUBPATTERN = "subpattern"

# positions
AT_BEGINNING = "at_beginning"
AT_BEGINNING_LINE = "at_beginning_line"
AT_BOUNDARY = "at_boundary"
AT_NON_BOUNDARY = "at_non_boundary"
AT_END = "at_end"
AT_END_LINE = "at_end_line"

# categories
CATEGORY_DIGIT = "category_digit"
CATEGORY_NOT_DIGIT = "category_not_digit"
CATEGORY_SPACE = "category_space"
CATEGORY_NOT_SPACE = "category_not_space"
CATEGORY_WORD = "category_word"
CATEGORY_NOT_WORD = "category_not_word"
CATEGORY_LINEBREAK = "category_linebreak"
CATEGORY_NOT_LINEBREAK = "category_not_linebreak"
CATEGORY_LOC_WORD = "category_loc_word"
CATEGORY_LOC_NOT_WORD = "category_loc_not_word"
CATEGORY_UNI_DIGIT = "category_uni_digit"
CATEGORY_UNI_NOT_DIGIT = "category_uni_not_digit"
CATEGORY_UNI_SPACE = "category_uni_space"
CATEGORY_UNI_NOT_SPACE = "category_uni_not_space"
CATEGORY_UNI_WORD = "category_uni_word"
CATEGORY_UNI_NOT_WORD = "category_uni_not_word"
CATEGORY_UNI_LINEBREAK = "category_uni_linebreak"
CATEGORY_UNI_NOT_LINEBREAK = "category_uni_not_linebreak"

OPCODES = [

    # failure=0 success=1 (just because it looks better that way :-)
    FAILURE, SUCCESS,

    ANY,
    ASSERT,
    AT,
    BRANCH,
    CALL,
    CATEGORY,
    GROUP, GROUP_IGNORE,
    IN, IN_IGNORE,
    INFO,
    JUMP,
    LITERAL, LITERAL_IGNORE,
    MARK,
    MAX_REPEAT,
    MAX_REPEAT_ONE,
    MIN_REPEAT,
    NOT_LITERAL, NOT_LITERAL_IGNORE,
    NEGATE,
    RANGE,
    REPEAT

]

ATCODES = [
    AT_BEGINNING, AT_BEGINNING_LINE, AT_BOUNDARY,
    AT_NON_BOUNDARY, AT_END, AT_END_LINE
]

CHCODES = [
    CATEGORY_DIGIT, CATEGORY_NOT_DIGIT, CATEGORY_SPACE,
    CATEGORY_NOT_SPACE, CATEGORY_WORD, CATEGORY_NOT_WORD,
    CATEGORY_LINEBREAK, CATEGORY_NOT_LINEBREAK, CATEGORY_LOC_WORD,
    CATEGORY_LOC_NOT_WORD, CATEGORY_UNI_DIGIT, CATEGORY_UNI_NOT_DIGIT,
    CATEGORY_UNI_SPACE, CATEGORY_UNI_NOT_SPACE, CATEGORY_UNI_WORD,
    CATEGORY_UNI_NOT_WORD, CATEGORY_UNI_LINEBREAK,
    CATEGORY_UNI_NOT_LINEBREAK
]

def makedict(list):
    d = {}
    i = 0
    for item in list:
	d[item] = i
	i = i + 1
    return d

OPCODES = makedict(OPCODES)
ATCODES = makedict(ATCODES)
CHCODES = makedict(CHCODES)

# replacement operations for "ignore case" mode
OP_IGNORE = {
    GROUP: GROUP_IGNORE,
    IN: IN_IGNORE,
    LITERAL: LITERAL_IGNORE,
    NOT_LITERAL: NOT_LITERAL_IGNORE
}

AT_MULTILINE = {
    AT_BEGINNING: AT_BEGINNING_LINE,
    AT_END: AT_END_LINE
}

CH_LOCALE = {
    CATEGORY_DIGIT: CATEGORY_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_LOC_WORD,
    CATEGORY_NOT_WORD: CATEGORY_LOC_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_NOT_LINEBREAK
}

CH_UNICODE = {
    CATEGORY_DIGIT: CATEGORY_UNI_DIGIT,
    CATEGORY_NOT_DIGIT: CATEGORY_UNI_NOT_DIGIT,
    CATEGORY_SPACE: CATEGORY_UNI_SPACE,
    CATEGORY_NOT_SPACE: CATEGORY_UNI_NOT_SPACE,
    CATEGORY_WORD: CATEGORY_UNI_WORD,
    CATEGORY_NOT_WORD: CATEGORY_UNI_NOT_WORD,
    CATEGORY_LINEBREAK: CATEGORY_UNI_LINEBREAK,
    CATEGORY_NOT_LINEBREAK: CATEGORY_UNI_NOT_LINEBREAK
}

# flags
SRE_FLAG_TEMPLATE = 1
SRE_FLAG_IGNORECASE = 2
SRE_FLAG_LOCALE = 4
SRE_FLAG_MULTILINE = 8
SRE_FLAG_DOTALL = 16
SRE_FLAG_UNICODE = 32
SRE_FLAG_VERBOSE = 64

if __name__ == "__main__":
    import string
    def dump(f, d, prefix):
	items = d.items()
	items.sort(lambda a, b: cmp(a[1], b[1]))
	for k, v in items:
	    f.write("#define %s_%s %s\n" % (prefix, string.upper(k), v))
    f = open("sre_constants.h", "w")
    f.write("/* generated from sre_constants.py */\n")
    dump(f, OPCODES, "SRE_OP")
    dump(f, ATCODES, "SRE")
    dump(f, CHCODES, "SRE")
    f.write("#define SRE_FLAG_TEMPLATE %d\n" % SRE_FLAG_TEMPLATE)
    f.write("#define SRE_FLAG_IGNORECASE %d\n" % SRE_FLAG_IGNORECASE)
    f.write("#define SRE_FLAG_LOCALE %d\n" % SRE_FLAG_LOCALE)
    f.write("#define SRE_FLAG_MULTILINE %d\n" % SRE_FLAG_MULTILINE)
    f.write("#define SRE_FLAG_DOTALL %d\n" % SRE_FLAG_DOTALL)
    f.write("#define SRE_FLAG_UNICODE %d\n" % SRE_FLAG_UNICODE)
    f.write("#define SRE_FLAG_VERBOSE %d\n" % SRE_FLAG_VERBOSE)
    f.close()
    print "done"
