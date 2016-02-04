import ast
import sys
from thonny.ast_utils import pretty 
from textwrap import dedent
from thonny import ast_utils

def test_pretty_without_end_markers():
    p = pretty(ast.parse(dedent("""
    age = int(input("Enter age: "))
    if age > 18:
        print("Hi")
    else:
        print("Hello!", end='')
        print("What's your name?")
    """).strip()))
    
    assert p == """/=Module
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

def test_mark_text_ranges_single_assignment():
    check_marked_ast("x=1", """/=Module
    body=[...]
        0=Assign @ 1.0  -  1.3
            targets=[...]
                0=Name @ 1.0  -  1.1
                    id='x'
                    ctx=Store
            value=Num @ 1.2  -  1.3
                n=1""")


def check_marked_ast(source, expected_pretty_ast
                     #,expected_for_py_34=None
                     ):
    
    #if (sys.version_info[:2] == (3,4) 
    #    and expected_for_py_34 is not None):
    #    expected_pretty_ast = expected_for_py_34
        
    source = dedent(source)
    root = ast.parse(source)
    ast_utils.mark_text_ranges(root, source)
    actual_pretty_ast = pretty(root)
    assert actual_pretty_ast.strip() == dedent(expected_pretty_ast).strip() 
    
