import tkinter as tk
from tkinter import ttk

from thonny import get_runner, get_workbench, misc_utils, ui_utils
from thonny.codeview import CodeView


class ShellMacroDialog(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)

        self.title("Configure shell macro")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.transient(master)
        self.grab_set()  # to make it active
        # self.grab_release() # to allow eg. copy something from the editor

        self._create_widgets()

        self.bind("<Escape>", self._on_close, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.main_command_text.focus_set()

    def _create_widgets(self):

        bg = "#ffff99"
        banner_frame = tk.Frame(self, background=bg)
        banner_frame.grid(row=0, column=0, sticky="nsew")
        banner_frame.rowconfigure(0, weight=1)
        banner_frame.columnconfigure(0, weight=1)
        banner_text = tk.Label(
            banner_frame,
            text="These\nare\ninstructions asdfa afs fa sfasdf",
            background=bg,
            justify="left",
        )
        banner_text.grid(column=0, row=0, pady=10, padx=10, sticky="nsew")

        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=15, pady=15)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.main_command_text = CodeView(main_frame, height=5)
        self.main_command_text.grid(column=0, row=1, sticky="nsew")
        # main_command_text["relief"] = "groove"

        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, sticky="nsew")

        run_button = ttk.Button(
            button_frame, text="Save and execute", command=self._save_exec
        )
        run_button.grid(row=0, column=1, sticky="nsew")
        ok_button = ttk.Button(button_frame, text="Save", command=self._save)
        ok_button.grid(row=0, column=2, sticky="nsew")
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        cancel_button.grid(row=0, column=3, sticky="nsew")
        button_frame.columnconfigure(0, weight=1)

    def _on_close(self, event=None):
        self.destroy()

    def _save_exec(self, event=None):
        self._save(event)
        execute_macro()

    def _save(self, event=None):
        source = self.main_command_text.text.get("1.0", "end")
        get_workbench().set_option("run.shell_macro_main", repr(source))
        self.destroy()

    def _cancel(self, event=None):
        self.destroy()


def show_dialog():
    dlg = ShellMacroDialog(get_workbench())
    ui_utils.show_dialog(dlg)


def execute_macro():
    if get_runner().is_waiting_toplevel_command():
        source = get_workbench().get_option("run.shell_macro_main")
        if source is not None:
            shell = get_workbench().show_view("ShellView")
            shell.submit_python_code(source.strip() + "\n")


def _load_plugin():
    get_workbench().set_default("run.shell_macro_main", None)
    get_workbench().add_command(
        "configure_shell_macro", "run", "Configure shell macro...", show_dialog
    )
    get_workbench().add_command(
        "execute_shell_macro",
        "run",
        "Execute shell macro",
        execute_macro,
        default_sequence="<F9>",
    )
