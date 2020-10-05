import ast

from thonny.plugins.cpython.cpython_backend import get_backend


def augment_source(source, cmd):
    if "Flask" not in source:
        # don't bother analyzing further
        return source

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source

    var_name = None
    found_run = False

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)  # TODO: could be also flask.Flask
            and node.value.func.id == "Flask"
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        ):
            var_name = node.targets[0].id
        elif (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == var_name
            and node.func.attr == "run"
        ):
            found_run = True

    if not var_name or found_run:
        return source
    else:
        return (
            source
            + """

if "{app_name}" in globals():
    import os as __temp_os__
    if "FLASK_ENV" not in __temp_os__.environ:
        __temp_os__.environ["FLASK_ENV"] = "development"
    del __temp_os__
    
    # Conservative options for minimum technical risks.
    # Users who need more control should call run explicitly.
    print(" # Running the app with options chosen by Thonny. See Help for details.")
    {app_name}.run(threaded=False, debug=False, use_reloader=False)
""".format(
                app_name=var_name
            )
        )


def load_plugin():
    get_backend().add_source_preprocessor(augment_source)
