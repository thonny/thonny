import tkinter as tk
from tkinter import ttk

from thonny.languages import tr
from thonny.ui_utils import CommonDialog

page_specs = []


class ExportDialog(CommonDialog):
    def __init__(self, master):
        super().__init__(master=master)

        self.title("Export file")
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        mainframe = ttk.Frame(self)
        mainframe.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.notebook = ttk.Notebook(mainframe)
        self.notebook.grid(row=3, column=0, columnspan=3, padx=20, pady=(20, 0), sticky="nsew")

        self.ok_button = ttk.Button(mainframe, text=tr("OK"), command=self.on_ok)
        self.ok_button.grid(row=4, column=1, sticky="e", padx=(20, 10), pady=(10, 20))

        self.cancel_button = ttk.Button(mainframe, text=tr("Cancel"), command=self.on_cancel)
        self.cancel_button.grid(row=4, column=2, sticky="e", padx=(0, 20), pady=(10, 20))

        mainframe.columnconfigure(0, weight=1)
        mainframe.rowconfigure(3, weight=1)

        for title, page_class in page_specs:
            page = page_class(self.notebook)
            self.notebook.add(page, text=title)

    def on_ok(self):
        print("OK")

    def on_cancel(self):
        print("Cancel")
        self.destroy()


class LocalFilesExportPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)


def add_export_page(title, page_class):
    page_specs.append((title, page_class))
