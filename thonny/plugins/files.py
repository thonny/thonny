# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

# from thonny.ui_utils import askstring TODO: doesn't work
from tkinter.simpledialog import askstring

from thonny import get_workbench, misc_utils
from thonny.base_file_browser import BaseFileBrowser
from thonny.ui_utils import lookup_style_option

class FilesView(tk.PanedWindow):
    def __init__(self, master=None):
        tk.PanedWindow.__init__(self, master, orient="vertical", borderwidth=0)
        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", 4))
        self.configure(background=lookup_style_option("TPanedWindow", "background"))
        
        self.local_files = MainFileBrowser(self)
        self.add(self.local_files)
        
        self.remote_files = RemoteFileBrowser(self)
        self.add(self.remote_files)
        

class MainFileBrowser(BaseFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        BaseFileBrowser.__init__(
            self, master, show_hidden_files, "file.last_browser_folder"
        )

        self.menu = tk.Menu(tk._default_root, tearoff=False)
        self.menu.add_command(label="Create new file", command=self.create_new_file)

        self.tree.bind("<3>", self.on_secondary_click, True)
        if misc_utils.running_on_mac_os():
            self.tree.bind("<2>", self.on_secondary_click, True)
            self.tree.bind("<Control-1>", self.on_secondary_click, True)
            
        self.set_breadcrumbs("C:\\Users\\Aivar\\Documents\\Python\\PyGame\\NikaNaka")

    def create_new_file(self):
        selected_path = self.get_selected_path()

        if not selected_path:
            return

        if os.path.isdir(selected_path):
            parent_path = selected_path
        else:
            parent_path = os.path.dirname(selected_path)

        initial_name = self.get_proposed_new_file_name(parent_path, ".py")
        name = askstring(
            "File name",
            "Provide filename",
            initialvalue=initial_name,
            # selection_range=(0, len(initial_name)-3)
        )

        if not name:
            return

        path = os.path.join(parent_path, name)

        if os.path.exists(path):
            showerror("Error", "The file '" + path + "' already exists", parent=get_workbench())
        else:
            open(path, "w").close()

        self.open_path_in_browser(path, True)
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

    def on_secondary_click(self, event):
        node_id = self.tree.identify_row(event.y)

        if node_id:
            self.tree.selection_set(node_id)
            self.tree.focus(node_id)
            self.menu.tk_popup(event.x_root, event.y_root)

    def on_double_click(self, event):
        path = self.get_selected_path()
        if os.path.isfile(path):
            get_workbench().get_editor_notebook().show_file(path)
            self.save_current_folder()
        elif os.path.isdir(path):
            self.refresh_tree(self.get_selected_node(), True)



class RemoteFileBrowser(BaseFileBrowser):
    def __init__(self, master, show_hidden_files=False):
        BaseFileBrowser.__init__(
            self, master, show_hidden_files, "device.last_browser_folder",
            breadcrumbs_pady=(0,7)
        )
        self.set_breadcrumbs("")

    def get_root_text(self):
        return "TARGET DEVICE"
    


def load_plugin() -> None:
    get_workbench().set_default("file.last_browser_folder", None)
    get_workbench().add_view(FilesView, "Files", "nw")
