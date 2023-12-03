import ast
import os.path
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from thonny import THONNY_USER_DIR, codeview, get_workbench, ui_utils
from thonny.base_file_browser import BaseLocalFileBrowser
from thonny.custom_notebook import CustomNotebook
from thonny.editors import BaseEditor
from thonny.languages import tr
from thonny.misc_utils import get_menu_char
from thonny.plugins.coloring import SyntaxColorer
from thonny.shell import BaseShellText
from thonny.ui_utils import CommonDialog, CustomToolbutton, ems_to_pixels, lookup_style_option


class ReplayWindow(CommonDialog):
    def __init__(self, master):
        super().__init__(
            master,
            background=lookup_style_option("TFrame", "background"),
            skip_tk_dialog_attributes=True,
        )
        outer_pad = ems_to_pixels(1)
        inner_pad = ems_to_pixels(1)

        ui_utils.set_zoomed(self, True)
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.grid(row=1, column=1, padx=outer_pad, pady=(outer_pad, 0), sticky=tk.NSEW)
        self.session_combo = ttk.Combobox(
            self.toolbar,
            values=[
                "Today • since 20:37",
                "Today • 16:23 • 2h 40min",
                "Yesterday • 16:23 • 2h",
                "2023-08-12 • 09:45 • 1h 15 min",
                "2023-08-11 • 09:45 • 1h 15 min",
                "2023-08-11 • 09:45 • 1h 15 min",
                "< Load another file… >",
            ],
            width=23,
            exportselection=False,
            takefocus=False,
            state="readonly",
        )
        self.session_combo.grid(column=1, row=1)

        self.play_pause_button = CustomToolbutton(self.toolbar, self.toggle_play_pause, text=" ▶ ")
        self.play_pause_button.grid(row=1, column=2, padx=(inner_pad, 0))

        self.scrubber = ttk.Scale(
            self.toolbar, from_=1, to=100, orient=tk.HORIZONTAL, takefocus=True
        )
        self.scrubber.grid(row=1, column=3, sticky="ew", padx=(inner_pad, 0))

        self.menu_button = CustomToolbutton(
            self.toolbar, self.post_menu, text=f" {get_menu_char()} "
        )
        self.menu_button.grid(row=1, column=4, padx=(inner_pad, 0))

        self.toolbar.columnconfigure(3, weight=1)

        self.main_pw = ReplayerPanedWindow(self.main_frame, orient=tk.HORIZONTAL, sashwidth=10)
        self.center_pw = ReplayerPanedWindow(self.main_pw, orient=tk.VERTICAL, sashwidth=10)
        self.right_frame = ttk.Frame(self.main_pw)
        self.right_pw = ReplayerPanedWindow(self.right_frame, orient=tk.VERTICAL, sashwidth=10)
        self.editor_notebook = ReplayerEditorNotebook(self.center_pw)
        shell_book = CustomNotebook(self.main_pw, closable=False)
        self.shell = ShellFrame(shell_book)
        self.details_frame = EventDetailsFrame(self.right_pw)

        self.log_frame = LogFrame(
            self.right_pw, self.editor_notebook, self.shell, self.details_frame
        )

        self.main_pw.grid(row=2, column=1, padx=outer_pad, pady=outer_pad, sticky=tk.NSEW)
        self.main_pw.add(self.center_pw, width=1000)
        # self.main_pw.add(self.right_frame, width=200)
        self.center_pw.add(self.editor_notebook, height=700)
        self.center_pw.add(shell_book, height=300)
        shell_book.add(self.shell, text="Shell")
        self.right_pw.grid(sticky=tk.NSEW)
        self.right_pw.add(self.log_frame, height=600)
        self.right_pw.add(self.details_frame, height=200)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.scrubber.focus_set()

    def toggle_play_pause(self) -> None:
        print("TOGGLE play pause")

    def post_menu(self) -> None:
        print("post menu")
        self.session_combo.select_clear()


class ReplayerFileBrowser(BaseLocalFileBrowser):
    def __init__(self, master, log_frame):
        super().__init__(master, True)
        self.log_frame = log_frame
        self.configure(border=1, relief=tk.GROOVE)

        user_logs_path = os.path.join(THONNY_USER_DIR, "user_logs")
        if os.path.exists(user_logs_path):
            self.focus_into(user_logs_path)
        else:
            self.focus_into(os.path.expanduser("~"))

    def on_double_click(self, event):
        # self.save_current_folder()
        path = self.get_selected_path()
        if path:
            kind = self.get_selected_kind()
            if kind == "dir":
                self.focus_into(path)
            else:
                self.log_frame.load_log(path)

        return "break"  # avoid default action of opening the node


class LogFrame(ui_utils.TreeFrame):
    def __init__(self, master, editor_book, shell, details_frame):
        ui_utils.TreeFrame.__init__(self, master, ("desc", "pause"))

        self.tree.heading("desc", text="Event", anchor=tk.W)
        self.tree.heading("pause", text="Pause (sec)", anchor=tk.W)

        self.configure(border=1, relief=tk.GROOVE)

        self.editor_notebook = editor_book
        self.shell = shell
        self.details_frame = details_frame
        self.all_events = []
        self.last_event_index = -1
        self.loading = False

    def load_log(self, filename):
        self._clear_tree()
        self.details_frame._clear_tree()
        self.all_events = []
        self.last_event_index = -1
        self.loading = True
        self.editor_notebook.clear()
        self.shell.clear()

        import json

        with open(filename, encoding="UTF-8") as f:
            events = json.load(f)
            last_event_time = None
            for event in events:
                node_id = self.tree.insert("", "end")
                self.tree.set(node_id, "desc", event["sequence"])
                if len(event["time"]) == 19:
                    # 0 fraction may have been skipped
                    event["time"] += ".0"
                event_time = datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S.%f")
                if last_event_time:
                    delta = event_time - last_event_time
                    pause = delta.seconds
                else:
                    pause = 0
                self.tree.set(node_id, "pause", str(pause if pause else ""))
                self.all_events.append(event)

                last_event_time = event_time

        self.loading = False

    def replay_event(self, event):
        "this should be called with events in correct order"
        # print("log replay", event)

        if "text_widget_id" in event:
            if (
                event.get("text_widget_context", None) == "shell"
                or event.get("text_widget_class") == "ShellText"
            ):
                self.shell.replay_event(event)
            else:
                self.editor_notebook.replay_event(event)

    def clear(self):
        self.shell.clear()
        self.editor_notebook.clear()
        self.last_event_index = -1

    def on_select(self, event):
        # parameter "event" is here tkinter event
        if self.loading:
            return
        iid = self.tree.focus()
        if iid != "":
            self.select_event(self.tree.index(iid))

    def select_event(self, event_index):
        event = self.all_events[event_index]
        self.details_frame.load_event(event)

        # here event means logged event
        if event_index > self.last_event_index:
            # replay all events between last replayed event up to and including this event
            while self.last_event_index < event_index:
                self.replay_event(self.all_events[self.last_event_index + 1])
                self.last_event_index += 1

        elif event_index < self.last_event_index:
            # Undo by resetting and replaying again
            self.clear()
            self.select_event(event_index)


class EventDetailsFrame(ui_utils.TreeFrame):
    def __init__(self, master):
        ui_utils.TreeFrame.__init__(self, master, columns=("attribute", "value"))
        self.tree.heading("attribute", text="Attribute", anchor=tk.W)
        self.tree.heading("value", text="Value", anchor=tk.W)
        self.configure(border=1, relief=tk.GROOVE)

    def load_event(self, event):
        self._clear_tree()
        for name in self.order_keys(event):
            node_id = self.tree.insert("", "end")
            self.tree.set(node_id, "attribute", name)
            self.tree.set(node_id, "value", event[name])

    def order_keys(self, event):
        return event.keys()


class ReplayerCodeView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)

        self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
        self.text = codeview.SyntaxText(
            self,
            yscrollcommand=self.vbar.set,
            xscrollcommand=self.hbar.set,
            borderwidth=0,
            font="EditorFont",
            wrap=tk.NONE,
            insertwidth=2,
            # selectborderwidth=2,
            inactiveselectbackground="gray",
            highlightthickness=0,  # TODO: try different in Mac and Linux
            # highlightcolor="gray",
            padx=5,
            pady=5,
            undo=True,
            autoseparators=False,
        )

        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        self.hbar["command"] = self.text.xview
        self.vbar["command"] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)


class ReplayerEditor(BaseEditor):
    def __init__(self, master):
        super().__init__(master, propose_remove_line_numbers=False)
        self._code_view.text.set_read_only(True)
        self.update_appearance()

    def replay_event(self, event):
        if event["sequence"] in ["TextInsert", "TextDelete"]:
            if event["sequence"] == "TextInsert":
                self._code_view.text.direct_insert(
                    event["index"], event["text"], ast.literal_eval(event["tags"])
                )

            elif event["sequence"] == "TextDelete":
                if event["index2"] and event["index2"] != "None":
                    self._code_view.text.direct_delete(event["index1"], event["index2"])
                else:
                    self._code_view.text.direct_delete(event["index1"])

            self.see_event(event)

    def see_event(self, event):
        for key in ["index", "index1", "index2"]:
            if key in event and event[key] and event[key] != "None":
                self._code_view.text.see(event[key])

    def clear(self):
        self._code_view.text.direct_delete("1.0", "end")


class ReplayerEditorNotebook(CustomNotebook):
    def __init__(self, master):
        CustomNotebook.__init__(self, master, closable=False)
        self._editors_by_text_widget_id = {}

    def clear(self):
        for child in self.winfo_children():
            child.destroy()

        self._editors_by_text_widget_id = {}

    def get_editor_by_text_widget_id(self, text_widget_id):
        if text_widget_id not in self._editors_by_text_widget_id:
            editor = ReplayerEditor(self)
            self.add(editor, text="<untitled>")
            self._editors_by_text_widget_id[text_widget_id] = editor

        return self._editors_by_text_widget_id[text_widget_id]

    def replay_event(self, event):
        if "text_widget_id" in event:
            editor = self.get_editor_by_text_widget_id(event["text_widget_id"])
            # print(event.editor_id, id(editor), event)
            self.select(editor)
            editor.replay_event(event)

            if "filename" in event:
                self.tab(editor, text=os.path.basename(event["filename"]))

    def clear(self):
        for editor in self.winfo_children():
            self.forget(editor)
            editor.destroy()

        self._editors_by_text_widget_id = {}


class ShellFrame(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=1, column=2, sticky=tk.NSEW)

        self.text = BaseShellText(
            self,
            self,
            font="EditorFont",
            # foreground="white",
            # background="#666666",
            highlightthickness=0,
            # highlightcolor="LightBlue",
            borderwidth=0,
            yscrollcommand=self.set_scrollbar,
            padx=0,
            pady=0,
            insertwidth=2,
            height=10,
            undo=True,
        )

        self.text.grid(row=1, column=1, sticky=tk.NSEW)
        self.vert_scrollbar["command"] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

    def set_scrollbar(self, *args):
        self.vert_scrollbar.set(*args)

    def clear(self):
        self.text.direct_delete("1.0", "end")

    def replay_event(self, event):
        if event["sequence"] in ["TextInsert", "TextDelete"]:
            if event["sequence"] == "TextInsert":
                self.text.direct_insert(
                    event["index"], event["text"], ast.literal_eval(event["tags"])
                )

            elif event["sequence"] == "TextDelete":
                if event["index2"] and event["index2"] != "None":
                    self.text.direct_delete(event["index1"], event["index2"])
                else:
                    self.text.direct_delete(event["index1"])

            self.see_event(event)

    def see_event(self, event):
        for key in ["index", "index1", "index2"]:
            if key in event and event[key] and event[key] != "None":
                self.text.see(event[key])


class ReplayerPanedWindow(tk.PanedWindow):
    def __init__(self, master=None, cnf={}, **kw):
        cnf = cnf.copy()
        cnf.update(kw)
        cnf["background"] = lookup_style_option("TFrame", "background")
        super().__init__(master=master, cnf=cnf)


def open_replayer():
    win = ReplayWindow(get_workbench())
    ui_utils.show_dialog(win, modal=False)


def load_plugin() -> None:
    get_workbench().set_default("tools.replayer_last_browser_folder", None)
    get_workbench().add_command(
        "open_replayer", "tools", tr("Open replayer..."), open_replayer, group=110
    )
