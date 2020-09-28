import os.path
import time
import tkinter as tk
from datetime import datetime

from thonny import THONNY_USER_DIR, get_workbench
from thonny.languages import tr
from thonny.shell import ShellView
from thonny.ui_utils import asksaveasfilename
from thonny.workbench import WorkbenchEvent


class EventLogger:
    def __init__(self, filename):
        self._filename = filename
        self._events = []

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
        data = self._extract_interesting_data(event, sequence)
        data["sequence"] = sequence
        data["time"] = datetime.now().isoformat()
        if len(data["time"]) == 19:
            # 0 fraction gets skipped, but reader assumes it
            data["time"] += ".0"
        self._events.append(data)

    def _on_worbench_close(self, event=None):
        import json

        with open(self._filename, encoding="UTF-8", mode="w") as fp:
            json.dump(self._events, fp, indent="    ")

        self._check_compress_logs()

    def _check_compress_logs(self):
        import zipfile

        # if uncompressed logs have grown over 10MB,
        # compress these into new zipfile

        log_dir = _get_log_dir()
        total_size = 0
        uncompressed_files = []
        for item in os.listdir(log_dir):
            if item.endswith(".txt"):
                full_name = os.path.join(log_dir, item)
                total_size += os.stat(full_name).st_size
                uncompressed_files.append((item, full_name))

        if total_size > 10 * 1024 * 1024:
            zip_filename = _generate_timestamp_file_name("zip")
            with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
                for item, full_name in uncompressed_files:
                    zipf.write(full_name, arcname=item)

            for _, full_name in uncompressed_files:
                os.remove(full_name)


def _generate_timestamp_file_name(extension):
    # generate log filename
    folder = _get_log_dir()
    if not os.path.exists(folder):
        os.makedirs(folder)

    for i in range(100):
        filename = os.path.join(
            folder, time.strftime("%Y-%m-%d_%H-%M-%S_{}.{}".format(i, extension))
        )
        if not os.path.exists(filename):
            return filename

    raise RuntimeError()


def _get_log_dir():
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

    log_dir = _get_log_dir()

    with zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for item in os.listdir(log_dir):
            if item.endswith(".txt") or item.endswith(".zip"):
                zipf.write(os.path.join(log_dir, item), arcname=item)


def load_plugin() -> None:
    get_workbench().set_default("general.event_logging", False)

    if get_workbench().get_option("general.event_logging"):
        get_workbench().add_command(
            "export_usage_logs", "tools", tr("Export usage logs..."), export, group=110
        )

        filename = _generate_timestamp_file_name("txt")
        # create logger
        EventLogger(filename)
