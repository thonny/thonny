# -*- coding: utf-8 -*-

"""Code for maintaining the background process and for running
user programs

Commands get executed via shell, this way the command line in the 
shell becomes kind of title for the execution.

"""


import collections
import logging
import os.path
import shlex
import shutil
import signal
import subprocess
import sys
import time
from logging import debug
from threading import Thread
from time import sleep

from tkinter import ttk

from thonny import THONNY_USER_DIR, common, get_runner, get_shell, get_workbench, ui_utils
from thonny.code import get_current_breakpoints, get_saved_current_script_filename, is_remote_path
from thonny.common import (
    BackendEvent,
    CommandToBackend,
    DebuggerCommand,
    DebuggerResponse,
    InlineCommand,
    InputSubmission,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    normpath_with_actual_case,
    is_same_path,
    parse_message,
    path_startswith,
    serialize_message,
    update_system_path,
    EOFCommand,
)
from thonny.misc_utils import construct_cmd_line, running_on_mac_os, running_on_windows

from typing import Any, List, Optional, Sequence, Set  # @UnusedImport; @UnusedImport
from thonny.terminal import run_in_terminal
from thonny.ui_utils import select_sequence, show_dialog, CommonDialogEx
from tkinter import messagebox
import warnings
import re
import traceback


WINDOWS_EXE = "python.exe"
OUTPUT_MERGE_THRESHOLD = 1000

RUN_COMMAND_LABEL = ""  # init later when gettext is ready
RUN_COMMAND_CAPTION = ""
EDITOR_CONTENT_TOKEN = "$EDITOR_CONTENT"

EXPECTED_TERMINATION_CODE = 123

ANSI_CODE_TERMINATOR = re.compile("[@-~]")

# other components may turn it on in order to avoid grouping output lines into one event
io_animation_required = False

_console_allocated = False


class Runner:
    def __init__(self) -> None:
        get_workbench().set_default("run.auto_cd", True)

        self._init_commands()
        self._state = "starting"
        self._proxy = None  # type: Any
        self._publishing_events = False
        self._polling_after_id = None
        self._postponed_commands = []  # type: List[CommandToBackend]

    def _remove_obsolete_jedi_copies(self) -> None:
        # Thonny 2.1 used to copy jedi in order to make it available
        # for the backend. Get rid of it now
        for item in os.listdir(THONNY_USER_DIR):
            if item.startswith("jedi_0."):
                shutil.rmtree(os.path.join(THONNY_USER_DIR, item), True)

    def start(self) -> None:
        global _console_allocated
        try:
            self._check_alloc_console()
            _console_allocated = True
        except Exception:
            logging.getLogger("thonny").exception("Problem allocating console")
            _console_allocated = False

        self.restart_backend(False, True)
        # temporary
        self._remove_obsolete_jedi_copies()

    def _init_commands(self) -> None:
        global RUN_COMMAND_CAPTION, RUN_COMMAND_LABEL

        RUN_COMMAND_LABEL = _("Run current script")
        RUN_COMMAND_CAPTION = _("Run")

        get_workbench().set_default("run.run_in_terminal_python_repl", False)
        get_workbench().set_default("run.run_in_terminal_keep_open", True)

        try:
            import thonny.plugins.debugger  # @UnusedImport

            debugger_available = True
        except ImportError:
            debugger_available = False

        get_workbench().add_command(
            "run_current_script",
            "run",
            RUN_COMMAND_LABEL,
            caption=RUN_COMMAND_CAPTION,
            handler=self.cmd_run_current_script,
            default_sequence="<F5>",
            extra_sequences=[select_sequence("<Control-r>", "<Command-r>")],
            tester=self.cmd_run_current_script_enabled,
            group=10,
            image="run-current-script",
            include_in_toolbar=not (get_workbench().in_simple_mode() and debugger_available),
            show_extra_sequences=True,
        )

        get_workbench().add_command(
            "run_current_script_in_terminal",
            "run",
            _("Run current script in terminal"),
            caption="RunT",
            handler=self._cmd_run_current_script_in_terminal,
            default_sequence="<Control-t>",
            extra_sequences=["<<CtrlTInText>>"],
            tester=self._cmd_run_current_script_in_terminal_enabled,
            group=35,
            image="terminal",
        )

        get_workbench().add_command(
            "restart",
            "run",
            _("Stop/Restart backend"),
            caption=_("Stop"),
            handler=self.cmd_stop_restart,
            default_sequence="<Control-F2>",
            group=100,
            image="stop",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "interrupt",
            "run",
            _("Interrupt execution"),
            handler=self._cmd_interrupt,
            tester=self._cmd_interrupt_enabled,
            default_sequence="<Control-c>",
            group=100,
            bell_when_denied=False,
        )

        get_workbench().add_command(
            "ctrld",
            "run",
            _("Send EOF / Soft reboot"),
            self.ctrld,
            self.ctrld_enabled,
            group=100,
            default_sequence="<Control-d>",
            extra_sequences=["<<CtrlDInText>>"],
        )

        get_workbench().add_command(
            "disconnect",
            "run",
            _("Disconnect"),
            self.disconnect,
            self.disconnect_enabled,
            group=100,
        )

    def get_state(self) -> str:
        """State is one of "running", "waiting_debugger_command", "waiting_toplevel_command"
        """
        return self._state

    def _set_state(self, state: str) -> None:
        if self._state != state:
            logging.debug("Runner state changed: %s ==> %s" % (self._state, state))
            self._state = state

    def is_running(self):
        return self._state == "running"

    def is_waiting(self):
        return self._state.startswith("waiting")

    def is_waiting_toplevel_command(self):
        return self._state == "waiting_toplevel_command"

    def is_waiting_debugger_command(self):
        return self._state == "waiting_debugger_command"

    def get_sys_path(self) -> List[str]:
        return self._proxy.get_sys_path()

    def send_command(self, cmd: CommandToBackend) -> None:
        if self._proxy is None:
            return

        if self._publishing_events:
            # allow all event handlers to complete before sending the commands
            # issued by first event handlers
            self._postpone_command(cmd)
            return

        # First sanity check
        if (
            isinstance(cmd, ToplevelCommand)
            and not self.is_waiting_toplevel_command()
            and cmd.name not in ["Reset", "Run", "Debug"]
            or isinstance(cmd, DebuggerCommand)
            and not self.is_waiting_debugger_command()
        ):
            get_workbench().bell()
            logging.warning(
                "RUNNER: Command %s was attempted at state %s" % (cmd, self.get_state())
            )
            return

        # Attach extra info
        if "debug" in cmd.name.lower():
            cmd["breakpoints"] = get_current_breakpoints()

        if "id" not in cmd:
            cmd["id"] = generate_command_id()

        cmd["local_cwd"] = get_workbench().get_local_cwd()

        # Offer the command
        logging.debug("RUNNER Sending: %s, %s", cmd.name, cmd)
        response = self._proxy.send_command(cmd)

        if response == "discard":
            return
        elif response == "postpone":
            self._postpone_command(cmd)
            return
        else:
            assert response is None
            get_workbench().event_generate("CommandAccepted", command=cmd)

        if isinstance(cmd, (ToplevelCommand, DebuggerCommand)):
            self._set_state("running")

        if cmd.name[0].isupper():
            get_workbench().event_generate("BackendRestart", full=False)

        if cmd.get("blocking"):
            dlg = BlockingDialog(get_workbench(), cmd)
            show_dialog(dlg)
            return dlg.response

    def _postpone_command(self, cmd: CommandToBackend) -> None:
        # in case of InlineCommands, discard older same type command
        if isinstance(cmd, InlineCommand):
            for older_cmd in self._postponed_commands:
                if older_cmd.name == cmd.name:
                    self._postponed_commands.remove(older_cmd)

        if len(self._postponed_commands) > 10:
            logging.warning("Can't pile up too many commands. This command will be just ignored")
        else:
            self._postponed_commands.append(cmd)

    def _send_postponed_commands(self) -> None:
        todo = self._postponed_commands
        self._postponed_commands = []

        for cmd in todo:
            logging.debug("Sending postponed command: %s", cmd)
            self.send_command(cmd)

    def send_program_input(self, data: str) -> None:
        assert self.is_running()
        self._proxy.send_program_input(data)

    def execute_script(
        self,
        script_path: str,
        args: List[str],
        working_directory: Optional[str] = None,
        command_name: str = "Run",
    ) -> None:

        if working_directory is not None and get_workbench().get_local_cwd() != working_directory:
            # create compound command
            # start with %cd
            cd_cmd_line = construct_cd_command(working_directory) + "\n"
            next_cwd = working_directory
        else:
            # create simple command
            cd_cmd_line = ""
            next_cwd = get_workbench().get_local_cwd()

        if not is_remote_path(script_path) and self._proxy.uses_local_filesystem():
            rel_filename = os.path.relpath(script_path, next_cwd)
            cmd_parts = ["%" + command_name, rel_filename] + args
        else:
            cmd_parts = ["%" + command_name, "-c", EDITOR_CONTENT_TOKEN] + args

        exe_cmd_line = construct_cmd_line(cmd_parts, [EDITOR_CONTENT_TOKEN]) + "\n"

        # submit to shell (shell will execute it)
        get_shell().submit_magic_command(cd_cmd_line + exe_cmd_line)

    def execute_current(self, command_name: str) -> None:
        """
        This method's job is to create a command for running/debugging
        current file/script and submit it to shell
        """

        if not self.is_waiting_toplevel_command():
            self.restart_backend(True, False, 2)

        filename = get_saved_current_script_filename()

        if not filename:
            # user has cancelled file saving
            return

        if is_remote_path(filename) or not self._proxy.uses_local_filesystem():
            working_directory = None
        else:
            # changing dir may be required
            script_dir = os.path.dirname(filename)

            if get_workbench().get_option("run.auto_cd") and command_name[0].isupper():
                working_directory = script_dir  # type: Optional[str]
            else:
                working_directory = None

        args = self._get_active_arguments()

        self.execute_script(filename, args, working_directory, command_name)

    def _get_active_arguments(self):
        if get_workbench().get_option("view.show_program_arguments"):
            args_str = get_workbench().get_option("run.program_arguments")
            get_workbench().log_program_arguments_string(args_str)
            return shlex.split(args_str)
        else:
            return []

    def cmd_run_current_script_enabled(self) -> bool:
        return (
            get_workbench().get_editor_notebook().get_current_editor() is not None
            and "run" in get_runner().get_supported_features()
        )

    def _cmd_run_current_script_in_terminal_enabled(self) -> bool:
        return (
            self._proxy
            and "run_in_terminal" in self._proxy.get_supported_features()
            and self.cmd_run_current_script_enabled()
        )

    def cmd_run_current_script(self) -> None:
        if get_workbench().in_simple_mode():
            get_workbench().hide_view("VariablesView")
        self.execute_current("Run")

    def _cmd_run_current_script_in_terminal(self) -> None:
        filename = get_saved_current_script_filename()
        self._proxy.run_script_in_terminal(
            filename,
            self._get_active_arguments(),
            get_workbench().get_option("run.run_in_terminal_python_repl"),
            get_workbench().get_option("run.run_in_terminal_keep_open"),
        )

    def _cmd_interrupt(self) -> None:
        if self._proxy is not None:
            if _console_allocated:
                self._proxy.interrupt()
            else:
                messagebox.showerror(
                    "No console",
                    "Can't interrupt as console was not allocated.\n\nUse Stop/Restart instead.",
                )
        else:
            logging.warning("Interrupting without proxy")

    def _cmd_interrupt_enabled(self) -> bool:
        if not self._proxy or not self._proxy.is_connected():
            return False
        # TODO: distinguish command and Ctrl+C shortcut

        widget = get_workbench().focus_get()
        if not running_on_mac_os():  # on Mac Ctrl+C is not used for Copy
            if widget is not None and hasattr(widget, "selection_get"):
                try:
                    selection = widget.selection_get()
                    if isinstance(selection, str) and len(selection) > 0:
                        # assuming user meant to copy, not interrupt
                        # (IDLE seems to follow same logic)
                        return False
                except Exception:
                    # selection_get() gives error when calling without selection on Ubuntu
                    pass

        return self.is_running() or self.is_waiting_toplevel_command()

    def cmd_stop_restart(self) -> None:
        if get_workbench().in_simple_mode():
            get_workbench().hide_view("VariablesView")

        self.restart_backend(True)

    def disconnect(self):
        proxy = self.get_backend_proxy()
        assert hasattr(proxy, "disconnect")
        proxy.disconnect()

    def disconnect_enabled(self):
        return hasattr(self.get_backend_proxy(), "disconnect")

    def ctrld(self):
        proxy = self.get_backend_proxy()
        if not proxy:
            return

        if get_shell().has_pending_input():
            messagebox.showerror(
                "Can't perform this action",
                "Ctrl+D only has effect on an empty line / prompt.\n"
                + "Submit current input (press ENTER) and try again",
            )
            return

        proxy.send_command(EOFCommand())
        self._set_state("running")

    def ctrld_enabled(self):
        proxy = self.get_backend_proxy()
        return proxy and proxy.is_connected()

    def _poll_vm_messages(self) -> None:
        """I chose polling instead of event_generate in listener thread,
        because event_generate across threads is not reliable
        http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        """
        self._polling_after_id = None
        if self._pull_vm_messages() is False:
            return

        self._polling_after_id = get_workbench().after(20, self._poll_vm_messages)

    def _pull_vm_messages(self):
        while self._proxy is not None:
            try:
                msg = self._proxy.fetch_next_message()
                if not msg:
                    break
                logging.debug(
                    "RUNNER GOT: %s, %s in state: %s", msg.event_type, msg, self.get_state()
                )

            except BackendTerminatedError as exc:
                self._report_backend_crash(exc)
                self.destroy_backend()
                return False

            if msg.get("SystemExit", False):
                self.restart_backend(True)
                return False

            # change state
            if isinstance(msg, ToplevelResponse):
                self._set_state("waiting_toplevel_command")
            elif isinstance(msg, DebuggerResponse):
                self._set_state("waiting_debugger_command")
            else:
                "other messages don't affect the state"

            if "cwd" in msg:
                if not self.supports_remote_files():
                    get_workbench().set_local_cwd(msg["cwd"])

            # Publish the event
            # NB! This may cause another command to be sent before we get to postponed commands.
            try:
                self._publishing_events = True
                class_event_type = type(msg).__name__
                get_workbench().event_generate(class_event_type, event=msg)  # more general event
                if msg.event_type != class_event_type:
                    # more specific event
                    get_workbench().event_generate(msg.event_type, event=msg)
            finally:
                self._publishing_events = False

            # TODO: is it necessary???
            # https://stackoverflow.com/a/13520271/261181
            # get_workbench().update()

        self._send_postponed_commands()

    def _report_backend_crash(self, exc: Exception) -> None:
        returncode = getattr(exc, "returncode", "?")
        err = "Backend terminated or disconnected."

        try:
            faults_file = os.path.join(THONNY_USER_DIR, "backend_faults.log")
            if os.path.exists(faults_file):
                with open(faults_file, encoding="ASCII") as fp:
                    err += fp.read()
        except Exception:
            logging.exception("Failed retrieving backend faults")

        err = err.strip() + " Use 'Stop/Restart' to restart.\n"

        if returncode != EXPECTED_TERMINATION_CODE:
            get_workbench().event_generate("ProgramOutput", stream_name="stderr", data="\n" + err)

        get_workbench().become_active_window(False)

    def restart_backend(self, clean: bool, first: bool = False, wait: float = 0) -> None:
        """Recreate (or replace) backend proxy / backend process."""

        if not first:
            get_shell().restart()
            get_shell().update_idletasks()

        self.destroy_backend()
        backend_name = get_workbench().get_option("run.backend_name")
        if backend_name not in get_workbench().get_backends():
            raise UserError(
                "Can't find backend '{}'. Please select another backend from options".format(
                    backend_name
                )
            )

        backend_class = get_workbench().get_backends()[backend_name].proxy_class
        self._set_state("running")
        self._proxy = None
        self._proxy = backend_class(clean)

        self._poll_vm_messages()

        if wait:
            start_time = time.time()
            while not self.is_waiting_toplevel_command() and time.time() - start_time <= wait:
                # self._pull_vm_messages()
                get_workbench().update()
                sleep(0.01)

        get_workbench().event_generate("BackendRestart", full=True)

    def destroy_backend(self) -> None:
        if self._polling_after_id is not None:
            get_workbench().after_cancel(self._polling_after_id)
            self._polling_after_id = None

        self._postponed_commands = []
        if self._proxy:
            self._proxy.destroy()
            self._proxy = None

        get_workbench().event_generate("BackendTerminated")

    def get_local_executable(self) -> Optional[str]:
        if self._proxy is None:
            return None
        else:
            return self._proxy.get_local_executable()

    def get_backend_proxy(self) -> "BackendProxy":
        return self._proxy

    def _check_alloc_console(self) -> None:
        if sys.executable.endswith("pythonw.exe"):
            # These don't have console allocated.
            # Console is required for sending interrupts.

            # AllocConsole would be easier but flashes console window

            import ctypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

            exe = sys.executable.replace("pythonw.exe", "python.exe")

            cmd = [exe, "-c", "print('Hi!'); input()"]
            child = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            child.stdout.readline()
            result = kernel32.AttachConsole(child.pid)
            if not result:
                err = ctypes.get_last_error()
                logging.info("Could not allocate console. Error code: " + str(err))
            child.stdin.write(b"\n")
            try:
                child.stdin.flush()
            except Exception:
                # May happen eg. when installation path has "&" in it
                # See https://bitbucket.org/plas/thonny/issues/508/cant-allocate-windows-console-when
                # Without flush the console window becomes visible, but Thonny can be still used
                logging.getLogger("thonny").exception("Problem with finalizing console allocation")

    def ready_for_remote_file_operations(self, show_message=False):
        if not self._proxy or not self.supports_remote_files():
            return False

        ready = self._proxy.ready_for_remote_file_operations()

        if not ready and show_message:
            if self._proxy.is_connected():
                msg = "Device is not connected"
            else:
                msg = (
                    "Device is busy -- can't perform this action now."
                    + "\nPlease wait or cancel current work and try again!",
                )
            messagebox.showerror("Can't complete", msg)

        return ready

    def get_supported_features(self) -> Set[str]:
        if self._proxy is None:
            return set()
        else:
            return self._proxy.get_supported_features()

    def supports_remote_files(self):
        if self._proxy is None:
            return False
        else:
            return self._proxy.supports_remote_files()

    def supports_remote_directories(self):
        if self._proxy is None:
            return False
        else:
            return self._proxy.supports_remote_directories()

    def get_node_label(self):
        if self._proxy is None:
            return "Back-end"
        else:
            return self._proxy.get_node_label()

    def using_venv(self) -> bool:
        return isinstance(self._proxy, CPythonProxy) and self._proxy._in_venv


class BackendProxy:
    """Communicates with backend process.
    
    All communication methods must be non-blocking, 
    ie. suitable for calling from GUI thread."""

    # backend_name will be overwritten on Workbench.add_backend
    # Subclasses don't need to worry about it.
    backend_name = None

    def __init__(self, clean: bool) -> None:
        """Initializes (or starts the initialization of) the backend process.
        
        Backend is considered ready when the runner gets a ToplevelResponse
        with attribute "welcome_text" from fetch_next_message.
        """

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        """Send the command to backend. Return None, 'discard' or 'postpone'"""
        raise NotImplementedError()

    def send_program_input(self, data: str) -> None:
        """Send input data to backend"""
        raise NotImplementedError()

    def fetch_next_message(self):
        """Read next message from the queue or None if queue is empty"""
        raise NotImplementedError()

    def run_script_in_terminal(self, script_path, interactive, keep_open):
        raise NotImplementedError()

    def get_sys_path(self):
        "backend's sys.path"
        return []

    def get_backend_name(self):
        return type(self).backend_name

    def interrupt(self):
        """Tries to interrupt current command without reseting the backend"""
        pass

    def destroy(self):
        """Called when Thonny no longer needs this instance 
        (Thonny gets closed or new backend gets selected)
        """
        pass

    def is_connected(self):
        return True

    def get_local_executable(self):
        """Return system command for invoking current interpreter"""
        return None

    def get_supported_features(self):
        return {"run"}

    def get_node_label(self):
        """Used as files caption if back-end has separate files"""
        return "Back-end"

    def supports_remote_files(self):
        """Whether remote file browser should be presented with this back-end"""
        return False

    def uses_local_filesystem(self):
        """Whether it runs code from local files"""
        return True

    def supports_remote_directories(self):
        return False

    def supports_trash(self):
        return True

    def ready_for_remote_file_operations(self):
        return False

    def get_cwd(self):
        return None


class SubprocessProxy(BackendProxy):
    def __init__(self, clean: bool, executable: str) -> None:
        super().__init__(clean)

        self._executable = executable
        self._response_queue = None
        self._welcome_text = ""

        self._proc = None
        self._response_queue = None
        self._sys_path = []
        self._usersitepackages = None
        self._gui_update_loop_id = None
        self._in_venv = None
        self._cwd = self._get_initial_cwd()
        self._start_background_process(clean=clean)

    def _get_initial_cwd(self):
        return None

    def _start_background_process(self, clean=None):
        # deque, because in one occasion I need to put messages back
        self._response_queue = collections.deque()

        # prepare environment
        env = get_environment_for_python_subprocess(self._executable)
        # variables controlling communication with the back-end process
        env["PYTHONIOENCODING"] = "utf-8"

        # because cmd line option -u won't reach child processes
        # see https://github.com/thonny/thonny/issues/808
        env["PYTHONUNBUFFERED"] = "1"

        # Let back-end know about plug-ins
        env["THONNY_USER_DIR"] = THONNY_USER_DIR
        env["THONNY_FRONTEND_SYS_PATH"] = repr(sys.path)

        env["THONNY_LANGUAGE"] = get_workbench().get_option("general.language")
        env["FRIENDLY_TRACEBACK_LEVEL"] = str(
            get_workbench().get_option("assistance.friendly_traceback_level")
        )

        if get_workbench().in_debug_mode():
            env["THONNY_DEBUG"] = "1"
        elif "THONNY_DEBUG" in env:
            del env["THONNY_DEBUG"]

        if not os.path.exists(self._executable):
            raise UserError(
                "Interpreter (%s) not found. Please recheck corresponding option!"
                % self._executable
            )

        cmd_line = [
            self._executable,
            "-u",  # unbuffered IO
            "-B",  # don't write pyo/pyc files
            # (to avoid problems when using different Python versions without write permissions)
        ] + self._get_launcher_with_args()

        creationflags = 0
        if running_on_windows():
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        debug("Starting the backend: %s %s", cmd_line, get_workbench().get_local_cwd())

        extra_params = {}
        if sys.version_info >= (3, 6):
            extra_params["encoding"] = "utf-8"

        self._proc = subprocess.Popen(
            cmd_line,
            bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.get_cwd() if self.uses_local_filesystem() else None,
            env=env,
            universal_newlines=True,
            creationflags=creationflags,
            **extra_params
        )

        # setup asynchronous output listeners
        Thread(target=self._listen_stdout, args=(self._proc.stdout,), daemon=True).start()
        Thread(target=self._listen_stderr, args=(self._proc.stderr,), daemon=True).start()

    def _get_launcher_with_args(self):
        raise NotImplementedError()

    def send_command(self, cmd: CommandToBackend) -> Optional[str]:
        """Send the command to backend. Return None, 'discard' or 'postpone'"""
        method_name = "_cmd_" + cmd.name
        if hasattr(self, method_name):
            return getattr(self, method_name)(cmd)

        if isinstance(cmd, ToplevelCommand) and cmd.name[0].isupper():
            self._clear_environment()

        self._send_msg(cmd)

    def _send_msg(self, msg):
        self._proc.stdin.write(serialize_message(msg) + "\n")
        self._proc.stdin.flush()

    def _clear_environment(self):
        pass

    def send_program_input(self, data):
        self._send_msg(InputSubmission(data))

    def process_is_alive(self):
        return self._proc is not None and self._proc.poll() is None

    def is_connected(self):
        return self.process_is_alive()

    def get_sys_path(self):
        return self._sys_path

    def interrupt(self):
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                except Exception:
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)

    def destroy(self):
        self._close_backend()

    def _close_backend(self):
        if self._proc is not None and self._proc.poll() is None:
            self._proc.kill()

        self._proc = None
        self._response_queue = None

    def _listen_stdout(self, stdout):
        # debug("... started listening to stdout")
        # will be called from separate thread

        message_queue = self._response_queue

        def publish_as_msg(data):
            msg = parse_message(data)
            if "cwd" in msg:
                self.cwd = msg["cwd"]
            message_queue.append(msg)

            if len(message_queue) > 50:
                # Probably backend runs an infinite/long print loop.
                # Throttle message thougput in order to keep GUI thread responsive.
                while len(message_queue) > 0:
                    sleep(0.1)

        while self.process_is_alive():
            data = stdout.readline()
            # debug("... read some stdout data", repr(data))
            if data == "":
                break
            else:
                try:
                    publish_as_msg(data)
                except Exception:
                    # Can mean the line was from subprocess,
                    # which can't be captured by stream faking.
                    # NB! If subprocess printed it without linebreak,
                    # then the suffix can be thonny message

                    parts = data.rsplit(common.MESSAGE_MARKER, maxsplit=1)

                    # print first part as it is
                    message_queue.append(
                        BackendEvent("ProgramOutput", data=parts[0], stream_name="stdout")
                    )

                    if len(parts) == 2:
                        second_part = common.MESSAGE_MARKER + parts[1]
                        try:
                            publish_as_msg(second_part)
                        except Exception:
                            # just print ...
                            message_queue.append(
                                BackendEvent(
                                    "ProgramOutput", data=second_part, stream_name="stdout"
                                )
                            )

    def _listen_stderr(self, stderr):
        # stderr is used only for debugger debugging
        while self.process_is_alive():
            data = stderr.readline()
            if data == "":
                break
            else:
                self._response_queue.append(
                    BackendEvent("ProgramOutput", stream_name="stderr", data=data)
                )

    def _store_state_info(self, msg):
        if "cwd" in msg:
            self._cwd = msg["cwd"]

        if "welcome_text" in msg:
            self._welcome_text = msg["welcome_text"]

        if "in_venv" in msg:
            self._in_venv = msg["in_venv"]

        if "path" in msg:
            self._sys_path = msg["path"]

        if "usersitepackages" in msg:
            self._usersitepackages = msg["usersitepackages"]

        if "prefix" in msg:
            self._sys_prefix = msg["prefix"]

        if "exe_dirs" in msg:
            self._exe_dirs = msg["exe_dirs"]

    def get_supported_features(self):
        return {"run"}

    def get_site_packages(self):
        # NB! site.sitepackages may not be present in virtualenv
        for d in self._sys_path:
            if ("site-packages" in d or "dist-packages" in d) and path_startswith(
                d, self._sys_prefix
            ):
                return d

        return None

    def get_user_site_packages(self):
        return self._usersitepackages

    def get_cwd(self):
        return self._cwd

    def get_exe_dirs(self):
        return self._exe_dirs

    def fetch_next_message(self):
        if not self._response_queue or len(self._response_queue) == 0:
            if not self.process_is_alive():
                raise BackendTerminatedError(self._proc.returncode if self._proc else None)
            else:
                return None

        msg = self._response_queue.popleft()
        self._store_state_info(msg)

        if msg.event_type == "ProgramOutput":
            # combine available small output messages to one single message,
            # in order to put less pressure on UI code

            wait_time = 0.01
            total_wait_time = 0
            while True:
                if len(self._response_queue) == 0:
                    if _ends_with_incomplete_ansi_code(msg["data"]) and total_wait_time < 0.1:
                        # Allow reader to send the remaining part
                        sleep(wait_time)
                        total_wait_time += wait_time
                        continue
                    else:
                        return msg
                else:
                    next_msg = self._response_queue.popleft()
                    if (
                        next_msg.event_type == "ProgramOutput"
                        and next_msg["stream_name"] == msg["stream_name"]
                        and (
                            len(msg["data"]) + len(next_msg["data"]) <= OUTPUT_MERGE_THRESHOLD
                            and ("\n" not in msg["data"] or not io_animation_required)
                            or _ends_with_incomplete_ansi_code(msg["data"])
                        )
                    ):
                        msg["data"] += next_msg["data"]
                    else:
                        # not to be sent in the same block, put it back
                        self._response_queue.appendleft(next_msg)
                        return msg

        else:
            return msg


def _ends_with_incomplete_ansi_code(data):
    pos = data.rfind("\033")
    if pos == -1:
        return False

    # note ANSI_CODE_TERMINATOR also includes [
    params_and_terminator = data[pos + 2 :]
    return not ANSI_CODE_TERMINATOR.search(params_and_terminator)


class CPythonProxy(SubprocessProxy):
    "abstract class"

    def __init__(self, clean: bool, executable: str) -> None:
        super().__init__(clean, executable)
        self._send_msg(ToplevelCommand("get_environment_info"))

    def _get_initial_cwd(self):
        return get_workbench().get_local_cwd()

    def _get_launcher_with_args(self):
        import thonny.backend_launcher

        return [thonny.backend_launcher.__file__]

    def _store_state_info(self, msg):
        super()._store_state_info(msg)

        if "gui_is_active" in msg:
            self._update_gui_updating(msg)

    def _clear_environment(self):
        self._close_backend()
        self._start_background_process()

    def _close_backend(self):
        self._cancel_gui_update_loop()
        super()._close_backend()

    def get_local_executable(self):
        return self._executable

    def _update_gui_updating(self, msg):
        """Enables running Tkinter or Qt programs which doesn't call mainloop. 
        
        When mainloop is omitted, then program can be interacted with
        from the shell after it runs to the end.
        
        Each ToplevelResponse is supposed to tell, whether gui is active
        and needs updating.
        """
        if not "gui_is_active" in msg:
            return

        if msg["gui_is_active"] and self._gui_update_loop_id is None:
            # Start updating
            self._loop_gui_update(True)
        elif not msg["gui_is_active"] and self._gui_update_loop_id is not None:
            self._cancel_gui_update_loop()

    def _loop_gui_update(self, force=False):
        if force or get_runner().is_waiting_toplevel_command():
            try:
                self.send_command(InlineCommand("process_gui_events"))
            except OSError:
                # the backend process may have been closed already
                # https://github.com/thonny/thonny/issues/966
                logging.getLogger("thonny").exception("Could not send process_gui_events")

        self._gui_update_loop_id = get_workbench().after(50, self._loop_gui_update)

    def _cancel_gui_update_loop(self):
        if self._gui_update_loop_id is not None:
            try:
                get_workbench().after_cancel(self._gui_update_loop_id)
            finally:
                self._gui_update_loop_id = None

    def run_script_in_terminal(self, script_path, args, interactive, keep_open):
        cmd = [self._executable]
        if interactive:
            cmd.append("-i")
        cmd.append(os.path.basename(script_path))
        cmd.extend(args)

        run_in_terminal(cmd, os.path.dirname(script_path), keep_open=keep_open)

    def get_supported_features(self):
        return {"run", "debug", "run_in_terminal", "pip_gui", "system_shell"}


class PrivateVenvCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        self._prepare_private_venv()
        super().__init__(clean, get_private_venv_executable())

    def _prepare_private_venv(self):
        path = get_private_venv_path()
        if os.path.isdir(path) and os.path.isfile(os.path.join(path, "pyvenv.cfg")):
            self._check_upgrade_private_venv(path)
        else:
            self._create_private_venv(
                path, "Please wait!\nThonny prepares its virtual environment."
            )

    def _check_upgrade_private_venv(self, path):
        # If home is wrong then regenerate
        # If only micro version is different, then upgrade
        info = _get_venv_info(path)

        if not is_same_path(info["home"], os.path.dirname(sys.executable)):
            self._create_private_venv(
                path,
                "Thonny's virtual environment was created for another interpreter.\n"
                + "Regenerating the virtual environment for current interpreter.\n"
                + "(You may need to reinstall your 3rd party packages)\n"
                + "Please wait!.",
                clear=True,
            )
        else:
            venv_version = tuple(map(int, info["version"].split(".")))
            sys_version = sys.version_info[:3]
            assert venv_version[0] == sys_version[0]
            assert venv_version[1] == sys_version[1]

            if venv_version[2] != sys_version[2]:
                self._create_private_venv(
                    path, "Please wait!\nUpgrading Thonny's virtual environment.", upgrade=True
                )

    def _create_private_venv(self, path, description, clear=False, upgrade=False):
        # Don't include system site packages
        # This way all students will have similar configuration
        # independently of system Python (if Thonny is used with system Python)

        # NB! Cant run venv.create directly, because in Windows bundle
        # it tries to link venv to thonny.exe.
        # Need to run it via proper python
        args = ["-m", "venv"]
        if clear:
            args.append("--clear")
        if upgrade:
            args.append("--upgrade")

        try:
            # pylint: disable=unused-variable
            import ensurepip  # @UnusedImport
        except ImportError:
            args.append("--without-pip")

        args.append(path)

        proc = create_frontend_python_process(args)

        from thonny.ui_utils import SubprocessDialog

        dlg = SubprocessDialog(
            get_workbench(), proc, "Preparing the backend", long_description=description
        )
        try:
            ui_utils.show_dialog(dlg)
        except Exception:
            # if using --without-pip the dialog may close very quickly
            # and for some reason wait_window would give error then
            logging.exception("Problem with waiting for venv creation dialog")
        get_workbench().become_active_window()  # Otherwise focus may get stuck somewhere

        bindir = os.path.dirname(get_private_venv_executable())
        # create private env marker
        marker_path = os.path.join(bindir, "is_private")
        with open(marker_path, mode="w") as fp:
            fp.write("# This file marks Thonny-private venv")

        # Create recommended pip conf to get rid of list deprecation warning
        # https://github.com/pypa/pip/issues/4058
        pip_conf = "pip.ini" if running_on_windows() else "pip.conf"
        with open(os.path.join(path, pip_conf), mode="w") as fp:
            fp.write("[list]\nformat = columns")

        assert os.path.isdir(path)


class SameAsFrontendCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        super().__init__(clean, get_interpreter_for_subprocess())

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            if is_bundled_python(self._executable):
                msg["welcome_text"] += " (bundled)"
            else:
                msg["welcome_text"] += " (" + self._executable + ")"
        return msg


class CustomCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        executable = get_workbench().get_option("CustomInterpreter.path")

        # Rembember the usage of this non-default interpreter
        used_interpreters = get_workbench().get_option("CustomInterpreter.used_paths")
        if executable not in used_interpreters:
            used_interpreters.append(executable)
        get_workbench().set_option("CustomInterpreter.used_paths", used_interpreters)

        super().__init__(clean, get_interpreter_for_subprocess(executable))

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            msg["welcome_text"] += " (" + self._executable + ")"
        return msg


def get_private_venv_path():
    if is_bundled_python(sys.executable.lower()):
        prefix = "BundledPython"
    else:
        prefix = "Python"
    return os.path.join(
        THONNY_USER_DIR, prefix + "%d%d" % (sys.version_info[0], sys.version_info[1])
    )


def get_private_venv_executable():
    venv_path = get_private_venv_path()

    if running_on_windows():
        exe = os.path.join(venv_path, "Scripts", WINDOWS_EXE)
    else:
        exe = os.path.join(venv_path, "bin", "python3")

    return exe


def _get_venv_info(venv_path):
    cfg_path = os.path.join(venv_path, "pyvenv.cfg")
    result = {}

    with open(cfg_path, encoding="UTF-8") as fp:
        for line in fp:
            if "=" in line:
                key, val = line.split("=", maxsplit=1)
                result[key.strip()] = val.strip()

    return result


def is_bundled_python(executable):
    return os.path.exists(os.path.join(os.path.dirname(executable), "thonny_python.ini"))


def create_backend_python_process(
    args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
):
    """Used for running helper commands (eg. pip) on CPython backend.
    Assumes current backend is CPython."""

    # TODO: if backend == frontend, then delegate to create_frontend_python_process

    python_exe = get_runner().get_local_executable()

    env = get_environment_for_python_subprocess(python_exe)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    # TODO: remove frontend python from path and add backend python to it

    return _create_python_process(python_exe, args, stdin, stdout, stderr, env=env)


def create_frontend_python_process(
    args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
):
    """Used for running helper commands (eg. for installing plug-ins on by the plug-ins)"""
    if _console_allocated:
        python_exe = get_interpreter_for_subprocess().replace("pythonw.exe", "python.exe")
    else:
        python_exe = get_interpreter_for_subprocess().replace("python.exe", "pythonw.exe")
    env = get_environment_for_python_subprocess(python_exe)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return _create_python_process(python_exe, args, stdin, stdout, stderr)


def _create_python_process(
    python_exe,
    args,
    stdin=None,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    shell=False,
    env=None,
    universal_newlines=True,
):

    cmd = [python_exe] + args

    if running_on_windows():
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    else:
        startupinfo = None
        creationflags = 0

    proc = subprocess.Popen(
        cmd,
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
        shell=shell,
        env=env,
        universal_newlines=universal_newlines,
        startupinfo=startupinfo,
        creationflags=creationflags,
    )

    proc.cmd = cmd
    return proc


class BackendTerminatedError(Exception):
    def __init__(self, returncode=None):
        Exception.__init__(self)
        self.returncode = returncode


def is_venv_interpreter_of_current_interpreter(executable):
    for location in [".", ".."]:
        cfg_path = os.path.join(location, "pyvenv.cfg")
        if os.path.isfile(cfg_path):
            with open(cfg_path) as fp:
                content = fp.read()
            for line in content.splitlines():
                if line.replace(" ", "").startswith("home="):
                    _, home = line.split("=", maxsplit=1)
                    home = home.strip()
                    if os.path.isdir(home) and os.path.samefile(home, sys.prefix):
                        return True
    return False


def get_environment_for_python_subprocess(target_executable):
    overrides = get_environment_overrides_for_python_subprocess(target_executable)
    return get_environment_with_overrides(overrides)


def get_environment_with_overrides(overrides):
    env = os.environ.copy()
    for key in overrides:
        if overrides[key] is None and key in env:
            del env[key]
        else:
            assert isinstance(overrides[key], str)
            if key.upper() == "PATH":
                update_system_path(env, overrides[key])
            else:
                env[key] = overrides[key]
    return env


def get_environment_overrides_for_python_subprocess(target_executable):
    """Take care of not not confusing different interpreter 
    with variables meant for bundled interpreter"""

    # At the moment I'm tweaking the environment only if current
    # exe is bundled for Thonny.
    # In remaining cases it is user's responsibility to avoid
    # calling Thonny with environment which may be confusing for
    # different Pythons called in a subprocess.

    this_executable = sys.executable.replace("pythonw.exe", "python.exe")
    target_executable = target_executable.replace("pythonw.exe", "python.exe")

    interpreter_specific_keys = [
        "TCL_LIBRARY",
        "TK_LIBRARY",
        "LD_LIBRARY_PATH",
        "DYLD_LIBRARY_PATH",
        "SSL_CERT_DIR",
        "SSL_CERT_FILE",
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONNOUSERSITE",
        "PYTHONUSERBASE",
    ]

    result = {}

    if os.path.samefile(
        target_executable, this_executable
    ) or is_venv_interpreter_of_current_interpreter(target_executable):
        # bring out some important variables so that they can
        # be explicitly set in macOS Terminal
        # (If they are set then it's most likely because current exe is in Thonny bundle)
        for key in interpreter_specific_keys:
            if key in os.environ:
                result[key] = os.environ[key]

        # never pass some variables to different interpreter
        # (even if it's venv or symlink to current one)
        if not is_same_path(target_executable, this_executable):
            for key in ["PYTHONPATH", "PYTHONHOME", "PYTHONNOUSERSITE", "PYTHONUSERBASE"]:
                if key in os.environ:
                    result[key] = None
    else:
        # interpreters are not related
        # interpreter specific keys most likely would confuse other interpreter
        for key in interpreter_specific_keys:
            if key in os.environ:
                result[key] = None

    # some keys should be never passed
    for key in [
        "PYTHONSTARTUP",
        "PYTHONBREAKPOINT",
        "PYTHONDEBUG",
        "PYTHONNOUSERSITE",
        "PYTHONASYNCIODEBUG",
    ]:
        if key in os.environ:
            result[key] = None

    # venv may not find (correct) Tk without assistance (eg. in Ubuntu)
    if is_venv_interpreter_of_current_interpreter(target_executable):
        try:
            if "TCL_LIBRARY" not in os.environ or "TK_LIBRARY" not in os.environ:
                result["TCL_LIBRARY"] = get_workbench().tk.exprstring("$tcl_library")
                result["TK_LIBRARY"] = get_workbench().tk.exprstring("$tk_library")
        except Exception:
            logging.exception("Can't compute Tcl/Tk library location")

    return result


def construct_cd_command(path):
    return construct_cmd_line(["%cd", normpath_with_actual_case(path)])


_command_id_counter = 0


def generate_command_id():
    global _command_id_counter
    _command_id_counter += 1
    return "cmd_" + str(_command_id_counter)


class BlockingDialog(CommonDialogEx):
    def __init__(self, master, cmd, mode="indeterminate"):
        super().__init__(master)
        self.title(_("Working..."))
        self.response = None
        self._sent_interrupt = False
        self._mode = mode

        self._cmd_id = cmd["id"]

        description = cmd.get("description", str(cmd))

        self._description_label = ttk.Label(self.main_frame, text=description)
        self._description_label.grid(row=0, column=0, padx=10, pady=10, sticky="new")

        self._progress_bar = ttk.Progressbar(self.main_frame, mode=self._mode, length=200)
        self._progress_bar.grid(row=1, column=0, padx=10, sticky="new")
        self._progress_bar.start()

        self._cancel_button = ttk.Button(self.main_frame, text=_("Cancel"), command=self._on_cancel)
        self._cancel_button.grid(row=2, column=0, padx=10, pady=10)

        self._start_time = time.time()

        if isinstance(cmd, InlineCommand):
            get_workbench().bind("InlineResponse", self._on_response, True)
            get_workbench().bind("InlineProgress", self._on_progress, True)
        else:
            raise NotImplementedError()

    def _on_response(self, event):
        self.response = event

        if event.get("command_id") == self._cmd_id:
            self.destroy()

        if event.get("error") and not event.get("interrupted"):
            messagebox.showerror("Error", event.get("error"))

    def _on_progress(self, event):
        if event.get("command_id") != self._cmd_id:
            return

        if self._mode == "indeterminate":
            self._progress_bar.stop()
            self._mode = "determinate"
            self._progress_bar.configure(mode=self._mode)
        self._progress_bar.configure(maximum=event["maximum"], value=event["value"])

    def _send_interrupt(self):
        self._sent_interrupt = True
        self._description_label.configure(text="Cancelling...")
        self._cancel_button.configure(text=_("Close"))
        get_runner()._cmd_interrupt()

    def on_close(self, event=None):
        self._on_cancel()

    def _on_cancel(self):
        if self._sent_interrupt:
            if messagebox.askyesno(
                "Interrupt again?",
                "Do you want to close this dialog without waiting cancelling to complete?",
            ):
                self.destroy()
            else:
                self._send_interrupt()

        else:
            if messagebox.askyesno(
                "Cancel current operation?", "Do you really want to cancel this operation?"
            ):
                self._send_interrupt()


def get_frontend_python():
    # TODO: deprecated (name can be misleading)
    warnings.warn("get_frontend_python is deprecated")
    return get_interpreter_for_subprocess(sys.executable)


def get_interpreter_for_subprocess(candidate=None):
    if candidate is None:
        candidate = sys.executable

    pythonw = candidate.replace("python.exe", "pythonw.exe")
    if not _console_allocated and os.path.exists(pythonw):
        return pythonw
    else:
        return candidate.replace("pythonw.exe", "python.exe")
