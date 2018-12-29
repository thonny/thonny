import os
import ast
from thonny.backend import get_vm

def augment_ast(root):
    # prepend "import pgzrun as __pgzrun"
    imp = ast.Import([ast.alias("pgzrun", "__pgzrun")])
    imp.lineno = 0
    imp.col_offset = 0
    ast.fix_missing_locations(imp)
    imp.tags = {"ignore"}
    root.body.insert(0, imp)
    
    # append "__pgzrun.go()"
    go = ast.Expr(
        ast.Call(
            ast.Attribute(
                ast.Name("__pgzrun", ast.Load()),
                "go",
                ast.Load()
            ),
            [],
            []
        )
    )
    go.lineno = 1000000
    go.col_offset = 0
    ast.fix_missing_locations(go)
    go.tags = {"ignore"}
    root.body.append(go)
    
def load_plugin():
    if os.environ.get("PGZERO_MODE", "False").lower() == "true":
        get_vm().add_ast_postprocessor(augment_ast)
        