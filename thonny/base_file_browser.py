import tkinter as tk
from tkinter import ttk
import os.path

from thonny import get_workbench, misc_utils, tktextext, get_runner
from thonny.ui_utils import scrollbar_style, lookup_style_option
from tkinter.simpledialog import askstring
from tkinter.messagebox import showerror
from thonny.common import InlineCommand, get_dirs_child_data
from copy import deepcopy
from thonny.misc_utils import running_on_windows

_dummy_node_text = "..."

TEXT_EXTENSIONS = [".py", ".pyw", ".txt", ".log", ".csv", ".json", ".yml", ".yaml"]
ROOT_NODE_ID = ""

class BaseFileBrowser(ttk.Frame):
    def __init__(self, master, show_hidden_files=False, last_folder_setting_name=None,
                 breadcrumbs_pady=(5,7)):
        self._cached_child_data = {}
        ttk.Frame.__init__(self, master, borderwidth=0, relief="flat")
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL,
                                            style=scrollbar_style("Vertical"))
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW, rowspan=3)
        
        tktextext.fixwordbreaks(tk._default_root)
        self.building_breadcrumbs = False
        self.init_header(row=0, column=0)
        
        
        spacer = ttk.Frame(self, height=1)
        spacer.grid(row=1, sticky="nsew")
        
        self.tree = ttk.Treeview(   
            self,
            columns=["#0", "kind", "path", "name", "size", "time"],
            displaycolumns=(
                #4,
                #5
                ),
            yscrollcommand=self.vert_scrollbar.set,
        )
        self.tree["show"] = "headings"
        self.tree.grid(row=2, column=0, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.show_hidden_files = show_hidden_files
        self.tree["show"] = ("tree"
                             #, "headings"
                             )
        
        self.tree.bind("<3>", self.on_secondary_click, True)
        if misc_utils.running_on_mac_os():
            self.tree.bind("<2>", self.on_secondary_click, True)
            self.tree.bind("<Control-1>", self.on_secondary_click, True)
        self.tree.bind('<Double-Button-1>', self.on_double_click, True)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)

        wb = get_workbench()
        self.folder_icon = wb.get_image("folder")
        self.python_file_icon = wb.get_image("python-file")
        self.text_file_icon = wb.get_image("text-file")
        self.generic_file_icon = wb.get_image("generic-file")
        self.hard_drive_icon = wb.get_image("hard-drive")

        self.tree.column("#0", width=200, anchor=tk.W)
        self.tree.heading("#0", text="Name")
        self.tree.column("kind", width=30, anchor=tk.W)
        self.tree.heading("kind", text="Kind")
        self.tree.column("path", width=300, anchor=tk.W)
        self.tree.heading("path", text="path")
        self.tree.column("name", width=60, anchor=tk.W)
        self.tree.heading("name", text="name")
        self.tree.column("size", width=40, anchor=tk.W)
        self.tree.heading("size", text="Size")
        self.tree.column("time", width=60, anchor=tk.W)
        self.tree.heading("time", text="Time")

        # set-up root node
        self.tree.set(ROOT_NODE_ID, "kind", "root")
        self.menu = tk.Menu(self.tree, tearoff=False)
        
        self._last_folder_setting_name = last_folder_setting_name
        self.focus_into_saved_folder()
        
    
    def init_header(self, row, column):
        header_frame = ttk.Frame(self, style="ViewToolbar.TFrame")
        header_frame.grid(row=row, column=column, sticky="nsew")
        header_frame.columnconfigure(0, weight=1)
        
        self.path_bar = tktextext.TweakableText(header_frame, borderwidth=0, relief="flat", height=1,
            font="TkDefaultFont", wrap="word", padx=6,
            pady=5, insertwidth=0,
            highlightthickness=0,
            background=lookup_style_option("ViewToolbar.TFrame", "background"))
        
        self.path_bar.grid(row=0, column=0, sticky="nsew")
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
            lineno = int(float(mouse_index))
            if lineno == 1:
                self.focus_into(ROOT_NODE_ID)
            else:
                assert lineno == 2
                dir_range = get_dir_range(event)
                if dir_range:
                    _, end_index = dir_range
                    path = self.path_bar.get("2.0", end_index)
                    if path.endswith(":"):
                        path += "\\"
                    self.focus_into(path)
        
        self.path_bar.tag_bind("dir", "<1>", dir_tag_click)
        self.path_bar.tag_bind("dir", "<Enter>", dir_tag_enter)
        self.path_bar.tag_bind("dir", "<Leave>", dir_tag_leave)
        self.path_bar.tag_bind("dir", "<Motion>", dir_tag_motion)
        
        
        #self.menu_button = ttk.Button(header_frame, text="≡ ", style="ViewToolbar.Toolbutton")
        self.menu_button = ttk.Button(header_frame, text=" ≡ ", style="ViewToolbar.Toolbutton")
        # self.menu_button.grid(row=0, column=1, sticky="ne")
        self.menu_button.place(anchor="ne", rely=0, relx=1)
    
    
    def focus_into(self, path):
        self.clear_error()
         
        # clear
        self.tree.set_children(ROOT_NODE_ID)
        
        self.tree.set(ROOT_NODE_ID, "path", path)

        self.building_breadcrumbs = True
        self.path_bar.direct_delete("1.0", "end")
        
        self.path_bar.direct_insert("1.0", self.get_root_text(), ("dir",))
        
        if path:
            self.path_bar.direct_insert("end", "\n")
            
            def create_spacer():
                return ttk.Frame(self.path_bar, height=1, width=4,
                                 style="ViewToolbar.TFrame")
            
            parts = self.split_path(path)
            for i, part in enumerate(parts):
                if i > 0:
                    if parts[i-1] != "":
                        self.path_bar.window_create("end", window=create_spacer())
                    self.path_bar.direct_insert("end", self.get_dir_separator())
                    self.path_bar.window_create("end", window=create_spacer())
                
                self.path_bar.direct_insert("end", part, tags=("dir",))
             
        self.building_breadcrumbs = False
        self.resize_path_bar()
        self.refresh_children()
        self.save_focused_folder()
    
    def split_path(self, path):
        return path.split(self.get_dir_separator())
    
    def get_root_text(self):
        return "THIS COMPUTER"
    
    def focus_into_saved_folder(self):
        if self._last_folder_setting_name:
            path = get_workbench().get_option(self._last_folder_setting_name)
            if path:
                self.focus_into(path)
                return
            
        self.focus_into("")

    def save_focused_folder(self):
        if not self._last_folder_setting_name:
            return

        path = self.get_focused_path()

        if not path:
            return

        get_workbench().set_option(self._last_folder_setting_name, path)

    def on_open_node(self, event):
        node_id = self.get_selected_node()
        path = self.tree.set(node_id, "path")
        if path: #and path not in self._cached_child_data:
            self.refresh_children(node_id)
            #self.request_dirs_child_data(node_id, [path])
        #else:
            

    def resize_path_bar(self, event=None):
        if self.building_breadcrumbs:
            return
        height = self.tk.call((self.path_bar, "count", "-update", "-displaylines", "1.0", "end"))
        self.path_bar.configure(height=height)

    def get_selected_node(self):
        nodes = self.tree.selection()
        assert len(nodes) <= 1
        if len(nodes) == 1:
            return nodes[0]
        else:
            return None
    
    def get_selected_path(self):
        return self.get_selected_value("path")
    
    def get_selected_kind(self):
        return self.get_selected_value("kind")
    
    def get_selected_value(self, key):
        node_id = self.get_selected_node()

        if node_id:
            return self.tree.set(node_id, key)
        else:
            return None
    
    def get_focused_path(self):
        path = self.tree.set(ROOT_NODE_ID, "path")
        return path

    def request_dirs_child_data(self, node_id, paths):
        raise NotImplementedError()
    
    def cache_dirs_child_data(self, data):
        data = deepcopy(data)
        
        for parent_path in data:
            children_data = data[parent_path]
            if isinstance(children_data, dict):
                for child_name in children_data:
                    child_data = children_data[child_name]
                    if child_data is None or isinstance(child_data, int):
                        # this is shortcut for simple systems
                        child_data = {"size" : child_data}
                        children_data[child_name] = child_data 
                        
                    assert isinstance(child_data, dict)
                    if "label" not in child_data:
                        child_data["label"] = child_name
                    
                    if "isdir" not in child_data:
                        child_data["isdir"] = child_data.get("size", 0) is None
            else:
                assert children_data in ("file", "missing")
        
        self._cached_child_data.update(data)    
    
    def get_open_paths(self, node_id=ROOT_NODE_ID):
        if self.tree.set(node_id, "kind") == "file":
            return set()
        
        elif node_id == ROOT_NODE_ID or self.tree.item(node_id, "open"):
            result = {self.tree.set(node_id, "path")}
            for child_id in self.tree.get_children(node_id):
                result.update(self.get_open_paths(child_id))
            return result
        
        else:
            return set()
    
    def refresh_children(self, node_id=""):
        """ This node is supposed to be a directory and 
        its contents needs to be shown and/or refreshed"""
        
        path = self.tree.set(node_id, "path")

        if path not in self._cached_child_data:
            self.request_dirs_child_data(node_id, self.get_open_paths() | {path})
            # leave it as is for now, it will be updated later
            return
        
        children_data = self._cached_child_data[path]
        
        if children_data in ["file", "missing"]:
            # path used to be a dir but is now a file or does not exist
            
            # if browser is focused into this path
            if node_id == "":
                self.show_error("Directory " + path + " does not exist anymore")
            elif children_data == "missing":
                self.tree.delete(node_id)
            else:
                assert children_data == "file"    
                self.tree.set_children(node_id) # clear the list of children
                self.tree.item(node_id, open=False)
                
        else:
            fs_children_names = children_data.keys()
            tree_children_ids = self.tree.get_children(node_id)
            
            # recollect children
            children = {}

            # first the ones, which are present already in tree
            for child_id in tree_children_ids:
                name = self.tree.set(child_id, "name")
                if name in fs_children_names:
                    children[name] = child_id
                    self.update_node_data(child_id, name, children_data[name])

            # add missing children
            for name in fs_children_names:
                if name not in children:
                    child_id = self.tree.insert(node_id, "end")
                    children[name] = child_id
                    self.tree.set(children[name], "path", self.join(path, name))
                    self.update_node_data(child_id, name, children_data[name])

            def file_order(name):
                # items in a folder should be ordered so that
                # folders come first and names are ordered case insensitively
                return (not children_data[name]["isdir"], # prefer directories
                        not ":" in name, # prefer drives
                        name.upper(), 
                        name)

            # update tree
            ids_sorted_by_name = list(
                map(
                    lambda key: children[key],
                    sorted(children.keys(), key=file_order),
                )
            )
            self.tree.set_children(node_id, *ids_sorted_by_name)

    def show_error(self, msg):
        "TODO:"
        "clear tree"
        "show message"
    
    def clear_error(self):
        "TODO:"

    def update_node_data(self, node_id, name, data):
        assert node_id != ""

        path = self.tree.set(node_id, "path")

        if data["isdir"]:
            self.tree.set(node_id, "kind", "dir")
            self.tree.set(node_id, "size", "")
            
            # Ensure that expand button is visible 
            # unless we know it doesn't have children
            children_ids = self.tree.get_children(node_id)
            if (len(children_ids) == 0 
                and (path not in self._cached_child_data
                     or self._cached_child_data[path])):
                self.tree.insert(node_id, "end", text=_dummy_node_text)
                
            if path.endswith(":") or path.endswith(":\\"):
                img = self.hard_drive_icon
            else:
                img = self.folder_icon
        else:
            self.tree.set(node_id, "kind", "file")
            self.tree.set(node_id, "size", data["size"])
            
            # Make sure it doesn't have children
            self.tree.set_children(node_id)
            
            if path.lower().endswith(".py"):
                img = self.python_file_icon
            elif path.lower().endswith(".txt") or path.lower().endswith(".csv"):
                img = self.text_file_icon
            else:
                img = self.generic_file_icon
        
        self.tree.set(node_id, "name", name)
        self.tree.item(node_id, text=" " + data["label"], image=img)
    
    
    def join(self, parent, child):
        if parent == "":
            if self.get_dir_separator() == "/":
                return "/" + child
            else:
                return child
             
        if parent.endswith(self.get_dir_separator()):
            return parent + child
        else:
            return parent + self.get_dir_separator() + child 
    
    def get_dir_separator(self):
        return os.path.sep
    
    def on_double_click(self, event):
        path = self.get_selected_path()
        kind = self.get_selected_kind()
        parts = path.split(".")
        ext = "." + parts[-1]
        if path.endswith(ext) and kind == "file" and ext.lower() in TEXT_EXTENSIONS:
            get_workbench().get_editor_notebook().show_file(path)
        elif kind == "dir":
            self.focus_into(path)
            
        return "break" 

    def on_secondary_click(self, event):
        node_id = self.tree.identify_row(event.y)

        if node_id:
            self.tree.selection_set(node_id)
            self.tree.focus(node_id)
            path = self.tree.set(node_id, "path")
            kind = self.tree.set(node_id, "kind")
            self.refresh_menu(path, kind)
            self.menu.tk_popup(event.x_root, event.y_root)
    
    def refresh_menu(self, selected_path, selected_kind):
        self.menu.delete(0, "end")
        
        self.menu.add_command(label="New file", command=self.create_new_file)
        self.menu.add_command(label="Delete", command=lambda: self.delete_path(selected_path, selected_kind))
        self.menu.add_command(label="Focus into", 
                              command=lambda: self.focus_into(selected_path),
                              state="active" if selected_kind == "dir" else "disabled")
    
    def delete_path(self, path, kind):
        print("DELETE")
    
    def create_new_file(self):
        selected_node_id = self.get_selected_node()
        
        if not selected_node_id:
            return
        
        selected_path = self.tree.set(selected_node_id, "path")
        selected_kind = self.tree.set(selected_node_id, "kind")


        if selected_kind == "dir":
            parent_path = selected_path
        else:
            parent_id = self.tree.parent(selected_node_id)
            parent_path = self.tree.set(parent_id, "path") 

        initial_name = self.get_proposed_new_file_name(parent_path, ".py")
        name = askstring(
            "File name",
            "Provide filename",
            initialvalue=initial_name,
            # selection_range=(0, len(initial_name)-3)
        )

        if not name:
            return


        path = self.join(parent_path, name)
        
        if name in self._cached_child_data[parent_path]:
            # TODO: ignore case in windows
            showerror("Error", "The file '" + path + "' already exists", parent=get_workbench())
        else:
            # Create file
            with open(path, "w"):
                pass

            self.open_path_in_browser(path, True)
        
            return path

class LocalFileBrowser(BaseFileBrowser):
    def request_dirs_child_data(self, node_id, paths):
        self.cache_dirs_child_data(get_dirs_child_data(paths))
        self.refresh_children(node_id)

    def split_path(self, path):
        parts = super().split_path(path)
        if running_on_windows() and path.startswith("\\\\"):
            # Don't split a network name!
            sep = self.get_dir_separator()
            for i in reversed(range(len(parts))):
                prefix = sep.join(parts[:i+1])
                if os.path.ismount(prefix):
                    return [prefix] + parts[i+1:]
            
            # Could not find the prefix corresponding to mount
            return [path]
        else:
            return parts
    

class BackEndFileBrowser(BaseFileBrowser):
    def __init__(self, master, show_hidden_files=False, 
                 last_folder_setting_name=None, 
                 breadcrumbs_pady=(5, 7)):
        super().__init__(master, 
                         show_hidden_files=show_hidden_files, 
                         last_folder_setting_name=last_folder_setting_name,
                         breadcrumbs_pady=breadcrumbs_pady)
        get_workbench().bind("DirectoryData", self.update_dir_data, True)
    
    def request_dirs_child_data(self, node_id, paths):
        if get_runner():
            get_runner().send_command(InlineCommand("get_child_data", node_id=node_id, paths=paths))
    
    def update_dir_data(self, msg):
        self.cache_dirs_child_data(msg["data"])
        self.refresh_children(msg["node_id"])

