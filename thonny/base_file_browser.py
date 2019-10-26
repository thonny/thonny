import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os.path

from thonny import get_workbench, misc_utils, tktextext, get_runner
from thonny.ui_utils import (
    scrollbar_style,
    lookup_style_option,
    show_dialog,
    create_string_var,
    CommonDialog,
)
from tkinter.simpledialog import askstring
from thonny.common import InlineCommand, get_dirs_child_data
from copy import deepcopy
from thonny.misc_utils import running_on_windows, sizeof_fmt
import datetime
import shutil

_dummy_node_text = "..."

LOCAL_FILES_ROOT_TEXT = ""  # needs to be initialized later
TEXT_EXTENSIONS = [".py", ".pyw", ".txt", ".log", ".csv", ".json", ".yml", ".yaml"]
ROOT_NODE_ID = ""


class BaseFileBrowser(ttk.Frame):
    def __init__(self, master, show_hidden_files=False, show_expand_buttons=True):
        global LOCAL_FILES_ROOT_TEXT
        LOCAL_FILES_ROOT_TEXT = _("This computer")

        self.show_expand_buttons = show_expand_buttons
        self._cached_child_data = {}
        self.path_to_highlight = None

        ttk.Frame.__init__(self, master, borderwidth=0, relief="flat")
        self.vert_scrollbar = ttk.Scrollbar(
            self, orient=tk.VERTICAL, style=scrollbar_style("Vertical")
        )
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW, rowspan=3)

        tktextext.fixwordbreaks(tk._default_root)
        self.building_breadcrumbs = False
        self.init_header(row=0, column=0)

        spacer = ttk.Frame(self, height=1)
        spacer.grid(row=1, sticky="nsew")

        self.tree = ttk.Treeview(
            self,
            columns=["#0", "kind", "path", "name", "time", "size"],
            displaycolumns=(
                # 4,
                # 5
            ),
            yscrollcommand=self.vert_scrollbar.set,
            selectmode="extended",
        )
        self.tree.grid(row=2, column=0, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self.show_hidden_files = show_hidden_files
        self.tree["show"] = "tree"

        self.tree.bind("<3>", self.on_secondary_click, True)
        if misc_utils.running_on_mac_os():
            self.tree.bind("<2>", self.on_secondary_click, True)
            self.tree.bind("<Control-1>", self.on_secondary_click, True)
        self.tree.bind("<Double-Button-1>", self.on_double_click, True)
        self.tree.bind("<<TreeviewOpen>>", self.on_open_node)

        wb = get_workbench()
        self.folder_icon = wb.get_image("folder")
        self.python_file_icon = wb.get_image("python-file")
        self.text_file_icon = wb.get_image("text-file")
        self.generic_file_icon = wb.get_image("generic-file")
        self.hard_drive_icon = wb.get_image("hard-drive")

        self.tree.column("#0", width=200, anchor=tk.W)
        self.tree.heading("#0", text="Name", anchor=tk.W)
        self.tree.column("time", width=60, anchor=tk.W)
        self.tree.heading("time", text="Time", anchor=tk.W)
        self.tree.column("size", width=40, anchor=tk.E)
        self.tree.heading("size", text="Size (bytes)", anchor=tk.E)
        self.tree.column("kind", width=30, anchor=tk.W)
        #         self.tree.heading("kind", text="Kind")
        #         self.tree.column("path", width=300, anchor=tk.W)
        #         self.tree.heading("path", text="path")
        #         self.tree.column("name", width=60, anchor=tk.W)
        #         self.tree.heading("name", text="name")

        # set-up root node
        self.tree.set(ROOT_NODE_ID, "kind", "root")
        self.menu = tk.Menu(self.tree, tearoff=False)
        self.current_focus = None

    def init_header(self, row, column):
        header_frame = ttk.Frame(self, style="ViewToolbar.TFrame")
        header_frame.grid(row=row, column=column, sticky="nsew")
        header_frame.columnconfigure(0, weight=1)

        self.path_bar = tktextext.TweakableText(
            header_frame,
            borderwidth=0,
            relief="flat",
            height=1,
            font="TkDefaultFont",
            wrap="word",
            padx=6,
            pady=5,
            insertwidth=0,
            highlightthickness=0,
            background=lookup_style_option("ViewToolbar.TFrame", "background"),
        )

        self.path_bar.grid(row=0, column=0, sticky="nsew")
        self.path_bar.set_read_only(True)
        self.path_bar.bind("<Configure>", self.resize_path_bar, True)
        self.path_bar.tag_configure(
            "dir", foreground=lookup_style_option("Url.TLabel", "foreground")
        )
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
                self.request_focus_into("")
            else:
                assert lineno == 2
                dir_range = get_dir_range(event)
                if dir_range:
                    _, end_index = dir_range
                    path = self.path_bar.get("2.0", end_index)
                    if path.endswith(":"):
                        path += "\\"
                    self.request_focus_into(path)

        self.path_bar.tag_bind("dir", "<1>", dir_tag_click)
        self.path_bar.tag_bind("dir", "<Enter>", dir_tag_enter)
        self.path_bar.tag_bind("dir", "<Leave>", dir_tag_leave)
        self.path_bar.tag_bind("dir", "<Motion>", dir_tag_motion)

        # self.menu_button = ttk.Button(header_frame, text="≡ ", style="ViewToolbar.Toolbutton")
        self.menu_button = ttk.Button(
            header_frame, text=" ≡ ", style="ViewToolbar.Toolbutton", command=self.post_button_menu
        )
        # self.menu_button.grid(row=0, column=1, sticky="ne")
        self.menu_button.place(anchor="ne", rely=0, relx=1)

    def clear(self):
        self.clear_error()
        self.invalidate_cache()
        self.path_bar.direct_delete("1.0", "end")
        self.tree.set_children("")
        self.current_focus = None

    def request_focus_into(self, path):
        return self.focus_into(path)

    def focus_into(self, path):
        self.clear_error()

        # clear
        self.tree.set_children(ROOT_NODE_ID)

        self.tree.set(ROOT_NODE_ID, "path", path)

        self.building_breadcrumbs = True
        self.path_bar.direct_delete("1.0", "end")

        self.path_bar.direct_insert("1.0", self.get_root_text(), ("dir",))

        if path and path != "/":
            self.path_bar.direct_insert("end", "\n")

            def create_spacer():
                return ttk.Frame(self.path_bar, height=1, width=4, style="ViewToolbar.TFrame")

            parts = self.split_path(path)
            for i, part in enumerate(parts):
                if i > 0:
                    if parts[i - 1] != "":
                        self.path_bar.window_create("end", window=create_spacer())
                    self.path_bar.direct_insert("end", self.get_dir_separator())
                    self.path_bar.window_create("end", window=create_spacer())

                self.path_bar.direct_insert("end", part, tags=("dir",))

        self.building_breadcrumbs = False
        self.resize_path_bar()
        self.render_children_from_cache()
        self.current_focus = path

    def split_path(self, path):
        return path.split(self.get_dir_separator())

    def get_root_text(self):
        return LOCAL_FILES_ROOT_TEXT

    def on_open_node(self, event):
        node_id = self.get_selected_node()
        path = self.tree.set(node_id, "path")
        if path:  # and path not in self._cached_child_data:
            self.render_children_from_cache(node_id)
            # self.request_dirs_child_data(node_id, [path])
        # else:

    def resize_path_bar(self, event=None):
        if self.building_breadcrumbs:
            return
        height = self.tk.call((self.path_bar, "count", "-update", "-displaylines", "1.0", "end"))
        self.path_bar.configure(height=height)

    def get_selected_node(self):
        """Returns single node (or nothing)"""
        nodes = self.tree.selection()
        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) > 1:
            return self.tree.focus() or None
        else:
            return None

    def get_selected_nodes(self, notify_if_empty=False):
        """Can return several nodes"""
        result = self.tree.selection()
        if not result and notify_if_empty:
            self.notify_missing_selection()
        return result

    def get_selection_info(self, notify_if_empty=False):
        nodes = self.get_selected_nodes(notify_if_empty)
        if not nodes:
            return None
        elif len(nodes) == 1:
            description = "'" + self.tree.set(nodes[0], "name") + "'"
        else:
            description = _("%d items") % len(nodes)

        paths = [self.tree.set(node, "path") for node in nodes]
        kinds = [self.tree.set(node, "kind") for node in nodes]

        return {"description": description, "nodes": nodes, "paths": paths, "kinds": kinds}

    def get_selected_path(self):
        return self.get_selected_value("path")

    def get_selected_kind(self):
        return self.get_selected_value("kind")

    def get_selected_name(self):
        return self.get_selected_value("name")

    def get_selected_value(self, key):
        node_id = self.get_selected_node()

        if node_id:
            return self.tree.set(node_id, key)
        else:
            return None

    def get_active_directory(self):
        path = self.tree.set(ROOT_NODE_ID, "path")
        return path

    def request_dirs_child_data(self, node_id, paths):
        raise NotImplementedError()

    def show_fs_info(self):
        path = self.get_selected_path()
        if path is None:
            path = self.current_focus
        self.request_fs_info(path)

    def request_fs_info(self, path):
        raise NotImplementedError()

    def present_fs_info(self, info):
        total_str = "?" if info["total"] is None else sizeof_fmt(info["total"])
        used_str = "?" if info["used"] is None else sizeof_fmt(info["used"])
        free_str = "?" if info["free"] is None else sizeof_fmt(info["free"])
        text = (
            "Storage space on this drive or filesystem:\n\n"
            "    total: %s\n" % total_str
            + "    used: %s\n" % used_str
            + "    free: %s\n" % free_str
        )

        if info.get("comment"):
            text += "\n" + info["comment"]

        messagebox.showinfo("Storage info", text)

    def cache_dirs_child_data(self, data):
        data = deepcopy(data)

        for parent_path in data:
            children_data = data[parent_path]
            if isinstance(children_data, dict):
                for child_name in children_data:
                    child_data = children_data[child_name]
                    assert isinstance(child_data, dict)
                    if "label" not in child_data:
                        child_data["label"] = child_name

                    if "isdir" not in child_data:
                        child_data["isdir"] = child_data.get("size", 0) is None
            else:
                assert children_data is None

        self._cached_child_data.update(data)

    def file_exists_in_cache(self, path):
        for parent_path in self._cached_child_data:
            # hard to split because it may not be in this system format
            name = path[len(parent_path) :]
            if name[0:1] in ["/", "\\"]:
                name = name[1:]

            if name in self._cached_child_data[parent_path]:
                return True

        return False

    def select_path_if_visible(self, path, node_id=""):
        for child_id in self.tree.get_children(node_id):
            if self.tree.set(child_id, "path") == path:
                self.tree.selection_set(child_id)
                return

            if self.tree.item(child_id, "open"):
                self.select_path_if_visible(path, child_id)

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

    def invalidate_cache(self, paths=None):
        if paths is None:
            self._cached_child_data.clear()
        else:
            for path in paths:
                if path in self._cached_child_data:
                    del self._cached_child_data[path]

    def render_children_from_cache(self, node_id=""):
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
                self.show_error("Directory " + path + " does not exist anymore", node_id)
            elif children_data == "missing":
                self.tree.delete(node_id)
            else:
                assert children_data == "file"
                self.tree.set_children(node_id)  # clear the list of children
                self.tree.item(node_id, open=False)

        elif children_data is None:
            raise RuntimeError("None data for %s" % path)
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
                return (
                    not children_data[name]["isdir"],  # prefer directories
                    not ":" in name,  # prefer drives
                    name.upper(),
                    name,
                )

            # update tree
            ids_sorted_by_name = list(
                map(lambda key: children[key], sorted(children.keys(), key=file_order))
            )
            self.tree.set_children(node_id, *ids_sorted_by_name)

            # recursively update open children
            for child_id in ids_sorted_by_name:
                if self.tree.item(child_id, "open"):
                    self.render_children_from_cache(child_id)

    def show_error(self, msg, node_id=""):
        if not node_id:
            # clear tree
            self.tree.set_children("")

        err_id = self.tree.insert(node_id, "end")
        self.tree.item(err_id, text=msg)
        self.tree.set_children(node_id, err_id)

    def clear_error(self):
        "TODO:"

    def update_node_data(self, node_id, name, data):
        assert node_id != ""

        path = self.tree.set(node_id, "path")

        if data.get("time"):
            try:
                dtime = datetime.datetime.fromtimestamp(int(data["time"]))
            except Exception:
                time_str = ""
            else:
                time_str = dtime.isoformat().replace("T", " ")
        else:
            time_str = ""

        self.tree.set(node_id, "time", time_str)

        if data["isdir"]:
            self.tree.set(node_id, "kind", "dir")
            self.tree.set(node_id, "size", "")

            # Ensure that expand button is visible
            # unless we know it doesn't have children
            children_ids = self.tree.get_children(node_id)
            if (
                self.show_expand_buttons
                and len(children_ids) == 0
                and (path not in self._cached_child_data or self._cached_child_data[path])
            ):
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
            self.open_file(path)
        elif kind == "dir":
            self.request_focus_into(path)

        return "break"

    def open_file(self, path):
        pass

    def on_secondary_click(self, event):
        node_id = self.tree.identify_row(event.y)

        if node_id:
            if node_id not in self.tree.selection():
                # replace current selection
                self.tree.selection_set(node_id)
            self.tree.focus(node_id)
        else:
            self.tree.selection_set()
            self.path_bar.focus_set()

        self.tree.update()

        self.refresh_menu()
        self.menu.tk_popup(event.x_root, event.y_root)

    def post_button_menu(self):
        self.refresh_menu()
        self.menu.tk_popup(
            self.menu_button.winfo_rootx(),
            self.menu_button.winfo_rooty() + self.menu_button.winfo_height(),
        )

    def refresh_menu(self):
        self.menu.delete(0, "end")
        self.add_first_menu_items()
        self.menu.add_separator()
        self.add_middle_menu_items()
        self.menu.add_separator()
        self.add_last_menu_items()

    def add_first_menu_items(self):
        selected_path = self.get_selected_path()
        selected_kind = self.get_selected_kind()

        self.menu.add_command(label=_("Refresh"), command=self.cmd_refresh_tree)

        if selected_kind == "dir":
            self.menu.add_command(
                label=_("Focus into"), command=lambda: self.request_focus_into(selected_path)
            )
        else:
            "TODO: add open command"

    def cmd_refresh_tree(self):
        self.refresh_tree()

    def add_middle_menu_items(self):
        if self.supports_trash():
            if running_on_windows():
                trash_label = _("Move to Recycle Bin")
            else:
                trash_label = _("Move to Trash")
            self.menu.add_command(label=trash_label, command=self.move_to_trash)
        else:
            self.menu.add_command(label=_("Delete"), command=self.delete)

        if self.supports_directories():
            self.menu.add_command(label=_("New directory") + "...", command=self.mkdir)

    def add_last_menu_items(self):
        self.menu.add_command(label=_("Properties"), command=self.show_properties)
        self.menu.add_command(label=_("Storage space"), command=self.show_fs_info)

    def show_properties(self):
        node_id = self.get_selected_node()
        if node_id is None:
            self.notify_missing_selection()
            return

        values = self.tree.set(node_id)

        text = _("Path") + ":\n    " + values["path"] + "\n\n"
        if values["kind"] == "dir":
            title = _("Directory properties")
        else:
            title = _("File properties")
            size_fmt_str = sizeof_fmt(int(values["size"]))
            bytes_str = str(values["size"]) + " " + _("bytes")

            text += (
                _("Size")
                + ":\n    "
                + (
                    bytes_str
                    if size_fmt_str.endswith(" B")
                    else size_fmt_str + "  (" + bytes_str + ")"
                )
                + "\n\n"
            )

        if values["time"].strip():
            text += _("Modified") + ":\n    " + values["time"] + "\n\n"

        messagebox.showinfo(title, text.strip())

    def refresh_tree(self, paths_to_invalidate=None):
        self.invalidate_cache(paths_to_invalidate)
        if self.winfo_ismapped():
            self.render_children_from_cache("")

        if self.path_to_highlight:
            self.select_path_if_visible(self.path_to_highlight)
            self.path_to_highlight = None

    def create_new_file(self):
        selected_node_id = self.get_selected_node()

        if selected_node_id:
            selected_path = self.tree.set(selected_node_id, "path")
            selected_kind = self.tree.set(selected_node_id, "kind")

            if selected_kind == "dir":
                parent_path = selected_path
            else:
                parent_id = self.tree.parent(selected_node_id)
                parent_path = self.tree.set(parent_id, "path")
        else:
            parent_path = self.current_focus

        name = askstring("File name", "Provide filename", initialvalue="")

        if not name:
            return

        path = self.join(parent_path, name)

        if name in self._cached_child_data[parent_path]:
            # TODO: ignore case in windows
            messagebox.showerror("Error", "The file '" + path + "' already exists")
        else:
            self.open_file(path)

    def delete(self):
        selection = self.get_selection_info(True)
        if not selection:
            return

        confirmation = "Are you sure want to delete %s?" % selection["description"]
        confirmation += "\n\nNB! Recycle bin won't be used (no way to undelete)!"
        if "dir" in selection["kinds"]:
            confirmation += "\n" + "Directories will be deleted with content."

        if not messagebox.askyesno("Are you sure?", confirmation):
            return

        self.perform_delete(selection["paths"], _("Deleting %s") % selection["description"])
        self.refresh_tree()

    def move_to_trash(self):
        assert self.supports_trash()

        selection = self.get_selection_info(True)
        if not selection:
            return

        trash = "Recycle Bin" if running_on_windows() else "Trash"
        if not messagebox.askokcancel(
            "Moving to %s" % trash,
            "I'll try to move %s to %s,\n" % (selection["description"], trash)
            + "but my method is not always reliable —\n"
            + "in some cases the files will be deleted\n"
            + "without the possibility to restore.",
            icon="info",
        ):
            return

        self.perform_move_to_trash(
            selection["paths"], _("Moving %s to %s") % (selection["description"], trash)
        )
        self.refresh_tree()

    def supports_trash(self):
        return False

    def mkdir(self):
        parent = self.get_selected_path()
        if parent is None:
            parent = self.current_focus
        else:
            if self.get_selected_kind() == "file":
                # dirname does the right thing even if parent is Linux path and runnning on Windows
                parent = os.path.dirname(parent)

        name = simpledialog.askstring(
            "New directory", "Enter name for new directory under\n%s" % parent
        )
        if not name or not name.strip():
            return

        self.perform_mkdir(parent, name.strip())
        self.refresh_tree()

    def perform_delete(self, paths, description):
        raise NotImplementedError()

    def perform_move_to_trash(self, paths, description):
        raise NotImplementedError()

    def supports_directories(self):
        return True

    def perform_mkdir(self, parent_dir, name):
        raise NotImplementedError()

    def notify_missing_selection(self):
        messagebox.showerror("Nothing selected", "Select an item and try again!")


class BaseLocalFileBrowser(BaseFileBrowser):
    def __init__(self, master, show_hidden_files=False, show_expand_buttons=True):
        super().__init__(
            master, show_hidden_files=show_hidden_files, show_expand_buttons=show_expand_buttons
        )
        get_workbench().bind("WindowFocusIn", self.on_window_focus_in, True)
        get_workbench().bind("LocalFileOperation", self.on_local_file_operation, True)

    def destroy(self):
        super().destroy()
        get_workbench().unbind("WindowFocusIn", self.on_window_focus_in)
        get_workbench().unbind("LocalFileOperation", self.on_local_file_operation)

    def request_dirs_child_data(self, node_id, paths):
        self.cache_dirs_child_data(get_dirs_child_data(paths))
        self.render_children_from_cache(node_id)

    def split_path(self, path):
        parts = super().split_path(path)
        if running_on_windows() and path.startswith("\\\\"):
            # Don't split a network name!
            sep = self.get_dir_separator()
            for i in reversed(range(len(parts))):
                prefix = sep.join(parts[: i + 1])
                if os.path.ismount(prefix):
                    return [prefix] + parts[i + 1 :]

            # Could not find the prefix corresponding to mount
            return [path]
        else:
            return parts

    def open_file(self, path):
        get_workbench().get_editor_notebook().show_file(path)

    def on_window_focus_in(self, event=None):
        self.refresh_tree()

    def on_local_file_operation(self, event):
        if event["operation"] in ["save", "delete"]:
            self.refresh_tree()
            self.select_path_if_visible(event["path"])
            # TODO: select this file in tree?

    def request_fs_info(self, path):
        if path == "":
            self.notify_missing_selection()
        else:
            if not os.path.isdir(path):
                path = os.path.dirname(path)

            self.present_fs_info(shutil.disk_usage(path)._asdict())

    def perform_delete(self, paths, description):
        # Deprecated. moving to trash should be used instead
        raise NotImplementedError()
        """
        for path in sorted(paths, key=len, reverse=True):
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
        """

    def perform_move_to_trash(self, paths, description):
        # TODO: do it with subprocess dialog
        import send2trash

        for path in paths:
            send2trash.send2trash(path)

    def perform_mkdir(self, parent_dir, name):
        os.mkdir(os.path.join(parent_dir, name), mode=0o700)

    def supports_trash(self):
        try:
            import send2trash  # @UnusedImport

            return True
        except ImportError:
            return False


class BaseRemoteFileBrowser(BaseFileBrowser):
    def __init__(self, master, show_hidden_files=False, show_expand_buttons=True):
        super().__init__(
            master, show_hidden_files=show_hidden_files, show_expand_buttons=show_expand_buttons
        )
        self.dir_separator = "/"

        get_workbench().bind("get_dirs_child_data_response", self.update_dir_data, True)
        get_workbench().bind("get_fs_info_response", self.present_fs_info, True)
        get_workbench().bind("RemoteFileOperation", self.on_remote_file_operation, True)

    def destroy(self):
        super().destroy()
        get_workbench().unbind("get_dirs_child_data_response", self.update_dir_data)
        get_workbench().unbind("get_fs_info_response", self.present_fs_info)
        get_workbench().unbind("RemoteFileOperation", self.on_remote_file_operation)

    def get_root_text(self):
        runner = get_runner()
        if runner:
            return runner.get_node_label()

        return "Back-end"

    def request_dirs_child_data(self, node_id, paths):
        if get_runner():
            get_runner().send_command(
                InlineCommand("get_dirs_child_data", node_id=node_id, paths=paths)
            )

    def request_fs_info(self, path):
        if get_runner():
            get_runner().send_command(InlineCommand("get_fs_info", path=path))

    def get_dir_separator(self):
        return self.dir_separator

    def update_dir_data(self, msg):
        if msg.get("error"):
            self.show_error(msg["error"])
        else:
            self.dir_separator = msg["dir_separator"]
            self.cache_dirs_child_data(msg["data"])
            self.render_children_from_cache(msg["node_id"])

        if self.path_to_highlight:
            self.select_path_if_visible(self.path_to_highlight)
            self.path_to_highlight = None

    def open_file(self, path):
        get_workbench().get_editor_notebook().show_remote_file(path)

    def supports_directories(self):
        runner = get_runner()
        if not runner:
            return False
        proxy = runner.get_backend_proxy()
        if not proxy:
            return False
        return proxy.supports_remote_directories()

    def on_remote_file_operation(self, event):
        path = event["path"]
        exists_in_cache = self.file_exists_in_cache(path)
        if (
            event["operation"] == "save"
            and exists_in_cache
            or event["operation"] == "delete"
            and not exists_in_cache
        ):
            # No need to refresh
            return

        if "/" in path:
            parent = path[: path.rfind("/")]
            if not parent:
                parent = "/"
        else:
            parent = ""

        self.refresh_tree([parent])
        self.path_to_highlight = path

    def perform_delete(self, paths, description):
        get_runner().send_command(
            InlineCommand("delete", paths=paths, blocking=True, description=description)
        )

    def perform_mkdir(self, parent_dir, name):
        get_runner().send_command(
            InlineCommand("mkdir", path=parent_dir + self.get_dir_separator() + name)
        )

    def supports_trash(self):
        return get_runner().get_backend_proxy().supports_trash()

    def request_focus_into(self, path):
        if not get_runner().ready_for_remote_file_operations(show_message=True):
            return False

        super().request_focus_into(path)

        if not get_runner().supports_remote_directories():
            assert path == ""
            self.focus_into(path)
        elif self.current_focus == path:
            # refreshes
            self.focus_into(path)
        else:
            self.request_new_focus(path)

    def request_new_focus(self, path):
        # Overridden in active browser
        self.focus_into(path)

    def cmd_refresh_tree(self):
        if not get_runner().ready_for_remote_file_operations(show_message=True):
            return

        super().cmd_refresh_tree()


class DialogRemoteFileBrowser(BaseRemoteFileBrowser):
    def __init__(self, master, dialog):
        super().__init__(master, show_expand_buttons=False)

        self.dialog = dialog
        self.tree["show"] = ("tree", "headings")
        self.tree.configure(displaycolumns=(5,))
        self.tree.configure(height=10)

    def open_file(self, path):
        self.dialog.double_click_file(path)


class BackendFileDialog(CommonDialog):
    def __init__(self, master, kind, initial_dir):
        super().__init__(master=master)
        self.result = None

        self.updating_selection = False

        self.kind = kind
        if kind == "open":
            self.title("Open from " + get_runner().get_node_label())
        else:
            assert kind == "save"
            self.title("Save to " + get_runner().get_node_label())

        background = ttk.Frame(self)
        background.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.browser = DialogRemoteFileBrowser(background, self)
        self.browser.grid(row=0, column=0, columnspan=4, sticky="nsew", pady=20, padx=20)
        self.browser.configure(borderwidth=1, relief="groove")
        self.browser.tree.configure(selectmode="browse")

        self.name_label = ttk.Label(background, text="File name:")
        self.name_label.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="w")

        self.name_var = create_string_var("")
        self.name_entry = ttk.Entry(
            background, textvariable=self.name_var, state="normal" if kind == "save" else "disabled"
        )
        self.name_entry.grid(row=1, column=1, pady=(0, 20), padx=(0, 20), sticky="we")
        self.name_entry.bind("<KeyRelease>", self.on_name_edit, True)

        self.ok_button = ttk.Button(background, text="OK", command=self.on_ok)
        self.ok_button.grid(row=1, column=2, pady=(0, 20), padx=(0, 20), sticky="e")

        self.cancel_button = ttk.Button(background, text="Cancel", command=self.on_cancel)
        self.cancel_button.grid(row=1, column=3, pady=(0, 20), padx=(0, 20), sticky="e")

        background.rowconfigure(0, weight=1)
        background.columnconfigure(1, weight=1)

        self.bind("<Escape>", self.on_cancel, True)
        self.bind("<Return>", self.on_ok, True)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        self.tree_select_handler_id = self.browser.tree.bind(
            "<<TreeviewSelect>>", self.on_tree_select, True
        )

        self.browser.request_focus_into(initial_dir)

    def on_ok(self, event=None):
        tree = self.browser.tree
        name = self.name_var.get()

        for node_id in tree.get_children(""):
            if name == tree.set(node_id, "name"):
                break
        else:
            node_id = None

        if node_id is not None:
            node_kind = tree.set(node_id, "kind")
            if node_kind != "file":
                messagebox.showerror(_("Error"), _("You need to select a file!"))
                return
            elif self.kind == "save":
                if not messagebox.askyesno(
                    _("Overwrite?"), _("Do you want to overwrite '%s' ?") % name
                ):
                    return

        parent_path = tree.set("", "path")
        if parent_path == "" or parent_path.endswith("/"):
            self.result = parent_path + name
        else:
            self.result = parent_path + "/" + name

        self.destroy()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()

    def on_tree_select(self, event=None):
        if self.updating_selection:
            return

        if self.browser.get_selected_kind() == "file":
            name = self.browser.get_selected_name()
            if name:
                self.name_var.set(name)

    def on_name_edit(self, event=None):
        self.updating_selection = True
        tree = self.browser.tree
        if self.tree_select_handler_id:
            tree.unbind("<<TreeviewSelect>>", self.tree_select_handler_id)
            self.tree_select_handler_id = None

        name = self.name_var.get()
        for node_id in tree.get_children(""):
            if name == tree.set(node_id, "name"):
                tree.selection_add(node_id)
            else:
                tree.selection_remove(node_id)

        self.updating_selection = False
        self.tree_select_handler_id = tree.bind("<<TreeviewSelect>>", self.on_tree_select, True)

    def double_click_file(self, path):
        assert path.endswith(self.name_var.get())
        self.on_ok()


class NodeChoiceDialog(CommonDialog):
    def __init__(self, master, prompt):
        super().__init__(master=master)
        self.result = None

        self.title(prompt)

        background = ttk.Frame(self)
        background.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        local_caption = LOCAL_FILES_ROOT_TEXT
        remote_caption = get_runner().get_node_label()

        button_width = max(len(local_caption), len(remote_caption)) + 10

        self.local_button = ttk.Button(
            background,
            text=" \n" + local_caption + "\n ",
            width=button_width,
            command=self.on_local,
        )
        self.local_button.grid(row=0, column=0, pady=20, padx=20)

        self.remote_button = ttk.Button(
            background,
            text=" \n" + remote_caption + "\n ",
            width=button_width,
            command=self.on_remote,
        )
        self.remote_button.grid(row=1, column=0, pady=(0, 20), padx=20)

        self.local_button.focus_set()

        self.bind("<Escape>", self.on_cancel, True)
        self.bind("<Return>", self.on_return, True)
        self.bind("<Down>", self.on_down, True)
        self.bind("<Up>", self.on_up, True)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

    def on_local(self, event=None):
        self.result = "local"
        self.destroy()

    def on_remote(self, event=None):
        self.result = "remote"
        self.destroy()

    def on_return(self, event=None):
        if self.focus_get() == self.local_button:
            return self.on_local(event)
        elif self.focus_get() == self.remote_button:
            return self.on_remote(event)

    def on_down(self, event=None):
        if self.focus_get() == self.local_button:
            self.remote_button.focus_set()

    def on_up(self, event=None):
        if self.focus_get() == self.remote_button:
            self.local_button.focus_set()

    def on_cancel(self, event=None):
        self.result = None
        self.destroy()


def ask_backend_path(master, dialog_kind):
    proxy = get_runner().get_backend_proxy()
    if not proxy:
        return None

    assert proxy.supports_remote_files()

    dlg = BackendFileDialog(master, dialog_kind, proxy.get_cwd())
    show_dialog(dlg, master)
    return dlg.result


def choose_node_for_file_operations(master, prompt):
    if get_runner().supports_remote_files():
        dlg = NodeChoiceDialog(master, prompt)
        show_dialog(dlg, master)
        if dlg.result == "remote" and not get_runner().ready_for_remote_file_operations(
            show_message=True
        ):
            return None
        return dlg.result
    else:
        return "local"
