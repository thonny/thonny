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
            current_backend_desc = (
                get_workbench().get_backends()[current_backend_name].description
            )
        except KeyError:
            current_backend_desc = ""

        self._combo_variable = create_string_var(current_backend_desc)

        label = ttk.Label(self, text="What should Thonny use for running your code?")
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

        self.labelframe = ttk.LabelFrame(self, text=" Details ")
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
            cp_constructor = self._backend_specs_by_desc[
                backend_desc
            ].config_page_constructor
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

        if (
            getattr(self._combo_variable, "modified")
            or self._current_page.should_restart()
        ):
            get_runner().restart_backend(False)

        return None


def load_plugin() -> None:
    get_workbench().add_configuration_page("Interpreter", BackendConfigurationPage)
