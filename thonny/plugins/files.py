# -*- coding: utf-8 -*-

import os
import pathlib
import tkinter as tk
from pathlib import PurePath, PureWindowsPath, PurePosixPath
from tkinter import messagebox
from tkinter.messagebox import showerror, askokcancel
from typing import Iterable, Type, List, Dict

from thonny import get_runner, get_shell, get_workbench
from thonny.base_file_browser import (
    BaseLocalFileBrowser,
    BaseRemoteFileBrowser,
    get_file_handler_conf_key,
)
from thonny.common import InlineCommand, normpath_with_actual_case, IGNORED_FILES_AND_DIRS
from thonny.languages import tr
from thonny.misc_utils import running_on_windows, sizeof_fmt, running_on_mac_os
from thonny.running import construct_cd_command
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
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files)
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
                )
            else:
                if upload(selection["paths"], self.get_active_directory(), target_dir):
                    self.master.remote_files.refresh_tree()

        self.menu.add_command(label=tr("Upload to %s") % target_dir_desc, command=_upload)

    def add_middle_menu_items(self, context):
        self.check_add_upload_command()
        super().add_middle_menu_items(context)


class ActiveRemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files)
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

            response = get_runner().send_command_and_wait(
                InlineCommand(
                    "prepare_download",
                    source_paths=selection["paths"],
                    description=tr("Downloading %s to %s") % (selection["description"], target_dir),
                ),
                dialog_title=tr("Preparing"),
            )
            prepared_items = self._prepare_download_items(
                response["all_items"], self.get_active_directory(), target_dir
            )
            existing_target_items = self._get_existing_target_items(prepared_items)
            picked_items = pick_transfer_items(prepared_items, existing_target_items)
            if picked_items:
                response = get_runner().send_command_and_wait(
                    InlineCommand("download", items=picked_items), dialog_title=tr("Copying")
                )
                _check_transfer_errors(response)

                self.master.local_files.refresh_tree()

        self.menu.add_command(label=tr("Download to %s") % target_dir, command=download)

    def _prepare_download_items(
        self, all_source_items: Dict[str, Dict], source_context_dir: str, target_dir: str
    ) -> List[Dict]:
        result = []
        for source_path, source_item in all_source_items.items():
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

    def add_middle_menu_items(self, context):
        self.add_download_command()
        super().add_middle_menu_items(context)


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
    prepared_items: List[Dict], existing_target_items: Dict[str, Dict]
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
        showerror("Error", format_items(errors))
        return []
    elif overwrites:
        if askokcancel(
            "Overwrite?", "This operation will overwrite\n\n" + format_items(overwrites)
        ):
            return prepared_items
        else:
            return []
    else:
        return prepared_items


def _check_transfer_errors(response):
    if response.get("error"):
        showerror(tr("Transfer error"), response["error"])
    elif response["errors"]:
        showerror(
            tr("Transfer error"), "Got following errors:\n" + format_items(response["errors"])
        )


def format_items(items):
    max_count = 10
    if len(items) == 1:
        return items[0]
    msg = "• " + "\n• ".join(items[:max_count])
    if len(items) > max_count:
        msg += "\n ... %d more ..."

    return msg


def upload(paths, source_dir, target_dir) -> bool:
    items = []
    for path in paths:
        for item in _prepare_upload_items(path, source_dir, target_dir):
            # same path could have been provided directly and also via its parent
            if item not in items:
                items.append(item)

    target_paths = [x["target_path"] for x in items]
    response = get_runner().send_command_and_wait(
        InlineCommand(
            "prepare_upload",
            target_paths=target_paths,
        ),
        dialog_title=tr("Preparing"),
    )

    picked_items = list(
        sorted(
            pick_transfer_items(items, response["existing_items"]), key=lambda x: x["target_path"]
        )
    )
    if picked_items:
        response = get_runner().send_command_and_wait(
            InlineCommand("upload", items=picked_items), dialog_title="Copying"
        )
        _check_transfer_errors(response)
        return True
    else:
        return False


def _prepare_upload_items(
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
                    _prepare_upload_items(
                        os.path.join(source_path, child), source_context_dir, target_dir
                    )
                )
    return result


def load_plugin() -> None:
    get_workbench().set_default(
        "file.last_browser_folder", normpath_with_actual_case(os.path.expanduser("~"))
    )

    get_workbench().add_view(FilesView, tr("Files"), "nw")

    for ext in [".py", ".pyw", ".pyi", ".txt", ".log", ".json", ".yml", ".yaml", ".md", ".rst"]:
        get_workbench().set_default(get_file_handler_conf_key(ext), "thonny")


if __name__ == "__main__":
    print(
        transpose_path(r"C:\kala\pala\kama.py", "C:", "/home/aivar", PureWindowsPath, PurePosixPath)
    )
