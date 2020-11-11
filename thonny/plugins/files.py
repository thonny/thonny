# -*- coding: utf-8 -*-

import os
import pathlib
import tkinter as tk
from pathlib import PurePath, PureWindowsPath, PurePosixPath
from tkinter import messagebox
from tkinter.messagebox import showerror, askokcancel
from typing import Iterable, Type, List, Dict, Optional

from thonny import get_runner, get_shell, get_workbench, ui_utils
from thonny.base_file_browser import (
    BaseLocalFileBrowser,
    BaseRemoteFileBrowser,
    get_file_handler_conf_key,
    HIDDEN_FILES_OPTION,
)
from thonny.common import (
    InlineCommand,
    normpath_with_actual_case,
    IGNORED_FILES_AND_DIRS,
    CommandToBackend,
    universal_dirname,
)
from thonny.languages import tr
from thonny.misc_utils import running_on_windows, sizeof_fmt, running_on_mac_os
from thonny.running import construct_cd_command, InlineCommandDialog
from thonny.ui_utils import lookup_style_option

minsize = 80


class FilesView(tk.PanedWindow):
    def __init__(self, master=None):
        tk.PanedWindow.__init__(self, master, orient="vertical", borderwidth=0)
        self.remote_added = False

        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", 4))
        self.configure(background=lookup_style_option("TPanedWindow", "background"))

        get_workbench().bind("BackendTerminated", self.on_backend_terminate, True)
        get_workbench().bind("BackendRestart", self.on_backend_restart, True)
        get_workbench().bind("WorkbenchClose", self.on_workbench_close, True)

        self.local_files = ActiveLocalFileBrowser(self)
        self.local_files.check_update_focus()
        self.add(self.local_files, minsize=minsize)

        self.remote_files = ActiveRemoteFileBrowser(self)
        self.reset_remote()

    def on_show(self):
        self.reset_remote()
        self.local_files.refresh_tree()

    def reset_remote(self, msg=None):
        runner = get_runner()
        if not runner:
            return

        proxy = runner.get_backend_proxy()
        if not proxy:
            self.hide_remote()
            return

        if proxy.supports_remote_files():
            # remote pane is needed
            if not self.remote_added:
                self.add(self.remote_files, minsize=minsize)
                self.remote_added = True
                self.restore_split()
            self.remote_files.clear()
            self.remote_files.check_update_focus()
        else:
            # remote pane not needed
            self.hide_remote()

    def hide_remote(self):
        if self.remote_added:
            self.save_split()
            self.remove(self.remote_files)
            self.remote_added = False

    def save_split(self):
        _, y = self.sash_coord(0)
        get_workbench().set_option("view.files_split", y)

    def restore_split(self):
        split = get_workbench().get_option("view.files_split", None)
        if split is None:
            if self.winfo_height() > 5:
                split = int(self.winfo_height() * 0.66)
            else:
                split = 600

        self.sash_place(0, 0, split)

    def on_backend_restart(self, event):
        if event.get("full"):
            self.reset_remote(event)

    def on_backend_terminate(self, event):
        self.reset_remote(event)

    def on_workbench_close(self, event=None):
        if self.remote_added:
            self.save_split()

    def get_active_local_dir(self):
        return self.local_files.get_active_directory()

    def get_active_remote_dir(self):
        if self.remote_added:
            return self.remote_files.get_active_directory()
        else:
            return None

    def destroy(self):
        get_workbench().unbind("BackendTerminated", self.on_backend_terminate)
        get_workbench().unbind("BackendRestart", self.on_backend_restart)
        get_workbench().unbind("WorkbenchClose", self.on_workbench_close)
        super().destroy()


class ActiveLocalFileBrowser(BaseLocalFileBrowser):
    def __init__(self, master):
        super().__init__(master)
        get_workbench().bind("ToplevelResponse", self.on_toplevel_response, True)

    def is_active_browser(self):
        return True

    def create_new_file(self):
        path = super().create_new_file()
        if path and path.endswith(".py"):
            get_workbench().get_editor_notebook().show_file(path)

    def get_proposed_new_file_name(self, folder, extension):
        base = "new_file"

        if os.path.exists(os.path.join(folder, base + extension)):
            i = 2

            while True:
                name = base + "_" + str(i) + extension
                path = os.path.join(folder, name)
                if os.path.exists(path):
                    i += 1
                else:
                    return name
        else:
            return base + extension

    def request_focus_into(self, path):
        if path == "":
            if running_on_windows():
                # list of drives, can't cd
                self.focus_into(path)
                return
            else:
                path = "/"

        if not os.path.isdir(path):
            return

        proxy = get_runner().get_backend_proxy()
        if (
            proxy
            and proxy.uses_local_filesystem()
            and proxy.get_cwd() != path
            and get_runner().is_waiting_toplevel_command()
        ):
            get_shell().submit_magic_command(construct_cd_command(normpath_with_actual_case(path)))
        else:
            # it's OK, if it's already focused into this directory
            # focus again to refresh
            self.focus_into(path)
            get_workbench().set_local_cwd(path)

    def on_toplevel_response(self, event):
        self.check_update_focus()

    def check_update_focus(self):
        cwd = get_workbench().get_local_cwd()
        if cwd != self.current_focus and os.path.isdir(cwd):
            self.focus_into(cwd)

    def check_add_upload_command(self):
        target_dir = self.master.get_active_remote_dir()
        if target_dir is None:
            return

        proxy = get_runner().get_backend_proxy()

        if not proxy.supports_remote_directories():
            target_dir_desc = proxy.get_node_label()
        else:
            target_dir_desc = target_dir

        def _upload():
            selection = self.get_selection_info(True)
            if not selection:
                return

            if "dir" in selection["kinds"] and not proxy.supports_remote_directories():
                messagebox.showerror(
                    "Can't upload directory",
                    "%s does not support directories.\n" % proxy.get_node_label()
                    + "You can only upload files.",
                    master=self,
                )
            else:
                if upload(selection["paths"], target_dir, master=self):
                    self.master.remote_files.refresh_tree()

        self.menu.add_command(label=tr("Upload to %s") % target_dir_desc, command=_upload)

    def add_middle_menu_items(self, context):
        self.check_add_upload_command()
        super().add_middle_menu_items(context)


class ActiveRemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master):
        super().__init__(master)
        get_workbench().bind("ToplevelResponse", self.on_toplevel_response, True)
        get_workbench().bind("RemoteFilesChanged", self.on_remote_files_changed, True)

    def is_active_browser(self):
        return True

    def on_toplevel_response(self, msg):
        if not self.winfo_ismapped():
            return
        if get_runner().get_backend_proxy().supports_remote_files():
            # pass cwd, as proxy may not yet know it
            self.check_update_focus(msg.get("cwd"))

    def on_remote_files_changed(self, event=None):
        if not self.winfo_ismapped():
            return

        if get_runner().get_backend_proxy().supports_remote_files():
            self.refresh_tree()

    def check_update_focus(self, new_cwd=None):
        if new_cwd is None:
            proxy = get_runner().get_backend_proxy()
            new_cwd = proxy.get_cwd()

        if self.current_focus != new_cwd:
            self.focus_into(new_cwd)

    def request_new_focus(self, path):
        get_shell().submit_magic_command(["%cd", path if path != "" else "/"])

    def add_download_command(self):
        target_dir = self.master.get_active_local_dir()

        def download():
            selection = self.get_selection_info(True)
            if not selection:
                return

            dlg = DownloadDialog(
                self,
                selection["paths"],
                selection["description"],
                target_dir,
            )
            ui_utils.show_dialog(dlg)
            if dlg.response is not None:
                self.master.local_files.refresh_tree()

        self.menu.add_command(label=tr("Download to %s") % target_dir, command=download)

    def add_middle_menu_items(self, context):
        self.add_download_command()
        super().add_middle_menu_items(context)


class TransferDialog(InlineCommandDialog):
    def _on_response(self, response):
        if response.get("command_id") != self._cmd["id"]:
            return

        if self._stage == "preparation":
            if self._confirm_and_start_main_work(response):
                self._stage = "main_work"
            else:
                self.response = None
                self.report_done(True)

        elif self._stage == "main_work":
            self.response = response
            self.report_done(self._check_success(response))

        self.update_ui()

    def _confirm_and_start_main_work(self, response):
        raise NotImplementedError()

    def _check_success(self, response):
        if response.get("error"):
            self.set_action_text("Error")
            self.append_text("\nError: %s\n" % response["error"])
            return False
        elif response["errors"]:
            self.set_action_text("Error")
            self.append_text("\nError: %s\n" % format_items(response["errors"]))
            return False
        else:
            self.set_action_text("Done!")
            return True


class UploadDialog(TransferDialog):
    def __init__(self, master, paths, target_dir):
        self._stage = "preparation"
        self.items = []
        source_names = []
        for path in paths:
            source_context_dir = os.path.dirname(path)
            for item in prepare_upload_items(path, source_context_dir, target_dir):
                # same path could have been provided directly and also via its parent
                if item not in self.items:
                    self.items.append(item)
                    source_names.append(os.path.basename(item["source_path"]))

        target_paths = [x["target_path"] for x in self.items]
        cmd = InlineCommand(
            "prepare_upload",
            target_paths=target_paths,
            description=get_transfer_description("Uploading", source_names, target_dir),
        )

        super(UploadDialog, self).__init__(master, cmd, "Uploading")

    def _confirm_and_start_main_work(self, preparation_response):
        picked_items = list(
            sorted(
                pick_transfer_items(self.items, preparation_response["existing_items"], self),
                key=lambda x: x["target_path"],
            )
        )
        if picked_items:
            self._cmd = InlineCommand("upload", items=picked_items)
            get_runner().send_command(self._cmd)
            return True
        else:
            return False


class DownloadDialog(TransferDialog):
    def __init__(self, master, paths, description, target_dir):
        self._stage = "preparation"
        self._target_dir = target_dir

        cmd = InlineCommand(
            "prepare_download",
            source_paths=paths,
            description=tr("Downloading %s to %s") % (description, target_dir),
        )

        super(DownloadDialog, self).__init__(master, cmd, "Downloading")

    def _prepare_download_items(
        self, all_source_items: Dict[str, Dict], target_dir: str
    ) -> List[Dict]:
        result = []
        for source_path, source_item in all_source_items.items():
            source_context_dir = universal_dirname(source_item["anchor"])
            result.append(
                {
                    "kind": source_item["kind"],
                    "size": source_item["size"],
                    "source_path": source_path,
                    "target_path": transpose_path(
                        source_path, source_context_dir, target_dir, PurePosixPath, pathlib.Path
                    ),
                }
            )
        return result

    def _get_existing_target_items(self, prepared_items: List[Dict]) -> Dict[str, Dict]:
        result = {}

        for item in prepared_items:
            target_path = item["target_path"]
            if os.path.exists(target_path):
                if os.path.isdir(target_path):
                    kind = "dir"
                    size = None
                else:
                    kind = "file"
                    size = os.path.getsize(target_path)

                result[target_path] = {
                    "kind": kind,
                    "size": size,
                }
        return result

    def _confirm_and_start_main_work(self, preparation_response):
        prepared_items = self._prepare_download_items(
            preparation_response["all_items"], self._target_dir
        )
        existing_target_items = self._get_existing_target_items(prepared_items)
        picked_items = pick_transfer_items(prepared_items, existing_target_items, self)
        if picked_items:
            self._cmd = InlineCommand("download", items=picked_items)
            get_runner().send_command(self._cmd)
            return True
        else:
            return False


def transpose_path(
    source_path: str,
    source_dir: str,
    target_dir: str,
    source_path_class: Type[PurePath],
    target_path_class: Type[PurePath],
) -> str:
    assert not source_dir.endswith(":")
    source_path_parts = source_path_class(source_path).parts
    source_dir_parts = source_path_class(source_dir).parts
    assert source_path_parts[: len(source_dir_parts)] == source_dir_parts
    source_suffix_parts = source_path_parts[len(source_dir_parts) :]

    target = target_path_class(target_dir).joinpath(*source_suffix_parts)
    return str(target)


def pick_transfer_items(
    prepared_items: List[Dict], existing_target_items: Dict[str, Dict], master
) -> List[Dict]:
    if not existing_target_items:
        return prepared_items

    errors = []
    overwrites = []

    for item in prepared_items:
        if item["target_path"] in existing_target_items:
            target_info = existing_target_items[item["target_path"]]
            if item["kind"] != target_info["kind"]:
                errors.append(
                    "Can't overwrite '%s' with '%s', because former is a %s but latter is a %s"
                    % (item["target_path"], item["source_path"], target_info["kind"], item["kind"])
                )
            elif item["kind"] == "file":
                size_diff = item["size"] - target_info["size"]
                if size_diff > 0:
                    replacement = "a larger file (%s + %s)" % (
                        sizeof_fmt(target_info["size"]),
                        sizeof_fmt(size_diff),
                    )
                elif size_diff < 0:
                    replacement = "a smaller file (%s - %s)" % (
                        sizeof_fmt(target_info["size"]),
                        sizeof_fmt(-size_diff),
                    )
                else:
                    replacement = "a file of same size (%s)" % sizeof_fmt(target_info["size"])

                overwrites.append("'%s' with %s" % (item["target_path"], replacement))

    if errors:
        showerror("Error", format_items(errors), master=master)
        return []
    elif overwrites:
        if askokcancel(
            "Overwrite?",
            "This operation will overwrite\n\n" + format_items(overwrites),
            master=master,
        ):
            return prepared_items
        else:
            return []
    else:
        return prepared_items


def format_items(items):
    max_count = 10
    if len(items) == 1:
        return items[0]
    msg = "• " + "\n• ".join(items[:max_count])
    if len(items) > max_count:
        msg += "\n ... %d more ..."

    return msg


def upload(paths, target_dir, master) -> bool:
    dlg = UploadDialog(master, paths, target_dir)
    ui_utils.show_dialog(dlg)
    return dlg.response is not None


def prepare_upload_items(
    source_path: str, source_context_dir: str, target_dir: str
) -> Iterable[Dict]:
    # assuming target system has Posix paths
    if os.path.isdir(source_path):
        kind = "dir"
        size = None
    else:
        kind = "file"
        size = os.path.getsize(source_path)

    result = [
        {
            "kind": kind,
            "size": size,
            "source_path": source_path,
            "target_path": transpose_path(
                source_path, source_context_dir, target_dir, pathlib.Path, PurePosixPath
            ),
        }
    ]

    if os.path.isdir(source_path):
        for child in os.listdir(source_path):
            if child not in IGNORED_FILES_AND_DIRS:
                result.extend(
                    prepare_upload_items(
                        os.path.join(source_path, child), source_context_dir, target_dir
                    )
                )
    return result


def get_transfer_description(verb, paths, target_dir):
    if len(paths) == 1:
        subject = "'%s'" % paths[0]
    else:
        subject = "%d items" % len(paths)

    return "%s %s to %s" % (verb, subject, target_dir)


def load_plugin() -> None:
    get_workbench().set_default(
        "file.last_browser_folder", normpath_with_actual_case(os.path.expanduser("~"))
    )

    get_workbench().set_default(HIDDEN_FILES_OPTION, False)

    get_workbench().add_view(FilesView, tr("Files"), "nw")

    for ext in [".py", ".pyw", ".pyi", ".txt", ".log", ".json", ".yml", ".yaml", ".md", ".rst"]:
        get_workbench().set_default(get_file_handler_conf_key(ext), "thonny")


if __name__ == "__main__":
    print(
        transpose_path(r"C:\kala\pala\kama.py", "C:", "/home/aivar", PureWindowsPath, PurePosixPath)
    )
