import os.path
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Optional, Tuple

import thonny
from thonny import get_workbench
from thonny.languages import tr
from thonny.misc_utils import version_str_to_tuple_of_ints
from thonny.plugins.backend_config_page import TabbedBackendDetailsConfigurationPage
from thonny.plugins.cpython_frontend import LocalCPythonProxy


class LocalCPythonUvProxy(LocalCPythonProxy):
    def __init__(self, clean: bool) -> None:
        super().__init__(clean)

    def compute_mgmt_executable(self):
        # TODO
        return os.path.expanduser("~/.cargo/bin/uv")

    def get_target_executable(self):
        # TODO: should give python exe?
        return self._mgmt_executable

    def get_mgmt_executable_special_switches(self) -> List[str]:
        cmd = ["run", "--project", self.get_cwd()]

        python = get_workbench().get_option(f"{self.backend_name}.python")
        if python != "auto":
            cmd += ["--python", python]
        cmd += ["python"]
        return cmd

    def get_mgmt_executable_validation_error(self) -> Optional[str]:
        if not os.path.isfile(self._mgmt_executable):
            return f"Executable {self._mgmt_executable!r} not found. Is uv installed?"

    @classmethod
    def _get_switcher_conf_for_python(cls, version: str) -> Dict[str, Any]:
        return {"run.backend_name": cls.backend_name, f"{cls.backend_name}.python": version}

    def get_current_switcher_configuration(self):
        return self._get_switcher_conf_for_python(
            get_workbench().get_option(f"{self.backend_name}.python")
        )

    @classmethod
    def get_switcher_configuration_label(cls, conf: Dict[str, Any]) -> str:
        python = conf[f"{cls.backend_name}.python"]

        return cls.backend_description + "  •  " + python

    @classmethod
    def get_switcher_entries(cls) -> List[Tuple[Dict[str, Any], str, str]]:
        def order(conf):
            python = conf[f"{cls.backend_name}.python"]
            if python == "auto":
                return (0, (0,), python)
            elif python.startswith("3."):
                return (1, tuple(map(lambda x: -x, version_str_to_tuple_of_ints(python))), python)
            else:
                return (2, (0,), python)

        confs = cls.get_last_configurations()
        for ver in thonny.SUPPORTED_VERSIONS:
            conf = cls._get_switcher_conf_for_python(ver)
            if conf not in confs:
                confs.append(conf)

        confs = sorted(confs, key=order)
        default_conf = cls._get_switcher_conf_for_python("auto")
        if default_conf not in confs:
            confs.insert(0, default_conf)

        return [
            (conf, cls.get_switcher_configuration_label(conf), "localhost")
            for conf in confs
            if cls.is_valid_configuration(conf)
        ]

    @classmethod
    def is_valid_configuration(cls, conf: Dict[str, Any]) -> bool:
        if "LocalCPythonUv.executable" in conf:
            import traceback

            traceback.print_stack()
        return cls.is_valid_python(conf[f"{cls.backend_name}.python"])

    @classmethod
    def is_valid_python(cls, python):
        # TODO: make it more complete
        if python.startswith("/"):
            return os.path.isfile(python)

        return True


class LocalCPythonUvConfigurationPage(TabbedBackendDetailsConfigurationPage):
    def should_restart(self, changed_options: List[str]) -> bool:
        # TODO
        return True

    def get_new_machine_id(self) -> str:
        return "localhost"

    def __init__(self, master):
        super().__init__(master)

        self.options_page = self.create_and_add_empty_page(tr("Options"))

        label = ttk.Label(self.options_page, text="uv")
        label.grid()
