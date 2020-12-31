import logging
import os
import queue
import signal
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from thonny import tktextext
from thonny.languages import tr
from thonny.misc_utils import running_on_windows
from thonny.ui_utils import CommonDialog, ems_to_pixels, create_action_label, set_text_if_different

logger = logging.getLogger(__name__)


class WorkDialog(CommonDialog):
    def __init__(self, master, autostart=False):
        super(WorkDialog, self).__init__(master)

        self._autostart = autostart
        self._state = "idle"
        self.success = False
        self._work_events_queue = queue.Queue()
        self.init_instructions_frame()
        self.init_main_frame()
        self.init_action_frame()
        self.init_log_frame()
        self.populate_main_frame()
        self.rowconfigure(4, weight=1)  # log frame
        self.columnconfigure(0, weight=1)
        self.title(self.get_title())
        self.stdout = ""
        self.stderr = ""

        self._update_scheduler = None
        self._keep_updating_ui()

        self.bind("<Escape>", self.on_cancel, True)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)

        if self._autostart:
            self.on_ok()

    def populate_main_frame(self):
        pass

    def is_ready_for_work(self):
        return True

    def init_instructions_frame(self):
        instructions = self.get_instructions()
        self.instructions_frame = ttk.Frame(self, style="Tip.TFrame")
        self.instructions_frame.grid(row=0, column=0, sticky="nsew")
        self.instructions_frame.rowconfigure(0, weight=1)
        self.instructions_frame.columnconfigure(0, weight=1)

        pad = self.get_padding()
        self.instructions_label = ttk.Label(self, style="Tip.TLabel", text=instructions)
        self.instructions_label.grid(row=0, column=0, sticky="w", padx=pad, pady=pad)

    def get_instructions(self) -> Optional[str]:
        return None

    def init_main_frame(self):
        self.main_frame = ttk.Frame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

    def init_action_frame(self):
        padding = self.get_padding()
        intpad = self.get_internal_padding()

        self.action_frame = ttk.Frame(self)
        self.action_frame.grid(row=2, column=0, sticky="nsew")

        self._progress_bar = ttk.Progressbar(
            self.action_frame, length=ems_to_pixels(4), mode="indeterminate"
        )

        self._current_action_label = create_action_label(
            self.action_frame,
            text="",
            width=round(self.get_action_text_max_length() * 1.1),
            click_handler=self.toggle_log_frame,
        )
        self._current_action_label.grid(
            row=1, column=2, sticky="we", pady=padding, padx=(0, intpad)
        )

        self._ok_button = ttk.Button(
            self.action_frame,
            text=self.get_ok_text(),
            command=self.on_ok,
            state="disabled",
            default="active",
        )
        if not self._autostart:
            self._ok_button.grid(column=4, row=1, pady=padding, padx=(0, intpad))

        self._cancel_button = ttk.Button(
            self.action_frame,
            text=self.get_cancel_text(),
            command=self.on_cancel,
        )
        self._cancel_button.grid(column=5, row=1, padx=(0, padding), pady=padding)

        self.action_frame.columnconfigure(2, weight=1)

    def get_action_text_max_length(self):
        return 35

    def init_log_frame(self):
        self.log_frame = ttk.Frame(self)
        self.log_frame.columnconfigure(1, weight=1)
        self.log_frame.rowconfigure(1, weight=1)
        fixed_font = tk.font.nametofont("TkFixedFont")
        font = fixed_font.copy()
        font.configure(size=round(fixed_font.cget("size") * 0.8))
        self.log_text = tktextext.TextFrame(
            self.log_frame,
            horizontal_scrollbar=False,
            wrap="word",
            borderwidth=1,
            height=5,
            width=20,
            font=font,
            read_only=True,
        )

        padding = self.get_padding()
        self.log_text.grid(row=1, column=1, sticky="nsew", padx=padding, pady=(0, padding))

    def update_ui(self):
        if self._state == "closed":
            return

        while not self._work_events_queue.empty():
            self.handle_work_event(*self._work_events_queue.get())
            if self._state == "closed":
                return

        if self._state == "idle":
            if self.is_ready_for_work():
                self._ok_button.configure(state="normal")
            else:
                self._ok_button.configure(state="disabled")
        else:
            self._ok_button.configure(state="disabled")

        if self._state == "done":
            set_text_if_different(self._cancel_button, tr("Close"))
        else:
            set_text_if_different(self._cancel_button, tr("Cancel"))

    def start_work(self):
        pass

    def get_title(self):
        return "Work dialog"

    def _keep_updating_ui(self):
        if self._state != "closed":
            self.update_ui()
            self._update_scheduler = self.after(200, self._keep_updating_ui)
        else:
            self._update_scheduler = None

    def close(self):
        self._state = "closed"
        if self._update_scheduler is not None:
            try:
                self.after_cancel(self._update_scheduler)
            except tk.TclError:
                pass

        self.destroy()

    def cancel_work(self):
        # worker should periodically check this value
        self._state = "cancelling"
        self.set_action_text(tr("Cancelling"))

    def toggle_log_frame(self, event=None):
        if self.log_frame.winfo_ismapped():
            self.log_frame.grid_forget()
            self.rowconfigure(2, weight=1)
            self.rowconfigure(4, weight=0)
        else:
            self.log_frame.grid(row=4, column=0, sticky="nsew")
            self.rowconfigure(2, weight=0)
            self.rowconfigure(4, weight=1)

    def get_ok_text(self):
        return tr("OK")

    def get_cancel_text(self):
        return tr("Cancel")

    def on_ok(self, event=None):
        assert self._state == "idle"
        if self.start_work() is not False:
            self._state = "working"
            self.success = False
            self.grid_progress_widgets()
            self._progress_bar["mode"] = "indeterminate"
            self._progress_bar.start()
            if not self._current_action_label["text"]:
                self._current_action_label["text"] = tr("Starting") + "..."

    def grid_progress_widgets(self):
        padding = self.get_padding()
        intpad = self.get_internal_padding()
        self._progress_bar.grid(row=1, column=1, sticky="w", padx=(padding, intpad), pady=padding)

    def on_cancel(self, event=None):
        if self._state in ("idle", "done"):
            self.close()
        elif self._state == "cancelling" and self.confirm_leaving_while_cancelling():
            self.close()
        elif self.confirm_cancel():
            self.cancel_work()

    def confirm_leaving_while_cancelling(self):
        return messagebox.askyesno(
            "Close dialog?",
            "Cancelling is in progress.\nDo you still want to close the dialog?",
            parent=self,
        )

    def confirm_cancel(self):
        return messagebox.askyesno(
            "Cancel work?",
            "Are you sure you want to cancel?",
            parent=self,
        )

    def append_text(self, text: str, stream_name="stdout") -> None:
        """Appends text to the details box. May be called from another thread."""
        self._work_events_queue.put(("append", (text, stream_name)))
        setattr(self, stream_name, getattr(self, stream_name) + text)

    def replace_last_line(self, text: str, stream_name="stdout") -> None:
        """Replaces last line in the details box. May be called from another thread."""
        self._work_events_queue.put(("replace", (text, stream_name)))
        setattr(self, stream_name, getattr(self, stream_name) + text)

    def report_progress(self, value: float, maximum: float) -> None:
        """Updates progress bar. May be called from another thread."""
        self._work_events_queue.put(("progress", (value, maximum)))

    def set_action_text(self, text: str) -> None:
        """Updates text above the progress bar. May be called from another thread."""
        self._work_events_queue.put(("action", (text,)))

    def set_action_text_smart(self, text: str) -> None:
        """Updates text above the progress bar. May be called from another thread."""
        text = text.strip()
        if not text:
            return
        if len(text) > self.get_action_text_max_length():
            text = text[: self.get_action_text_max_length() - 3] + "..."
        self.set_action_text(text)

    def report_done(self, success):
        """May be called from another thread."""
        self._work_events_queue.put(("done", (success,)))

    def handle_work_event(self, type, args):
        if type in ("append", "replace"):
            text, stream_name = args
            if type == "replace":
                self.log_text.text.direct_delete("end-1c linestart", "end-1c")
            self.log_text.text.direct_insert("end", text, (stream_name,))
            self.log_text.text.see("end")
        elif type == "action":
            set_text_if_different(self._current_action_label, args[0])
        elif type == "progress":
            value, maximum = args
            if value is None or maximum is None:
                if self._progress_bar["mode"] != "indeterminate":
                    self._progress_bar["mode"] = "indeterminate"
                    self._progress_bar.start()
            else:
                if self._progress_bar["mode"] != "determinate":
                    self._progress_bar["mode"] = "determinate"
                    self._progress_bar.stop()
                self._progress_bar.configure(value=value, maximum=maximum)
        elif type == "done":
            self.on_done(args[0])

    def on_done(self, success):
        """NB! Don't call from non-ui thread!"""
        self.success = success
        if self.success:
            self._state = "done"
            self._cancel_button.focus_set()
            self._cancel_button["default"] = "active"
            self._ok_button["default"] = "normal"
        elif self._autostart:
            # Can't try again if failed with autostart
            self._state = "done"
            self._cancel_button.focus_set()
            self._cancel_button["default"] = "active"
            self._ok_button["default"] = "normal"
        else:
            # allows trying again when failed
            self._state = "idle"
            self._ok_button.focus_set()
            self._ok_button["default"] = "active"
            self._cancel_button["default"] = "normal"

        self._progress_bar.stop()
        # need to put to determinate mode, otherwise it looks half done
        self._progress_bar["mode"] = "determinate"
        if self.success and self._autostart and not self.log_frame.winfo_ismapped():
            self.close()

        if not self.success and not self.log_frame.winfo_ismapped():
            self.toggle_log_frame()


class SubprocessDialog(WorkDialog):
    """Shows incrementally the output of given subprocess.
    Allows cancelling"""

    def __init__(self, master, proc, title, long_description=None, autostart=True):
        self._proc = proc
        self.stdout = ""
        self.stderr = ""
        self._stdout_thread = None
        self._stderr_thread = None
        self._title = title
        self._long_description = long_description
        self.returncode = None

        super().__init__(master, autostart=autostart)

    def is_ready_for_work(self):
        return True

    def get_title(self):
        return self._title

    def get_instructions(self) -> Optional[str]:
        return self._long_description

    def start_work(self):
        if hasattr(self._proc, "cmd"):
            try:
                self.append_text(subprocess.list2cmdline(self._proc.cmd) + "\n")
            except:
                logger.warning("Could not extract cmd (%s)", self._proc.cmd)
        self._start_listening_current_proc()

    def _start_listening_current_proc(self):
        def listen_stream(stream_name):
            stream = getattr(self._proc, stream_name)
            while True:
                data = stream.readline()
                self.append_text(data, stream_name)
                self._check_set_action_text_from_output_line(data)
                setattr(self, stream_name, getattr(self, stream_name) + data)
                if data == "":
                    logger.debug("Finished reading %s", stream_name)
                    break

            if stream_name == "stdout":
                self._finish_process()

            logger.debug("Returning from reading %s", stream_name)

        self._stdout_thread = threading.Thread(target=listen_stream, args=["stdout"], daemon=True)
        self._stdout_thread.start()
        if self._proc.stderr is not None:
            self._stderr_thread = threading.Thread(
                target=listen_stream, args=["stderr"], daemon=True
            )
            self._stderr_thread.start()

    def _finish_process(self):
        self.returncode = self._proc.wait()
        logger.debug("Process ended with returncode %s", self.returncode)
        if self.returncode:
            self.set_action_text("Error")
            self.append_text("Error: process returned with code %s\n" % self.returncode)
        else:
            self.set_action_text("Done!")
            self.append_text("Done!")

        self.report_done(self.returncode == 0)

    def get_action_text_max_length(self):
        return 35

    def _check_set_action_text_from_output_line(self, line):
        if len(line) > self.get_action_text_max_length():
            line = line[: self.get_action_text_max_length() - 3].strip() + "..."
        if line:
            self.set_action_text(line.strip())

    def cancel_work(self):
        super().cancel_work()
        # try gently first
        try:
            try:
                if running_on_windows():
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # pylint: disable=no-member
                else:
                    os.kill(self._proc.pid, signal.SIGINT)

                self._proc.wait(2)
            except subprocess.TimeoutExpired:
                if self._proc.poll() is None:
                    # now let's be more concrete
                    self._proc.kill()
        except OSError as e:
            messagebox.showerror("Error", "Could not kill subprocess: " + str(e), master=self)
            logger.error("Could not kill subprocess", exc_info=e)
