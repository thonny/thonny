import ast
from textwrap import dedent

from thonny import ast_utils
from thonny.ast_utils import pretty


def test_single_assignment():
    check_marked_ast(
        "x=1",
        """/=Module
    body=[...]
        0=Assign @ 1.0  -  1.3
            targets=[...]
                0=Name @ 1.0  -  1.1
                    id='x'
                    ctx=Store
            value=Num @ 1.2  -  1.3
                n=1""",
    )


def test_simple_io_program():
    check_marked_ast(
        """age = int(input("Enter age: "))
if age > 18:
    print("Hi")
else:
    print("Hello!", end='')
    print("What's your name?")
""",
        """/=Module
    body=[...]
        0=Assign @ 1.0  -  1.31
            targets=[...]
                0=Name @ 1.0  -  1.3
                    id='age'
                    ctx=Store
            value=Call @ 1.6  -  1.31
                func=Name @ 1.6  -  1.9
                    id='int'
                    ctx=Load
                args=[...]
                    0=Call @ 1.10  -  1.30
                        func=Name @ 1.10  -  1.15
                            id='input'
                            ctx=Load
                        args=[...]
                            0=Str @ 1.16  -  1.29
                                s='Enter age: '
                        keywords=[]
                keywords=[]
        1=If @ 2.0  -  6.30
            test=Compare @ 2.3  -  2.11
                left=Name @ 2.3  -  2.6
                    id='age'
                    ctx=Load
                ops=[...]
                    0=Gt
                comparators=[...]
                    0=Num @ 2.9  -  2.11
                        n=18
            body=[...]
                0=Expr @ 3.4  -  3.15
                    value=Call @ 3.4  -  3.15
                        func=Name @ 3.4  -  3.9
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 3.10  -  3.14
                                s='Hi'
                        keywords=[]
            orelse=[...]
                0=Expr @ 5.4  -  5.27
                    value=Call @ 5.4  -  5.27
                        func=Name @ 5.4  -  5.9
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 5.10  -  5.18
                                s='Hello!'
                        keywords=[...]
                            0=keyword
                                arg='end'
                                value=Str @ 5.24  -  5.26
                                    s=''
                1=Expr @ 6.4  -  6.30
                    value=Call @ 6.4  -  6.30
                        func=Name @ 6.4  -  6.9
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 6.10  -  6.29
                                s="What's your name?"
                        keywords=[]""",
    )


def test_two_trivial_defs():
    check_marked_ast(
        """def f():
    pass
def f():
    pass""",
        """/=Module
    body=[...]
        0=FunctionDef @ 1.0  -  2.8
            name='f'
            args=arguments
                args=[]
                vararg=None
                kwonlyargs=[]
                kw_defaults=[]
                kwarg=None
                defaults=[]
            body=[...]
                0=Pass @ 2.4  -  2.8
            decorator_list=[]
            returns=None
        1=FunctionDef @ 3.0  -  4.8
            name='f'
            args=arguments
                args=[]
                vararg=None
                kwonlyargs=[]
                kw_defaults=[]
                kwarg=None
                defaults=[]
            body=[...]
                0=Pass @ 4.4  -  4.8
            decorator_list=[]
            returns=None""",
    )


def test_id_def():
    check_marked_ast(
        """def f(x):
    return x
""",
        """/=Module
    body=[...]
        0=FunctionDef @ 1.0  -  2.12
            name='f'
            args=arguments
                args=[...]
                    0=arg @ 1.6  -  1.7
                        arg='x'
                        annotation=None
                vararg=None
                kwonlyargs=[]
                kw_defaults=[]
                kwarg=None
                defaults=[]
            body=[...]
                0=Return @ 2.4  -  2.12
                    value=Name @ 2.11  -  2.12
                        id='x'
                        ctx=Load
            decorator_list=[]
            returns=None""",
    )


def test_simple_while_program():
    check_marked_ast(
        """x = int(input("Enter number: "))

while x > 0:
    print(x)
    x -= 1
""",
        """/=Module
    body=[...]
        0=Assign @ 1.0  -  1.32
            targets=[...]
                0=Name @ 1.0  -  1.1
                    id='x'
                    ctx=Store
            value=Call @ 1.4  -  1.32
                func=Name @ 1.4  -  1.7
                    id='int'
                    ctx=Load
                args=[...]
                    0=Call @ 1.8  -  1.31
                        func=Name @ 1.8  -  1.13
                            id='input'
                            ctx=Load
                        args=[...]
                            0=Str @ 1.14  -  1.30
                                s='Enter number: '
                        keywords=[]
                keywords=[]
        1=While @ 3.0  -  5.10
            test=Compare @ 3.6  -  3.11
                left=Name @ 3.6  -  3.7
                    id='x'
                    ctx=Load
                ops=[...]
                    0=Gt
                comparators=[...]
                    0=Num @ 3.10  -  3.11
                        n=0
            body=[...]
                0=Expr @ 4.4  -  4.12
                    value=Call @ 4.4  -  4.12
                        func=Name @ 4.4  -  4.9
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Name @ 4.10  -  4.11
                                id='x'
                                ctx=Load
                        keywords=[]
                1=AugAssign @ 5.4  -  5.10
                    target=Name @ 5.4  -  5.5
                        id='x'
                        ctx=Store
                    op=Sub
                    value=Num @ 5.9  -  5.10
                        n=1
            orelse=[]""",
    )


def test_call_with_pos_and_kw_arg():
    check_marked_ast(
        """f(3, t=45)
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.10
            value=Call @ 1.0  -  1.10
                func=Name @ 1.0  -  1.1
                    id='f'
                    ctx=Load
                args=[...]
                    0=Num @ 1.2  -  1.3
                        n=3
                keywords=[...]
                    0=keyword
                        arg='t'
                        value=Num @ 1.7  -  1.9
                            n=45""",
    )


def test_call_with_pos_star_kw():
    check_marked_ast(
        """f(3, *kala, t=45)
    """,
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.17
            value=Call @ 1.0  -  1.17
                func=Name @ 1.0  -  1.1
                    id='f'
                    ctx=Load
                args=[...]
                    0=Num @ 1.2  -  1.3
                        n=3
                    1=Starred @ 1.5  -  1.10
                        value=Name @ 1.6  -  1.10
                            id='kala'
                            ctx=Load
                        ctx=Load
                keywords=[...]
                    0=keyword
                        arg='t'
                        value=Num @ 1.14  -  1.16
                            n=45""",
    )


def test_call_with_single_keyword():
    check_marked_ast(
        """fff(t=45)
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.9
            value=Call @ 1.0  -  1.9
                func=Name @ 1.0  -  1.3
                    id='fff'
                    ctx=Load
                args=[]
                keywords=[...]
                    0=keyword
                        arg='t'
                        value=Num @ 1.6  -  1.8
                            n=45""",
    )


def test_call_without_arguments():
    check_marked_ast(
        """fff()
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.5
            value=Call @ 1.0  -  1.5
                func=Name @ 1.0  -  1.3
                    id='fff'
                    ctx=Load
                args=[]
                keywords=[]""",
    )


def test_call_with_attribute_function_and_keyword_arg():
    check_marked_ast(
        """rida.strip().split(maxsplit=1)
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.30
            value=Call @ 1.0  -  1.30
                func=Attribute @ 1.0  -  1.18
                    value=Call @ 1.0  -  1.12
                        func=Attribute @ 1.0  -  1.10
                            value=Name @ 1.0  -  1.4
                                id='rida'
                                ctx=Load
                            attr='strip'
                            ctx=Load
                        args=[]
                        keywords=[]
                    attr='split'
                    ctx=Load
                args=[]
                keywords=[...]
                    0=keyword
                        arg='maxsplit'
                        value=Num @ 1.28  -  1.29
                            n=1""",
    )


def test_del_from_list_with_integer():
    check_marked_ast(
        """del x[0]""",
        """/=Module
    body=[...]
        0=Delete @ 1.0  -  1.8
            targets=[...]
                0=Subscript @ 1.4  -  1.8
                    value=Name @ 1.4  -  1.5
                        id='x'
                        ctx=Load
                    slice=Index
                        value=Num @ 1.6  -  1.7
                            n=0
                    ctx=Del""",
    )


def test_del_from_list_with_string():
    check_marked_ast(
        """del x["blah"]""",
        """/=Module
    body=[...]
        0=Delete @ 1.0  -  1.13
            targets=[...]
                0=Subscript @ 1.4  -  1.13
                    value=Name @ 1.4  -  1.5
                        id='x'
                        ctx=Load
                    slice=Index
                        value=Str @ 1.6  -  1.12
                            s='blah'
                    ctx=Del""",
    )


def test_full_slice1():
    check_marked_ast(
        """blah[:]
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.7
            value=Subscript @ 1.0  -  1.7
                value=Name @ 1.0  -  1.4
                    id='blah'
                    ctx=Load
                slice=Slice
                    lower=None
                    upper=None
                    step=None
                ctx=Load""",
    )


def test_full_slice2():
    check_marked_ast(
        """blah[::]
""",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.8
            value=Subscript @ 1.0  -  1.8
                value=Name @ 1.0  -  1.4
                    id='blah'
                    ctx=Load
                slice=Slice
                    lower=None
                    upper=None
                    step=None
                ctx=Load""",
    )


def test_non_ascii_letters_with_calls_etc():
    check_marked_ast(
        """täpitähed = "täpitähed"
print(täpitähed["tšahh"])
pöhh(pöhh=3)
""",
        """/=Module
    body=[...]
        0=Assign @ 1.0  -  1.23
            targets=[...]
                0=Name @ 1.0  -  1.9
                    id='täpitähed'
                    ctx=Store
            value=Str @ 1.12  -  1.23
                s='täpitähed'
        1=Expr @ 2.0  -  2.25
            value=Call @ 2.0  -  2.25
                func=Name @ 2.0  -  2.5
                    id='print'
                    ctx=Load
                args=[...]
                    0=Subscript @ 2.6  -  2.24
                        value=Name @ 2.6  -  2.15
                            id='täpitähed'
                            ctx=Load
                        slice=Index
                            value=Str @ 2.16  -  2.23
                                s='tšahh'
                        ctx=Load
                keywords=[]
        2=Expr @ 3.0  -  3.12
            value=Call @ 3.0  -  3.12
                func=Name @ 3.0  -  3.4
                    id='pöhh'
                    ctx=Load
                args=[]
                keywords=[...]
                    0=keyword
                        arg='pöhh'
                        value=Num @ 3.10  -  3.11
                            n=3""",
    )


def test_nested_binops():
    """http://bugs.python.org/issue18374"""
    check_marked_ast(
        "1+2-3",
        """/=Module
    body=[...]
        0=Expr @ 1.0  -  1.5
            value=BinOp @ 1.0  -  1.5
                left=BinOp @ 1.0  -  1.3
                    left=Num @ 1.0  -  1.1
                        n=1
                    op=Add
                    right=Num @ 1.2  -  1.3
                        n=2
                op=Sub
                right=Num @ 1.4  -  1.5
                    n=3""",
    )


def test_multiline_string():
    """http://bugs.python.org/issue18370"""
    check_marked_ast(
        """pass
blah = \"\"\"first
second
third\"\"\"
pass""",
        """/=Module
    body=[...]
        0=Pass @ 1.0  -  1.4
        1=Assign @ 2.0  -  4.8
            targets=[...]
                0=Name @ 2.0  -  2.4
                    id='blah'
                    ctx=Store
            value=Str @ 2.7  -  4.8
                s='first\\nsecond\\nthird'
        2=Pass @ 5.0  -  5.4""",
    )


def check_marked_ast(
    source,
    expected_pretty_ast
    # ,expected_for_py_34=None
):

    # if (sys.version_info[:2] == (3,4)
    #    and expected_for_py_34 is not None):
    #    expected_pretty_ast = expected_for_py_34

    source = dedent(source)
    root = ast.parse(source)
    ast_utils.mark_text_ranges(root, source.encode("utf-8"))
    actual_pretty_ast = pretty(root)
    # print("ACTUAL", actual_pretty_ast)
    # print("EXPECTED", expected_pretty_ast)
    assert actual_pretty_ast.strip() == expected_pretty_ast.strip()
