import os.path
import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from thonny import get_workbench, ui_utils
from thonny.backend import delete_stored_ssh_password, get_ssh_password_file_path
from thonny.config_ui import (
    ConfigurationPage,
    add_option_checkbox,
    add_option_combobox,
    add_option_entry,
    add_vertical_separator,
)
from thonny.languages import tr
from thonny.misc_utils import (
    PASSWORD_METHOD,
    PUBLIC_KEY_NO_PASS_METHOD,
    PUBLIC_KEY_WITH_PASS_METHOD,
)
from thonny.running import BackendProxy
from thonny.ui_utils import CommonDialogEx, create_string_var, ems_to_pixels


class BackendDetailsConfigPage(ConfigurationPage):
    backend_name: Optional[str] = None  # Will be overwritten on Workbench.add_backend
    proxy_class: Optional[type[BackendProxy]] = None  # ditto

    def should_restart(self, changed_options: List[str]):
        raise NotImplementedError()


class TabbedBackendDetailsConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master):
        super().__init__(master)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew")

    def create_and_add_empty_page(self, caption: str, weighty_column=1) -> ttk.Frame:
        page = ttk.Frame(self.notebook, padding=self.get_tab_content_padding())
        page.columnconfigure(weighty_column, weight=1)
        self.notebook.add(page, text=caption)
        return page

    def create_and_add_stubs_page(self, proxy_class: type[BackendProxy]) -> ttk.Frame:
        from thonny.plugins.pip_gui import StubsPipFrame

        page = StubsPipFrame(self.notebook, proxy_class, padding=self.get_tab_content_padding())
        self.notebook.add(page, text=tr("Type stubs"))
        return page

    def get_tab_content_padding(self) -> List[int]:
        return [
            ems_to_pixels(1),
            ems_to_pixels(0.5),
            ems_to_pixels(1),
            ems_to_pixels(0.5),
        ]


class OnlyTextConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master, text):
        super().__init__(master)
        label = ttk.Label(self, text=text)
        label.grid()

    def should_restart(self, changed_options: List[str]):
        return False


class BackendConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        super().__init__(master)

        self._backend_specs_by_desc = {
            spec.description: spec for spec in get_workbench().get_backends().values()
        }
        self._conf_pages = {}
        self._current_page = None

        current_backend_name = get_workbench().get_option("run.backend_name")
        try:
            current_backend_desc = get_workbench().get_backends()[current_backend_name].description
        except KeyError:
            current_backend_desc = ""

        self._combo_variable = create_string_var(current_backend_desc)

        label = ttk.Label(
            self, text=tr("Which kind of interpreter should Thonny use for running your code?")
        )
        label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        sorted_backend_specs = sorted(
            self._backend_specs_by_desc.values(), key=lambda x: x.sort_key
        )

        self._combo = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._combo_variable,
            values=[spec.description for spec in sorted_backend_specs],
            height=25,
        )

        self._combo.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 10))
        self._combo.state(["!disabled", "readonly"])

        self.content_frame = ttk.Frame(self)
        self.content_frame.grid(row=2, column=0, sticky="nsew")
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._combo_variable.trace("w", self._backend_changed)
        self._backend_changed()

    def _backend_changed(self, *args):
        backend_desc = self._combo_variable.get()

        if backend_desc == "":
            if self._current_page is not None:
                self._current_page.grid_forget()
            return

        page = self._get_conf_page(backend_desc)

        if page != self._current_page:
            if self._current_page is not None:
                self._current_page.grid_forget()

            page.grid(sticky="nsew", row=0, column=0, padx=0, pady=0)
            self._current_page = page

    def _get_conf_page(self, backend_desc):
        if backend_desc not in self._conf_pages:
            cp_constructor = self._backend_specs_by_desc[backend_desc].config_page_constructor
            if isinstance(cp_constructor, str):
                self._conf_pages[backend_desc] = OnlyTextConfigurationPage(
                    self.content_frame, cp_constructor
                )
            else:
                self._conf_pages[backend_desc] = cp_constructor(self.content_frame)

        return self._conf_pages[backend_desc]

    def apply(self, changed_options: List[str]):
        if self._current_page is None:
            return None

        result = self._current_page.apply(changed_options)

        if result is False:
            return False

        backend_desc = self._combo_variable.get()
        backend_name = self._backend_specs_by_desc[backend_desc].name
        get_workbench().set_option("run.backend_name", backend_name)

        # should_restart did not accept changed_options parameter before 5.0
        from inspect import signature

        if len(signature(self._current_page.should_restart).parameters) > 0:
            should_restart = self._current_page.should_restart(changed_options)
        else:
            should_restart = self._current_page.should_restart()

        if getattr(self._combo_variable, "modified") or should_restart:
            self.dialog.backend_restart_required = True

        return None


class BaseSshProxyConfigPage(TabbedBackendDetailsConfigurationPage):
    def __init__(self, master):
        super().__init__(master)
        self.connection_page = self.create_and_add_empty_page(tr("Connection"))
        self.options_page = self.create_and_add_empty_page(tr("Options"))
        self._init_connection_page()
        self._init_options_page()

    def _init_connection_page(self):

        add_option_entry(self.connection_page, self.backend_name + ".host", tr("Host"), width=20)
        add_option_entry(
            self.connection_page, self.backend_name + ".user", tr("Username"), width=20
        )

        from thonny.misc_utils import (
            PASSWORD_METHOD,
            PUBLIC_KEY_NO_PASS_METHOD,
            PUBLIC_KEY_WITH_PASS_METHOD,
        )

        add_option_combobox(
            self.connection_page,
            self.backend_name + ".auth_method",
            tr("Authentication method"),
            choices=[PASSWORD_METHOD, PUBLIC_KEY_NO_PASS_METHOD, PUBLIC_KEY_WITH_PASS_METHOD],
            width=30,
        )
        interpreter_entry = add_option_entry(
            self.connection_page,
            self.backend_name + ".executable",
            "Interpreter",
            width=30,
        )

        if not self.has_editable_interpreter():
            interpreter_entry.configure(state="disabled")

    def _init_options_page(self):
        add_option_checkbox(
            self.options_page,
            f"{self.backend_name}.make_uploaded_shebang_scripts_executable",
            tr("Make uploaded shebang scripts executable"),
        )

    def has_editable_interpreter(self) -> bool:
        return True

    def apply(self, changed_options: List[str]):
        if self.should_restart(changed_options):
            delete_stored_ssh_password()
            # reset cwd setting to default
            get_workbench().set_option(self.backend_name + ".cwd", "")

    def should_restart(self, changed_options: List[str]):
        for option in [
            self.backend_name + ".host",
            self.backend_name + ".user",
            self.backend_name + ".auth_method",
            self.backend_name + ".executable",
        ]:
            if option in changed_options:
                return True
        return False


class PasswordDialog(CommonDialogEx):
    def __init__(self, master, host, user, method):
        super(PasswordDialog, self).__init__(master)

        self.password = ""
        self.save_password = False

        margin = self.get_large_padding()
        spacing = margin // 2

        self.title(tr("Authentication"))
        if method == PUBLIC_KEY_WITH_PASS_METHOD:
            prompt = tr("Enter the passphrase of your private key for\n{}")
        else:
            assert method == PASSWORD_METHOD
            prompt = tr("Enter your password for\n{}")

        prompt = prompt.format(user + "@" + host)

        self.prompt_label = ttk.Label(self.main_frame, text=prompt)
        self.prompt_label.grid(row=1, column=1, columnspan=2, padx=margin, pady=(margin, spacing))

        self.entry_widget = ttk.Entry(self.main_frame, width=15, show="•")
        self.bind("<Return>", self.on_ok, True)
        self.bind("<Escape>", self.on_cancel, True)
        self.bind("<KP_Enter>", self.on_ok, True)
        self.entry_widget.grid(
            row=3, column=1, columnspan=2, sticky="we", padx=margin, pady=(0, spacing)
        )

        self.save_variable = tk.BooleanVar(value=False)
        self.save_checkbox = ttk.Checkbutton(
            self.main_frame,
            text=tr("Save password"),
            variable=self.save_variable,
            offvalue=False,
            onvalue=True,
        )
        if method == PASSWORD_METHOD:
            self.save_checkbox.grid(
                row=5, padx=margin, pady=(0, spacing), column=1, columnspan=2, sticky="w"
            )

        self.ok_button = ttk.Button(
            self.main_frame, text=tr("OK"), command=self.on_ok, default="active"
        )
        self.ok_button.grid(
            row=10, column=1, padx=(margin, spacing), pady=(margin, margin), sticky="e"
        )
        self.cancel_button = ttk.Button(self.main_frame, text=tr("Cancel"), command=self.on_cancel)
        self.cancel_button.grid(
            row=10, column=2, padx=(0, margin), pady=(margin, margin), sticky="e"
        )

        self.main_frame.columnconfigure(1, weight=1)

        self.entry_widget.focus_set()

    def on_ok(self, event=None):
        self.password = self.entry_widget.get()
        self.save_password = self.save_variable.get()
        self.destroy()

    def on_cancel(self, event=None):
        self.password = None
        self.save_variable = False
        self.destroy()


def get_ssh_password(conf_group):
    host = get_workbench().get_option(conf_group + ".host")
    user = get_workbench().get_option(conf_group + ".user")
    method = get_workbench().get_option(conf_group + ".auth_method")
    if method == PUBLIC_KEY_NO_PASS_METHOD:
        return None
    elif os.path.exists(get_ssh_password_file_path()):
        with open(get_ssh_password_file_path()) as fp:
            return fp.read().strip()
    else:
        dlg = PasswordDialog(get_workbench(), host, user, method)
        ui_utils.show_dialog(dlg)
        if dlg.password and dlg.save_password:
            with open(get_ssh_password_file_path(), "w") as fp:
                fp.write(dlg.password)

        if not dlg.save_password or not dlg.password:
            delete_stored_ssh_password()

        return dlg.password


def load_plugin() -> None:
    def select_device():
        get_workbench().show_options("interpreter")

    get_workbench().add_configuration_page(
        "interpreter", tr("Interpreter"), BackendConfigurationPage, 20
    )
    get_workbench().add_command(
        "select_interpreter", "run", tr("Configure interpreter..."), select_device, group=1
    )
