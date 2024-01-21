from __future__ import annotations

import ast
import datetime
import os.path
import re
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
from thonny.tktextext import TweakableText
from thonny.ui_utils import (
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
instance: Optional[Replayer] = None

CURRENT_SESSION_VALUE = "__CURRENT_SESSION__"

_dialog_filetypes = [(tr("Event logs"), ".jsonl .gz .txt"), (tr("all files"), ".*")]


class Replayer(tk.Toplevel):
    def __init__(self, master):
        self.events = None
        self.last_event_index = -1
        self.loading = False
        self.commands: List[ReplayerCommand] = []
        self._scrubbing_after_id = None

        super().__init__(
            master,
            background=lookup_style_option("TFrame", "background"),
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

        get_workbench().set_default("replayer.sash_position", ems_to_pixels(30))
        sash_position = get_workbench().get_option("replayer.sash_position")
        self.center_pw = ReplayerPanedWindow(
            self.main_frame, orient=tk.VERTICAL, sashwidth=ems_to_pixels(0.7)
        )
        self.center_pw.grid(row=2, column=1, sticky="nsew", padx=outer_pad, pady=outer_pad)
        self.editor_notebook = ReplayerEditorNotebook(self.center_pw)
        shell_book = CustomNotebook(self.center_pw, closable=False)
        self.shell = ShellFrame(shell_book)

        self.center_pw.add(self.editor_notebook, height=sash_position, minsize=ems_to_pixels(2))
        self.center_pw.add(shell_book, minsize=ems_to_pixels(2))
        shell_book.add(self.shell, text="Shell")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.update_title()
        self.scrubber.focus_set()

        self.protocol("WM_DELETE_WINDOW", self.close)
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
        # Need a fixed copy. The source list can be appended to, and we want to tweak things.
        self.events = events.copy()

        for event in self.events:
            if event["sequence"] == "ToplevelResponse":
                break
        else:
            # Infer ToplevelResponse events for old format logs
            for i in reversed(range(0, len(self.events) - 1)):
                event = self.events[i]
                if (
                    event["sequence"] == "TextInsert"
                    and event["text"] == ">>> "
                    and "prompt" in event["tags"]
                ):
                    self.events.insert(
                        i + 1,
                        {
                            "event_type": "ToplevelResponse",
                            "sequence": "ToplevelResponse",
                            "time": event["time"],
                        },
                    )

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
            # need to apply all events in order to record reversion information
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
        self._do_select_event(index)
        event = self.events[self.last_event_index]
        if not from_scrubber:
            self.scrubber.set(event["epoch_time"])
        self.update_title()
        self.update_idletasks()

    def _do_select_event(self, index):
        if index > self.last_event_index:
            # replay all events between last replayed event up to and including this event
            while self.last_event_index < index:
                self.process_event(self.events[self.last_event_index + 1], reverse=False)
                self.last_event_index += 1

        elif index < self.last_event_index:
            # undo events up to and including the event following the desired event
            while self.last_event_index > index:
                self.process_event(self.events[self.last_event_index], reverse=True)
                self.last_event_index -= 1

    def update_title(self):
        session_label = self.session_combo.get()
        if session_label and session_label.startswith(FILE_TOKEN):
            s = session_label
        else:
            s = tr("Thonny Replayer")

        if self.last_event_index is not None and self.last_event_index > -1:
            event = self.events[self.last_event_index]
            event_sequence = event["sequence"]
            timestamp = float(self.scrubber.cget("value"))
            dt = datetime.datetime.fromtimestamp(timestamp)
            date_s = dt.strftime("%x")
            time_s = dt.strftime("%X")
            s += f" • {event_sequence} @ {date_s} • {time_s}"

        self.title(s)

    def process_event(self, event, reverse: bool):
        "this should be called with events in correct order"
        if "text_widget_id" in event:
            if (
                event.get("text_widget_context", None) == "shell"
                or event.get("text_widget_class") == "ShellText"
            ):
                self.shell.process_event(event, reverse)
            elif event.get("text_widget_class") == "EditorCodeViewText":
                self.editor_notebook.process_event(event, reverse)

    def reset_session(self):
        self.shell.clear()
        self.editor_notebook.clear()
        self.last_event_index = -1

    def on_scrub(self, value):
        if self.loading:
            return

        index = self.find_closest_index(float(value), 0, len(self.events) - 1)
        self.select_event(index, from_scrubber=True)

    def close(self, event=None):
        global instance

        get_workbench().set_option("replayer.zoomed", ui_utils.get_zoomed(self))
        if not ui_utils.get_zoomed(self) or running_on_mac_os():
            # can't restore zoom on mac without setting actual dimensions
            gparts = re.findall(r"\d+", self.wm_geometry())
            get_workbench().set_option("replayer.width", int(gparts[0]))
            get_workbench().set_option("replayer.height", int(gparts[1]))
            get_workbench().set_option("replayer.left", int(gparts[2]))
            get_workbench().set_option("replayer.top", int(gparts[3]))

        get_workbench().set_option("replayer.sash_position", self.editor_notebook.winfo_height())

        self.destroy()
        instance = None

        """Alternative:
        # self.withdraw()

        get_workbench().winfo_toplevel().lift()
        get_workbench().winfo_toplevel().focus_force()
        get_workbench().winfo_toplevel().grab_set()
        if running_on_mac_os():
            get_workbench().winfo_toplevel().grab_release()
        """

    def show(self):
        self.title("Thonny")

        get_workbench().set_default("replayer.zoomed", False)
        get_workbench().set_default("replayer.width", ems_to_pixels(70))
        get_workbench().set_default("replayer.height", ems_to_pixels(50))
        get_workbench().set_default("replayer.left", ems_to_pixels(20))
        get_workbench().set_default("replayer.top", ems_to_pixels(10))

        logger.info(
            "height: %r, %r, %r",
            get_workbench().get_option("replayer.height"),
            ems_to_pixels(20),
            self.winfo_screenheight(),
        )

        geometry = "{0}x{1}+{2}+{3}".format(
            min(
                max(get_workbench().get_option("replayer.width"), ems_to_pixels(30)),
                self.winfo_screenwidth(),
            ),
            min(
                max(get_workbench().get_option("replayer.height"), ems_to_pixels(20)),
                self.winfo_screenheight(),
            ),
            min(
                max(get_workbench().get_option("replayer.left"), 0),
                self.winfo_screenwidth() - ems_to_pixels(10),
            ),
            min(
                max(get_workbench().get_option("replayer.top"), 0),
                self.winfo_screenheight() - ems_to_pixels(10),
            ),
        )
        logger.info("Replayer geometry: %r", geometry)
        self.geometry(geometry)

        if get_workbench().get_option("replayer.zoomed"):
            ui_utils.set_zoomed(self, True)

        self.lift()
        self.deiconify()


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

    def process_event(self, event, reverse):
        if not reverse:
            self.apply_event(event)
        else:
            self.revert_event(event)

    def apply_event(self, event):
        if "previous_modified" not in event and event["sequence"] in [
            "TextInsert",
            "TextDelete",
            "Opened",
            "Saved",
        ]:
            # Mark the state change
            event["previous_modified"] = self.is_modified()

        if event["sequence"] in ["TextInsert", "TextDelete"]:
            _apply_event_on_text(event, self._code_view.text)
            self._code_view.text.edit_modified(True)
        elif event["sequence"] in ["Opened", "Saved"]:
            # Can't use old events Open, Save and SaveAs as they are not aligned with edit_modified
            self._code_view.text.edit_modified(False)

        if "filename" in event:
            if "previous_filename" not in event:
                # store information for reverting this event
                event["previous_filename"] = self._filename

            self._filename = event["filename"]

    def revert_event(self, event):
        _revert_event_on_text(event, self._code_view.text)
        if "previous_modified" in event:
            self._code_view.text.edit_modified(event["previous_modified"])

        if "previous_filename" in event:
            self._filename = event["previous_filename"]

    def shorten_filename_for_title(self, path: str) -> str:
        # the path can be saved in Posix and replayed in Windows and vice versa
        return path.replace("\\", "/").split("/")[-1]

    def clear(self):
        self._code_view.text.direct_delete("1.0", "end")
        self._filename = None
        self._code_view.text.edit_modified(False)


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

    def process_event(self, event, reverse):
        if "text_widget_id" in event:
            editor = self.get_editor_by_text_widget_id(event["text_widget_id"])
            self.select(editor)
            editor.process_event(event, reverse)

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

    def process_event(self, event, reverse):
        if event["sequence"] in ["TextInsert", "TextDelete"]:
            if not reverse:
                _apply_event_on_text(event, self.text)
            else:
                _revert_event_on_text(event, self.text)


class ReplayerPanedWindow(tk.PanedWindow):
    def __init__(self, master=None, **kw):
        kw["background"] = lookup_style_option("TFrame", "background")
        super().__init__(master=master, **kw)


@dataclass
class ReplayerCommand:
    label: str
    button: CustomToolbutton
    command: Callable
    tester: Callable


def _apply_event_on_text(event: Dict, text: TweakableText) -> None:
    if event["sequence"] == "TextInsert":
        text.direct_insert(event["index"], event["text"], ast.literal_eval(event["tags"]))
        text.see(event["index"])

    elif event["sequence"] == "TextDelete":
        index1 = event["index1"]
        index2 = event.get("index2", None)
        if index2 == "None":
            index2 = None
        index2 = index2 or index1 + "+1c"

        assert index1
        assert index2

        if "chunks" not in event:
            # remember the information required for reverting the event
            event["chunks"] = _export_text_range_with_tags(text, index1, index2)
            # logger.trace("Deletion from %r to %r chunks %r", index1, index2, event["chunks"])

        text.direct_delete(index1, index2)
        text.see(event["index1"])


def _revert_event_on_text(event: Dict, text: TweakableText) -> None:
    if event["sequence"] == "TextInsert":
        index1 = event["index"]
        text_len = len(event["text"])
        text.direct_delete(index1, f"{index1}+{text_len}c")
        text.see(event["index"])
    elif event["sequence"] == "TextDelete":
        assert "chunks" in event
        for chunk in event["chunks"]:
            text.direct_insert(chunk["start_index"], chunk["chars"], chunk["tags"])
        if event["chunks"]:  # yes, there can be deletions of 0 chars. Beats me.
            text.see(event["chunks"][0]["start_index"])
            text.see("%s+%dc" % (event["chunks"][-1]["start_index"], len(event)))


def _export_text_range_with_tags(text: tk.Text, index1: str, index2: str) -> List[Dict]:
    # If this approach brings some problems then consider using Text.dump
    # logger.debug("Exporting %r to %r", index1, index2)
    chunks = []
    offset = 0
    while True:
        current_index = f"{index1}+{offset}c"
        if text.compare(current_index, "<", index2):
            char = text.get(current_index)
            tags = text.tag_names(current_index)
            chunks.append({"start_index": current_index, "chars": char, "tags": tags})
            offset += 1
        else:
            break

    i = len(chunks) - 1
    while i > 0:
        # try combining with preceding chunk
        if chunks[i]["tags"] == chunks[i - 1]["tags"]:
            chunks[i - 1]["chars"] += chunks[i]["chars"]
            del chunks[i]

        i -= 1

    return chunks


def open_replayer():
    global instance
    if instance is None:
        instance = Replayer(get_workbench())
        instance.refresh()
        instance.show()
    else:
        if instance.winfo_ismapped():
            instance.lift()
        else:
            instance.deiconify()


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
