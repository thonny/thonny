import logging
import tkinter as tk
from tkinter import ttk
from typing import Optional

from thonny import get_workbench, ui_utils
from thonny.languages import tr
from thonny.ui_utils import CommonDialog, ems_to_pixels

logger = logging.getLogger(__name__)


class ConfigurationDialog(CommonDialog):
    last_shown_tab_index = 0

    def __init__(self, master, page_records_with_order):
        super().__init__(master)
        width = ems_to_pixels(53)
        height = ems_to_pixels(43)
        self.geometry("%dx%d" % (width, height))
        self.title(tr("Thonny options"))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.backend_restart_required = False
        self.gui_restart_required = False

        main_frame = ttk.Frame(self)  # otherwise there is wrong color background with clam
        main_frame.grid(row=0, column=0, sticky=tk.NSEW)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self._notebook = ttk.Notebook(main_frame)
        self._notebook.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW, padx=10, pady=10)

        self._ok_button = ttk.Button(main_frame, text=tr("OK"), command=self._ok, default="active")
        self._cancel_button = ttk.Button(main_frame, text=tr("Cancel"), command=self._cancel)
        self._ok_button.grid(row=1, column=1, padx=(0, 11), pady=(0, 10))
        self._cancel_button.grid(row=1, column=2, padx=(0, 11), pady=(0, 10))

        self._page_records = []
        for key, title, page_class, _ in sorted(
            page_records_with_order, key=lambda r: (r[3], r[0])
        ):
            try:
                spacer = ttk.Frame(self)
                spacer.rowconfigure(0, weight=1)
                spacer.columnconfigure(0, weight=1)
                page = page_class(spacer)
                page.key = key
                page.dialog = self
                self._page_records.append((key, title, page))
                page.grid(sticky=tk.NSEW, pady=(15, 10), padx=15)
                self._notebook.add(spacer, text=title)
            except Exception as e:
                logger.exception("Could not create configuration page %s", key, exc_info=e)

        self.bind("<Return>", self._ok, True)
        self.bind("<Escape>", self._cancel, True)

        self._notebook.select(self._notebook.tabs()[ConfigurationDialog.last_shown_tab_index])

    def select_page(self, key):
        for i, tab in enumerate(self._notebook.tabs()):
            if self._page_records[i][0] == key:
                self._notebook.select(tab)

    def _ok(self, event=None):
        for _, title, page in self._page_records:
            try:
                if page.apply() is False:
                    return
            except Exception:
                get_workbench().report_exception("Error when applying options in " + title)

        self.destroy()

    def _cancel(self, event=None):
        for _, title, page in self._page_records:
            try:
                page.cancel()
            except Exception:
                get_workbench().report_exception("Error when cancelling options in " + title)

        self.destroy()

    def destroy(self):
        ConfigurationDialog.last_shown_tab_index = self._notebook.index(self._notebook.select())
        super().destroy()


class ConfigurationPage(ttk.Frame):
    """This is an example dummy implementation of a configuration page.

    It's not required that configuration pages inherit from this class
    (can be any widget), but the class must have constructor with single parameter
    for getting the master."""

    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.dialog = None  # type: Optional[ConfigurationDialog]

    def add_checkbox(
        self, flag_name, description, row=None, column=0, padx=0, pady=0, columnspan=1, tooltip=None
    ):
        variable = get_workbench().get_variable(flag_name)
        checkbox = ttk.Checkbutton(self, text=description, variable=variable)
        checkbox.grid(
            row=row, column=column, sticky=tk.W, padx=padx, pady=pady, columnspan=columnspan
        )

        if tooltip is not None:
            ui_utils.create_tooltip(checkbox, tooltip)

    def add_combobox(
        self, variable, values, row=None, column=0, padx=0, pady=0, columnspan=1, width=None
    ):
        if isinstance(variable, str):
            variable = get_workbench().get_variable(variable)
        combobox = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=variable,
            state="readonly",
            height=15,
            width=width,
            values=values,
        )
        combobox.grid(
            row=row, column=column, sticky=tk.W, pady=pady, padx=padx, columnspan=columnspan
        )
        return variable

    def add_entry(self, option_name, row=None, column=0, pady=0, padx=0, columnspan=1, **kw):
        variable = get_workbench().get_variable(option_name)
        entry = ttk.Entry(self, textvariable=variable, **kw)
        entry.grid(row=row, column=column, sticky=tk.W, pady=pady, columnspan=columnspan, padx=padx)

    def apply(self):
        """Apply method should return False, when page contains invalid
        input and configuration dialog should not be closed."""
        pass

    def cancel(self):
        """Called when dialog gets cancelled"""
        pass
