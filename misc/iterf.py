import ast

prog = """
try:
    3
except:
    "adf"
"""

root = ast.parse(prog)


def print_ast(node, level):
    print(" " * level, node)
    for name, child in ast.iter_fields(node):
        if isinstance(child, ast.AST):
            print(" " * level, name, ":")
            print_ast(child, level + 1)
        elif isinstance(child, list):
            print(" " * level, name, ":[")
            for elem in child:
                print_ast(elem, level + 1)
            print(" " * level, "]")
        else:
            pass
            # print(" " * level, "OOOO", node)


print_ast(root, 0)
