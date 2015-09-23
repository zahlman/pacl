import ast
import types
import decimal
import unittest

a_global = 'global variable'

# You could argue that I'm too strict in looking for specific error
#  values with assertRaisesRegex, but without it it's way too easy to
#  make a syntax error in the test strings. Especially with all of the
#  triple quotes, raw strings, backslashes, etc. I think it's a
#  worthwhile tradeoff. When I switched to this method, I found many
#  examples where I wasn't testing what I thought I was.

class TestCase(unittest.TestCase):
    def assertAllRaise(self, exception_type, regex, error_strings):
        for str in error_strings:
            with self.subTest(str=str):
                with self.assertRaisesRegex(exception_type, regex):
                    eval(str)

    def test__format__lookup(self):
        # Make sure __format__ is looked up on the type, not the instance.
        class X:
            def __format__(self, spec):
                return 'class'

        x = X()

        # Add a bound __format__ method to the 'y' instance, but not
        #  the 'x' instance.
        y = X()
        y.__format__ = types.MethodType(lambda self, spec: 'instance', y)

        self.assertEqual(f'{y}', format(y))
        self.assertEqual(f'{y}', 'class')
        self.assertEqual(format(x), format(y))

        # __format__ is not called this way, but still make sure it
        #  returns what we expect (so we can make sure we're bypassing
        #  it).
        self.assertEqual(x.__format__(''), 'class')
        self.assertEqual(y.__format__(''), 'instance')

        # This is how __format__ is actually called.
        self.assertEqual(type(x).__format__(x, ''), 'class')
        self.assertEqual(type(y).__format__(y, ''), 'class')

    def test_ast(self):
        # Inspired by http://bugs.python.org/issue24975
        class X:
            def __init__(self):
                self.called = False
            def __call__(self):
                self.called = True
                return 4
        x = X()
        expr = """
a = 10
f'{a * x()}'"""
        t = ast.parse(expr)
        c = compile(t, '', 'exec')

        # Make sure x was not called.
        self.assertFalse(x.called)

        # Actually run the code.
        exec(c)

        # Make sure x was called.
        self.assertTrue(x.called)

    def test_literal_eval(self):
        # With no expressions, an f-string is okay.
        self.assertEqual(ast.literal_eval("f'x'"), 'x')
        self.assertEqual(ast.literal_eval("f'x' 'y'"), 'xy')

        # But this should raise an error.
        with self.assertRaisesRegex(ValueError, 'malformed node or string'):
            ast.literal_eval("f'x{3}'")

        # As should this, which uses a different ast node
        with self.assertRaisesRegex(ValueError, 'malformed node or string'):
            ast.literal_eval("f'{3}'")

    def test_ast_compile_time_concat(self):
        x = ['']

        expr = """x[0] = 'foo' f'{3}'"""
        t = ast.parse(expr)
        c = compile(t, '', 'exec')
        exec(c)
        self.assertEqual(x[0], 'foo3')

    def test_literal(self):
        self.assertEqual(f'', '')
        self.assertEqual(f'a', 'a')
        self.assertEqual(f' ', ' ')
        self.assertEqual(f'\N{GREEK CAPITAL LETTER DELTA}',
                         '\N{GREEK CAPITAL LETTER DELTA}')
        self.assertEqual(f'\N{GREEK CAPITAL LETTER DELTA}',
                         '\u0394')
        self.assertEqual(f'\N{True}', '\u22a8')
        self.assertEqual(rf'\N{True}', r'\NTrue')

    def test_escape_order(self):
        # note that hex(ord('{')) == 0x7b, so this
        #  string becomes f'a{4*10}b'
        self.assertEqual(f'a\u007b4*10}b', 'a40b')
        self.assertEqual(f'a\x7b4*10}b', 'a40b')
        self.assertEqual(f'a\x7b4*10\N{RIGHT CURLY BRACKET}b', 'a40b')
        self.assertEqual(f'{"a"!\N{LATIN SMALL LETTER R}}', "'a'")
        self.assertEqual(f'{10\x3a02X}', '0A')
        self.assertEqual(f'{10:02\N{LATIN CAPITAL LETTER X}}', '0A')

        self.assertAllRaise(SyntaxError, "f-string: single '}' is not allowed",
                            [r"""f'a{\u007b4*10}b'""",    # mis-matched brackets
                             ])
        self.assertAllRaise(SyntaxError, 'unexpected character after line continuation character',
                            [r"""f'{"a"\!r}'""",
                             r"""f'{a\!r}'""",
                             ])

    def test_unterminated_string(self):
        self.assertAllRaise(SyntaxError, 'f-string: unterminated string',
                            [r"""f'{"x'""",
                             r"""f'{"x}'""",
                             r"""f'{("x'""",
                             r"""f'{("x}'""",
                             ])

    def test_mismatched_parens(self):
        self.assertAllRaise(SyntaxError, 'f-string: mismatched',
                            ["f'{((}'",
                             ])

    def test_double_braces(self):
        self.assertEqual(f'{{', '{')
        self.assertEqual(f'a{{', 'a{')
        self.assertEqual(f'{{b', '{b')
        self.assertEqual(f'a{{b', 'a{b')
        self.assertEqual(f'}}', '}')
        self.assertEqual(f'a}}', 'a}')
        self.assertEqual(f'}}b', '}b')
        self.assertEqual(f'a}}b', 'a}b')

        self.assertEqual(f'{{{10}', '{10')
        self.assertEqual(f'}}{10}', '}10')
        self.assertEqual(f'}}{{{10}', '}{10')
        self.assertEqual(f'}}a{{{10}', '}a{10')

        self.assertEqual(f'{10}{{', '10{')
        self.assertEqual(f'{10}}}', '10}')
        self.assertEqual(f'{10}}}{{', '10}{')
        self.assertEqual(f'{10}}}a{{' '}', '10}a{}')

        # Inside of strings, don't interpret doubled brackets.
        self.assertEqual(f'{"{{}}"}', '{{}}')

        self.assertAllRaise(TypeError, 'unhashable type',
                            ["f'{ {{}} }'", # dict in a set
                             ])

    def test_compile_time_concat(self):
        x = 'def'
        self.assertEqual('abc' f'## {x}ghi', 'abc## defghi')
        self.assertEqual('abc' f'{x}' 'ghi', 'abcdefghi')
        self.assertEqual('abc' f'{x}' 'gh' f'i{x:4}', 'abcdefghidef ')
        self.assertEqual('{x}' f'{x}', '{x}def')
        self.assertEqual('{x' f'{x}', '{xdef')
        self.assertEqual('{x}' f'{x}', '{x}def')
        self.assertEqual('{{x}}' f'{x}', '{{x}}def')
        self.assertEqual('{{x' f'{x}', '{{xdef')
        self.assertEqual('x}}' f'{x}', 'x}}def')
        self.assertEqual(f'{x}' 'x}}', 'defx}}')
        self.assertEqual(f'{x}' '', 'def')
        self.assertEqual('' f'{x}' '', 'def')
        self.assertEqual('' f'{x}', 'def')
        self.assertEqual(f'{x}' '2', 'def2')
        self.assertEqual('1' f'{x}' '2', '1def2')
        self.assertEqual('1' f'{x}', '1def')
        self.assertEqual(f'{x}' f'-{x}', 'def-def')
        self.assertEqual('' f'', '')
        self.assertEqual('' f'' '', '')
        self.assertEqual('' f'' '' f'', '')
        self.assertEqual(f'', '')
        self.assertEqual(f'' '', '')
        self.assertEqual(f'' '' f'', '')
        self.assertEqual(f'' '' f'' '', '')

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{3' f'}'",  # can't concat to get a valid f-string
                             ])

    def test_comments(self):
        # These aren't comments, since they're in strings.
        d = {'#': 'hash'}
        self.assertEqual(f'{"#"}', '#')
        self.assertEqual(f'{d["#"]}', 'hash')

        self.assertAllRaise(SyntaxError, "f-string cannot include '#'",
                            ["f'{1#}'",   # error because the expression becomes "(1#)"
                             "f'{3(#)}'",
                             ])

    def test_many_expressions(self):
        # Create a string with many expressions in it. Note that
        #  because we have a space in here as a literal, we're actually
        #  going to use twice as many ast nodes: one for each literal
        #  plus one for each expression.
        def build_fstr(n, extra=''):
            return "f'" + ('{x} ' * n) + extra + "'"

        x = 'X'
        width = 1

        # Test around 256.
        for i in range(250, 260):
            self.assertEqual(eval(build_fstr(i)), (x+' ')*i)

        # Test concatenating 2 largs fstrings.
        self.assertEqual(eval(build_fstr(255)*256), (x+' ')*(255*256))

        s = build_fstr(253, '{x:{width}} ')
        self.assertEqual(eval(s), (x+' ')*254)

        # Test lots of expressions and constants, concatenated.
        s = "f'{1}' 'x' 'y'" * 1024
        self.assertEqual(eval(s), '1xy' * 1024)

    def test_format_specifier_expressions(self):
        width = 10
        precision = 4
        value = decimal.Decimal('12.34567')
        self.assertEqual(f'result: {value:{width}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width!r}.{precision}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{width:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{1}{0:0}.{precision:1}}', 'result:      12.35')
        self.assertEqual(f'result: {value:{ 1}{ 0:0}.{ precision:1}}', 'result:      12.35')
        self.assertEqual(f'{10:#{1}0x}', '       0xa')
        self.assertEqual(f'{10:{"#"}1{0}{"x"}}', '       0xa')
        self.assertEqual(f'{-10:-{"#"}1{0}x}', '      -0xa')
        self.assertEqual(f'{-10:{"-"}#{1}0{"x"}}', '      -0xa')
        self.assertEqual(f'{10:#{3 != {4:5} and width}x}', '       0xa')

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["""f'{"s"!r{":10"}}'""",

                             # This looks like a nested format spec.
                             ])

        self.assertAllRaise(SyntaxError, "invalid syntax",
                            [# Invalid sytax inside a nested spec.
                             "f'{4:{/5}}'",
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expressions nested too deeply",
                            [# Can't nest format specifiers.
                             "f'result: {value:{width:{0}}.{precision:1}}'",
                             ])

        self.assertAllRaise(SyntaxError, 'f-string: invalid conversion character',
                            [# No expansion inside conversion or for
                             #  the : or ! itself.
                             """f'{"s"!{"r"}}'""",
                             ])

    def test_side_effect_order(self):
        class X:
            def __init__(self):
                self.i = 0
            def __format__(self, spec):
                self.i += 1
                return str(self.i)

        x = X()
        self.assertEqual(f'{x} {x}', '1 2')

    def test_missing_expression(self):
        self.assertAllRaise(SyntaxError, 'f-string: empty expression not allowed',
                            ["f'{}'",
                             "f'{ }'"
                             "f' {} '",
                             "f'{!r}'",
                             "f'{ !r}'",
                             "f'{10:{ }}'",
                             "f' { } '",
                             r"f'{\n}'",
                             r"f'{\n \n}'",

                             # Catch the empty expression before the
                             #  invalid conversion.
                             "f'{!x}'",
                             "f'{ !xr}'",
                             "f'{!x:}'",
                             "f'{!x:a}'",
                             "f'{ !xr:}'",
                             "f'{ !xr:a}'",

                             "f'{!}'",
                             "f'{:}'",

                             # We find the empty expression before the
                             #  missing closing brace.
                             "f'{!'",
                             "f'{!s:'",
                             "f'{:'",
                             "f'{:x'",
                             ])

    def test_parens_in_expressions(self):
        self.assertEqual(f'{3,}', '(3,)')

        # Add these because when an expression is evaluated, parens
        #  are added around it. But we shouldn't go from an invalid
        #  expression to a valid one. The added parens are just
        #  supposed to allow whitespace (including newlines).
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["f'{,}'",
                             "f'{,}'",  # this is (,), which is an error
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{3)+(4}'",
                             ])

        self.assertAllRaise(SyntaxError, 'EOL while scanning string literal',
                            ["f'{\n}'",
                             ])

    def test_newlines_in_expressions(self):
        self.assertEqual(f'{0}', '0')
        self.assertEqual(f'{0\n}', '0')
        self.assertEqual(f'{0\r}', '0')
        self.assertEqual(f'{\n0\n}', '0')
        self.assertEqual(f'{\r0\r}', '0')
        self.assertEqual(f'{\n0\r}', '0')
        self.assertEqual(f'{\n0}', '0')
        self.assertEqual(f'{3+\n4}', '7')
        self.assertEqual(f'{3+\\\n4}', '7')
        self.assertEqual(rf'''{3+
4}''', '7')
        self.assertEqual(f'''{3+\
4}''', '7')

        self.assertAllRaise(SyntaxError, 'f-string: empty expression not allowed',
                            [r"f'{\n}'",
                             ])

    def test_lambda(self):
        x = 5
        self.assertEqual(f'{(lambda y:x*y)("8")!r}', "'88888'")
        self.assertEqual(f'{(lambda y:x*y)("8")!r:10}', "'88888'   ")
        self.assertEqual(f'{(lambda y:x*y)("8"):10}', "88888     ")

        # lambda doesn't work without parens, because the colon
        #  makes the parser think it's a format_spec
        self.assertAllRaise(SyntaxError, 'unexpected EOF while parsing',
                            ["f'{lambda x:x}'",
                             ])

    def test_yield(self):
        # Not terribly useful, but make sure the yield turns
        #  a function into a generator
        def fn(y):
            f'y:{yield y*2}'

        g = fn(4)
        self.assertEqual(next(g), 8)

    def test_yield_send(self):
        def fn(x):
            yield f'x:{yield (lambda i: x * i)}'

        g = fn(10)
        the_lambda = next(g)
        self.assertEqual(the_lambda(4), 40)
        self.assertEqual(g.send('string'), 'x:string')

    def test_expressions_with_triple_quoted_strings(self):
        self.assertEqual(f"{'''x'''}", 'x')
        self.assertEqual(f"{'''eric's'''}", "eric's")
        self.assertEqual(f'{"""eric\'s"""}', "eric's")
        self.assertEqual(f"{'''eric\"s'''}", 'eric"s')
        self.assertEqual(f'{"""eric"s"""}', 'eric"s')

        # Test concatenation within an expression
        self.assertEqual(f'{"x" """eric"s""" "y"}', 'xeric"sy')
        self.assertEqual(f'{"x" """eric"s"""}', 'xeric"s')
        self.assertEqual(f'{"""eric"s""" "y"}', 'eric"sy')
        self.assertEqual(f'{"""x""" """eric"s""" "y"}', 'xeric"sy')
        self.assertEqual(f'{"""x""" """eric"s""" """y"""}', 'xeric"sy')
        self.assertEqual(f'{r"""x""" """eric"s""" """y"""}', 'xeric"sy')

    def test_multiple_vars(self):
        x = 98
        y = 'abc'
        self.assertEqual(f'{x}{y}', '98abc')

        self.assertEqual(f'X{x}{y}', 'X98abc')
        self.assertEqual(f'{x}X{y}', '98Xabc')
        self.assertEqual(f'{x}{y}X', '98abcX')

        self.assertEqual(f'X{x}Y{y}', 'X98Yabc')
        self.assertEqual(f'X{x}{y}Y', 'X98abcY')
        self.assertEqual(f'{x}X{y}Y', '98XabcY')

        self.assertEqual(f'X{x}Y{y}Z', 'X98YabcZ')

    def test_closure(self):
        def outer(x):
            def inner():
                return f'x:{x}'
            return inner

        self.assertEqual(outer('987')(), 'x:987')
        self.assertEqual(outer(7)(), 'x:7')

    def test_arguments(self):
        y = 2
        def f(x, width):
            return f'x={x*y:{width}}'

        self.assertEqual(f('foo', 10), 'x=foofoo    ')
        x = 'bar'
        self.assertEqual(f(10, 10), 'x=        20')

    def test_locals(self):
        value = 123
        self.assertEqual(f'v:{value}', 'v:123')

    def test_missing_variable(self):
        with self.assertRaises(NameError):
            f'v:{value}'

    def test_missing_format_spec(self):
        class O:
            def __format__(self, spec):
                if not spec:
                    return '*'
                return spec

        self.assertEqual(f'{O():x}', 'x')
        self.assertEqual(f'{O()}', '*')
        self.assertEqual(f'{O():}', '*')

        self.assertEqual(f'{3:}', '3')
        self.assertEqual(f'{3!s:}', '3')

    def test_global(self):
        self.assertEqual(f'g:{a_global}', 'g:global variable')
        self.assertEqual(f'g:{a_global!r}', "g:'global variable'")

        a_local = 'local variable'
        self.assertEqual(f'g:{a_global} l:{a_local}',
                         'g:global variable l:local variable')
        self.assertEqual(f'g:{a_global!r}',
                         "g:'global variable'")
        self.assertEqual(f'g:{a_global} l:{a_local!r}',
                         "g:global variable l:'local variable'")

        self.assertIn("module 'unittest' from", f'{unittest}')

    def test_shadowed_global(self):
        a_global = 'really a local'
        self.assertEqual(f'g:{a_global}', 'g:really a local')
        self.assertEqual(f'g:{a_global!r}', "g:'really a local'")

        a_local = 'local variable'
        self.assertEqual(f'g:{a_global} l:{a_local}',
                         'g:really a local l:local variable')
        self.assertEqual(f'g:{a_global!r}',
                         "g:'really a local'")
        self.assertEqual(f'g:{a_global} l:{a_local!r}',
                         "g:really a local l:'local variable'")

    def test_call(self):
        def foo(x):
            return 'x=' + str(x)

        self.assertEqual(f'{foo(10)}', 'x=10')

    def test_nested_fstrings(self):
        y = 5
        self.assertEqual(f'{f"{0}"*3}', '000')
        self.assertEqual(f'{f"{y}"*3}', '555')
        self.assertEqual(f'{f"{\'x\'}"*3}', 'xxx')

        self.assertEqual(f"{r'x' f'{\"s\"}'}", 'xs')
        self.assertEqual(f"{r'x'rf'{\"s\"}'}", 'xs')

    def test_invalid_string_prefixes(self):
        self.assertAllRaise(SyntaxError, 'unexpected EOF while parsing',
                            ["fu''",
                             "uf''",
                             "Fu''",
                             "fU''",
                             "Uf''",
                             "uF''",
                             "ufr''",
                             "urf''",
                             "fur''",
                             "fru''",
                             "rfu''",
                             "ruf''",
                             "FUR''",
                             "Fur''",
                             ])

    def test_leading_trailing_spaces(self):
        self.assertEqual(f'{ 3}', '3')
        self.assertEqual(f'{  3}', '3')
        self.assertEqual(f'{\t3}', '3')
        self.assertEqual(f'{\t\t3}', '3')
        self.assertEqual(f'{3 }', '3')
        self.assertEqual(f'{3  }', '3')
        self.assertEqual(f'{3\t}', '3')
        self.assertEqual(f'{3\t\t}', '3')

        self.assertEqual(f'expr={ {x: y for x, y in [(1, 2), ]}}',
                         'expr={1: 2}')
        self.assertEqual(f'expr={ {x: y for x, y in [(1, 2), ]} }',
                         'expr={1: 2}')

    def test_character_name(self):
        self.assertEqual(f'{4}\N{GREEK CAPITAL LETTER DELTA}{3}',
                         '4\N{GREEK CAPITAL LETTER DELTA}3')
        self.assertEqual(f'{{}}\N{GREEK CAPITAL LETTER DELTA}{3}',
                         '{}\N{GREEK CAPITAL LETTER DELTA}3')

    def test_not_equal(self):
        # There's a special test for this because there's a special
        #  case in the f-string parser to look for != as not ending an
        #  expression. Normally it would, while looking for !s or !r.

        self.assertEqual(f'{3!=4}', 'True')
        self.assertEqual(f'{3!=4:}', 'True')
        self.assertEqual(f'{3!=4!s}', 'True')
        self.assertEqual(f'{3!=4!s:.3}', 'Tru')

    def test_conversions(self):
        self.assertEqual(f'{3.14:10.10}', '      3.14')
        self.assertEqual(f'{3.14!s:10.10}', '3.14      ')
        self.assertEqual(f'{3.14!r:10.10}', '3.14      ')
        self.assertEqual(f'{3.14!a:10.10}', '3.14      ')

        self.assertEqual(f'{"a"}', 'a')
        self.assertEqual(f'{"a"!r}', "'a'")
        self.assertEqual(f'{"a"!a}', "'a'")

        # Not a conversion.
        self.assertEqual(f'{"a!r"}', "a!r")

        # Not a conversion, but show that ! is allowed in a format spec.
        self.assertEqual(f'{3.14:!<10.10}', '3.14!!!!!!')

        self.assertEqual(f'{"\N{GREEK CAPITAL LETTER DELTA}"}', '\u0394')
        self.assertEqual(f'{"\N{GREEK CAPITAL LETTER DELTA}"!r}', "'\u0394'")
        self.assertEqual(f'{"\N{GREEK CAPITAL LETTER DELTA}"!a}', "'\\u0394'")

        self.assertAllRaise(SyntaxError, 'f-string: invalid conversion character',
                            ["f'{3!g}'",
                             "f'{3!A}'",
                             "f'{3!A}'",
                             "f'{3!A}'",
                             "f'{3!!}'",
                             "f'{3!:}'",
                             "f'{3!\N{GREEK CAPITAL LETTER DELTA}}'",
                             "f'{3! s}'",  # no space before conversion char
                             "f'{x!\\x00:.<10}'",
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{x!s{y}}'",
                             "f'{3!ss}'",
                             "f'{3!ss:}'",
                             "f'{3!ss:s}'",
                             ])

    def test_assignment(self):
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["f'' = 3",
                             "f'{0}' = x",
                             "f'{x}' = x",
                             ])

    def test_del(self):
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            ["del f''",
                             "del '' f''",
                             ])

    def test_mismatched_braces(self):
        self.assertAllRaise(SyntaxError, "f-string: single '}' is not allowed",
                            ["f'{{}'",
                             "f'{{}}}'",
                             "f'}'",
                             "f'x}'",
                             "f'x}x'",

                             # Can't have { or } in a format spec.
                             "f'{3:}>10}'",
                             r"f'{3:\\}>10}'",
                             "f'{3:}}>10}'",
                             ])

        self.assertAllRaise(SyntaxError, "f-string: expecting '}'",
                            ["f'{3:{{>10}'",
                             "f'{3'",
                             "f'{3!'",
                             "f'{3:'",
                             "f'{3!s'",
                             "f'{3!s:'",
                             "f'{3!s:3'",
                             "f'x{'",
                             "f'x{x'",
                             "f'{3:s'",
                             "f'{{{'",
                             "f'{{}}{'",
                             "f'{'",
                             ])

        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            [r"f'{3:\\{>10}'",
                             ])

        # But these are just normal strings.
        self.assertEqual(f'{"{"}', '{')
        self.assertEqual(f'{"}"}', '}')
        self.assertEqual(f'{3:{"}"}>10}', '}}}}}}}}}3')
        self.assertEqual(f'{2:{"{"}>10}', '{{{{{{{{{2')

    def test_if_conditional(self):
        # There's special logic in compile.c to test if the
        #  conditional for an if (and while) are constants. Exercise
        #  that code.

        def test_fstring(x, expected):
            flag = 0
            if f'{x}':
                flag = 1
            else:
                flag = 2
            self.assertEqual(flag, expected)

        def test_concat_empty(x, expected):
            flag = 0
            if '' f'{x}':
                flag = 1
            else:
                flag = 2
            self.assertEqual(flag, expected)

        def test_concat_non_empty(x, expected):
            flag = 0
            if ' ' f'{x}':
                flag = 1
            else:
                flag = 2
            self.assertEqual(flag, expected)

        test_fstring('', 2)
        test_fstring(' ', 1)

        test_concat_empty('', 2)
        test_concat_empty(' ', 1)

        test_concat_non_empty('', 1)
        test_concat_non_empty(' ', 1)

    def test_empty_format_specifier(self):
        x = 'test'
        self.assertEqual(f'{x}', 'test')
        self.assertEqual(f'{x:}', 'test')
        self.assertEqual(f'{x!s:}', 'test')
        self.assertEqual(f'{x!r:}', "'test'")

    def test_str_format_differences(self):
        d = {'a': 'string',
             0: 'integer',
             }
        a = 0
        self.assertEqual(f'{d[0]}', 'integer')
        self.assertEqual(f'{d["a"]}', 'string')
        self.assertEqual(f'{d[a]}', 'integer')
        self.assertEqual('{d[a]}'.format(d=d), 'string')
        self.assertEqual('{d[0]}'.format(d=d), 'integer')

    def test_invalid_expressions(self):
        self.assertAllRaise(SyntaxError, 'invalid syntax',
                            [r"f'{a[4)}'",
                             r"f'{a(4]}'",
                            ])

    def test_loop(self):
        for i in range(1000):
            self.assertEqual(f'i:{i}', 'i:' + str(i))

    def test_dict(self):
        d = {'"': 'dquote',
             "'": 'squote',
             'foo': 'bar',
             }
        self.assertEqual(f'{d["\'"]}', 'squote')
        self.assertEqual(f"{d['\"']}", 'dquote')

        self.assertEqual(f'''{d["'"]}''', 'squote')
        self.assertEqual(f"""{d['"']}""", 'dquote')

        self.assertEqual(f'{d["foo"]}', 'bar')
        self.assertEqual(f"{d['foo']}", 'bar')
        self.assertEqual(f'{d[\'foo\']}', 'bar')
        self.assertEqual(f"{d[\"foo\"]}", 'bar')

    def test_escaped_quotes(self):
        d = {'"': 'a',
             "'": 'b'}

        self.assertEqual(fr"{d['\"']}", 'a')
        self.assertEqual(fr'{d["\'"]}', 'b')
        self.assertEqual(fr"{'\"'}", '"')
        self.assertEqual(fr'{"\'"}', "'")
        self.assertEqual(f'{"\\"3"}', '"3')

        self.assertAllRaise(SyntaxError, 'f-string: unterminated string',
                            [r'''f'{"""\\}' ''',  # Backslash at end of expression
                             ])
        self.assertAllRaise(SyntaxError, 'unexpected character after line continuation',
                            [r"rf'{3\}'",
                             ])


if __name__ == '__main__':
    unittest.main()
