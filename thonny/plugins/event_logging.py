import os.path
import time
import tkinter as tk
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, Tuple

from thonny import THONNY_USER_DIR, get_shell, get_workbench
from thonny.languages import tr
from thonny.shell import ShellView
from thonny.ui_utils import asksaveasfilename
from thonny.workbench import WorkbenchEvent

logger = getLogger(__name__)

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

session_events = []
session_start_time: Optional[time.struct_time] = None
session_start_epoch_time: Optional[float] = None

IDLE_SECONDS_FOR_SESSION_SPLIT = 15 * 60


class EventLogger:
    def __init__(self):
        self._closing = False
        self._last_event_epoch_time: Optional[float] = None

        wb = get_workbench()
        wb.bind("WorkbenchClose", self._on_worbench_close, True)

        for sequence in [
            "<<Undo>>",
            "<<Redo>>",
            "<<Cut>>",
            "<<Copy>>",
            "<<Paste>>",
            # "<<Selection>>",
            # "<Key>",
            # "<KeyRelease>",
            "<Button-1>",
            "<Button-2>",
            "<Button-3>",
        ]:
            self._bind_all(sequence)

        for sequence in [
            "UiCommandDispatched",
            "MagicCommand",
            "Open",  # Event happens before the editor text gets updated
            "Opened",
            "Save",  # Event happens before save is attempted, user may cancel or saving may fail
            "SaveAs",  # Event happens before save is attempted, user may cancel or saving may fail
            "Saved",
            "NewFile",
            "EditorTextCreated",
            "EditorTextDestroyed",
            # "ShellTextCreated", # Too bad, this event happens before event_logging is loaded
            "ShellCommand",
            "ShellInput",
            "ShowView",
            "HideView",
            "TextInsert",
            "TextDelete",
            "ToplevelResponse",
        ]:
            self._bind_workbench(sequence)

        self._bind_workbench("<FocusIn>", True)
        self._bind_workbench("<FocusOut>", True)

        ### log_user_event(KeyPressEvent(self, e.char, e.keysym, self.text.index(tk.INSERT)))
        self._start_session()

    def _bind_workbench(self, sequence, only_workbench_widget=False):
        def handle(event):
            if not only_workbench_widget or event.widget == get_workbench():
                self._consider_splitting_and_log_event(sequence, event)

        get_workbench().bind(sequence, handle, True)

    def _bind_all(self, sequence):
        def handle(event):
            self._consider_splitting_and_log_event(sequence, event)

        tk._default_root.bind_all(sequence, handle, True)

    def _extract_interesting_data(self, event, sequence):
        attributes = vars(event)

        # generate some new attributes
        if "text_widget" not in attributes:
            if "editor" in attributes:
                attributes["text_widget"] = attributes["editor"].get_text_widget()

            if "widget" in attributes and isinstance(attributes["widget"], tk.Text):
                attributes["text_widget"] = attributes["widget"]

        if "text_widget" in attributes:
            widget = attributes["text_widget"]
            if isinstance(widget.master.master, ShellView):
                attributes["text_widget_context"] = "shell"

        # select attributes
        data = {}
        for name in attributes:
            # skip some attributes
            if (
                name.startswith("_")
                or isinstance(event, WorkbenchEvent)
                and name in ["update", "setdefault"]
                or isinstance(event, tk.Event)
                and name not in ["widget", "text_widget", "text_widget_context"]
            ):
                continue

            value = attributes[name]

            if isinstance(value, (tk.BaseWidget, tk.Tk)):
                data[name + "_id"] = id(value)
                data[name + "_class"] = value.__class__.__name__

            elif isinstance(value, (str, int, float)):
                data[name] = value

            else:
                data[name] = repr(value)

        return data

    def _consider_splitting_and_log_event(self, sequence, event):
        now = time.time()
        if (
            self._last_event_epoch_time is not None
            and now - self._last_event_epoch_time > IDLE_SECONDS_FOR_SESSION_SPLIT
        ):
            logger.info(
                "Splitting because %r is more than %r seconds later than %r",
                time.ctime(now),
                IDLE_SECONDS_FOR_SESSION_SPLIT,
                time.ctime(self._last_event_epoch_time),
            )
            self._split_session()

        self._log_event(sequence, event)

    def _log_event(self, sequence, event):
        if self._closing:
            logger.info("Won't log %r because we are closing", sequence)
            return

        event_time = datetime.now()
        import json

        widget_str = getattr(event, "widget", None)
        try:
            widget = get_workbench().nametowidget(widget_str) if widget_str is not None else None
        except Exception as e:
            if "popdown" not in str(e):
                logger.warning(
                    "Could not extract widget %r from event %r", widget_str, event, exc_info=True
                )
            widget = None

        if widget is None:
            widget = getattr(event, "text_widget", None)

        if widget is not None:
            try:
                if widget.winfo_toplevel() is not get_workbench():
                    # logger.debug("Skipping non-workspace event %r", event)
                    return
            except tk.TclError:
                logger.error("Could not get winfo_toplevel", exc_info=True)
                return
        else:
            logger.warning("Event without widget: %r", event)

        data = self._extract_interesting_data(event, sequence)
        data["sequence"] = sequence
        data["time"] = event_time.isoformat()
        if len(data["time"]) == 19:
            # 0 fraction gets skipped, but reader assumes it
            data["time"] += ".0"
        session_events.append(data)
        json.dump(data, self._out_fp)
        self._out_fp.write("\n")

        self._last_event_epoch_time = event_time.timestamp()

    def _on_worbench_close(self, event):
        self._consider_splitting_and_log_event("WorkbenchClose", event)
        self._closing = True
        self._close_session()

    def _start_session(self):
        global session_start_time
        now = datetime.now()
        session_start_time = now.timetuple()

        self._file_path = os.path.join(
            get_log_dir(), format_time_range(session_start_time, None) + ".jsonl"
        )
        self._out_fp = open(self._file_path, mode="w", encoding="utf-8", buffering=1)
        logger.info("Starting logging user events into %r", self._file_path)

    def _close_session(self):
        # save the file, compress it and remove the uncompressed copy
        logger.info("Closing event log")
        self._out_fp.close()
        out_file_path = os.path.join(
            get_log_dir(), format_time_range(session_start_time, time.localtime()) + ".jsonl.gz"
        )
        import gzip

        logger.info("Events will be saved to %r", out_file_path)
        with gzip.open(out_file_path, mode="wb") as out_fp:
            with open(self._file_path, mode="rb") as in_fp:
                out_fp.write(in_fp.read())

        os.remove(self._file_path)
        session_events.clear()

    def _split_session(self):
        self._close_session()
        self._start_session()

        texts = [
            editor.get_text_widget()
            for editor in get_workbench().get_editor_notebook().get_all_editors()
        ]
        texts.insert(0, get_shell().text)

        for text in texts:
            self._log_event(
                "TextInsert",
                WorkbenchEvent(
                    sequence="TextInsert",
                    index="1.0",
                    text=text.get("1.0", "end-1c"),
                    tags=(),
                    text_widget=text,
                    trivial_for_coloring=False,
                    trivial_for_parens=False,
                ),
            )


def get_log_dir():
    return os.path.join(THONNY_USER_DIR, "user_logs")


def export():
    import zipfile

    filename = asksaveasfilename(
        filetypes=[("Zip-files", ".zip"), ("all files", ".*")],
        defaultextension=".zip",
        initialdir=get_workbench().get_local_cwd(),
        initialfile=time.strftime("ThonnyUsageLogs_%Y-%m-%d.zip"),
        parent=get_workbench(),
    )

    if not filename:
        return

    log_dir = get_log_dir()

    with zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for item in os.listdir(log_dir):
            if item.endswith(".txt") or item.endswith(".zip"):
                zipf.write(os.path.join(log_dir, item), arcname=item)


def format_time_range(
    start_time: time.struct_time, end_time: Optional[time.struct_time] = None
) -> str:
    start_str = time.strftime(TIMESTAMP_FORMAT, start_time)
    if end_time is not None:
        end_str = time.strftime(TIMESTAMP_FORMAT, end_time)
    else:
        end_str = "unknown"
    return start_str + "__" + end_str


def parse_time_range(s: str) -> Tuple[time.struct_time, Optional[time.struct_time]]:
    parts = s.split("__")
    assert len(parts) == 2
    start_time = time.strptime(parts[0], TIMESTAMP_FORMAT)
    if parts[1] == "unknown":
        end_time = None
    else:
        end_time = time.strptime(parts[1], TIMESTAMP_FORMAT)

    return start_time, end_time


def parse_file_name(name: str) -> Tuple[time.struct_time, Optional[time.struct_time]]:
    parts = name.split(".")
    return parse_time_range(parts[0])


def load_events_from_file(path: str) -> List[Dict]:
    import json

    if path.endswith(".txt"):
        # old Json format before Thonny 5.0
        with open(path, encoding="utf-8") as fp:
            return json.load(fp)

    else:
        # new JSON lines format, compressed or not
        if path.endswith(".jsonl.gz"):
            import gzip

            open_fun = gzip.open
        else:
            assert path.endswith(".jsonl")
            open_fun = open

        result = []
        with open_fun(path, mode="rt", encoding="utf-8") as fp:
            for line in fp:
                result.append(json.loads(line))

        return result


def load_plugin() -> None:
    if not os.path.exists(get_log_dir()):
        os.makedirs(get_log_dir())

    get_workbench().set_default("general.event_logging", True)

    if get_workbench().get_option("general.event_logging"):
        get_workbench().add_command(
            "export_usage_logs", "tools", tr("Export usage logs..."), export, group=110
        )

        # create logger
        EventLogger()
