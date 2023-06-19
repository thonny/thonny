import urllib.parse
from logging import getLogger
from tkinter import messagebox
from typing import Any, Dict, List, Optional

from thonny.languages import tr
from thonny.misc_utils import levenshtein_distance
from thonny.plugins.micropython import LocalMicroPythonProxy, MicroPythonProxy
from thonny.plugins.pip_gui import BackendPipDialog, get_not_supported_translation

MICROPYTHON_ORG_JSON = "https://micropython.org/pi/v2/index.json"

logger = getLogger(__name__)


class MicroPythonPipDialog(BackendPipDialog):
    def __init__(self, master):
        self._mp_org_index_data = None
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
        if package_data.get("mp_org", False):
            return True

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

    def get_search_button_text(self):
        return tr("Search micropython-lib and PyPI")

    def _download_package_info(self, name: str, version_str: Optional[str]) -> Dict:
        # Try mp.org first
        index_data = self._get_mp_org_index_data()

        for package in index_data["packages"]:
            if self._normalize_name(package["name"]) == self._normalize_name(name):
                info = {
                    "name": package["name"],
                    "version": package["version"],
                }
                if package.get("author"):
                    info["author"] = package["author"]
                if package.get("license"):
                    info["license"] = package["license"]
                if package.get("description"):
                    info["summary"] = package["description"]
                # TODO: deps?

                releases = {ver: [] for ver in package["versions"]["py"]}

                return {"info": info, "releases": releases, "mp_org": True}

        return super()._download_package_info(name, version_str)

    def _get_mp_org_index_data(self) -> Dict[str, Any]:
        if not self._mp_org_index_data:
            import json
            from urllib.request import urlopen

            with urlopen(MICROPYTHON_ORG_JSON, timeout=10) as fp:
                self._mp_org_index_data = json.load(fp)

        return self._mp_org_index_data

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

    def _fetch_search_results(self, query: str) -> Dict[str, List[Dict[str, str]]]:
        """Will be executed in background thread"""

        mp_org_result = self._perform_micropython_org_search(query)
        pypi_result = self._perform_pypi_search(query, source="PyPI")

        combined_result = []
        mp_org_names = set()

        for item in mp_org_result:
            combined_result.append(item)
            mp_org_names.add(item["name"])

        for item in pypi_result:
            # TODO: normalize?
            if item["name"] not in mp_org_names:
                # add slight penalty for non-perfect PyPI matches, as most users look for mp.org results
                if item["distance"] != 0:
                    item["distance"] += 1
                combined_result.append(item)

        sorted_result = sorted(combined_result, key=lambda x: x["distance"])
        filtered_result = filter(lambda x: x["distance"] < 5, sorted_result[:20])

        # Combining, because this makes the shadowing performed by Pipkin more clear
        return {"combined": list(filtered_result)}

    def _perform_micropython_org_search(self, query: str) -> List[Dict[str, str]]:
        logger.info("Searching %r for %r", MICROPYTHON_ORG_JSON, query)
        data = self._get_mp_org_index_data()

        result = []
        for package in data["packages"]:
            result.append(
                {
                    "name": package["name"],
                    "description": package["description"] or None,
                    "source": "micropython-lib",
                    "distance": levenshtein_distance(query, package["name"]),
                }
            )

        logger.info("Got %r items", len(result))
        return result

    def _get_interpreter_description(self):
        return self._backend_proxy.get_full_label()
