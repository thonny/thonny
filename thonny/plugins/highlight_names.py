import time
import tkinter as tk
from logging import getLogger
from tkinter import messagebox
from typing import List, Union

from thonny import get_runner, get_workbench, lsp_types
from thonny.codeview import SyntaxText
from thonny.editor_helpers import get_cursor_ls_position
from thonny.editors import Editor
from thonny.languages import tr
from thonny.lsp_types import DocumentHighlightParams, LspResponse, TextDocumentIdentifier

logger = getLogger(__name__)


def _is_python_name_char(char: str) -> bool:
    return bool(char) and (char == "_" or char.isalnum())


class OccurrencesHighlighter:
    def __init__(self, text):
        self.text: SyntaxText = text
        self._request_scheduled: bool = False
        self._request_in_progress: bool = False
        self._request_refresh_pending: bool = False
        self._active_request_serial: Union[int, None] = None
        self._last_request_serial: int = 0

    def get_positions_for(self, source, line, column):
        raise NotImplementedError()

    def get_positions(self):
        index = self.text.index("insert")

        # ignore if cursor in open string
        if self.text.tag_prevrange("open_string", index) or self.text.tag_prevrange(
            "open_string3", index
        ):
            return set()

        source = self.text.get("1.0", "end")
        index_parts = index.split(".")
        line, column = int(index_parts[0]), int(index_parts[1])

        return self.get_positions_for(source, line, column)

    def _should_request(self) -> bool:
        previous_char = self.text.get("insert -1 chars", "insert")
        current_char = self.text.get("insert", "insert +1 chars")
        return _is_python_name_char(previous_char) or _is_python_name_char(current_char)

    def trigger(self):
        self._clear()

        if (
            not get_workbench().get_option("view.name_highlighting")
            or not self.text.is_python_text()
        ):
            return

        if not self._should_request():
            return

        if self._request_in_progress:
            self._request_refresh_pending = True
            return

        def consider_request():
            if time.time() - self.text.get_last_operation_time() < 0.3:
                # wait a bit more, there may be more keypresses or cursor location changes coming
                self.text.after(100, consider_request)
            else:
                try:
                    if self._should_request():
                        if self._request_in_progress:
                            self._request_refresh_pending = True
                        else:
                            self._request()
                finally:
                    self._request_scheduled = False

        if not self._request_scheduled:
            self._request_scheduled = True
            self.text.after_idle(consider_request)

    def _clear(self) -> None:
        self.text.tag_remove("matched_name", "1.0", "end")

    def _request(self):
        self._clear()

        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is None:
            return

        editor = self.text.master.master
        assert isinstance(editor, Editor)
        editor.send_changes_to_primed_servers()

        pos = get_cursor_ls_position(self.text)
        uri = editor.get_uri()
        if uri is None:
            return

        self._request_in_progress = True
        self._request_refresh_pending = False
        self._last_request_serial += 1
        request_serial = self._last_request_serial
        self._active_request_serial = request_serial
        self.text.after(2500, lambda serial=request_serial: self._handle_request_timeout(serial))

        def handle_response(
            response: LspResponse[Union[List[lsp_types.DocumentHighlight], None]],
        ) -> None:
            self._handle_response(request_serial, response)

        ls_proxy.request_document_highlight(
            DocumentHighlightParams(textDocument=TextDocumentIdentifier(uri=uri), position=pos),
            handle_response,
        )

    def _handle_request_timeout(self, request_serial: int) -> None:
        self._finish_request(request_serial)

    def _finish_request(self, request_serial: int) -> None:
        if request_serial != self._active_request_serial:
            return

        self._active_request_serial = None
        self._request_in_progress = False

        if self._request_refresh_pending:
            self._request_refresh_pending = False
            self.text.after_idle(self.trigger)

    def _handle_response(
        self, request_serial: int, response: LspResponse[Union[List[lsp_types.DocumentHighlight], None]]
    ) -> None:
        if request_serial != self._active_request_serial:
            return

        try:
            error = response.get_error()
            if error:
                messagebox.showerror(tr("Error"), str(error), master=get_workbench())
                return

            # TODO: check if the situation is still the same
            result = response.get_result_or_raise()

            if not result:
                return

            if len(result) > 1:
                for ref in result:
                    # TODO: UTF-16
                    range = ref.range
                    start_index = f"{range.start.line + 1}.{range.start.character}"
                    end_index = f"{range.end.line + 1}.{range.end.character}"
                    self.text.tag_add("matched_name", start_index, end_index)
        except Exception as e:
            logger.exception("Problem when updating name highlighting", exc_info=e)
        finally:
            self._finish_request(request_serial)


def update_highlighting(event):
    if not get_workbench().ready:
        # don't slow down loading process
        return

    if not get_runner() or not get_runner().get_backend_proxy():
        # too early
        return

    assert isinstance(event.widget, tk.Text)
    text = event.widget
    if not hasattr(text, "name_highlighter"):
        text.name_highlighter = OccurrencesHighlighter(text)

    if getattr(event, "sequence", None) == "<<TextChange>>":
        text.name_highlighter._clear()
        return

    text.name_highlighter.trigger()


def load_plugin() -> None:
    wb = get_workbench()
    wb.set_default("view.name_highlighting", True)
    wb.bind_class("EditorCodeViewText", "<<CursorMove>>", update_highlighting, True)
    wb.bind_class("EditorCodeViewText", "<<TextChange>>", update_highlighting, True)
    wb.bind("<<UpdateAppearance>>", update_highlighting, True)
