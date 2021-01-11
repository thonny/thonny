import ast
import os.path
import tkinter as tk
from datetime import datetime
from tkinter import ttk

from thonny import THONNY_USER_DIR, codeview, get_workbench, ui_utils
from thonny.base_file_browser import BaseLocalFileBrowser
from thonny.languages import tr
from thonny.plugins.coloring import SyntaxColorer
from thonny.ui_utils import CommonDialog, lookup_style_option


class ReplayWindow(CommonDialog):
    def __init__(self, master):
        super().__init__(master, background=lookup_style_option("TFrame", "background"))
        ui_utils.set_zoomed(self, True)

        self.main_pw = ReplayerPanedWindow(self, orient=tk.HORIZONTAL, sashwidth=10)
        self.center_pw = ReplayerPanedWindow(self.main_pw, orient=tk.VERTICAL, sashwidth=10)
        self.right_frame = ttk.Frame(self.main_pw)
        self.right_pw = ReplayerPanedWindow(self.right_frame, orient=tk.VERTICAL, sashwidth=10)
        self.editor_notebook = ReplayerEditorNotebook(self.center_pw)
        shell_book = ttk.Notebook(self.main_pw)
        self.shell = ShellFrame(shell_book)
        self.details_frame = EventDetailsFrame(self.right_pw)
        self.log_frame = LogFrame(
            self.right_pw, self.editor_notebook, self.shell, self.details_frame
        )
        self.browser = ReplayerFileBrowser(self.main_pw, self.log_frame)
        self.control_frame = ControlFrame(self.right_frame)

        self.main_pw.grid(padx=10, pady=10, sticky=tk.NSEW)
        self.main_pw.add(self.browser, width=200)
        self.main_pw.add(self.center_pw, width=1000)
        self.main_pw.add(self.right_frame, width=200)
        self.center_pw.add(self.editor_notebook, height=700)
        self.center_pw.add(shell_book, height=300)
        shell_book.add(self.shell, text="Shell")
        self.right_pw.grid(sticky=tk.NSEW)
        self.control_frame.grid(sticky=tk.NSEW)
        self.right_pw.add(self.log_frame, height=600)
        self.right_pw.add(self.details_frame, height=200)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)


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


class ControlFrame(ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master=master, **kw)

        self.toggle_button = ttk.Button(self, text="Play")
        self.speed_scale = ttk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)

        self.toggle_button.grid(row=0, column=0, sticky=tk.NSEW, pady=(10, 0), padx=(0, 5))
        self.speed_scale.grid(row=0, column=1, sticky=tk.NSEW, pady=(10, 0), padx=(5, 0))

        self.columnconfigure(1, weight=1)


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
        self.editor_notebook.reset()
        self.shell.reset()

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

    def reset(self):
        self.shell.reset()
        self.editor_notebook.reset()
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
            self.reset()
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
            # highlightthickness=0, # TODO: try different in Mac and Linux
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


class ReplayerEditor(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.code_view = ReplayerCodeView(self)
        self.code_view.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def replay_event(self, event):
        if event["sequence"] in ["TextInsert", "TextDelete"]:
            if event["sequence"] == "TextInsert":
                self.code_view.text.insert(
                    event["index"], event["text"], ast.literal_eval(event["tags"])
                )

            elif event["sequence"] == "TextDelete":
                if event["index2"] and event["index2"] != "None":
                    self.code_view.text.delete(event["index1"], event["index2"])
                else:
                    self.code_view.text.delete(event["index1"])

            self.see_event(event)

    def see_event(self, event):
        for key in ["index", "index1", "index2"]:
            if key in event and event[key] and event[key] != "None":
                self.code_view.text.see(event[key])

    def reset(self):
        self.code_view.text.delete("1.0", "end")


class ReplayerEditorProper(ReplayerEditor):
    def __init__(self, master):
        ReplayerEditor.__init__(self, master)
        self.set_colorer()

    def set_colorer(self):
        self.colorer = SyntaxColorer(self.code_view.text)

    def replay_event(self, event):
        ReplayerEditor.replay_event(self, event)
        # TODO: some problem when doing fast rewind
        # self.colorer.notify_range("1.0", "end")

    def reset(self):
        ReplayerEditor.reset(self)
        self.set_colorer()


class ReplayerEditorNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master, padding=0)
        self._editors_by_text_widget_id = {}

    def clear(self):

        for child in self.winfo_children():
            child.destroy()

        self._editors_by_text_widget_id = {}

    def get_editor_by_text_widget_id(self, text_widget_id):
        if text_widget_id not in self._editors_by_text_widget_id:
            editor = ReplayerEditorProper(self)
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

    def reset(self):
        for editor in self.winfo_children():
            self.forget(editor)
            editor.destroy()

        self._editors_by_text_widget_id = {}


class ShellFrame(ReplayerEditor):
    def __init__(self, master):
        ReplayerEditor.__init__(self, master)

        # TODO: use same source as shell
        vert_spacing = 10
        io_indent = 16
        self.code_view.text.tag_configure("toplevel", font="EditorFont")
        self.code_view.text.tag_configure("prompt", foreground="purple", font="BoldEditorFont")
        self.code_view.text.tag_configure("command", foreground="black")
        self.code_view.text.tag_configure("version", foreground="DarkGray")
        self.code_view.text.tag_configure("automagic", foreground="DarkGray")
        self.code_view.text.tag_configure(
            "value", foreground="DarkBlue"
        )  # TODO: see also _text_key_press and _text_key_release
        self.code_view.text.tag_configure("error", foreground="Red")

        self.code_view.text.tag_configure(
            "io", lmargin1=io_indent, lmargin2=io_indent, rmargin=io_indent, font="IOFont"
        )
        self.code_view.text.tag_configure("stdin", foreground="Blue")
        self.code_view.text.tag_configure("stdout", foreground="Black")
        self.code_view.text.tag_configure("stderr", foreground="Red")
        self.code_view.text.tag_configure("hyperlink", foreground="#3A66DD", underline=True)

        self.code_view.text.tag_configure("vertically_spaced", spacing1=vert_spacing)
        self.code_view.text.tag_configure("inactive", foreground="#aaaaaa")


class ReplayerPanedWindow(tk.PanedWindow):
    def __init__(self, master=None, cnf={}, **kw):
        cnf = cnf.copy()
        cnf.update(kw)
        cnf["background"] = lookup_style_option("TFrame", "background")
        super().__init__(master=master, cnf=cnf)


def load_plugin() -> None:
    def open_replayer():
        win = ReplayWindow(get_workbench())
        ui_utils.show_dialog(win)

    get_workbench().set_default("tools.replayer_last_browser_folder", None)
    if get_workbench().get_ui_mode() == "expert":
        get_workbench().add_command(
            "open_replayer", "tools", tr("Open replayer..."), open_replayer, group=110
        )
