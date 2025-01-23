import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional, Union

from thonny import get_workbench, logger, lsp_types
from thonny.editors import Editor
from thonny.languages import tr
from thonny.lsp_types import DocumentSymbolParams, LspResponse, SymbolKind, TextDocumentIdentifier
from thonny.ui_utils import (
    SafeScrollbar,
    TreeviewLayout,
    export_treeview_layout,
    restore_treeview_layout,
)


class OutlineView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self._init_widgets()
        self._editor: Optional[Editor] = None

        self._last_layouts_by_editor_id: Dict[str, TreeviewLayout] = {}

        self._tab_changed_binding = (
            get_workbench()
            .get_editor_notebook()
            .bind("<<NotebookTabChanged>>", self._request_document_symbols, True)
        )
        get_workbench().bind("AfterSendingDocumentUpdates", self._request_document_symbols, True)

        self._request_document_symbols()

    def destroy(self):
        if get_workbench().get_editor_notebook().winfo_exists():
            get_workbench().get_editor_notebook().unbind(
                "<<NotebookTabChanged>>", self._tab_changed_binding
            )
        self.vert_scrollbar["command"] = None
        ttk.Frame.destroy(self)

    def _init_widgets(self):
        # init and place scrollbar
        self.vert_scrollbar = SafeScrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

        # init and place tree
        self.tree = ttk.Treeview(self, yscrollcommand=self.vert_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.tree.yview

        # set single-cell frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # init tree events
        self.tree.bind("<<TreeviewSelect>>", self._on_select, True)
        self.tree.bind("<Map>", self._request_document_symbols, True)

        # configure the only tree column
        self.tree.column("#0", anchor=tk.W, stretch=True)
        # self.tree.heading('#0', text='Item (type @ line)', anchor=tk.W)
        self.tree["show"] = ("tree",)

        self._class_img = get_workbench().get_image("outline-class")
        self._method_img = get_workbench().get_image("outline-method")

    def _request_document_symbols(self, event=None):
        current_editor = get_workbench().get_editor_notebook().get_current_editor()
        if current_editor is None:
            return

        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is None:
            return

        # ignore the pending results for last request
        ls_proxy.unbind_request_handler(self._handle_document_symbols_response)

        ls_proxy.request_document_symbol(
            DocumentSymbolParams(textDocument=TextDocumentIdentifier(uri=current_editor.get_uri())),
            self._handle_document_symbols_response,
        )

    def _handle_document_symbols_response(
        self,
        response: LspResponse[
            Union[List[lsp_types.SymbolInformation], List[lsp_types.DocumentSymbol], None]
        ],
    ):
        if not self.winfo_ismapped():
            return

        self._save_and_clear()

        result = response._result
        # TODO: check whether the result is for this editor
        self._editor = get_workbench().get_editor_notebook().get_current_editor()
        if self._editor is None:
            return

        if result is None:
            logger.warning("Got None document/symbol response")
            return

        for item in result:
            if isinstance(item, lsp_types.SymbolInformation):
                logger.warning("Not handling SymbolInformation, %r", item)
                return
            assert isinstance(item, lsp_types.DocumentSymbol)

            self._add_document_symbol_to_tree("", item)

        prev_layout = self._last_layouts_by_editor_id.get(str(self._editor.winfo_id()), None)
        if prev_layout is not None:
            restore_treeview_layout(self.tree, prev_layout)

    # adds a single item to the tree, recursively calls itself to add any child nodes
    def _add_document_symbol_to_tree(self, parent_iid: str, symbol: lsp_types.DocumentSymbol):

        iid = f"{parent_iid}.{symbol.name}".strip(".")
        while self.tree.exists(iid):
            # shouldn't happen, but just in case ...
            iid += "_"

        item_text = " " + symbol.name

        if symbol.kind == SymbolKind.Class:
            image = self._class_img
        elif symbol.kind == SymbolKind.Method:
            image = self._method_img
        elif symbol.kind == SymbolKind.Function:
            image = self._method_img
        else:
            return

        lineno = symbol.range.start.line + 1

        # insert the symbol, set lineno as a 'hidden' value
        current = self.tree.insert(
            parent_iid, index="end", iid=iid, text=item_text, values=[lineno], image=image
        )

        for child in symbol.children:
            self._add_document_symbol_to_tree(current, child)

    # clears the tree by deleting all items
    def _save_and_clear(self):
        if self._editor is not None and self._editor.winfo_exists():
            editor_id = str(self._editor.winfo_id())
            self._last_layouts_by_editor_id[editor_id] = export_treeview_layout(self.tree)

        for child_id in self.tree.get_children():
            self.tree.delete(child_id)

    def _on_select(self, event):
        if self._editor:
            code_view = self._editor.get_code_view()
            focus = self.tree.focus()
            if not focus:
                return

            values = self.tree.item(focus)["values"]
            if not values:
                return

            lineno = values[0]
            index = code_view.text.index(str(lineno) + ".0")
            code_view.text.see(index)  # make sure that the double-clicked item is visible
            code_view.text.select_lines(lineno, lineno)

            get_workbench().event_generate(
                "OutlineDoubleClick", item_text=self.tree.item(self.tree.focus(), option="text")
            )


def load_plugin() -> None:
    get_workbench().add_view(OutlineView, tr("Outline"), "ne")
