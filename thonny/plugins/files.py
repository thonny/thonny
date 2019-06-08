# -*- coding: utf-8 -*-

import os
import tkinter as tk

from thonny import get_workbench, get_runner, get_shell
from thonny.base_file_browser import BaseLocalFileBrowser, BaseRemoteFileBrowser
from thonny.ui_utils import lookup_style_option
from thonny.common import normpath_with_actual_case
from thonny.running import construct_cd_command
from thonny.misc_utils import running_on_windows


minsize = 80


class FilesView(tk.PanedWindow):
    def __init__(self, master=None):
        tk.PanedWindow.__init__(self, master, orient="vertical", borderwidth=0)
        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", 4))
        self.configure(background=lookup_style_option("TPanedWindow", "background"))

        get_workbench().bind("BackendRestart", self.reset_remote, True)
        get_workbench().bind("WorkbenchClose", self.on_workbench_close, True)

        self.local_files = LocalFileBrowser(self)
        self.local_files.change_to_cwd()
        self.add(self.local_files, minsize=minsize)

        self.remote_files = RemoteFileBrowser(self)
        self.remote_added = False
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

        if proxy.has_own_filesystem():
            if not self.remote_added:
                self.add(self.remote_files, minsize=minsize)
                self.remote_added = True
                self.restore_split()
            self.remote_files.invalidate_cache()
            self.remote_files.focus_into(proxy.get_default_directory())
        else:
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

    def on_workbench_close(self, event=None):
        if self.remote_added:
            self.save_split()


class LocalFileBrowser(BaseLocalFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files)
        get_workbench().bind("LocalWorkingDirectoryChanged", self.on_local_backend_cd, True)

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
        if not path:
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
            and get_workbench().get_local_cwd() != path
            and get_runner().is_waiting_toplevel_command()
        ):
            get_shell().submit_magic_command(construct_cd_command(path))
        else:
            # change directly without notifying (non-existing, busy or remote) back-end
            get_workbench().set_local_cwd(path)

    def on_local_backend_cd(self, event):
        self.change_to_cwd()

    def change_to_cwd(self):
        cwd = get_workbench().get_local_cwd()
        if os.path.isdir(cwd):
            self.focus_into(cwd)


class RemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files, "device.last_browser_folder")
        get_workbench().bind("RemoteWorkingDirectoryChanged", self.on_remote_backend_cd, True)

    def on_remote_backend_cd(self, event):
        print("new remote cwd:", event.cwd)


def load_plugin() -> None:
    get_workbench().set_default(
        "file.last_browser_folder", normpath_with_actual_case(os.path.expanduser("~"))
    )

    get_workbench().add_view(FilesView, _("Files"), "nw")
