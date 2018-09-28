import tkinter as tk

from jedi import Script

from thonny import get_workbench
from thonny.ui_utils import control_is_pressed


def goto_definition(event):
    if not control_is_pressed(event.state):
        return

    assert isinstance(event.widget, tk.Text)
    text = event.widget

    source = text.get("1.0", "end")
    index = text.index("insert")
    index_parts = index.split(".")
    line, column = int(index_parts[0]), int(index_parts[1])
    # TODO: find current editor filename
    script = Script(source, line=line, column=column, path="")
    defs = script.goto_definitions()
    if len(defs) > 0:
        module_path = defs[0].module_path
        module_name = defs[0].module_name
        line = defs[0].line
        if module_path and line is not None:
            get_workbench().get_editor_notebook().show_file(module_path, line)
        elif module_name == "" and line is not None:  # current editor
            get_workbench().get_editor_notebook().get_current_editor().select_range(
                line
            )


def load_plugin() -> None:
    wb = get_workbench()
    wb.bind_class("CodeViewText", "<1>", goto_definition, True)
