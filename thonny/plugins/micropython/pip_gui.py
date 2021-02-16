import os
import shutil
import subprocess
import tempfile
import threading
import tkinter as tk
from tkinter.messagebox import showerror
from tkinter import ttk
from typing import cast, Tuple

from thonny import running, get_runner, get_workbench, ui_utils
from thonny.common import InlineCommand
from thonny.languages import tr
from thonny.plugins.files import upload, prepare_upload_items
from thonny.plugins.micropython import MicroPythonProxy, LocalMicroPythonProxy
from thonny.plugins.micropython.micropip import MICROPYTHON_ORG_JSON
from thonny.plugins.pip_gui import (
    BackendPipDialog,
    _fetch_url_future,
    get_not_supported_translation,
)
from thonny.running import InlineCommandDialog
from thonny.workdlg import SubprocessDialog


class MicroPythonPipDialog(BackendPipDialog):
    def __init__(self, master):
        self._current_temp_dir = None
        self._checkboxes = []
        super().__init__(master)
        assert isinstance(self._backend_proxy, MicroPythonProxy)

    def _create_pip_process(self, args):
        return self._create_python_process(["-m", "thonny.plugins.micropython.micropip"] + args)

    def _get_active_version(self, name):
        # Don't have dist-level information
        return None

    def _on_install_click(self):
        if self.install_button["text"] == self.get_install_button_text():
            super()._on_install_click()
        elif self.install_button["text"] == self.get_search_button_text():
            self.search_box.delete(0, "end")
            self.search_box.insert(
                0, "micropython pycopy " + self.current_package_data["info"]["name"]
            )
            self._on_search(None)
        else:
            raise RuntimeError(
                "Unexpected text '%s' on install button" % self.install_button["text"]
            )

    def _on_uninstall_click(self):
        if self.uninstall_button["text"] == self.get_uninstall_button_text():
            super()._on_uninstall_click()
        elif self.uninstall_button["text"] == self.get_delete_selected_button_text():
            self._delete_selected()
        else:
            raise RuntimeError(
                "Unexpected text '%s' on install button" % self.install_button["text"]
            )

    def _delete_selected(self):
        paths = []
        for cb in self._checkboxes:
            if cb.variable.get():
                paths.append(cb.full_path)

        if paths:
            self._delete_paths(paths)
            self._start_update_list(self.current_package_data["info"]["name"])

    def _delete_paths(self, paths):
        get_runner().send_command_and_wait(
            InlineCommand("delete", paths=paths),
            dialog_title=tr("Deleting"),
        )

    def _get_install_command(self):
        return ["install", "-p", self._current_temp_dir]

    def _perform_pip_action(self, action: str) -> bool:
        if self._perform_pip_action_without_refresh(action):
            self._show_instructions()  # Make the old package go away as fast as possible

            # don't know which module to show, therefore None arg
            self._start_update_list(None)
            get_workbench().event_generate("RemoteFilesChanged")

    def _perform_pip_action_without_refresh(self, action: str) -> bool:
        assert action in ["install", "advanced"]

        self._current_temp_dir = tempfile.mkdtemp()
        try:
            return super()._perform_pip_action_without_refresh(action)
        finally:
            shutil.rmtree(self._current_temp_dir, ignore_errors=True)
            self._current_temp_dir = None

    def _create_upload_command(self) -> InlineCommand:
        paths = []
        for (dirpath, dirnames, filenames) in os.walk(self._current_temp_dir):
            if dirpath != self._current_temp_dir:
                paths.append(dirpath)

            for filename in filenames:
                source_path = os.path.join(dirpath, filename)
                paths.append(source_path)

        items = []
        for path in paths:
            for item in prepare_upload_items(
                path, self._current_temp_dir, self._get_target_directory()
            ):
                if item not in items:
                    items.append(item)

        if not items:
            raise RuntimeError("Could not find anything in temp directory. Was it a dummy package?")

        return InlineCommand("upload", items=items)

    def _create_python_process(self, args):
        proc = running.create_frontend_python_process(args, stderr=subprocess.STDOUT)
        return proc, proc.cmd

    def _on_listbox_select_package(self, name):
        self._start_show_module_info(name)

    def _start_show_module_info(self, name):
        self._clear_info_text()
        self.command_frame.grid_remove()
        self.title_label["text"] = tr("Module") + (" '%s'" % name)
        self.title_label.grid()
        self._set_state("fetching")
        self.advanced_button.grid_remove()

        get_workbench().bind("get_module_info_response", self._complete_display_module_info, True)
        get_runner().send_command(InlineCommand("get_module_info", module_name=name))

    def _complete_display_module_info(self, msg):
        self._set_state("idle")
        self.current_package_data = {"info": {"name": msg.module_name}}
        get_workbench().unbind("get_module_info_response", self._complete_display_module_info)

        self._append_info_text(tr("Installed to:") + " ", ("caption",))
        self._append_info_text(msg["location"] + "\n")

        for cb in self._checkboxes:
            cb.destroy()
        self._checkboxes.clear()

        for item in msg["effective_items"]:
            self._append_file_checkbox(item, msg["location"])

        if msg["shadowed_items"]:
            self._append_info_text("\n")
            self._append_info_text(tr("Shadowed items (not importable):") + "\n", ("caption",))
            for item in msg["shadowed_items"]:
                self._append_file_checkbox(item, None)

        self.command_frame.grid()
        self.uninstall_button.grid()
        self.install_button["text"] = self.get_search_button_text()
        self.uninstall_button["text"] = self.get_delete_selected_button_text()
        self.uninstall_button["state"] = "normal" if self._checkboxes else "disabled"
        self._select_list_item(msg.module_name)

    def _append_file_checkbox(self, full_path, context_dir):
        if context_dir:
            text = full_path[len(context_dir) :].strip("/")
        else:
            text = full_path

        if self._can_delete(full_path):
            cb = ttk.Checkbutton(self.info_text, text=text)
            var = tk.IntVar(value=1)
            cb.variable = var  # to avoid it being gc-d
            cb["variable"] = var
            cb.full_path = full_path
            self._checkboxes.append(cb)
            self.info_text.window_create("end", window=cb)
        else:
            self._append_info_text("• " + text)

        self._append_info_text("\n")

    def _show_package_info(self, name, data, error_code=None):
        super(MicroPythonPipDialog, self)._show_package_info(name, data, error_code)

        if name.lower().startswith("micropython-"):
            self._set_state("fetching")
            self._append_info_text("\n\n")
            self.info_text.mark_set("wait", "end-1c")
            self.info_text.mark_gravity("wait", "left")
            self._append_info_text("Querying micropython.org, please wait...")
            _start_fetching_micropython_org_info(name, self._add_micropython_org_info)

    def _add_micropython_org_info(self, name, data, error_code=None):
        self._set_state("idle")
        self.info_text.direct_delete("wait", "end")
        self.info_text.mark_unset("wait")
        self._append_info_text("\n")

        if error_code == 404:
            self._append_info_text(
                tr(
                    "Package is not available at micropython.org. "
                    "Version at PyPI will be installed."
                )
            )
        elif error_code:
            self._append_info_text("Error %s\n" % error_code)
            self._append_info_text(data.get("error", "") + "\n")
        else:
            ver = data["info"]["version"]
            self._append_info_text(
                tr(
                    "NB! micropython.org has published version %s of this package "
                    "and this will be installed by default."
                )
                % ver
                + "\n",
                ("bold",),
            )
            self._append_info_text(
                "If you want to install a version from PyPI, then use the advanced install button '...'. "
                "Note that PyPI version may require a specific fork of MicroPython."
            )

    def _can_delete(self, path):
        return not path.startswith("/usr/lib")

    def _get_target_directory(self):
        target_dir = self._backend_proxy.get_pip_target_dir()
        return target_dir

    def _read_only(self):
        return self._get_target_directory() is None

    def _show_instructions_about_existing_packages(self):
        self._append_info_text(tr("Upgrade or uninstall") + "\n", ("caption",))
        self.info_text.direct_insert(
            "end", tr("For upgrading simply install the package again.") + "\n"
        )
        self.info_text.direct_insert(
            "end", tr("For uninstalling delete corresponding files.") + "\n\n"
        )

    def _show_instructions_about_installing_from_local_file(self):
        # not supported
        pass

    def _use_user_install(self):
        return False

    def does_support_update_deps_switch(self):
        return False

    def _show_instructions_about_target(self):
        self._append_info_text(tr("Scope") + "\n", ("caption",))

        if isinstance(self._backend_proxy, LocalMicroPythonProxy):
            dir_tags = ("url",)
        else:
            dir_tags = ()

        if len(self._backend_proxy.get_lib_dirs()) == 1:
            self._append_info_text(self._get_target_directory(), dir_tags)
            self._append_info_text("\n")
        else:

            self.info_text.direct_insert(
                "end", tr("This dialog lists top-level modules from following directories:\n")
            )

            for path in self._backend_proxy.get_lib_dirs():
                self._append_info_text("• ")
                self._append_info_text(path, dir_tags)
                self._append_info_text("\n")

            self._append_info_text("\n")
            self._append_info_text(tr("New packages will be installed to") + "\n")
            self._append_info_text("• ")
            self._append_info_text(self._get_target_directory(), dir_tags)
            self._append_info_text("\n")

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

    def _get_interpreter(self):
        return self._backend_proxy.get_full_label()

    def _get_extra_switches(self):
        return []

    def _run_pip_with_dialog(self, args, title) -> Tuple[int, str, str]:
        args = ["-m", "thonny.plugins.micropython.micropip"] + args
        proc = running.create_frontend_python_process(args, stderr=subprocess.STDOUT)
        cmd = proc.cmd
        dlg = InstallAndUploadDialog(
            self,
            proc,
            back_cmd=self._create_upload_command,
            title="micropip",
            instructions=title,
            autostart=True,
            output_prelude=subprocess.list2cmdline(cmd) + "\n",
        )
        ui_utils.show_dialog(dlg)
        assert dlg.returncode is not None
        return dlg.returncode, dlg.stdout, dlg.stderr


class LocalMicroPythonPipDialog(MicroPythonPipDialog):
    def _get_install_command(self):
        return ["install", "-p", self._get_target_directory()]

    def _upload_installed_files(self) -> bool:
        "nothing to do -- micropip installed files directly to the right directory"

    def _delete_paths(self, paths):
        # assuming all files are listed if their directory is listed
        for path in sorted(paths, key=len, reverse=True):
            if os.path.isfile(path):
                os.remove(path)
            else:
                os.removedirs(path)

    def _run_pip_with_dialog(self, args, title) -> Tuple[int, str, str]:
        args = ["-m", "thonny.plugins.micropython.micropip"] + args
        proc = running.create_frontend_python_process(args, stderr=subprocess.STDOUT)
        cmd = proc.cmd
        dlg = SubprocessDialog(self, proc, "micropip", long_description=title, autostart=True)
        ui_utils.show_dialog(dlg)
        return dlg.returncode, dlg.stdout, dlg.stderr


def _start_fetching_micropython_org_info(name, completion_handler):
    import urllib.error
    import urllib.parse

    # Fetch info from PyPI
    url = MICROPYTHON_ORG_JSON % urllib.parse.quote(name)

    url_future = _fetch_url_future(url)

    def poll_fetch_complete():
        import json

        if url_future.done():
            try:
                _, bin_data = url_future.result()
                raw_data = bin_data.decode("UTF-8")
                completion_handler(name, json.loads(raw_data), None)
            except urllib.error.HTTPError as e:
                completion_handler(
                    name, {"info": {"name": name}, "error": str(e), "releases": {}}, e.code
                )
        else:
            tk._default_root.after(200, poll_fetch_complete)

    poll_fetch_complete()


class InstallAndUploadDialog(InlineCommandDialog):
    def __init__(
        self, master, proc, back_cmd, title, instructions=None, output_prelude=None, autostart=True
    ):
        self._stage = "install"
        self._proc = proc
        super().__init__(
            master,
            back_cmd,
            title,
            instructions=instructions,
            output_prelude=output_prelude,
            autostart=autostart,
        )

    def start_work(self):
        threading.Thread(target=self.work_in_thread, daemon=True).start()

    def work_in_thread(self):
        self.set_action_text("Installing to temp directory")
        self.append_text("Installing to temp directory\n")
        while True:
            line = self._proc.stdout.readline()
            if not line:
                break
            self.append_text(line)
            self.set_action_text_smart(line)
        self.returncode = self._proc.wait()
        if self.returncode:
            self.set_action_text("Error")
            self.append_text("\nmicropip returned with error code %s\n" % self.returncode)
        else:
            self.set_action_text("Copying to the device")
            self.append_text("Copying to the device\n")
        self.report_done(self.returncode == 0)

    def on_done(self, success):
        if not success or self._stage == "upload":
            super().on_done(success)
            if self._stage == "upload":
                # Returcode is required by the superclass
                if success:
                    self.returncode = 0
                else:
                    self.returncode = -1
            return

        assert self._stage == "install"
        # only half of the work is done
        self._stage = "upload"
        super().send_command_to_backend()
