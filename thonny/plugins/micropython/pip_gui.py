import urllib.parse
from logging import getLogger
from tkinter import messagebox
from typing import Dict, Optional

from thonny.languages import tr
from thonny.plugins.micropython import LocalMicroPythonProxy, MicroPythonProxy
from thonny.plugins.pip_gui import BackendPipDialog, get_not_supported_translation

MICROPYTHON_ORG_JSON = "https://micropython.org/pi/%s/json"

logger = getLogger(__name__)


class MicroPythonPipDialog(BackendPipDialog):
    def __init__(self, master):
        super().__init__(master)
        assert isinstance(self._backend_proxy, MicroPythonProxy)

    def _confirm_install(self, package_data: Dict) -> bool:
        if not self._looks_like_micropython_package(package_data):
            if not messagebox.askyesno(
                title=tr("Confirmation"),
                message=tr(
                    "This doesn't look like MicroPython/CircuitPython package.\n"
                    "Are you sure you want to install it?"
                ),
                parent=self,
            ):
                return False

        return super()._confirm_install(package_data)

    def _looks_like_micropython_package(self, package_data: Dict) -> bool:
        name = package_data["info"]["name"]
        for token in ["micropython", "circuitpython", "pycopy"]:
            if token in name.lower():
                return True

        classifiers = package_data["info"].get("classifiers", [])
        logger.debug("package classifiers: %s", classifiers)
        for mp_class in [
            "Programming Language :: Python :: Implementation :: MicroPython",
            "Programming Language :: Python :: Implementation :: CircuitPython",
        ]:
            if mp_class in classifiers:
                return True

        return False

    def _get_package_metadata_url(self, name: str, version_str: Optional[str]) -> str:
        return "https://micropython.org/pi/{}/json".format(urllib.parse.quote(name))

    def _get_package_metadata_fallback_url(
        self, name: str, version_str: Optional[str]
    ) -> Optional[str]:
        return super()._get_package_metadata_url(name, version_str)

    def _get_target_directory(self):
        # TODO: should this be pipkin's decision?
        target_dir = self._backend_proxy.get_pip_target_dir()
        return target_dir

    def _is_read_only(self):
        return self._get_target_directory() is None

    def does_support_update_deps_switch(self):
        return False

    def _use_user_install(self):
        return False

    def _installer_runs_locally(self):
        return True

    def _show_instructions_about_target(self):
        self._append_info_text(tr("Target") + "\n", ("caption",))

        if isinstance(self._backend_proxy, LocalMicroPythonProxy):
            dir_tags = ("url",)
        else:
            dir_tags = ()

        self._append_info_text(self._get_target_directory(), dir_tags)
        self._append_info_text("\n")

    def _show_extra_instructions(self):
        self._append_info_text("\n\n")
        self._append_info_text("Under the hood " + "\n", ("caption", "right"))
        self._append_info_text(
            "This dialog uses `pipkin`, a new command line tool for managing "
            "MicroPython and CircuitPython packages. ",
            ("right",),
        )
        self._append_info_text("See ", ("right",))
        self._append_info_text("https://pypi.org/project/pipkin/", ("url", "right"))
        self._append_info_text(" for more info. \n", ("right",))

    def _show_read_only_instructions(self):
        self._append_info_text(tr("Not available") + "\n", ("caption",))
        if not self._get_target_directory():
            reason = " (" + tr("no absolute lib directory in sys.path") + ")"
        else:
            reason = ""
        self.info_text.direct_insert(
            "end",
            get_not_supported_translation() + reason + "\n\n",
        )

    def _tweak_search_results(self, results, query):
        if results is None:
            return results
        query = query.lower()

        def get_order(item):
            name = item["name"].lower()
            if name == query:
                return 0
            elif name == "micropython-" + query:
                return 1
            elif name == "pycopy-" + query:
                return 2
            elif "micropython" in name:
                return 3
            elif "pycopy" in name:
                return 4
            elif item.get("description"):
                description = item["description"]
                if "micropython" in description.lower() or "pycopy" in description.lower():
                    return 5

            return 6

        return sorted(results, key=get_order)

    def _get_interpreter_description(self):
        return self._backend_proxy.get_full_label()
