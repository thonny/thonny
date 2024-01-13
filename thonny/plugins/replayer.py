import ast
import datetime
import os.path
import time
import tkinter as tk
from dataclasses import dataclass
from logging import getLogger
from tkinter import ttk
from typing import Callable, Dict, List, Optional

from thonny import codeview, get_workbench, ui_utils
from thonny.custom_notebook import CustomNotebook
from thonny.editors import BaseEditor
from thonny.languages import tr
from thonny.misc_utils import get_menu_char, running_on_mac_os
from thonny.shell import BaseShellText
from thonny.ui_utils import (
    CommonDialog,
    CustomToolbutton,
    MappingCombobox,
    askopenfilename,
    ems_to_pixels,
    lookup_style_option,
    select_sequence,
    sequence_to_accelerator,
)

KEY_EVENTS = ["ToplevelResponse"]

FILE_TOKEN = "file://"

logger = getLogger(__name__)
_REPLAYER = None

CURRENT_SESSION_VALUE = "__CURRENT_SESSION__"

_dialog_filetypes = [(tr("Event logs"), ".jsonl .gz"), (tr("all files"), ".*")]


class ReplayWindow(CommonDialog):
    def __init__(self, master):
        self.events = None
        self.last_event_index = -1
        self.loading = False
        self.commands: List[ReplayerCommand] = []
        self._scrubbing_after_id = None

        super().__init__(
            master,
            background=lookup_style_option("TFrame", "background"),
            skip_tk_dialog_attributes=True,
        )
        outer_pad = ems_to_pixels(1)
        inner_pad = ems_to_pixels(1)

        self.menu = tk.Menu(self)
        load_from_file_sequence = select_sequence("<Control-o>", "<Command-o>")
        self.menu.add_command(
            label=tr("Load events from file"),
            command=self.cmd_open,
            accelerator=sequence_to_accelerator(load_from_file_sequence),
        )
        self.bind(load_from_file_sequence, self.cmd_open, True)

        ui_utils.set_zoomed(self, True)
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.rowconfigure(2, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.grid(row=1, column=1, padx=outer_pad, pady=(outer_pad, 0), sticky=tk.NSEW)
        self.session_combo = MappingCombobox(
            self.toolbar,
            width=23,
            exportselection=False,
            takefocus=False,
        )
        self.session_combo.grid(column=1, row=1, padx=(0, inner_pad))
        self.session_combo.bind("<<ComboboxSelected>>", self.select_session_from_combobox, True)

        default_font = tk.font.nametofont("TkDefaultFont")
        self.larger_font = default_font.copy()
        self.larger_font.config(size=int(default_font.cget("size") * 1.3))

        self._add_command(
            " « ", self.select_prev_key_event, self.can_select_event, tr("Previous run")
        )
        self._add_command(" » ", self.select_next_key_event, self.can_select_event, tr("Next run"))
        self._add_command(
            " ‹ ", self.select_prev_event, self.can_select_event, tr("Previous event")
        )
        self._add_command(" › ", self.select_next_event, self.can_select_event, tr("Next event"))

        self.scrubber = ttk.Scale(
            self.toolbar,
            from_=1,
            to=100,
            orient=tk.HORIZONTAL,
            takefocus=True,
            command=self.on_scrub,
            state="disabled",
        )
        self.scrubber.grid(row=1, column=10, sticky="ew", padx=(inner_pad, 0))

        self.menu_button = CustomToolbutton(
            self.toolbar, self.post_menu, text=f" {get_menu_char()} "
        )
        self.menu_button.grid(row=1, column=20, padx=(inner_pad, 0))

        self.toolbar.columnconfigure(10, weight=1)
        self.center_pw = ReplayerPanedWindow(
            self.main_frame, orient=tk.VERTICAL, sashwidth=ems_to_pixels(0.7)
        )
        self.center_pw.grid(row=2, column=1, sticky="nsew", padx=outer_pad, pady=outer_pad)
        self.editor_notebook = ReplayerEditorNotebook(self.center_pw)
        shell_book = CustomNotebook(self.center_pw, closable=False)
        self.shell = ShellFrame(shell_book)

        self.center_pw.add(self.editor_notebook, height=700, minsize=100)
        self.center_pw.add(shell_book, height=300, minsize=100)
        shell_book.add(self.shell, text="Shell")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.update_title()
        self.scrubber.focus_set()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after_idle(self._after_ready)

    def _after_ready(self):
        self.session_combo.select_value(CURRENT_SESSION_VALUE)
        self.select_session_from_combobox(None)

    def _add_command(self, label: str, command: Callable, tester: Callable, tooltip: str) -> None:
        pad = ems_to_pixels(0.3)

        def tested_command(event=None):
            if tester():
                command()
            else:
                self.bell()

        button = CustomToolbutton(
            self.toolbar, tested_command, text=label, font=self.larger_font, state="disabled"
        )
        button.grid(row=1, column=len(self.commands) + 2, padx=(pad, 0))

        self.commands.append(ReplayerCommand(label, button, command, tester))
        ui_utils.create_tooltip(button, tooltip)

    def refresh(self):
        self.session_combo.set_mapping(self.create_sessions_mapping())
        self.session_combo.select_clear()

    def post_menu(self) -> None:
        post_x = (
            self.menu_button.winfo_rootx()
            + self.menu_button.winfo_width()
            - self.menu.winfo_reqwidth()
        )
        post_y = self.menu_button.winfo_rooty() + self.menu_button.winfo_height()
        self.menu.tk_popup(post_x, post_y)

    def create_sessions_mapping(self):
        from thonny.plugins.event_logging import get_log_dir, parse_file_name, session_start_time

        current_session_label = (
            tr("Current session")
            + f" • {_custom_time_format(session_start_time, without_seconds=True)} - ???"
        )

        mapping = {current_session_label: CURRENT_SESSION_VALUE}

        log_dir = get_log_dir()

        filenames = list(reversed(sorted(os.listdir(log_dir))))

        # Need to know how many sessions were started at the same minute
        all_minute_prefixes = [name[:16] for name in filenames]

        for name in filenames:
            if not (name.endswith(".txt") or name.endswith(".jsonl") or name.endswith(".jsonl.gz")):
                continue

            full_path = os.path.join(log_dir, name)

            try:
                minute_prefix = name[:16]
                without_seconds = all_minute_prefixes.count(minute_prefix) == 1
                start_time, end_time = parse_file_name(name)
                # need mktime, because the tuples may have different value in dst field, which makes them unequal
                if time.mktime(start_time) == time.mktime(session_start_time):
                    # Don't read current session from file
                    continue
                date_s = _custom_date_format(start_time)
                time_s = _custom_time_format(start_time, without_seconds) + " - "
                if end_time is None:
                    time_s += "???"
                else:
                    time_s += _custom_time_format(end_time, without_seconds)
                label = f"{date_s} • {time_s}"
            except Exception:
                logger.exception(f"Could not parse filename {name}")
                label = name
            mapping[label] = full_path

        return mapping

    def select_session_from_combobox(self, event: Optional[tk.Event] = None) -> None:
        from thonny.plugins.event_logging import load_events_from_file, session_events

        session_path = self.session_combo.get_selected_value()
        logger.info("User selected session %r", session_path)

        if session_path == CURRENT_SESSION_VALUE:
            events = session_events.copy()
        elif os.path.isfile(session_path):
            events = load_events_from_file(session_path)
        else:
            raise RuntimeError("File does not exist: " + str(session_path))

        self.load_session(events)
        self.session_combo.select_clear()

    def load_session(self, events: List[Dict]) -> None:
        self.loading = True
        self.events = events.copy()  # Need fixed list. The source list can be appended to
        try:
            for event in self.events:
                event_time_str = event["time"]
                if len(event_time_str) == 19:
                    # 0 fraction may have been skipped
                    event_time_str += ".0"
                event_time = datetime.datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S.%f")
                # yes, I'm modifying the argument. I'll live with this hack.
                event["epoch_time"] = event_time.timestamp()
            self.reset_session()
            self.scrubber.config(state="normal")
            for cmd in self.commands:
                cmd.button.configure(state="normal")

            self.scrubber.config(
                from_=self.events[0]["epoch_time"], to=self.events[-1]["epoch_time"]
            )
            self.select_event(len(self.events) - 1)
            self.scrubber.focus_set()
        finally:
            self.loading = False

    def can_select_event(self) -> bool:
        return True

    def select_prev_key_event(self):
        index = self.last_event_index
        while index > 0:
            index -= 1
            if self.events[index]["sequence"] in KEY_EVENTS:
                self.select_event(index)
                return
        else:
            self.bell()

    def select_next_key_event(self):
        index = self.last_event_index
        while index < len(self.events) - 1:
            index += 1
            if self.events[index]["sequence"] in KEY_EVENTS:
                self.select_event(index)
                return
        else:
            self.bell()

    def select_prev_event(self):
        if self.last_event_index == 0:
            self.bell()
            return

        self.select_event(self.last_event_index - 1)

    def select_next_event(self):
        if self.last_event_index == len(self.events) - 1:
            self.bell()
            return

        self.select_event(self.last_event_index + 1)

    def find_closest_index(self, target_timestamp: float, start_index: int, end_index: int) -> int:
        if start_index == end_index:
            return start_index

        if end_index - start_index == 1:
            start_timestamp = self.events[start_index]["epoch_time"]
            end_timestamp = self.events[end_index]["epoch_time"]
            if abs(start_timestamp - target_timestamp) < abs(end_timestamp - target_timestamp):
                return start_index
            else:
                return end_index

        middle_index = (start_index + end_index) // 2
        middle_timestamp = self.events[middle_index]["epoch_time"]
        if target_timestamp < middle_timestamp:
            return self.find_closest_index(target_timestamp, start_index, middle_index)
        else:
            return self.find_closest_index(target_timestamp, middle_index, end_index)

    def select_event(self, index: int, from_scrubber: bool = False) -> None:
        self._select_event(index)
        event = self.events[self.last_event_index]
        if not from_scrubber:
            self.scrubber.set(event["epoch_time"])
        self.update_title()
        self.update_idletasks()

    def cmd_open(self, event=None):
        try:
            initialdir = get_workbench().get_option("tools.replayer_last_browser_folder")
            if not os.path.isdir(initialdir):
                initialdir = os.path.normpath(os.path.expanduser("./"))

            path = askopenfilename(filetypes=_dialog_filetypes, initialdir=initialdir, parent=self)
            if path:
                self.session_combo.add_pair(FILE_TOKEN + os.path.basename(path), path)
                self.session_combo.select_value(path)
                self.select_session_from_combobox(event)
                get_workbench().set_option(
                    "tools.replayer_last_browser_folder", os.path.dirname(path)
                )
        finally:
            return "break"

    def _select_event(self, index):
        if index > self.last_event_index:
            # replay all events between last replayed event up to and including this event
            while self.last_event_index < index:
                self.replay_event(self.events[self.last_event_index + 1])
                self.last_event_index += 1

        elif index < self.last_event_index:
            # Undo by resetting and replaying again
            self.reset_session()
            self._select_event(index)

    def update_title(self):
        session_label = self.session_combo.get()
        if session_label and session_label.startswith(FILE_TOKEN):
            s = session_label
        else:
            s = tr("History")

        if self.last_event_index is not None and self.last_event_index > -1:
            event = self.events[self.last_event_index]
            event_sequence = event["sequence"]
            timestamp = float(self.scrubber.cget("value"))
            dt = datetime.datetime.fromtimestamp(timestamp)
            date_s = dt.strftime("%x")
            time_s = dt.strftime("%X")
            s += f" • {event_sequence} @ {date_s} • {time_s}"

        self.title(s)

    def replay_event(self, event):
        "this should be called with events in correct order"
        if "text_widget_id" in event:
            if (
                event.get("text_widget_context", None) == "shell"
                or event.get("text_widget_class") == "ShellText"
            ):
                self.shell.replay_event(event)
            elif event.get("text_widget_class") == "EditorCodeViewText":
                self.editor_notebook.replay_event(event)

    def reset_session(self):
        self.shell.clear()
        self.editor_notebook.clear()
        self.last_event_index = -1

    def on_scrub(self, value):
        if self.loading:
            return

        index = self.find_closest_index(float(value), 0, len(self.events) - 1)
        self.select_event(index, from_scrubber=True)

    def on_close(self, event=None):
        global _REPLAYER
        self.destroy()
        _REPLAYER = None

        """Alternative:
        # self.withdraw()

        get_workbench().winfo_toplevel().lift()
        get_workbench().winfo_toplevel().focus_force()
        get_workbench().winfo_toplevel().grab_set()
        if running_on_mac_os():
            get_workbench().winfo_toplevel().grab_release()
        """


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

        if "filename" in event:
            self._filename = event["filename"]

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
            self.forget(child)
            child.destroy()

        assert self.current_page is None

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
            self.select(editor)
            editor.replay_event(event)

            if "filename" in event:
                self.tab(editor, text=editor.get_title())


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
            read_only=True,
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


@dataclass
class ReplayerCommand:
    label: str
    button: CustomToolbutton
    command: Callable
    tester: Callable


def open_replayer():
    global _REPLAYER
    if _REPLAYER is None:
        _REPLAYER = ReplayWindow(get_workbench())
        _REPLAYER.refresh()
        ui_utils.show_dialog(_REPLAYER, modal=False, width=1200, height=900)
    else:
        if _REPLAYER.winfo_ismapped():
            _REPLAYER.lift()
        else:
            _REPLAYER.deiconify()


def _custom_date_format(timestamp: time.struct_time):
    # Useful with locale specific formats, which would be a hassle to construct from parts
    now = time.localtime()
    if (
        timestamp.tm_year == now.tm_year
        and timestamp.tm_mon == now.tm_mon
        and timestamp.tm_mday == now.tm_mday
    ):
        return tr("Today")

    s = time.strftime("%x", timestamp)
    for sep in [" ", "-", ".", "/"]:
        year_part = sep + str(now.tm_year)
        if year_part in s:
            return s.replace(year_part, "").strip()

    return s


def _custom_time_format(timestamp: time.struct_time, without_seconds: bool):
    # Useful with locale specific formats, which would be a hassle to construct from parts
    s = time.strftime("%X", timestamp)
    if without_seconds:
        seconds_part = ":%02d" % (timestamp.tm_sec,)
        seconds_index = s.rfind(seconds_part)
        if seconds_index == -1:
            return s

        return s[:seconds_index] + s[seconds_index + len(seconds_part) :]
    else:
        return s


def load_plugin() -> None:
    get_workbench().set_default("tools.replayer_last_browser_folder", os.path.expanduser("~/"))
    get_workbench().add_command(
        "open_replayer",
        "tools",
        tr("Open replayer..."),
        open_replayer,
        include_in_toolbar=False,
        caption="Replayer",
        group=110,
    )
