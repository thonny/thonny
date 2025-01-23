import tkinter as tk
from logging import getLogger
from tkinter import messagebox
from typing import Optional

from thonny import editor_helpers, get_workbench
from thonny.codeview import CodeViewText, SyntaxText
from thonny.editor_helpers import DocuBoxBase, get_active_text_widget
from thonny.editors import Editor
from thonny.languages import tr
from thonny.lsp_types import (
    LspResponse,
    SignatureHelp,
    SignatureHelpParams,
    SignatureInformation,
    TextDocumentIdentifier,
)
from thonny.shell import ShellText
from thonny.ui_utils import ems_to_pixels

logger = getLogger(__name__)


class CalltipBox(DocuBoxBase):
    def __init__(self, calltipper: "Calltipper"):
        super(CalltipBox, self).__init__(show_vertical_scrollbar=False)
        self._calltipper = calltipper
        self._max_width = 40

    def present_signatures(self, text: SyntaxText, signature_help: SignatureHelp):
        self._target_text_widget = text
        self._check_bind_for_keypress(text)
        self.text.direct_delete("1.0", "end")
        self.render_signature_help(signature_help)

        char_count = self.text.count("1.0", "end", "chars")[0]
        extra_width_factor = 1.0
        # NB! Width should be set here, not in update_size, so that it that on-screen
        # height calculation already uses this
        if char_count * extra_width_factor < self._max_width:
            self.text["width"] = max(round(char_count * extra_width_factor), 10)
        else:
            self.text["width"] = self._max_width

        self.text["height"] = 3

        expected_height = 10  # TODO
        # call_bracket_start = ... # TODO
        row, column = editor_helpers.get_cursor_position(text)
        if isinstance(text, ShellText):
            row -= text.get_current_line_ls_offset()
            column -= text.get_current_column_ls_offset()

        self._show_on_target_text(
            "%d.%d" % (row, column),
            expected_height,
            "above",
            y_offset=-ems_to_pixels(0.3),
        )

    def _update_size(self):
        # will be called while box is off the screen
        display_line_count = self.text.count("1.0", "end", "displaylines")[0]
        self.text["height"] = display_line_count

    def _on_text_keypress(self, event=None):
        if not self.is_visible():
            return

        if event.keysym == "Escape":
            return

        if event.char or event.keysym in [
            "Left",
            "Right",
            "Up",
            "Down",
            "KP_Left",
            "KP_Right",
            "KP_Up",
            "KP_Down",
        ]:
            self.after_idle(self._calltipper.request_calltip)

    def render_signature_help(self, signature_help: SignatureHelp) -> None:
        for i, sig in enumerate(signature_help.signatures):
            if i > 0:
                self._append_chars("\n")
            self.render_signature(
                sig,
                is_active=i == signature_help.activeSignature,
                global_active_parameter=signature_help.activeParameter,
            )

    def render_signature(
        self, sig: SignatureInformation, is_active: bool, global_active_parameter: Optional[int]
    ) -> None:
        active_parameter = sig.activeParameter
        if active_parameter is None:
            active_parameter = global_active_parameter

        if active_parameter is None or len(sig.parameters) <= active_parameter:
            self._append_chars(sig.label)
        else:
            active_start, active_end = sig.parameters[active_parameter].label
            self._append_chars(sig.label[:active_start])
            self._append_chars(sig.label[active_start:active_end], tags=("active",))
            self._append_chars(sig.label[active_end:])


class Calltipper:
    def __init__(self):
        self._last_request_text: Optional[SyntaxText] = None
        self._last_request_uri = None
        self._last_request_position = None
        self._calltip_box: Optional[CalltipBox] = None
        get_workbench().bind("get_editor_calltip_response", self.handle_response, True)
        get_workbench().bind("get_shell_calltip_response", self.handle_response, True)
        get_workbench().bind("AutocompletionInserted", self._on_autocomplete_insertion, True)
        get_workbench().bind_class("EditorCodeViewText", "<Key>", self._on_text_key, True)
        get_workbench().bind_class("ShellText", "<Key>", self._on_text_key, True)

    def request_calltip(self) -> None:
        text = get_active_text_widget()
        if not text:
            return
        self.request_calltip_for_text(text)

    def request_calltip_for_text(self, text: SyntaxText) -> None:
        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is None:
            return

        ls_proxy.unbind_request_handler(self.handle_response)

        if isinstance(text, CodeViewText):
            editor = text.master.master
            assert isinstance(editor, Editor)

            editor.send_changes_to_primed_servers()
            uri = editor.get_uri()
            position = editor_helpers.get_cursor_ls_position(text)
        elif isinstance(text, ShellText):
            text.send_changes_to_language_server()
            uri = text.get_ls_uri()
            position = editor_helpers.get_cursor_ls_position(
                text, text.get_current_line_ls_offset(), text.get_current_column_ls_offset()
            )

        else:
            logger.warning("Unexpected calltip request in %r", text)
            return

        if uri is None:
            # TODO:
            return

        self._last_request_text = text
        ls_proxy.request_signature_help(
            SignatureHelpParams(
                textDocument=TextDocumentIdentifier(uri), position=position, context=None
            ),
            self.handle_response,
        )
        self._last_request_uri = uri
        self._last_request_position = position

    def handle_response(self, response: LspResponse[Optional[SignatureHelp]]) -> None:
        if not self._last_request_text:
            logger.warning("SignatureHelp response without _last_request_text")
            return

        if isinstance(self._last_request_text, CodeViewText):
            editor = self._last_request_text.master.master
            assert isinstance(editor, Editor)
            uri = editor.get_uri()
            position = editor_helpers.get_cursor_ls_position(self._last_request_text)
        else:
            assert isinstance(self._last_request_text, ShellText)
            uri = self._last_request_text.get_ls_uri()
            position = editor_helpers.get_cursor_ls_position(
                self._last_request_text,
                self._last_request_text.get_current_line_ls_offset(),
                self._last_request_text.get_current_column_ls_offset(),
            )

        if uri != self._last_request_uri or position != self._last_request_position:
            logger.warning("Got outdated SignatureHelp response: %r", response)
            return

        if response.get_error():
            self._hide_box()
            messagebox.showerror(
                "Calltip error", response.get_error().message, master=get_workbench()
            )
            return

        result = response.get_result_or_raise()

        if not result or not result.signatures:
            logger.info("Server gave 0 signatures")
            self._hide_box()
        else:
            if not self._calltip_box:
                self._calltip_box = CalltipBox(self)
            self._calltip_box.present_signatures(self._last_request_text, result)

    def _on_autocomplete_insertion(self, event=None):
        text = get_active_text_widget()
        if not text:
            return

        if (
            self._box_is_visible()
            or self._should_show_automatically()
            and text.get("insert -1 chars") == "("
        ):
            self.request_calltip_for_text(text)

    def _should_show_automatically(self) -> bool:
        return get_workbench().get_option("edit.automatic_calltips")

    def _box_is_visible(self):
        return self._calltip_box and self._calltip_box.is_visible()

    def _hide_box(self) -> None:
        if self._calltip_box:
            self._calltip_box.hide()

    def _on_text_key(self, event: tk.Event) -> None:
        if event.char == "(" and self._should_show_automatically():
            self.request_calltip_for_text(event.widget)


def load_plugin():
    calltipper = Calltipper()

    get_workbench().set_default("edit.automatic_calltips", False)

    get_workbench().add_command(
        "open_calltip",
        "edit",
        tr("Show parameter info"),
        calltipper.request_calltip,
        # TODO: tester
        default_sequence="<<ShiftControlSpaceInText>>",
        accelerator="Ctrl-Shift-Space",
    )
