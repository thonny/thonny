import tkinter.font as tk_font
from dataclasses import dataclass
from logging import getLogger
from typing import Dict, List, Optional

from thonny import get_workbench
from thonny.codeview import get_syntax_options_for_tag
from thonny.languages import tr
from thonny.lsp_proxy import LanguageServerProxy
from thonny.lsp_types import Diagnostic, PublishDiagnosticsParams
from thonny.misc_utils import is_editor_supported_uri, is_local_uri, uri_to_long_title
from thonny.tktextext import TextFrame
from thonny.ui_utils import ems_to_pixels, get_hyperlink_cursor

logger = getLogger(__name__)

ITEM_PREFIX = " • "


@dataclass
class DiagnosticWithProxy:
    diagnostic: Diagnostic
    ls_proxy: LanguageServerProxy


class ProblemsView(TextFrame):
    def __init__(self, master):
        super().__init__(master, horizontal_scrollbar=False, wrap="word", font="TkDefaultFont")
        self._current_diagnostics_per_uri: Dict[str, List[DiagnosticWithProxy]] = {}

        for ls_proxy in get_workbench().get_initialized_ls_proxies():
            self._connect_to_language_server(ls_proxy)
        get_workbench().bind("LanguageServerInitialized", self._connect_to_language_server, True)
        get_workbench().bind(
            "LanguageServerInvalidated", self._disconnect_from_language_server, True
        )

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
            if is_editor_supported_uri(tag):
                get_workbench().open_url(tag)

    def _remove_uri_block(self, uri: str) -> None:
        indices = self.text.tag_nextrange(uri, "1.0")
        if not indices:
            return

        start = indices[0]
        _, end = self.text.tag_prevrange(uri, "end")

        self.text.direct_delete(start, end)

    def _add_uri_block(self, uri: str, diagnostics: List[DiagnosticWithProxy]) -> None:

        this_title = uri_to_long_title(uri)

        next_title_start = "1.0"
        while True:
            indices = self.text.tag_nextrange("path", next_title_start)
            if not indices:
                next_title_start = "end"
                break

            next_title_start, next_title_end = indices
            next_title = self.text.get(next_title_start, next_title_end)

            if this_title < next_title:
                break
            else:
                next_title_start = next_title_end

        self._insert_uri_block(uri, this_title, diagnostics, next_title_start)

    def _insert_uri_block(
        self, uri: str, title: str, diagnostics: List[DiagnosticWithProxy], start_index
    ) -> None:
        mark = "insertion_point"

        def append(chars, extra_tags=()):
            self.text.direct_insert(mark, chars, (uri,) + extra_tags)

        def append_editor_link(text: str, uri: str, target_line: Optional[int], extra_tags=()):
            url = uri
            if target_line is not None:
                url += f"#{target_line}"

            append(text, ("link", url) + extra_tags)

        self.text.mark_set(mark, start_index)
        append_editor_link(title, uri, None, ("path",))
        append("\n")

        for ds in diagnostics:
            diagnostic = ds.diagnostic
            message = diagnostic.message.replace("\n\xa0\xa0", ". ")
            message_lines = message.splitlines()
            first_line_tags = ("diagnostics_first_line",)
            append(ITEM_PREFIX, first_line_tags)
            line = diagnostic.range.start.line + 1  # LSP uses 0-based numbering
            append(f"{diagnostic.source} => ")
            append_editor_link(tr("Line") + f" {line}", uri, line, first_line_tags)
            append(" : ", first_line_tags)
            append(message_lines[0] + "\n", first_line_tags)
            for line in message_lines[1:]:
                append(line + "\n", ("diagnostics_next_line",))

        append("\n")

    def _handle_diagnostics_notification(
        self, params: PublishDiagnosticsParams, ls_proxy: LanguageServerProxy
    ) -> None:
        # NB! Even though each diagnostic has "source" attribute, proxy reference is needed in order to clear
        # right diagnostics when the list of new diagnostics is empty.

        # Remove old diagnostics from the same server and add the new ones
        current_diagnostics = self._current_diagnostics_per_uri.get(params.uri, [])
        self._current_diagnostics_per_uri[params.uri] = list(
            filter(lambda ds: ds.ls_proxy is not ls_proxy, current_diagnostics)
        ) + [DiagnosticWithProxy(diagnostic, ls_proxy) for diagnostic in params.diagnostics]

        self._remove_uri_block(params.uri)
        if params.diagnostics:
            self._add_uri_block(params.uri, self._current_diagnostics_per_uri[params.uri])

    def _connect_to_language_server(self, ls_proxy: LanguageServerProxy):
        logger.info("Connecting to ls_proxy %s", ls_proxy)

        def handle(params: PublishDiagnosticsParams) -> None:
            self._handle_diagnostics_notification(params, ls_proxy)

        ls_proxy.bind_publish_diagnostics(handle)

    def _disconnect_from_language_server(self, ls_proxy: LanguageServerProxy) -> None:
        logger.info("Disconnecting from ls_proxy %s", ls_proxy)
        ls_proxy.unbind_notification_handler(self._handle_diagnostics_notification)


def load_plugin():
    get_workbench().add_view(
        ProblemsView, tr("Problems"), default_location="s", visible_by_default=False
    )
