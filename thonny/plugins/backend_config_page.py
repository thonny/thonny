import os.path
import tkinter as tk
from tkinter import ttk
from typing import Union

from thonny import get_runner, get_workbench, ui_utils
from thonny.backend import delete_stored_ssh_password, get_ssh_password_file_path
from thonny.config_ui import ConfigurationPage
from thonny.languages import tr
from thonny.misc_utils import (
    PUBLIC_KEY_NO_PASS_METHOD,
    PUBLIC_KEY_WITH_PASS_METHOD,
    PASSWORD_METHOD,
)
from thonny.ui_utils import create_string_var, ems_to_pixels, CommonDialogEx


class BackendDetailsConfigPage(ConfigurationPage):
    def should_restart(self):
        raise NotImplementedError()

    def _on_change(self):
        pass

    def _add_text_field(
        self, label_text, variable_name, row, show=None, pady: Union[int, tuple] = 0, width=None
    ):

        if isinstance(pady, int):
            pady = (pady, pady)

        entry_label = ttk.Label(self, text=label_text)
        entry_label.grid(row=row, column=0, sticky="w", pady=pady)

        variable = create_string_var(get_workbench().get_option(variable_name), self._on_change)
        entry = ttk.Entry(self, textvariable=variable, show=show, width=width)
        entry.grid(row=row, column=1, sticky="we", pady=pady, padx=ems_to_pixels(1))
        return variable

    def _add_combobox_field(
        self, label_text, variable_name, row, options, pady: Union[int, tuple] = 0, width=None
    ):
        if isinstance(pady, int):
            pady = (pady, pady)

        label = ttk.Label(self, text=label_text)
        label.grid(row=row, column=0, sticky="w", pady=pady)

        variable = create_string_var(get_workbench().get_option(variable_name), self._on_change)
        return self.add_combobox(
            variable, options, row=row, column=1, pady=pady, padx=ems_to_pixels(1), width=width
        )


class OnlyTextConfigurationPage(BackendDetailsConfigPage):
    def __init__(self, master, text):
        super().__init__(master)
        label = ttk.Label(self, text=text)
        label.grid()

    def should_restart(self):
        return False


class BackendConfigurationPage(ConfigurationPage):
    def __init__(self, master):
        ConfigurationPage.__init__(self, master)

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
            self, text=tr("Which interpreter or device should Thonny use for running your code?")
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

        self.labelframe = ttk.LabelFrame(self, text=" " + tr("Details") + " ")
        self.labelframe.grid(row=2, column=0, sticky="nsew")
        self.labelframe.columnconfigure(0, weight=1)
        self.labelframe.rowconfigure(0, weight=1)

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

            page.grid(sticky="nsew", padx=10, pady=5)
            self._current_page = page

    def _get_conf_page(self, backend_desc):
        if backend_desc not in self._conf_pages:
            cp_constructor = self._backend_specs_by_desc[backend_desc].config_page_constructor
            if isinstance(cp_constructor, str):
                self._conf_pages[backend_desc] = OnlyTextConfigurationPage(
                    self.labelframe, cp_constructor
                )
            else:
                assert issubclass(cp_constructor, ConfigurationPage)
                self._conf_pages[backend_desc] = cp_constructor(self.labelframe)

        return self._conf_pages[backend_desc]

    def apply(self):
        if self._current_page is None:
            return None

        result = self._current_page.apply()

        if result is False:
            return False

        backend_desc = self._combo_variable.get()
        backend_name = self._backend_specs_by_desc[backend_desc].name
        get_workbench().set_option("run.backend_name", backend_name)

        if getattr(self._combo_variable, "modified") or self._current_page.should_restart():
            self.dialog.backend_restart_required = True

        return None


class BaseSshProxyConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master, conf_group):
        super().__init__(master)
        self._changed = False
        self._conf_group = conf_group

        inner_pad = ems_to_pixels(0.6)

        self._host_var = self._add_text_field(
            "Host", self._conf_group + ".host", 1, pady=(0, inner_pad), width=20
        )
        self._user_var = self._add_text_field(
            "Username", self._conf_group + ".user", 3, pady=(0, inner_pad), width=20
        )

        from thonny.misc_utils import (
            PASSWORD_METHOD,
            PUBLIC_KEY_NO_PASS_METHOD,
            PUBLIC_KEY_WITH_PASS_METHOD,
        )

        self._method_var = self._add_combobox_field(
            "Authentication method",
            self._conf_group + ".auth_method",
            5,
            [PASSWORD_METHOD, PUBLIC_KEY_NO_PASS_METHOD, PUBLIC_KEY_WITH_PASS_METHOD],
            pady=(0, inner_pad),
            width=30,
        )
        self._interpreter_var = self._add_text_field(
            "Interpreter",
            self._conf_group + ".executable",
            30,
            pady=(2 * inner_pad, inner_pad),
            width=30,
        )

    def _on_change(self):
        self._changed = True

    def apply(self):
        if self._changed:
            get_workbench().set_option(self._conf_group + ".host", self._host_var.get())
            get_workbench().set_option(self._conf_group + ".user", self._user_var.get())
            get_workbench().set_option(self._conf_group + ".auth_method", self._method_var.get())
            get_workbench().set_option(
                self._conf_group + ".executable", self._interpreter_var.get()
            )

            delete_stored_ssh_password()

            # reset cwd setting to default
            get_workbench().set_option(self._conf_group + ".cwd", "")

    def should_restart(self):
        return self._changed


class PasswordDialog(CommonDialogEx):
    def __init__(self, master, host, user, method):
        super(PasswordDialog, self).__init__(master)

        self.password = ""
        self.save_password = False

        margin = self.get_padding()
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
        "select_interpreter", "run", tr("Select interpreter") + "...", select_device, group=1
    )
