import ast
from textwrap import dedent

from thonny.ast_utils import pretty


def test_pretty_without_end_markers():
    p = pretty(
        ast.parse(
            dedent(
                """
    age = int(input("Enter age: "))
    if age > 18:
        print("Hi")
    else:
        print("Hello!", end='')
        print("What's your name?")
    """
            ).strip()
        )
    )

    assert (
        p
        == """/=Module
    body=[...]
        0=Assign @ 1.0
            targets=[...]
                0=Name @ 1.0
                    id='age'
                    ctx=Store
            value=Call @ 1.6
                func=Name @ 1.6
                    id='int'
                    ctx=Load
                args=[...]
                    0=Call @ 1.10
                        func=Name @ 1.10
                            id='input'
                            ctx=Load
                        args=[...]
                            0=Str @ 1.16
                                s='Enter age: '
                        keywords=[]
                keywords=[]
        1=If @ 2.0
            test=Compare @ 2.3
                left=Name @ 2.3
                    id='age'
                    ctx=Load
                ops=[...]
                    0=Gt
                comparators=[...]
                    0=Num @ 2.9
                        n=18
            body=[...]
                0=Expr @ 3.4
                    value=Call @ 3.4
                        func=Name @ 3.4
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 3.10
                                s='Hi'
                        keywords=[]
            orelse=[...]
                0=Expr @ 5.4
                    value=Call @ 5.4
                        func=Name @ 5.4
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 5.10
                                s='Hello!'
                        keywords=[...]
                            0=keyword
                                arg='end'
                                value=Str @ 5.24
                                    s=''
                1=Expr @ 6.4
                    value=Call @ 6.4
                        func=Name @ 6.4
                            id='print'
                            ctx=Load
                        args=[...]
                            0=Str @ 6.10
                                s="What's your name?"
                        keywords=[]"""
    )
