# -*- coding: utf-8 -*-

import os
import tkinter as tk

from thonny import get_workbench, get_runner, get_shell
from thonny.base_file_browser import BaseLocalFileBrowser, BaseRemoteFileBrowser
from thonny.ui_utils import lookup_style_option
from thonny.common import normpath_with_actual_case, InlineCommand
from thonny.running import construct_cd_command
from thonny.misc_utils import running_on_windows
from tkinter import messagebox

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
                self.add(self.remote_files, before=self.local_files, minsize=minsize)
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
                return self.focus_into(path)
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
            get_shell().submit_magic_command(construct_cd_command(path))
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

        def upload():
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
                response = get_runner().send_command(
                    InlineCommand(
                        "upload",
                        allow_overwrite=False,
                        source_paths=selection["paths"],
                        target_dir=target_dir,
                        blocking=True,
                        description=_("Uploading %s to %s")
                        % (selection["description"], target_dir),
                    )
                )
                check_upload_download_response("upload", response)
                self.master.remote_files.refresh_tree()

        self.menu.add_command(label=_("Upload to %s") % target_dir_desc, command=upload)

    def add_middle_menu_items(self):
        self.check_add_upload_command()
        super().add_middle_menu_items()


class ActiveRemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files)
        get_workbench().bind("ToplevelResponse", self.on_toplevel_response, True)

    def on_toplevel_response(self, event):
        if get_runner().get_backend_proxy().supports_remote_files():
            self.check_update_focus()

    def check_update_focus(self):
        proxy = get_runner().get_backend_proxy()
        if self.current_focus != proxy.get_cwd():
            self.focus_into(proxy.get_cwd())

    def request_new_focus(self, path):
        get_shell().submit_magic_command(["%cd", path if path != "" else "/"])

    def add_download_command(self):
        target_dir = self.master.get_active_local_dir()

        def download():
            selection = self.get_selection_info(True)
            if not selection:
                return

            response = get_runner().send_command(
                InlineCommand(
                    "download",
                    allow_overwrite=False,
                    source_paths=selection["paths"],
                    target_dir=target_dir,
                    blocking=True,
                    description=_("Downloading %s to %s") % (selection["description"], target_dir),
                )
            )
            check_upload_download_response("download", response)
            self.master.local_files.refresh_tree()

        self.menu.add_command(label=_("Download to %s") % target_dir, command=download)

    def add_middle_menu_items(self):
        self.add_download_command()
        super().add_middle_menu_items()


def check_upload_download_response(command_name, command_response):
    if command_response and command_response.get("existing_files"):
        # command was not performed because overwriting existing files need confirmation
        existing = sorted(command_response["existing_files"][:25])
        if len(command_response["existing_files"]) > 25:
            existing.append("...")

        user_response = messagebox.askokcancel(
            "Overwriting",
            "Some file(s) will be overwritten:\n\n" + "   " + "\n   ".join(existing),
            icon="info",
        )
        if not user_response:
            return

        else:
            get_runner().send_command(
                InlineCommand(
                    command_name,
                    allow_overwrite=True,
                    source_paths=command_response["source_paths"],
                    target_dir=command_response["target_dir"],
                    blocking=True,
                    description=command_response["description"],
                )
            )


def load_plugin() -> None:
    get_workbench().set_default(
        "file.last_browser_folder", normpath_with_actual_case(os.path.expanduser("~"))
    )

    get_workbench().add_view(FilesView, _("Files"), "nw")
