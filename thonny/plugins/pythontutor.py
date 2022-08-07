import webbrowser
from urllib.parse import urlencode

from thonny import get_workbench
from thonny.languages import tr


def _do_visualize() -> None:
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if editor is None:
        return

    content = editor.get_content()
    if not content.strip():
        return

    args = {
        "code": content,
        "cumulative": "false",
        "curInstr": "0",
        "heapPrimitives": "nevernest",
        "mode": "display",
        "origin": "opt-frontend.js",
        "py": "3",
        "rawInputLstJSON": "[]",
        "textReferences": "false",
    }
    url = f"https://pythontutor.com/visualize.html#{urlencode(args)}"
    webbrowser.open(url)


def _can_visualize() -> bool:
    editor = get_workbench().get_editor_notebook().get_current_editor()
    return editor is not None and editor.get_content().strip()


def load_plugin():
    get_workbench().add_command(
        "visualize_in_pythontutor",
        "run",
        tr("Visualize current script at Python Tutor"),
        _do_visualize,
        tester=_can_visualize,
        group=11,
    )
