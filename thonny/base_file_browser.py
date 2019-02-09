import os.path
import tkinter as tk
from tkinter import ttk

from thonny import get_workbench, misc_utils, tktextext
from thonny.ui_utils import scrollbar_style, lookup_style_option
import re

_dummy_node_text = "..."


class BaseFileBrowser(ttk.Frame):
    def __init__(self, master, show_hidden_files=False, last_folder_setting_name=None,
                 breadcrumbs_pady=(5,7)):
        ttk.Frame.__init__(self, master, borderwidth=0, relief="flat")
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                            style=scrollbar_style("Vertical"))
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW, rowspan=3)
        
        tktextext.fixwordbreaks(tk._default_root)
        self.building_breadcrumbs = False
        self.path_bar = tktextext.TweakableText(self, borderwidth=0, relief="flat", height=1,
            font="TkDefaultFont", wrap="word", padx=6,
            pady=5, insertwidth=0,
            background=lookup_style_option("ViewToolbar.TFrame", "background"))
        self.init_path_bar()
        self.path_bar.grid(row=0, sticky="nsew")
        
        spacer = ttk.Frame(self, height=1)
        spacer.grid(row=1, sticky="nsew")
        
        self.tree = ttk.Treeview(   
            self,
            columns=["#0", "kind", "path"],
            displaycolumns=(0,),
            yscrollcommand=self.vert_scrollbar.set,
        )
        self.tree["show"] = "headings"
        self.tree.grid(row=2, column=0, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.show_hidden_files = show_hidden_files
        self.tree["show"] = ("tree",)

        wb = get_workbench()
        self.folder_icon = wb.get_image("folder")
        self.python_file_icon = wb.get_image("python-file")
        self.text_file_icon = wb.get_image("text-file")
        self.generic_file_icon = wb.get_image("generic-file")
        self.hard_drive_icon = wb.get_image("hard-drive")

        self.tree.column("#0", width=500, anchor=tk.W)

        # set-up root node
        self.tree.set("", "kind", "root")
        self.tree.set("", "path", "")
        self.refresh_tree()

        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)

        self._last_folder_setting_name = last_folder_setting_name
        self.open_initial_folder()
    
    def init_toolbar(self):
        self.title_label = ttk.Label(self.toolbar, text=self.get_root_text(), anchor="w",
                                     style="ViewToolbar.TLabel")
        self.title_label.grid(row=0, column=1, sticky="nw", padx=0, pady=(2,4))
        
        self.menu_label = ttk.Button(self.toolbar, text=" ≡ ", 
                                     style="ViewToolbar.Toolbutton")
        self.menu_label.grid(row=0, column=2, padx=4, pady=(2,4))
        
        self.toolbar.columnconfigure(1, weight=1)
        
        
        #self.star_label = ttk.Label(self.toolbar, image=get_workbench().get_image("031"), text="s")
        #self.star_label.grid(row=0, column=2)
    
    def init_path_bar(self):
        self.path_bar.set_read_only(True)
        self.path_bar.bind("<Configure>", self.resize_path_bar, True)
        self.path_bar.tag_configure("dir", 
                                    foreground=lookup_style_option("Url.TLabel", "foreground"))
        self.path_bar.tag_configure("underline", underline=True)
        
        def get_dir_range(event):
            mouse_index = self.path_bar.index("@%d,%d" % (event.x, event.y))
            return self.path_bar.tag_prevrange("dir", mouse_index + "+1c")
        
        def dir_tag_motion(event):
            self.path_bar.tag_remove("underline", "1.0", "end")
            dir_range = get_dir_range(event)
            if dir_range:
                range_start, range_end = dir_range
                self.path_bar.tag_add("underline", range_start, range_end)
    
        def dir_tag_enter(event):
            self.path_bar.config(cursor="hand2")
        
        def dir_tag_leave(event):
            self.path_bar.config(cursor="")
            self.path_bar.tag_remove("underline", "1.0", "end")
        
        def dir_tag_click(event):
            mouse_index = self.path_bar.index("@%d,%d" % (event.x, event.y))
            print(mouse_index)
            lineno = int(float(mouse_index))
            if lineno == 1:
                print("select root")
            else:
                assert lineno == 2
                dir_range = get_dir_range(event)
                if dir_range:
                    _, end_index = dir_range
                    print("select", self.path_bar.get("2.0", end_index))
        
        self.path_bar.tag_bind("dir", "<1>", dir_tag_click)
        self.path_bar.tag_bind("dir", "<Enter>", dir_tag_enter)
        self.path_bar.tag_bind("dir", "<Leave>", dir_tag_leave)
        self.path_bar.tag_bind("dir", "<Motion>", dir_tag_motion)
    
    def set_breadcrumbs(self, path):
        self.building_breadcrumbs = True
        self.path_bar.direct_delete("1.0", "end")
        
        self.path_bar.direct_insert("1.0", self.get_root_text(), ("dir",))
        
        if not path:
            return 
        
        self.path_bar.direct_insert("end", "\n")
        
        def create_spacer():
            return ttk.Frame(self.path_bar, height=1, width=4,
                             style="ViewToolbar.TFrame")
        
        if "/" in path:
            sep = "/"
        else:
            sep = "\\"
        
        parts = path.split(sep)
        for i, part in enumerate(parts):
            if i > 0:
                if parts[0] != "":
                    self.path_bar.window_create("end", window=create_spacer())
                self.path_bar.direct_insert("end", sep)
                self.path_bar.window_create("end", window=create_spacer())
            
            self.path_bar.direct_insert("end", part, tags=("dir",))
             
        self.building_breadcrumbs = False
    
    def get_root_text(self):
        return "THIS COMPUTER"
    
    def open_initial_folder(self):
        if self._last_folder_setting_name:
            path = get_workbench().get_option(self._last_folder_setting_name)
            if path:
                self.open_path_in_browser(path, True)

    def save_current_folder(self):
        if not self._last_folder_setting_name:
            return

        path = self.get_selected_path()

        if not path:
            return

        if os.path.isfile(path):
            path = os.path.dirname(path)
        get_workbench().set_option(self._last_folder_setting_name, path)

    def on_open_node(self, event):
        node_id = self.get_selected_node()
        if node_id:
            self.refresh_tree(node_id, True)

    def get_selected_node(self):
        nodes = self.tree.selection()
        assert len(nodes) <= 1
        if len(nodes) == 1:
            return nodes[0]
        else:
            return None
    
    def resize_path_bar(self, event):
        if self.building_breadcrumbs:
            return
        height = self.tk.call((self.path_bar, "count", "-update", "-displaylines", "1.0", "end"))
        self.path_bar.configure(height=height)

    def get_selected_path(self):
        node_id = self.get_selected_node()

        if node_id:
            return self.tree.set(node_id, "path")
        else:
            return None

    def open_path_in_browser(self, path, see=True):

        # unfortunately os.path.split splits from the wrong end (for this case)
        def split(path):
            head, tail = os.path.split(path)
            if head == "" and tail == "":
                return []
            elif head == path or tail == path:
                return [path]
            elif head == "":
                return [tail]
            elif tail == "":
                return split(head)
            else:
                return split(head) + [tail]

        parts = split(path)
        current_node_id = ""
        current_path = ""

        while parts != []:
            current_path = os.path.join(current_path, parts.pop(0))

            for child_id in self.tree.get_children(current_node_id):
                child_path = self.tree.set(child_id, "path")
                if child_path == current_path:
                    self.tree.item(child_id, open=True)
                    self.refresh_tree(child_id)
                    current_node_id = child_id
                    break

        if see:
            self.tree.selection_set(current_node_id)
            self.tree.focus(current_node_id)

            if self.tree.set(current_node_id, "kind") == "file":
                self.tree.see(self.tree.parent(current_node_id))
            else:
                self.tree.see(current_node_id)

    

    def refresh_tree(self, node_id="", opening=None):
        path = self.tree.set(node_id, "path")
        # print("REFRESH", path)

        if os.path.isfile(path):
            self.tree.set_children(node_id)
            self.tree.item(node_id, open=False)
        else:
            # either root or directory
            if node_id == "" or self.tree.item(node_id, "open") or opening == True:
                fs_children_names = self.listdir(path, self.show_hidden_files)
                tree_children_ids = self.tree.get_children(node_id)

                # recollect children
                children = {}

                # first the ones, which are present already in tree
                for child_id in tree_children_ids:
                    name = self.tree.item(child_id, "text")
                    if name in fs_children_names:
                        children[name] = child_id

                # add missing children
                for name in fs_children_names:
                    if name not in children:
                        children[name] = self.tree.insert(node_id, "end")
                        self.tree.set(children[name], "path", os.path.join(path, name))

                def file_order(name):
                    # items in a folder should be ordered so that
                    # folders come first and names are ordered case insensitively
                    return (os.path.isfile(os.path.join(path, name)), name.upper())

                # update tree
                ids_sorted_by_name = list(
                    map(
                        lambda key: children[key],
                        sorted(children.keys(), key=file_order),
                    )
                )
                self.tree.set_children(node_id, *ids_sorted_by_name)

                for child_id in ids_sorted_by_name:
                    self.update_node_format(child_id)
                    self.refresh_tree(child_id)

            else:
                # closed dir
                # Don't fetch children yet, but ensure that expand button is visible
                children_ids = self.tree.get_children(node_id)
                if len(children_ids) == 0:
                    self.tree.insert(node_id, "end", text=_dummy_node_text)

    def update_node_format(self, node_id):
        assert node_id != ""

        path = self.tree.set(node_id, "path")

        if os.path.isdir(path) or path.endswith(":") or path.endswith(":\\"):
            self.tree.set(node_id, "kind", "dir")
            if path.endswith(":") or path.endswith(":\\"):
                img = self.hard_drive_icon
            else:
                img = self.folder_icon
        else:
            self.tree.set(node_id, "kind", "file")
            if path.lower().endswith(".py"):
                img = self.python_file_icon
            elif path.lower().endswith(".txt") or path.lower().endswith(".csv"):
                img = self.text_file_icon
            else:
                img = self.generic_file_icon

        # compute caption
        text = os.path.basename(path)
        if text == "":  # in case of drive roots
            text = path

        self.tree.item(node_id, text=" " + text, image=img)
        self.tree.set(node_id, "path", path)

    def listdir(self, path="", include_hidden_files=False):

        if path == "" and misc_utils.running_on_windows():
            result = misc_utils.get_win_drives()
        else:
            if path == "":
                first_level = True
                path = "/"
            else:
                first_level = False
            result = [
                x
                for x in os.listdir(path)
                if include_hidden_files
                or not misc_utils.is_hidden_or_system_file(os.path.join(path, x))
            ]

            if first_level:
                result = ["/" + x for x in result]

        return sorted(result, key=str.upper)
