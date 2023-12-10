import os.path
import time
import tkinter as tk
from datetime import datetime
from logging import getLogger
from typing import Dict, List, Optional, Tuple

from thonny import THONNY_USER_DIR, get_workbench
from thonny.languages import tr
from thonny.shell import ShellView
from thonny.ui_utils import asksaveasfilename
from thonny.workbench import WorkbenchEvent

logger = getLogger(__name__)

TIMESTAMP_FORMAT = "%Y-%m-%d_%H-%M-%S"

SESSION_EVENTS = []


class EventLogger:
    def __init__(self):
        self._closing = False
        self._start_time = time.localtime()
        self._file_path = os.path.join(
            get_log_dir(), format_time_range(time.localtime(), None) + ".jsonl"
        )

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
            "Open",
            "Save",
            "SaveAs",
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
        ]:
            self._bind_workbench(sequence)

        self._bind_workbench("<FocusIn>", True)
        self._bind_workbench("<FocusOut>", True)

        ### log_user_event(KeyPressEvent(self, e.char, e.keysym, self.text.index(tk.INSERT)))

        # TODO: if event data includes an Editor, then look up also text id
        self._out_fp = open(self._file_path, mode="w", encoding="utf-8", buffering=1)

        logger.info("Starting logging user events into %r", self._file_path)

    def _bind_workbench(self, sequence, only_workbench_widget=False):
        def handle(event):
            if not only_workbench_widget or event.widget == get_workbench():
                self._log_event(sequence, event)

        get_workbench().bind(sequence, handle, True)

    def _bind_all(self, sequence):
        def handle(event):
            self._log_event(sequence, event)

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

    def _log_event(self, sequence, event):
        if self._closing:
            logger.info("Won't log %r because we are closing", sequence)
            return

        import json

        data = self._extract_interesting_data(event, sequence)
        data["sequence"] = sequence
        data["time"] = datetime.now().isoformat()
        if len(data["time"]) == 19:
            # 0 fraction gets skipped, but reader assumes it
            data["time"] += ".0"
        SESSION_EVENTS.append(data)
        json.dump(data, self._out_fp)
        self._out_fp.write("\n")

    def _on_worbench_close(self, event=None):
        # save the file, compress it and remove the uncompressed copy
        self._closing = True
        self._out_fp.close()
        out_file_path = os.path.join(
            get_log_dir(), format_time_range(self._start_time, time.localtime()) + ".jsonl.gz"
        )
        import gzip

        with gzip.open(out_file_path, mode="wb") as out_fp:
            with open(self._file_path, mode="rb") as in_fp:
                out_fp.write(in_fp.read())

        os.remove(self._file_path)


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
        with open_fun(path, mode="r", encoding="utf-8") as fp:
            for line in fp:
                result.append(json.loads(line))

        for event in result:
            if len(event["time"]) == 19:
                # 0 fraction may have been skipped
                event["time"] += ".0"
            event["time"] = datetime.strptime(event["time"], "%Y-%m-%dT%H:%M:%S.%f")

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
