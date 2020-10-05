import ast
import os
import sys

from thonny.plugins.cpython.cpython_backend import get_backend, MainCPythonBackend


def augment_ast(root):
    mode = os.environ.get("PGZERO_MODE", "False")
    assert mode != "False"

    warning_prelude = "WARNING: Pygame Zero mode is turned on (Run → Pygame Zero mode)"
    try:
        import pgzero  # @UnusedImport
    except ImportError:
        if mode == "True":
            print(
                warning_prelude
                + ",\nbut pgzero module is not found. Running program in regular mode.\n",
                file=sys.stderr,
            )
        else:
            assert mode == "auto"

        return

    # Check if draw is defined
    for stmt in root.body:
        if isinstance(stmt, ast.FunctionDef) and stmt.name == "draw":
            break
    else:
        if mode == "auto":
            return
        else:
            print(
                warning_prelude
                + ",\nbut your program doesn't look like usual Pygame Zero program\n"
                + "(draw function is missing).\n",
                file=sys.stderr,
            )

    # need more checks in auto mode
    if mode == "auto":
        # check that draw method is not called in the code
        for node in ast.walk(root):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "draw"
            ):
                return

    # prepend "import pgzrun as __pgzrun"
    imp = ast.Import([ast.alias("pgzrun", "__pgzrun")])
    imp.lineno = 0
    imp.col_offset = 0
    ast.fix_missing_locations(imp)
    imp.tags = {"ignore"}
    root.body.insert(0, imp)

    # append "__pgzrun.go()"
    go = ast.Expr(
        ast.Call(ast.Attribute(ast.Name("__pgzrun", ast.Load()), "go", ast.Load()), [], [])
    )
    go.lineno = 1000000
    go.col_offset = 0
    ast.fix_missing_locations(go)
    go.tags = {"ignore"}
    root.body.append(go)


def patched_editor_autocomplete(self, cmd):
    # Make extra builtins visible for Jedi
    prefix = "from pgzero.builtins import *\n"
    cmd["source"] = prefix + cmd["source"]
    cmd["row"] = cmd["row"] + 1

    result = get_backend()._original_editor_autocomplete(cmd)
    result["row"] = result["row"] - 1
    result["source"] = result["source"][len(prefix) :]

    return result


def load_plugin():
    if os.environ.get("PGZERO_MODE", "False").lower() == "false":
        return

    get_backend().add_ast_postprocessor(augment_ast)
    MainCPythonBackend._original_editor_autocomplete = MainCPythonBackend._cmd_editor_autocomplete
    MainCPythonBackend._cmd_editor_autocomplete = patched_editor_autocomplete
