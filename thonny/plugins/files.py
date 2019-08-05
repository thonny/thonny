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

        if proxy.has_own_filesystem():
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

    def _check_add_upload_command(self):
        target_dir = self.master.get_active_remote_dir()

        if target_dir is None:
            return

        nodes = self.get_selected_nodes()

        if not nodes:
            return
        elif len(nodes) == 1:
            source_desc = self.tree.set(nodes[0], "name")
        else:
            source_desc = _("%d items") % len(nodes)

        proxy = get_runner().get_backend_proxy()

        if not proxy.supports_directories():
            target_dir_desc = proxy.get_node_label()
        else:
            target_dir_desc = target_dir

        label = _("Upload") + " %s → %s" % (source_desc, target_dir_desc)

        paths = [self.tree.set(node, "path") for node in nodes]
        kinds = [self.tree.set(node, "kind") for node in nodes]

        def upload():
            if "dir" in kinds and not proxy.supports_directories():
                messagebox.showerror(
                    "Can't upload directory",
                    "%s does not support directories.\n" % proxy.get_node_label()
                    + "You can only upload files.",
                )
            else:
                get_runner().send_command(
                    InlineCommand(
                        "upload",
                        source_paths=paths,
                        target_dir=target_dir,
                        blocking=True,
                        description=label,
                    )
                )
                self.master.remote_files.refresh_tree()

        self.menu.add_command(label=label, command=upload)

    def add_first_menu_items(self):
        super().add_first_menu_items()
        self.menu.add_separator()
        self._check_add_upload_command()


class ActiveRemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        super().__init__(master, show_hidden_files)
        get_workbench().bind("ToplevelResponse", self.on_toplevel_response, True)

    def on_toplevel_response(self, event):
        self.check_update_focus()

    def check_update_focus(self):
        proxy = get_runner().get_backend_proxy()
        if self.current_focus != proxy.get_cwd():
            self.focus_into(proxy.get_cwd())

    def request_focus_into(self, path):
        proxy = get_runner().get_backend_proxy()
        if proxy:
            assert proxy.has_own_filesystem()

            if not get_runner().is_waiting_toplevel_command():
                messagebox.showerror(
                    "Error",
                    "Can't change or refresh directories when device is busy.\n"
                    + "Wait until current command completes and try again.",
                )
            elif not proxy.supports_directories():
                assert path == ""
                self.focus_into(path)
            elif self.current_focus == path:
                # refreshes
                self.focus_into(path)
            else:
                get_shell().submit_magic_command(["%cd", path if path != "" else "/"])

    def _add_download_command(self):
        nodes = self.get_selected_nodes()

        target_dir = self.master.get_active_local_dir()

        if not nodes:
            return
        elif len(nodes) == 1:
            source_desc = self.tree.set(nodes[0], "name")
        else:
            source_desc = _("%d items") % len(nodes)

        label = _("Download") + " %s → %s" % (source_desc, target_dir)

        paths = [self.tree.set(node, "path") for node in nodes]

        def download():
            get_runner().send_command(
                InlineCommand(
                    "download",
                    source_paths=paths,
                    target_dir=target_dir,
                    blocking=True,
                    description=label,
                )
            )
            self.master.local_files.refresh_tree()

        self.menu.add_command(label=label, command=download)

    def add_first_menu_items(self):
        super().add_first_menu_items()
        self.menu.add_separator()
        self._add_download_command()


def load_plugin() -> None:
    get_workbench().set_default(
        "file.last_browser_folder", normpath_with_actual_case(os.path.expanduser("~"))
    )

    get_workbench().add_view(FilesView, _("Files"), "nw")
