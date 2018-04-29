# -*- coding: utf-8 -*-

"""Code for maintaining the background process and for running
user programs

Commands get executed via shell, this way the command line in the 
shell becomes kind of title for the execution.

""" 


from _thread import start_new_thread
from logging import debug
import os.path
import subprocess
import sys

from thonny.common import serialize_message, ToplevelCommand, \
    InlineCommand, parse_message, DebuggerCommand, InputSubmission,\
    UserError, construct_cmd_line
from thonny import get_workbench, get_runner, get_shell
from thonny import THONNY_USER_DIR
from thonny.misc_utils import running_on_windows, running_on_mac_os, eqfn
import shutil
import collections
import signal
import logging
import traceback
from time import sleep


WINDOWS_EXE = "python.exe"

class Runner:
    def __init__(self):
        get_workbench().set_default("run.auto_cd", True)
        
        from thonny.shell import ShellView
        get_workbench().add_view(ShellView, "Shell", "s",
            visible_by_default=True,
            default_position_key='A')
        
        self._init_commands()
        
        self._state = None
        self._proxy = None
        self._polling_after_id = None
        self._postponed_commands = []
        
        self._check_alloc_console()
        
        # temporary
        self._remove_obsolete_jedi_copies()
    
    def _remove_obsolete_jedi_copies(self):
        """Thonny 2.1 used to copy jedi in order to make it available
        for the backend"""
        for item in os.listdir(THONNY_USER_DIR):
            if item.startswith("jedi_0."):
                shutil.rmtree(os.path.join(THONNY_USER_DIR, item), True)
    
    def start(self):
        self.restart_backend(False, True)
    
    def _init_commands(self):
        get_workbench().add_command('run_current_script', "run", 'Run current script',
            caption="Run",
            handler=self._cmd_run_current_script,
            default_sequence="<F5>",
            tester=self._cmd_run_current_script_enabled,
            group=10,
            image="run-current-script",
            include_in_toolbar=True)
        
        get_workbench().add_command('restart', "run", 'Stop/Restart',
            caption="Stop",
            handler=self.cmd_stop_restart,
            default_sequence="<Control-F2>",
            group=70,
            image="stop",
            include_in_toolbar=True)
        
        get_workbench().add_command('interrupt', "run", "Interrupt execution",
            handler=self._cmd_interrupt,
            tester=self._cmd_interrupt_enabled,
            default_sequence="<Control-c>",
            bell_when_denied=False)
    
    def get_state(self):
        """State is one of "running", "waiting_debugger_command",
            "waiting_toplevel_command"
        """
        return self._state
    
    def _set_state(self, state):
        if self._state != state:
            logging.debug("Runner state changed: %s ==> %s" % (self._state, state))
            self._state = state
    
    def get_sys_path(self):
        return self._proxy.get_sys_path()
    
    def send_command(self, cmd):
        if self._proxy is None:
            return

        # First sanity check
        if (isinstance(cmd, ToplevelCommand)
            and self.get_state() != "waiting_toplevel_command"
            and cmd.command not in ["Reset", "Run", "Debug"]
            or 
            isinstance(cmd, DebuggerCommand)
            and self.get_state() != "waiting_debugger_command"
            ):
            get_workbench().bell()
            logging.info("RUNNER: Command %s was attempted at state %s" % (cmd, self.get_state()))
            return
            
        # Offer the command
        logging.debug("RUNNER Sending: %s, %s", cmd.command, cmd)
        response = self._proxy.send_command(cmd)
        
        if response == "discard":
            return
        elif response == "postpone":
            self._postpone_command(cmd)
            return
        else:
            assert response is None

            
        if isinstance(cmd, (ToplevelCommand, DebuggerCommand)):
            self._set_state("running")
    
        if cmd.command in ("Run", "Debug", "Reset"):
            get_workbench().event_generate("BackendRestart")
                
    def _postpone_command(self, cmd):
        # in case of InlineCommands, discard older same type command
        if isinstance(cmd, InlineCommand):
            for older_cmd in self._postponed_commands:
                if older_cmd.command == cmd.command:
                    self._postponed_commands.remove(older_cmd)
        
        if len(self._postponed_commands) > 10: 
            logging.warning("Can't pile up too many commands. This command will be just ignored")
        else:
            self._postponed_commands.append(cmd)
    
    def _send_postponed_commands(self):
        todo = self._postponed_commands
        self._postponed_commands = []
        
        for cmd in todo:
            logging.debug("Sending postponed command: %s", cmd)
            self.send_command(cmd)
    
    def send_program_input(self, data):
        assert self.get_state() == "running"
        self._proxy.send_program_input(data)
        
    def execute_script(self, script_path, args, working_directory=None, command_name="Run"):
        if (working_directory is not None and get_workbench().get_cwd() != working_directory):
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
        exe_cmd_line = construct_cmd_line(["%" + command_name, rel_filename] + args) + "\n"
        
        # submit to shell (shell will execute it)
        get_shell().submit_magic_command(cd_cmd_line + exe_cmd_line)
        
    def execute_current(self, command_name, always_change_to_script_dir=False):
        """
        This method's job is to create a command for running/debugging
        current file/script and submit it to shell
        """
        editor = get_workbench().get_current_editor()
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
        script_dir = os.path.realpath(os.path.dirname(filename))
        
        if (get_workbench().get_option("run.auto_cd") 
            and command_name[0].isupper() or always_change_to_script_dir):
            working_directory = script_dir
        else:
            working_directory = None
        
        self.execute_script(filename, [], working_directory, command_name)
        
    def _cmd_run_current_script_enabled(self):
        return (get_workbench().get_editor_notebook().get_current_editor() is not None
                and get_runner().get_state() == "waiting_toplevel_command"
                and "run" in get_runner().supported_features())
    
    def _cmd_run_current_script(self):
        self.execute_current("Run")
    
    def _cmd_interrupt(self):
        if self._proxy is not None:
            self._proxy.interrupt()
        else:
            logging.warning("Interrupting without proxy")
        
    def _cmd_interrupt_enabled(self):
        # TODO: distinguish command and Ctrl+C shortcut
        
        widget = get_workbench().focus_get()
        if not running_on_mac_os(): # on Mac Ctrl+C is not used for Copy
            if hasattr(widget, "selection_get"):
                try:
                    if widget.selection_get() != "":
                        # assuming user meant to copy, not interrupt
                        # (IDLE seems to follow same logic)
                        return False
                except:
                    # selection_get() gives error when calling without selection on Ubuntu
                    pass

        # TODO: should it be get_runner().get_state() != "waiting_toplevel_command" ??
        return True
    
    def cmd_stop_restart(self):
        self.restart_backend(True)
    
            
        
    
    def _poll_vm_messages(self):
        """I chose polling instead of event_generate in listener thread,
        because event_generate across threads is not reliable
        http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        """
        self._polling_after_id = None
        
        while self._proxy is not None:
            try:
                msg = self._proxy.fetch_next_message()
                if not msg:
                    break
                logging.debug("RUNNER GOT: %s, %s in state: %s", msg["message_type"], msg, self.get_state())
                
            except BackendTerminatedError as exc:
                self._report_backend_crash(exc)
                return
            
            if msg.get("SystemExit", False):
                self.restart_backend(True)
                return
            
            
            # change state
            if msg["message_type"] == "ToplevelResult":
                self._set_state("waiting_toplevel_command")
            elif msg["message_type"] == "DebuggerProgress":
                self._set_state("waiting_debugger_command")
            else:
                "other messages don't affect the state"
            
            if "cwd" in msg:
                get_workbench().set_cwd(msg["cwd"])
            
            # NB! This may cause another command to be sent before we get to postponed commands
            get_workbench().event_generate(msg["message_type"], **msg)
            
            # TODO: is it necessary???
            # https://stackoverflow.com/a/13520271/261181
            #get_workbench().update() 
            
        self._send_postponed_commands()
            
        self._polling_after_id = get_workbench().after(50, self._poll_vm_messages)
    
    def _report_backend_crash(self, exc):
        err = "Backend terminated (returncode: %s)\n" % exc.returncode
        
        try:
            faults_file = os.path.join(THONNY_USER_DIR, "backend_faults.log")
            if os.path.exists(faults_file):
                with open(faults_file, encoding="ASCII") as fp:
                    err += fp.read()
        except:
            logging.exception("Failed retrieving backend faults")
                
        err = err.strip() + "\nUse 'Stop/Restart' to restart the backend ...\n"
        
        get_workbench().event_generate("ProgramOutput",
                                       stream_name="stderr",
                                       data=err)
        
        get_workbench().become_topmost_window()
        
    
    def restart_backend(self, clean, first=False):
        """Recreate (or replace) backend proxy / backend process."""
        
        if not first:
            get_shell().restart()
        
        self.destroy_backend()
        backend_name = get_workbench().get_option("run.backend_name")
        if backend_name not in get_workbench().get_backends():
            raise UserError("Can't find backend '{}'. Please select another backend from options"
                            .format(backend_name))
        
        backend_class = get_workbench().get_backends()[backend_name].proxy_class
        self._set_state("running")
        self._proxy = None
        self._proxy = backend_class(clean)
        
        self._poll_vm_messages()
        
    
    def destroy_backend(self):
        if self._polling_after_id is not None:
            get_workbench().after_cancel(self._polling_after_id)
            self._polling_after_id = None
            
        self._postponed_commands = []
        if self._proxy:
            self._proxy.destroy()
            self._proxy = None

    def get_interpreter_command(self):
        return self._proxy.get_interpreter_command()
    
    def get_backend_proxy(self):
        return self._proxy
    
    def _check_alloc_console(self):
        if (sys.executable.endswith("thonny.exe")
            or sys.executable.endswith("pythonw.exe")):
            # These don't have console allocated.
            # Console is required for sending interrupts.
            
            # AllocConsole would be easier but flashes console window
            
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            
            exe = (sys.executable
                      .replace("thonny.exe", "python.exe") 
                      .replace("pythonw.exe", "python.exe"))
            
            cmd = [exe, "-c", "print('Hi!'); input()"]
            child = subprocess.Popen(cmd,
                                     stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     shell=True)
            child.stdout.readline()
            result = kernel32.AttachConsole(child.pid)
            if not result:
                err = ctypes.get_last_error()
                logging.info("Could not allocate console. Error code: " +str(err))
            child.stdin.write(b"\n")
            child.stdin.flush()

    def supported_features(self):
        if self._proxy is None:
            return set()
        else:
            return self._proxy.supported_features()
            
            
    def using_venv(self):
        return isinstance(self._proxy,  CPythonProxy) and self._proxy.in_venv

class BackendProxy:
    """Communicates with backend process.
    
    All communication methods must be non-blocking, 
    ie. suitable for calling from GUI thread."""
    
    # backend_name will be overwritten on Workbench.add_backend
    # Subclasses don't need to worry about it.
    backend_name = None 
    
    def __init__(self, clean):
        """Initializes (or starts the initialization of) the backend process.
        
        Backend is considered ready when the runner gets a ToplevelResult
        with attribute "welcome_text" from fetch_next_message.
        """
    
    def send_command(self, cmd):
        """Send the command to backend. Return None, 'discard' or 'postpone'"""
        method_name = "_cmd_" + cmd.command
        if hasattr(self, method_name):
            return getattr(self, method_name)(cmd)
        else:
            return "discard"
    
    def send_program_input(self, data):
        """Send input data to backend"""
        raise NotImplementedError()
    
    def fetch_next_message(self):
        """Read next message from the queue or None if queue is empty"""
        raise NotImplementedError()

    def get_sys_path(self):
        "backend's sys.path"
        return []
    
    def interrupt(self):
        """Tries to interrupt current command without reseting the backend"""
        pass
    
    def destroy(self):
        """Called when Thonny no longer needs this instance 
        (Thonny gets closed or new backend gets selected)
        """
        pass
    
    def get_interpreter_command(self):
        """Return system command for invoking current interpreter"""
        raise NotImplementedError()
    
    def supported_features(self):
        return {"run"}

    

class CPythonProxy(BackendProxy):
    "abstract class"
    
    def __init__(self, executable):
        self._executable = executable
        
        self._proc = None
        self._message_queue = None
        self._sys_path = []
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
        
        if msg["message_type"] == "ProgramOutput":
            # combine available output messages to one single message, 
            # in order to put less pressure on UI code
            
            while True:
                if len(self._message_queue) == 0:
                    return msg
                else:
                    next_msg = self._message_queue.popleft()
                    if (next_msg["message_type"] == "ProgramOutput" 
                        and next_msg["stream_name"] == msg["stream_name"]):
                        msg["data"] += next_msg["data"]
                    else:
                        # not same type of message, put it back
                        self._message_queue.appendleft(next_msg)
                        return msg
            
        else: 
            return msg
    
    def send_command(self, cmd):
        if isinstance(cmd, ToplevelCommand) and cmd.command in ("Run", "Debug", "Reset"):
            self._close_backend()
            self._start_new_process(cmd)
        
        self._send_msg(cmd)
    
    def _send_msg(self, msg):
        self._proc.stdin.write(serialize_message(msg) + "\n")
        self._proc.stdin.flush()
    
    def send_program_input(self, data):
        self.send_command(InputSubmission(data=data))
        
    def get_sys_path(self):
        return self._sys_path
    
    def interrupt(self):
        if self._proc is not None and self._proc.poll() is None:
            if running_on_windows():
                try:
                    os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                except:
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
            get_private_venv_executable()]:
            
            # Keep only the variables, that are not related to Python
            my_env = {name : my_env[name] for name in my_env 
                      if "python" not in name.lower() and name not in ["TK_LIBRARY", "TCL_LIBRARY"]}
            
            # Remove variables used to tweak bundled Thonny-private Python
            if using_bundled_python():
                my_env = {name : my_env[name] for name in my_env
                          if name not in ["SSL_CERT_FILE", "SSL_CERT_DIR", "LD_LIBRARY_PATH"]}
        
        # variables controlling communication with the back-end process
        my_env["PYTHONIOENCODING"] = "ASCII" 
        my_env["PYTHONUNBUFFERED"] = "1" 
        
        
        my_env["THONNY_USER_DIR"] = THONNY_USER_DIR
        
        # venv may not find (correct) Tk without assistance (eg. in Ubuntu)
        if self._executable == get_private_venv_executable():
            try:
                my_env["TCL_LIBRARY"] = get_workbench().tk.exprstring('$tcl_library')
                my_env["TK_LIBRARY"] = get_workbench().tk.exprstring('$tk_library')
            except:
                logging.exception("Can't find Tcl/Tk library")
        
        
        if not os.path.exists(self._executable):
            raise UserError("Interpreter (%s) not found. Please recheck corresponding option!"
                            % self._executable)
        
        
        import thonny.backend_launcher
        cmd_line = [
            self._executable, 
            '-u', # unbuffered IO (neccessary in Python 3.1)
            '-B', # don't write pyo/pyc files 
                  # (to avoid problems when using different Python versions without write permissions)
            thonny.backend_launcher.__file__
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
        self._proc = subprocess.Popen (
            cmd_line,
            #bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=get_workbench().get_cwd(),
            env=my_env,
            universal_newlines=True,
            creationflags=creationflags
        )
        
        # send init message
        self._send_msg({"frontend_sys_path" : sys.path})
        
        if cmd:
            # Consume the ready message, cmd will get its own result message
            ready_line = self._proc.stdout.readline()
            if ready_line == "": # There was some problem
                error_msg = self._proc.stderr.read()
                raise Exception("Error starting backend process: " + error_msg)
            
            #ready_msg = parse_message(ready_line)
            #self._sys_path = ready_msg["path"]
            #debug("Backend ready: %s", ready_msg)
        
        # setup asynchronous output listeners
        start_new_thread(self._listen_stdout, ())
        start_new_thread(self._listen_stderr, ())
    
    def _listen_stdout(self):
        #debug("... started listening to stdout")
        # will be called from separate thread
        while True:
            data = self._proc.stdout.readline()
            #debug("... read some stdout data", repr(data))
            if data == '':
                break
            else:
                try:
                    msg = parse_message(data)
                    self._message_queue.append(msg)
                
                    if len(self._message_queue) > 100:
                        # Probably backend runs an infinite/long print loop.
                        # Throttle message throughput in order to keep GUI thread responsive.
                        sleep(0.1)
                except:
                    logging.exception("\nError when handling message from the backend: " + str(data))
                    self._message_queue.append({"message_type" : "ProgramOutput",
                                                "data" : "Error handling message: " + traceback.format_exc(),
                                                "stream_name" : "stderr"})
                    raise

    def _listen_stderr(self):
        # stderr is used only for debugger debugging
        while True:
            data = self._proc.stderr.readline()
            if data == '':
                break
            else:
                logging.debug("BACKEND: %s", data.strip())
        
    def get_interpreter_command(self):
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
        if force or get_runner().get_state() == "waiting_toplevel_command":
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
            self._create_private_venv(path, "Please wait!\nThonny prepares its virtual environment.")
        
    def _check_upgrade_private_venv(self, path):
        # If home is wrong then regenerate
        # If only micro version is different, then upgrade
        info = _get_venv_info(path)
        
        if not eqfn(info["home"], os.path.dirname(sys.executable)):
            self._create_private_venv(path, 
                                 "Thonny's virtual environment was created for another interpreter.\n"
                                 + "Regenerating the virtual environment for current interpreter.\n"
                                 + "(You may need to reinstall your 3rd party packages)\n"
                                 + "Please wait!.",
                                 clear=True)
        else:
            venv_version = tuple(map(int, info["version"].split(".")))
            sys_version = sys.version_info[:3]
            assert venv_version[0] == sys_version[0]
            assert venv_version[1] == sys_version[1]
            
            if venv_version[2] != sys_version[2]:
                self._create_private_venv(path, "Please wait!\nUpgrading Thonny's virtual environment.",
                                     upgrade=True)
                
    
    def _create_private_venv(self, path, description, clear=False, upgrade=False):
        base_exe = sys.executable
        if sys.executable.endswith("thonny.exe"):
            # assuming that thonny.exe is in the same dir as "python.exe"
            base_exe = sys.executable.replace("thonny.exe", "python.exe")
        
        
        # Don't include system site packages
        # This way all students will have similar configuration
        # independently of system Python (if Thonny is used with system Python)
        
        # NB! Cant run venv.create directly, because in Windows 
        # it tries to link venv to thonny.exe.
        # Need to run it via proper python
        cmd = [base_exe, "-m", "venv"]
        if clear:
            cmd.append("--clear")
        if upgrade:
            cmd.append("--upgrade")
        
        try:
            import ensurepip  # @UnusedImport
        except ImportError:
            cmd.append("--without-pip")
            
        cmd.append(path)
        startupinfo = None
        if running_on_windows():
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmd, startupinfo=startupinfo,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                universal_newlines=True)
             
        from thonny.ui_utils import SubprocessDialog
        dlg = SubprocessDialog(get_workbench(), proc, "Preparing the backend", long_description=description)
        try:
            get_workbench().wait_window(dlg)
        except:
            # if using --without-pip the dialog may close very quickly 
            # and for some reason wait_window would give error then
            logging.exception("Problem with waiting for venv creation dialog")
        get_workbench().become_topmost_window() # Otherwise focus may get stuck somewhere
        
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
    return os.path.join(THONNY_USER_DIR, prefix + "%d%d" % (sys.version_info[0], sys.version_info[1]))

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
    
    return result;


def using_bundled_python():
    return os.path.exists(os.path.join(
        os.path.dirname(sys.executable),
        "thonny_python.ini"
    ))

class BackendTerminatedError(Exception):
    def __init__(self, returncode):
        Exception.__init__(self)
        self.returncode = returncode    


def get_frontend_python():
    return sys.executable.replace("thonny.exe", "python.exe")
