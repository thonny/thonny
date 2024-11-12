import os.path
import threading
import tkinter.font as tk_font
from logging import getLogger
from typing import List, Optional

from thonny import get_workbench
from thonny.codeview import get_syntax_options_for_tag
from thonny.common import (
    REMOTE_URI_PREFIX,
    ToplevelResponse,
    editor_path_matches_uri,
    file_uri_to_path,
)
from thonny.editors import make_remote_path
from thonny.languages import tr
from thonny.lsp_proxy import LanguageServerProxy
from thonny.lsp_types import Diagnostic, PublishDiagnosticsParams
from thonny.program_analysis import ProgramAnalyzer, ProgramAnalyzerResponseItem
from thonny.tktextext import TextFrame
from thonny.ui_utils import ems_to_pixels, get_hyperlink_cursor

logger = getLogger(__name__)

ITEM_PREFIX = " • "


class ProblemsView(TextFrame):
    def __init__(self, master):
        super().__init__(master, horizontal_scrollbar=False, wrap="word", font="TkDefaultFont")
        self._analyzers: List[ProgramAnalyzer] = []

        self._ls_proxy: Optional[LanguageServerProxy] = None

        get_workbench().bind("LanguageServerInitialized", self._language_server_initialized, True)
        get_workbench().bind("LanguageServerInvalidated", self._language_server_invalidated, True)

        get_workbench().bind("ToplevelResponse", self.handle_toplevel_response, True)
        base_font = tk_font.nametofont("TkDefaultFont")
        link_font = tk_font.nametofont("LinkFont")
        self.text.tag_configure("path", spacing3=ems_to_pixels(0.3))

        bullet_prefix_width = base_font.measure(ITEM_PREFIX)
        self.text.tag_configure("diagnostics_first_line", lmargin2=bullet_prefix_width)
        self.text.tag_configure(
            "diagnostics_next_line", lmargin1=bullet_prefix_width, lmargin2=bullet_prefix_width
        )

        hyperlink_opts = get_syntax_options_for_tag("hyperlink")
        hyperlink_opts["underline"] = False  # underline coming from the font looks better
        hyperlink_opts["font"] = link_font
        self.text.tag_configure("link", **hyperlink_opts)

        self.text.tag_bind("link", "<Enter>", self._hyperlink_enter)
        self.text.tag_bind("link", "<Leave>", self._hyperlink_leave)
        self.text.tag_bind("link", "<ButtonRelease-1>", self._hyperlink_click)

    def handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        if msg.get("filename") and os.path.exists(msg["filename"]):
            self.start_analyses(msg["filename"])

    def start_analyses(self, main_file_path: str) -> None:
        for analyzer in self._analyzers:
            analyzer.cancel()

        self._analyzers = [
            analyzer
            for name, analyzer in get_workbench().program_analyzers.items()
            if get_workbench().get_option(f"analysis.{name}.enabled")
        ]

        for analyzer in self._analyzers:
            threading.Thread(
                target=analyzer.analyze,
                daemon=True,
                args=(main_file_path,),
            ).start()

    def _hyperlink_enter(self, event):
        self.text.config(cursor=get_hyperlink_cursor())

    def _hyperlink_leave(self, event):
        self.text.config(cursor="")

    def _hyperlink_click(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        if not index:
            logger.warning("Could not get click index")
            return

        for tag in self.text.tag_names(index):
            if "thonny-editor://" in tag:
                get_workbench().open_url(tag)

    def _remove_uri_block(self, uri: str) -> None:
        indices = self.text.tag_nextrange(uri, "1.0")
        if not indices:
            return

        start = indices[0]
        _, end = self.text.tag_prevrange(uri, "end")

        self.text.direct_delete(start, end)

    def _add_uri_block(self, uri: str, diagnostics: List[Diagnostic]) -> None:
        this_target_path = file_uri_to_path(uri)
        if uri.startswith(REMOTE_URI_PREFIX):
            this_path = make_remote_path(this_target_path)
        else:
            this_path = this_target_path

        next_path_start = "1.0"
        while True:
            indices = self.text.tag_nextrange("path", next_path_start)
            if not indices:
                next_path_start = "end"
                break

            next_path_start, next_path_end = indices
            next_path = self.text.get(next_path_start, next_path_end)

            if this_path < next_path:
                break
            else:
                next_path_start = next_path_end

        self._insert_uri_block(uri, this_path, diagnostics, next_path_start)

    def _insert_uri_block(
        self, uri: str, path: str, diagnostics: List[Diagnostic], start_index
    ) -> None:
        mark = "insertion_point"

        def append(chars, extra_tags=()):
            self.text.direct_insert(mark, chars, (uri,) + extra_tags)

        def append_file_link(
            text: str, target_path: str, target_line: Optional[int], extra_tags=()
        ):
            url = f"thonny-editor://{target_path}"
            if target_line is not None:
                url += f"#{target_line}"

            append(text, ("link", url) + extra_tags)

        self.text.mark_set(mark, start_index)
        append_file_link(path, path, None, ("path",))
        append("\n")

        for diagnostic in diagnostics:
            message = diagnostic.message.replace("\n\xa0\xa0", ". ")
            message_lines = message.splitlines()
            first_line_tags = ("diagnostics_first_line",)
            append(ITEM_PREFIX, first_line_tags)
            line = diagnostic.range.start.line + 1  # LSP uses 0-based numbering
            append_file_link(tr("Line") + f" {line}", path, line, first_line_tags)
            append(" : ", first_line_tags)
            append(message_lines[0] + "\n", first_line_tags)
            for line in message_lines[1:]:
                append(line + "\n", ("diagnostics_next_line",))

        append("\n")

    def _handle_diagnostics_notification(self, params: PublishDiagnosticsParams) -> None:
        self._remove_uri_block(params.uri)
        if params.diagnostics:
            self._add_uri_block(params.uri, params.diagnostics)

    def _language_server_initialized(self, ls_proxy: LanguageServerProxy) -> None:
        self._try_bind_to_language_server()

    def _try_bind_to_language_server(self):
        ls_proxy = get_workbench().get_language_server_proxy()

        if self._ls_proxy != ls_proxy:
            self._ls_proxy = ls_proxy
            self._ls_proxy.bind_publish_diagnostics(self._handle_diagnostics_notification)

    def _language_server_invalidated(self, ls_proxy: LanguageServerProxy) -> None:
        self._ls_proxy = None
        ls_proxy.unbind_notification_handler(self._handle_diagnostics_notification)


def load_plugin():
    get_workbench().add_view(
        ProblemsView, tr("Problems"), default_location="s", visible_by_default=False
    )
