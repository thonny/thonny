import os.path
import logging
import tkinter as tk

from thonny import get_workbench, jedi_utils
from thonny.ui_utils import control_is_pressed

logger = logging.getLogger(__name__)


def goto_definition(event):
    if not control_is_pressed(event.state):
        return

    assert isinstance(event.widget, tk.Text)
    text = event.widget

    source = text.get("1.0", "end")
    index = text.index("insert")
    index_parts = index.split(".")
    line, column = int(index_parts[0]), int(index_parts[1])
    try:
        editor = text.master.home_widget
        path = editor.get_filename()
    except Exception as e:
        logger.warning("Could not get path", exc_info=e)
        path = None

    defs = jedi_utils.get_definitions(source, line, column, path)
    if len(defs) > 0:
        # TODO: handle multiple results like PyCharm
        module_path = str(defs[0].module_path)
        if not os.path.isfile(module_path):
            logger.warning("%s is not a file", module_path)
            return

        module_name = defs[0].module_name
        line = defs[0].line
        if module_path and line is not None:
            get_workbench().get_editor_notebook().show_file(module_path, line)
        elif module_name == "" and line is not None:  # current editor
            get_workbench().get_editor_notebook().get_current_editor().select_range(line)


def load_plugin() -> None:
    wb = get_workbench()
    wb.bind_class("CodeViewText", "<1>", goto_definition, True)
