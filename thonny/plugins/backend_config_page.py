import tkinter as tk
from tkinter import ttk

from thonny import get_runner, get_workbench
from thonny.config_ui import ConfigurationPage
from thonny.ui_utils import create_string_var


class BackendDetailsConfigPage(ConfigurationPage):
    def should_restart(self):
        raise NotImplementedError()


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
            self, text=_("Which interpreter or device should Thonny use for running your code?")
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
        )

        self._combo.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW, pady=(0, 10))
        self._combo.state(["!disabled", "readonly"])

        self.labelframe = ttk.LabelFrame(self, text=" " + _("Details") + " ")
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
            get_runner().restart_backend(False)

        return None


class BaseSshProxyConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master, conf_group):
        super().__init__(master)
        self._changed = False
        self._conf_group = conf_group

        self._host_var = self._add_text_field("Host", self._conf_group + ".host", 1)
        self._user_var = self._add_text_field("Username", self._conf_group + ".user", 3)
        self._password_var = self._add_text_field(
            "Password", self._conf_group + ".password", 5, show="•"
        )
        self._executable_var = self._add_text_field(
            "Interpreter", self._conf_group + ".executable", 30
        )

    def _add_text_field(self, label_text, variable_name, row, show=None):
        entry_label = ttk.Label(self, text=label_text)
        entry_label.grid(row=row, column=0, sticky="w")

        variable = create_string_var(get_workbench().get_option(variable_name), self._on_change)
        entry = ttk.Entry(self, textvariable=variable, show=show)
        entry.grid(row=row + 1, column=0, sticky="we")
        return variable

    def _on_change(self):
        print("detected change")
        self._changed = True

    def apply(self):
        get_workbench().set_option(self._conf_group + ".host", self._host_var.get())
        get_workbench().set_option(self._conf_group + ".user", self._user_var.get())
        get_workbench().set_option(self._conf_group + ".password", self._password_var.get())
        get_workbench().set_option(self._conf_group + ".executable", self._executable_var.get())

    def should_restart(self):
        return self._changed


def load_plugin() -> None:
    def select_device():
        get_workbench().show_options("interpreter")

    get_workbench().add_configuration_page(
        "interpreter", _("Interpreter"), BackendConfigurationPage, 20
    )
    get_workbench().add_command(
        "select_interpreter", "run", _("Select interpreter") + "...", select_device, group=1
    )
