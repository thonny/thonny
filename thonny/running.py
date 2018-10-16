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
import traceback
from logging import debug
from threading import Thread
from time import sleep

from thonny import (
    THONNY_USER_DIR,
    common,
    get_runner,
    get_shell,
    get_workbench,
    ui_utils,
)
from thonny.code import get_current_breakpoints
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
)
from thonny.misc_utils import construct_cmd_line, running_on_mac_os, running_on_windows

from typing import Any, List, Optional, Sequence, Set  # @UnusedImport; @UnusedImport


WINDOWS_EXE = "python.exe"


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
        self._check_alloc_console()
        self.restart_backend(False, True)
        # temporary
        self._remove_obsolete_jedi_copies()

    def _init_commands(self) -> None:
        get_workbench().add_command(
            "run_current_script",
            "run",
            "Run current script",
            caption="Run",
            handler=self._cmd_run_current_script,
            default_sequence="<F5>",
            tester=self._cmd_run_current_script_enabled,
            group=10,
            image="run-current-script",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "restart",
            "run",
            "Stop/Restart backend",
            caption="Stop",
            handler=self.cmd_stop_restart,
            default_sequence="<Control-F2>",
            group=70,
            image="stop",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "interrupt",
            "run",
            "Interrupt execution",
            handler=self._cmd_interrupt,
            tester=self._cmd_interrupt_enabled,
            default_sequence="<Control-c>",
            group=70,
            bell_when_denied=False,
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
            get_workbench().event_generate("BackendRestart")

    def _postpone_command(self, cmd: CommandToBackend) -> None:
        # in case of InlineCommands, discard older same type command
        if isinstance(cmd, InlineCommand):
            for older_cmd in self._postponed_commands:
                if older_cmd.name == cmd.name:
                    self._postponed_commands.remove(older_cmd)

        if len(self._postponed_commands) > 10:
            logging.warning(
                "Can't pile up too many commands. This command will be just ignored"
            )
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
        if (
            working_directory is not None
            and get_workbench().get_cwd() != working_directory
        ):
            # create compound command
            # start with %cd
            cd_cmd_line = construct_cmd_line(["%cd", working_directory]) + "\n"
            next_cwd = working_directory
        else:
            # create simple command
            cd_cmd_line = ""
            next_cwd = get_workbench().get_cwd()

        # append main command (Run, run, Debug or debug)
        rel_filename = os.path.relpath(script_path, next_cwd)
        exe_cmd_line = (
            construct_cmd_line(["%" + command_name, rel_filename] + args) + "\n"
        )

        # submit to shell (shell will execute it)
        get_shell().submit_magic_command(cd_cmd_line + exe_cmd_line)

    def execute_current(
        self, command_name: str, always_change_to_script_dir: bool = False
    ) -> None:
        """
        This method's job is to create a command for running/debugging
        current file/script and submit it to shell
        """

        if not self.is_waiting_toplevel_command():
            self.restart_backend(False, False, 2)

        editor = get_workbench().get_editor_notebook().get_current_editor()
        if not editor:
            return

        filename = editor.get_filename(True)
        if not filename:
            return

        if editor.is_modified():
            filename = editor.save_file()
            if not filename:
                return

        # changing dir may be required
        script_dir = normpath_with_actual_case(os.path.dirname(filename))

        if (
            get_workbench().get_option("run.auto_cd")
            and command_name[0].isupper()
            or always_change_to_script_dir
        ):
            working_directory = script_dir  # type: Optional[str]
        else:
            working_directory = None

        if get_workbench().get_option("view.show_program_arguments"):
            args_str = get_workbench().get_option("run.program_arguments")
            get_workbench().log_program_arguments_string(args_str)
            args = shlex.split(args_str)
        else:
            args = []

        self.execute_script(filename, args, working_directory, command_name)

    def _cmd_run_current_script_enabled(self) -> bool:
        return (
            get_workbench().get_editor_notebook().get_current_editor() is not None
            and "run" in get_runner().supported_features()
        )

    def _cmd_run_current_script(self) -> None:
        self.execute_current("Run")

    def _cmd_interrupt(self) -> None:
        if self._proxy is not None:
            self._proxy.interrupt()
        else:
            logging.warning("Interrupting without proxy")

    def _cmd_interrupt_enabled(self) -> bool:
        if not self._proxy or not self._proxy.is_functional():
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

        # TODO: should it be get_runner().is_waiting_toplevel_command() ??
        return True

    def cmd_stop_restart(self) -> None:
        self.restart_backend(True)

    def _poll_vm_messages(self) -> None:
        """I chose polling instead of event_generate in listener thread,
        because event_generate across threads is not reliable
        http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        """
        self._polling_after_id = None
        if self._pull_vm_messages() is False:
            return

        self._polling_after_id = get_workbench().after(50, self._poll_vm_messages)

    def _pull_vm_messages(self):
        while self._proxy is not None:
            try:
                msg = self._proxy.fetch_next_message()
                if not msg:
                    break
                logging.debug(
                    "RUNNER GOT: %s, %s in state: %s",
                    msg.event_type,
                    msg,
                    self.get_state(),
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
                get_workbench().set_cwd(msg["cwd"])

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
        err = "Backend terminated (returncode: %s)\n" % getattr(exc, "returncode", "?")

        try:
            faults_file = os.path.join(THONNY_USER_DIR, "backend_faults.log")
            if os.path.exists(faults_file):
                with open(faults_file, encoding="ASCII") as fp:
                    err += fp.read()
        except Exception:
            logging.exception("Failed retrieving backend faults")

        err = err.strip() + "\nUse 'Stop/Restart' to restart the backend ...\n"

        get_workbench().event_generate("ProgramOutput", stream_name="stderr", data=err)

        get_workbench().become_active_window()

    def restart_backend(
        self, clean: bool, first: bool = False, wait: float = 0
    ) -> None:
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
            while (
                not self.is_waiting_toplevel_command()
                and time.time() - start_time <= wait
            ):
                # self._pull_vm_messages()
                get_workbench().update()
                sleep(0.01)

        get_workbench().event_generate("BackendRestart")

    def destroy_backend(self) -> None:
        if self._polling_after_id is not None:
            get_workbench().after_cancel(self._polling_after_id)
            self._polling_after_id = None

        self._postponed_commands = []
        if self._proxy:
            self._proxy.destroy()
            self._proxy = None

    def get_executable(self) -> Optional[str]:
        if self._proxy is None:
            return None
        else:
            return self._proxy.get_executable()

    def get_backend_proxy(self) -> "BackendProxy":
        return self._proxy

    def _check_alloc_console(self) -> None:
        if sys.executable.endswith("thonny.exe") or sys.executable.endswith(
            "pythonw.exe"
        ):
            # These don't have console allocated.
            # Console is required for sending interrupts.

            # AllocConsole would be easier but flashes console window

            import ctypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

            exe = sys.executable.replace("thonny.exe", "python.exe").replace(
                "pythonw.exe", "python.exe"
            )

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
                logging.getLogger("thonny").exception(
                    "Problem with finalizing console allocation"
                )

    def supported_features(self) -> Set[str]:
        if self._proxy is None:
            return set()
        else:
            return self._proxy.supported_features()

    def using_venv(self) -> bool:
        return isinstance(self._proxy, CPythonProxy) and self._proxy.in_venv


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
        method_name = "_cmd_" + cmd.name
        if hasattr(self, method_name):
            return getattr(self, method_name)(cmd)
        else:
            return "discard"

    def send_program_input(self, data: str) -> None:
        """Send input data to backend"""
        raise NotImplementedError()

    def fetch_next_message(self):
        """Read next message from the queue or None if queue is empty"""
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

    def is_functional(self):
        """Used in MicroPython proxies"""
        return True

    def get_executable(self):
        """Return system command for invoking current interpreter"""
        return None

    def supported_features(self):
        return {"run"}


class CPythonProxy(BackendProxy):
    "abstract class"

    def __init__(self, executable):
        super().__init__(True)
        self._executable = executable

        self._proc = None
        self._message_queue = None
        self._sys_path = []
        self._usersitepackages = None
        self._gui_update_loop_id = None
        self.in_venv = None
        self._start_new_process()

    def fetch_next_message(self):
        if not self._message_queue or len(self._message_queue) == 0:
            if self._proc is not None:
                retcode = self._proc.poll()
                if retcode is not None:
                    raise BackendTerminatedError(retcode)
            return None

        msg = self._message_queue.popleft()
        if "gui_is_active" in msg:
            self._update_gui_updating(msg)

        if "in_venv" in msg:
            self.in_venv = msg["in_venv"]

        if "path" in msg:
            self._sys_path = msg["path"]

        if "usersitepackages" in msg:
            self._usersitepackages = msg["usersitepackages"]

        if "prefix" in msg:
            self._sys_prefix = msg["prefix"]

        if msg.event_type == "ProgramOutput":
            # combine available output messages to one single message,
            # in order to put less pressure on UI code

            while True:
                if len(self._message_queue) == 0:
                    return msg
                else:
                    next_msg = self._message_queue.popleft()
                    if (
                        next_msg.event_type == "ProgramOutput"
                        and next_msg["stream_name"] == msg["stream_name"]
                    ):
                        msg["data"] += next_msg["data"]
                    else:
                        # not same type of message, put it back
                        self._message_queue.appendleft(next_msg)
                        return msg

        else:
            return msg

    def send_command(self, cmd):
        if isinstance(cmd, ToplevelCommand) and cmd.name[0].isupper():
            self._close_backend()
            self._start_new_process(cmd)

        self._send_msg(cmd)

    def _send_msg(self, msg):
        self._proc.stdin.write(serialize_message(msg) + "\n")
        self._proc.stdin.flush()

    def send_program_input(self, data):
        self._send_msg(InputSubmission(data))

    def get_sys_path(self):
        return self._sys_path

    def interrupt(self):
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(
                        self._proc.pid, signal.CTRL_BREAK_EVENT
                    )  # @UndefinedVariable
                except Exception:
                    logging.exception("Could not interrupt backend process")
            else:
                self._proc.send_signal(signal.SIGINT)

    def destroy(self):
        self._close_backend()

    def _close_backend(self):
        self._cancel_gui_update_loop()

        if self._proc is not None and self._proc.poll() is None:
            self._proc.kill()

        self._proc = None
        self._message_queue = None

    def _start_new_process(self, cmd=None):
        this_python = get_frontend_python()
        # deque, because in one occasion I need to put messages back
        self._message_queue = collections.deque()

        # prepare the environment
        my_env = os.environ.copy()

        # Delete some environment variables if the backend is (based on) a different Python instance
        if self._executable not in [
            this_python,
            this_python.replace("python.exe", "pythonw.exe"),
            this_python.replace("pythonw.exe", "python.exe"),
        ]:

            # Keep only the variables, that are not related to Python
            my_env = {
                name: my_env[name]
                for name in my_env
                if "python" not in name.lower()
                and name not in ["TK_LIBRARY", "TCL_LIBRARY"]
            }

            # Remove variables used to tweak bundled Thonny-private Python
            if using_bundled_python():
                my_env = {
                    name: my_env[name]
                    for name in my_env
                    if name not in ["SSL_CERT_FILE", "SSL_CERT_DIR", "LD_LIBRARY_PATH"]
                }

        # variables controlling communication with the back-end process
        my_env["PYTHONIOENCODING"] = "utf-8"

        # Let back-end know about plug-ins
        my_env["THONNY_USER_DIR"] = THONNY_USER_DIR

        if get_workbench().in_debug_mode():
            my_env["THONNY_DEBUG"] = "1"
        elif "THONNY_DEBUG" in my_env:
            del my_env["THONNY_DEBUG"]

        # venv may not find (correct) Tk without assistance (eg. in Ubuntu)
        if self._executable == get_private_venv_executable():
            try:
                my_env["TCL_LIBRARY"] = get_workbench().tk.exprstring("$tcl_library")
                my_env["TK_LIBRARY"] = get_workbench().tk.exprstring("$tk_library")
            except Exception:
                logging.exception("Can't find Tcl/Tk library")

        if not os.path.exists(self._executable):
            raise UserError(
                "Interpreter (%s) not found. Please recheck corresponding option!"
                % self._executable
            )

        import thonny.backend_launcher

        cmd_line = [
            self._executable,
            "-u",  # unbuffered IO
            "-B",  # don't write pyo/pyc files
            # (to avoid problems when using different Python versions without write permissions)
            thonny.backend_launcher.__file__,
        ]

        if hasattr(cmd, "filename"):
            cmd_line.append(cmd.filename)
            if hasattr(cmd, "args"):
                cmd_line.extend(cmd.args)

        if hasattr(cmd, "environment"):
            my_env.update(cmd.environment)

        creationflags = 0
        if running_on_windows():
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        debug("Starting the backend: %s %s", cmd_line, get_workbench().get_cwd())
        self._proc = subprocess.Popen(
            cmd_line,
            # bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=get_workbench().get_cwd(),
            env=my_env,
            universal_newlines=True,
            creationflags=creationflags,
        )

        # send init message
        self._send_msg({"frontend_sys_path": sys.path})

        if cmd:
            # Consume the ready message, cmd will get its own result message
            ready_line = self._proc.stdout.readline()
            if ready_line == "":  # There was some problem
                error_msg = self._proc.stderr.read()
                raise Exception("Error starting backend process: " + error_msg)

        # setup asynchronous output listeners
        Thread(target=self._listen_stdout, daemon=True).start()
        Thread(target=self._listen_stderr, daemon=True).start()

    def _listen_stdout(self):
        # debug("... started listening to stdout")
        # will be called from separate thread
        def publish_as_msg(data):
            msg = parse_message(data)
            if "cwd" in msg:
                self.cwd = msg["cwd"]
            self._message_queue.append(msg)

            if len(self._message_queue) > 100:
                # Probably backend runs an infinite/long print loop.
                # Throttle message thougput in order to keep GUI thread responsive.
                sleep(0.1)

        while True:
            data = self._proc.stdout.readline()
            # debug("... read some stdout data", repr(data))
            if data == "":
                break
            else:
                try:
                    publish_as_msg(data)
                except Exception:
                    traceback.print_exc()
                    # Can mean the line was from subprocess,
                    # which can't be captured by stream faking.
                    # NB! If subprocess printed it without linebreak,
                    # then the suffix can be thonny message

                    parts = data.rsplit(common.MESSAGE_MARKER, maxsplit=1)

                    # print first part as it is
                    self._message_queue.append(
                        BackendEvent(
                            "ProgramOutput", data=parts[0], stream_name="stdout"
                        )
                    )

                    if len(parts) == 2:
                        second_part = common.MESSAGE_MARKER + parts[1]
                        try:
                            publish_as_msg(second_part)
                        except Exception:
                            # just print ...
                            self._message_queue.append(
                                BackendEvent(
                                    "ProgramOutput",
                                    data=second_part,
                                    stream_name="stdout",
                                )
                            )

    def _listen_stderr(self):
        # stderr is used only for debugger debugging
        while True:
            data = self._proc.stderr.readline()
            if data == "":
                break
            else:
                self._message_queue.append(
                    BackendEvent("ProgramOutput", stream_name="stderr", data=data)
                )

    def get_executable(self):
        return self._executable

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
            self.send_command(InlineCommand("process_gui_events"))

        self._gui_update_loop_id = get_workbench().after(50, self._loop_gui_update)

    def _cancel_gui_update_loop(self):
        if self._gui_update_loop_id is not None:
            try:
                get_workbench().after_cancel(self._gui_update_loop_id)
            finally:
                self._gui_update_loop_id = None

    def supported_features(self):
        return {"run", "debug", "pip_gui", "system_shell"}


class PrivateVenvCPythonProxy(CPythonProxy):
    def __init__(self, clean):
        self._prepare_private_venv()
        CPythonProxy.__init__(self, get_private_venv_executable())

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
                    path,
                    "Please wait!\nUpgrading Thonny's virtual environment.",
                    upgrade=True,
                )

    def _create_private_venv(self, path, description, clear=False, upgrade=False):
        # Don't include system site packages
        # This way all students will have similar configuration
        # independently of system Python (if Thonny is used with system Python)

        # NB! Cant run venv.create directly, because in Windows
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
        CPythonProxy.__init__(self, get_frontend_python())

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            if using_bundled_python():
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

        CPythonProxy.__init__(self, executable)

    def fetch_next_message(self):
        msg = super().fetch_next_message()
        if msg and "welcome_text" in msg:
            msg["welcome_text"] += " (" + self._executable + ")"
        return msg


def get_private_venv_path():
    if "thonny" in sys.executable.lower():
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


def using_bundled_python():
    return os.path.exists(
        os.path.join(os.path.dirname(sys.executable), "thonny_python.ini")
    )


def create_pythonless_environment():
    # If I want to call another python version, then
    # I need to remove from environment the items installed by current interpreter
    env = {}

    for key in os.environ:
        if "python" not in key.lower() and key not in ["TK_LIBRARY", "TCL_LIBRARY"]:
            env[key] = os.environ[key]

    return env


def create_backend_python_process(
    args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
):
    """Used for running helper commands (eg. pip) on CPython backend.
    Assumes current backend is CPython."""

    # TODO: if backend == frontend, then delegate to create_frontend_python_process

    python_exe = get_runner().get_executable()

    env = create_pythonless_environment()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    # TODO: remove frontend python from path and add backend python to it

    return _create_python_process(python_exe, args, stdin, stdout, stderr, env=env)


def create_frontend_python_process(
    args, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
):
    """Used for running helper commands (eg. for installing plug-ins on by the plug-ins)"""
    python_exe = get_frontend_python().replace("pythonw.exe", "python.exe")
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
    def __init__(self, returncode):
        Exception.__init__(self)
        self.returncode = returncode


def get_frontend_python():
    return sys.executable.replace("thonny.exe", "python.exe")
