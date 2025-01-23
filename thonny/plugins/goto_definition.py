import tkinter as tk
from logging import getLogger
from tkinter import messagebox
from typing import List, Set, Union, cast

from thonny import get_workbench, lsp_types
from thonny.codeview import CodeViewText, SyntaxText
from thonny.editor_helpers import get_cursor_ls_position
from thonny.editors import Editor
from thonny.languages import tr
from thonny.lsp_types import DefinitionParams, LspResponse, TextDocumentIdentifier
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

        editor = text.master.master
        assert isinstance(editor, Editor)
        uri = editor.get_uri()
        if uri is None:
            return  # TODO
        pos = get_cursor_ls_position(text)

        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is None:
            return

        ls_proxy.unbind_request_handler(self.handle_definitions_response)

        ls_proxy.request_definition(
            DefinitionParams(TextDocumentIdentifier(uri=uri), position=pos),
            self.handle_definitions_response,
        )

    def proper_modifier_is_pressed(self, event: tk.Event) -> bool:
        if running_on_mac_os():
            return command_is_pressed(event)
        else:
            return control_is_pressed(event)

    def handle_definitions_response(
        self, response: LspResponse[Union[lsp_types.Definition, List[lsp_types.LocationLink], None]]
    ) -> None:

        result = response.get_result_or_raise()
        if not result:
            messagebox.showerror(
                tr("Problem"), tr("Could not find definition"), master=get_workbench()
            )
            return

        if isinstance(result, list):
            # TODO: handle multiple results like PyCharm
            first_def = result[0]
        else:
            first_def = cast(lsp_types.Location, result)

        if isinstance(first_def, lsp_types.LocationLink):
            uri = first_def.targetUri
            range = first_def.targetRange
        else:
            assert isinstance(first_def, lsp_types.Location)
            uri = first_def.uri
            range = first_def.range

        if range is not None:
            # TODO: Select range instead?
            line = range.start.line + 1
        else:
            line = None

        logger.info("Going to %s, line %s", uri, line)
        get_workbench().get_editor_notebook().show_file(uri, line)

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
