import os.path
import tkinter as tk
from logging import getLogger
from tkinter import messagebox
from typing import Set, cast

from thonny import get_runner, get_workbench
from thonny.codeview import CodeViewText, SyntaxText
from thonny.common import InlineCommand
from thonny.editor_helpers import get_relevant_source_and_cursor_position, get_text_filename
from thonny.languages import tr
from thonny.misc_utils import running_on_mac_os
from thonny.ui_utils import command_is_pressed, control_is_pressed, get_hyperlink_cursor

logger = getLogger(__name__)


class GotoHandler:
    def __init__(self):
        wb = get_workbench()
        wb.bind_class("EditorCodeViewText", "<1>", self.request_definitions, True)
        wb.bind_class("EditorCodeViewText", "<Any-Motion>", self.on_motion, True)
        wb.bind_class("EditorCodeViewText", "<Any-Leave>", self.remove_underline, True)
        if running_on_mac_os():
            wb.bind_class("EditorCodeViewText", "<Command-KeyRelease>", self.remove_underline, True)
        else:
            wb.bind_class("EditorCodeViewText", "<Control-KeyRelease>", self.remove_underline, True)
        wb.bind("get_definitions_response", self.handle_definitions_response, True)

    def request_definitions(self, event=None):
        if not self.proper_modifier_is_pressed(event):
            return

        assert isinstance(event.widget, CodeViewText)
        text = event.widget

        source, row, column = get_relevant_source_and_cursor_position(text)
        filename = get_text_filename(text)
        if not get_runner() or not get_runner().get_backend_proxy():
            return

        get_runner().send_command(
            InlineCommand(
                "get_definitions", source=source, row=row, column=column, filename=filename
            )
        )

    def proper_modifier_is_pressed(self, event: tk.Event) -> bool:
        if running_on_mac_os():
            return command_is_pressed(event)
        else:
            return control_is_pressed(event)

    def handle_definitions_response(self, msg):
        defs = msg.definitions
        if len(defs) != 1:
            messagebox.showerror(
                tr("Problem"), tr("Could not find definition"), master=get_workbench()
            )
            return

        # TODO: handle multiple results like PyCharm

        module_path = str(defs[0].module_path)
        if not os.path.isfile(module_path):
            logger.warning("%s is not a file", module_path)
            return

        module_name = defs[0].module_name
        row = defs[0].row
        if module_path and row is not None:
            get_workbench().get_editor_notebook().show_file(module_path, row)
        elif module_name == "" and row is not None:  # current editor
            get_workbench().get_editor_notebook().get_current_editor().select_range(row)

    def on_motion(self, event):
        text = cast(SyntaxText, event.widget)
        if self.proper_modifier_is_pressed(event):
            self.remove_underline(event)
            start_index = text.index(f"@{event.x},{event.y} wordstart")
            end_index = text.index(f"@{event.x},{event.y} wordend")
            # sometimes, start_index will contain wrong line number
            start_line, start_col = start_index.split(".")
            end_line, end_col = end_index.split(".")
            if start_line != end_line:
                start_index = end_line + "." + start_col

            word = text.get(start_index, end_index)
            if (
                word
                and (word[0].isalpha() or word[0] == "_")
                # and not iskeyword(word)
                and self._index_doesnt_have_tags(
                    text,
                    start_index,
                    {"string", "string3", "open_string", "open_string3", "comment"},
                )
            ):
                text.tag_add("name_link", start_index, end_index)
                text["cursor"] = get_hyperlink_cursor()
                text.underlined = True
        else:
            if getattr(text, "underlined", False):
                self.remove_underline(event)

    def _index_doesnt_have_tags(self, text, index, tags: Set[str]) -> bool:
        return not (set(text.tag_names(index)) & tags)

    def remove_underline(self, event=None):
        text = cast(SyntaxText, event.widget)
        text.tag_remove("name_link", "1.0", "end")
        text["cursor"] = ""
        text.underlined = False


def load_plugin() -> None:
    goto_handler = GotoHandler()
