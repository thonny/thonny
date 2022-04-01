import tkinter as tk
import traceback
from logging import getLogger
from tkinter import messagebox
from typing import List, Optional

from thonny import editor_helpers, get_runner, get_workbench
from thonny.codeview import SyntaxText
from thonny.common import InlineCommand, SignatureInfo
from thonny.editor_helpers import DocuBoxBase, get_active_text_widget, get_text_filename
from thonny.languages import tr
from thonny.shell import ShellText
from thonny.ui_utils import ems_to_pixels

logger = getLogger(__name__)


class CalltipBox(DocuBoxBase):
    def __init__(self, calltipper: "Calltipper"):
        super(CalltipBox, self).__init__(show_vertical_scrollbar=False)
        self._calltipper = calltipper
        self._max_width = 40

    def present_signatures(self, text: SyntaxText, signatures: List[SignatureInfo]):
        self._target_text_widget = text
        self._check_bind_for_keypress(text)
        self.text.direct_delete("1.0", "end")
        self.render_signatures(signatures, only_params=True)

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
        pos = signatures[0].call_bracket_start
        if pos:
            self._show_on_target_text(
                "%d.%d" % pos,
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


class Calltipper:
    def __init__(self):
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
        source, row, column = editor_helpers.get_relevant_source_and_cursor_position(text)
        get_runner().send_command(
            InlineCommand(
                "get_shell_calltip" if isinstance(text, ShellText) else "get_editor_calltip",
                row=row,
                column=column,
                source=source,
                filename=get_text_filename(text),
            )
        )

    def handle_response(self, msg) -> None:
        text = get_active_text_widget()
        if not text:
            return

        source, row, column = editor_helpers.get_relevant_source_and_cursor_position(text)

        if msg.get("error"):
            self._hide_box()
            messagebox.showerror("Calltip error", msg.error, master=get_workbench())
        elif msg.source != source or msg.row != row or msg.column != column:
            # situation has changed, information is obsolete
            return
        elif not msg.signatures:
            logger.debug("Back-end gave 0 signatures")
            self._hide_box()
        else:
            if not self._calltip_box:
                self._calltip_box = CalltipBox(self)
            self._calltip_box.present_signatures(text, msg.signatures)

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
