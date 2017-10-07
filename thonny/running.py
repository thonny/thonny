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
    InlineCommand, parse_shell_command, \
    CommandSyntaxError, parse_message, DebuggerCommand, InputSubmission,\
    UserError
from thonny.globals import get_workbench, get_runner
import shlex
from thonny import THONNY_USER_DIR
from thonny.misc_utils import running_on_windows, running_on_mac_os, eqfn
from shutil import which
import shutil
import tokenize
import collections
import signal
import logging
from time import sleep


DEFAULT_CPYTHON_INTERPRETER = "default"
SAME_AS_FRONTEND_INTERPRETER = "same as front-end"
WINDOWS_EXE = "python.exe"

class Runner:
    def __init__(self):
        get_workbench().set_default("run.working_directory", os.path.expanduser("~"))
        get_workbench().set_default("run.auto_cd", True)
        get_workbench().set_default("run.backend_configuration", "Python (%s)" % DEFAULT_CPYTHON_INTERPRETER)
        get_workbench().set_default("run.used_interpreters", [])
        get_workbench().add_backend("Python", CPythonProxy)
        
        from thonny.shell import ShellView
        get_workbench().add_view(ShellView, "Shell", "s",
            visible_by_default=True,
            default_position_key='A')
        
        self._init_commands()
        
        self._state = None
        self._proxy = None
        self._postponed_commands = []
        self._current_toplevel_command = None
        self._current_command = None
        
        self._check_alloc_console()
    
    def start(self):
        try:
            self.reset_backend()
        finally:
            self._poll_vm_messages()
    
    def _init_commands(self):
        shell = get_workbench().get_view("ShellView")
        shell.add_command("Run", self.handle_execute_from_shell)
        shell.add_command("Reset", self._handle_reset_from_shell)
        shell.add_command("cd", self._handle_cd_from_shell)
        
        get_workbench().add_command('run_current_script', "run", 'Run current script',
            handler=self._cmd_run_current_script,
            default_sequence="<F5>",
            tester=self._cmd_run_current_script_enabled,
            group=10,
            image_filename="run.run_current_script.gif",
            include_in_toolbar=True)
        
        get_workbench().add_command('reset', "run", 'Interrupt/Reset',
            handler=self.cmd_interrupt_reset,
            default_sequence="<Control-F2>",
            tester=self._cmd_interrupt_reset_enabled,
            group=70,
            image_filename="run.stop.gif",
            include_in_toolbar=True)
        
        get_workbench().add_command('interrupt', "run", "Interrupt execution",
            handler=self._cmd_interrupt,
            tester=self._cmd_interrupt_enabled,
            default_sequence="<Control-c>",
            bell_when_denied=False)
    
    def get_cwd(self):
        # TODO: make it nicer
        if hasattr(self._proxy, "cwd"):
            return self._proxy.cwd
        else:
            return ""
    
    def get_state(self):
        """State is one of "running", "waiting_input", "waiting_debugger_command",
            "waiting_toplevel_command"
        """
        return self._state
    
    def _set_state(self, state):
        if self._state != state:
            logging.debug("Runner state changed: %s ==> %s" % (self._state, state))
            self._state = state
            if self._state == "waiting_toplevel_command":
                self._current_toplevel_command = None
            
            if self._state != "running":
                self._current_command = None
    
    def get_current_toplevel_command(self):
        return self._current_toplevel_command
            
    def get_current_command(self):
        return self._current_command
            
    def get_sys_path(self):
        return self._proxy.get_sys_path()
    
    def send_command(self, cmd):
        if self._proxy is None:
            return
        
        if not self._state_is_suitable(cmd):
            if isinstance(cmd, DebuggerCommand) and self.get_state() == "running":
                # probably waiting behind some InlineCommand
                self._postpone_command(cmd)
                return
            elif isinstance(cmd, InlineCommand):
                self._postpone_command(cmd)
                return
            else:
                raise AssertionError("Trying to send " + str(cmd) + " in state " + self.get_state())
        
        if cmd.command in ("Run", "Debug", "Reset"):
            get_workbench().event_generate("BackendRestart")
        
        accepted = self._proxy.send_command(cmd)
        
        if (accepted and isinstance(cmd, (ToplevelCommand, DebuggerCommand, InlineCommand))):
            self._set_state("running")
            self._current_command = cmd
            if isinstance(cmd, ToplevelCommand):
                self._current_toplevel_command = cmd
        
    
    def send_program_input(self, data):
        assert self.get_state() == "waiting_input"
        self._proxy.send_program_input(data)
        self._set_state("running")
        
    def execute_script(self, script_path, args, working_directory=None, command_name="Run"):
        if (working_directory is not None and self._proxy.cwd != working_directory):
            # create compound command
            # start with %cd
            cmd_line = "%cd " + shlex.quote(working_directory) + "\n"
            next_cwd = working_directory
        else:
            # create simple command
            cmd_line = ""
            next_cwd = self._proxy.cwd
        
        # append main command (Run, run, Debug or debug)
        rel_filename = os.path.relpath(script_path, next_cwd)
        cmd_line += "%" + command_name + " " + shlex.quote(rel_filename)
        
        # append args
        for arg in args:
            cmd_line += " " + shlex.quote(arg) 
        
        cmd_line += "\n"
        
        # submit to shell (shell will execute it)
        get_workbench().get_view("ShellView").submit_command(cmd_line)
        
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
        
    def handle_execute_from_shell(self, cmd_line):
        """
        Handles all commands that take a filename and 0 or more extra arguments.
        Passes the command to backend.
        
        (Debugger plugin may also use this method)
        """
        command, args = parse_shell_command(cmd_line)
        
        if len(args) >= 1:
            get_workbench().get_editor_notebook().save_all_named_editors()
            cmd = ToplevelCommand(command=command,
                               filename=args[0],
                               args=args[1:])
            
            if os.path.isabs(cmd.filename):
                cmd.full_filename = cmd.filename
            else:
                cmd.full_filename = os.path.join(self.get_cwd(), cmd.filename)
                
            if command in ["Run", "run", "Debug", "debug"]:
                with tokenize.open(cmd.full_filename) as fp:
                    cmd.source = fp.read()
                
            self.send_command(cmd)
        else:
            raise CommandSyntaxError("Command '%s' takes at least one argument", command)

    def _handle_reset_from_shell(self, cmd_line):
        command, args = parse_shell_command(cmd_line)
        assert command == "Reset"
        
        if len(args) == 0:
            self.send_command(ToplevelCommand(command="Reset"))
        else:
            raise CommandSyntaxError("Command 'Reset' doesn't take arguments")
        

    def _handle_cd_from_shell(self, cmd_line):
        command, args = parse_shell_command(cmd_line)
        assert command == "cd"
        
        if len(args) == 1:
            self.send_command(ToplevelCommand(command="cd", path=args[0]))
        else:
            raise CommandSyntaxError("Command 'cd' takes one argument")

    def _cmd_run_current_script_enabled(self):
        return (get_workbench().get_editor_notebook().get_current_editor() is not None
                and get_runner().get_state() == "waiting_toplevel_command"
                and "run" in get_runner().supported_features())
    
    def _cmd_run_current_script(self):
        self.execute_current("Run")
    
    def _cmd_interrupt(self):
        self.interrupt_backend()
        
    def _cmd_interrupt_enabled(self):
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

        return get_runner().get_state() != "waiting_toplevel_command"
    
    def cmd_interrupt_reset(self):
        if self.get_state() == "waiting_toplevel_command":
            get_workbench().get_view("ShellView").submit_command("%Reset\n")
        else:
            get_runner().interrupt_backend()
    
            
    def _cmd_interrupt_reset_enabled(self):
        return True
    
    def _postpone_command(self, cmd):
        # in case of InlineCommands, discard older same type command
        if isinstance(cmd, InlineCommand):
            for older_cmd in self._postponed_commands:
                if older_cmd.command == cmd.command:
                    self._postponed_commands.remove(older_cmd)
        
        if len(self._postponed_commands) > 10: 
            "Can't pile up too many commands. This command will be just ignored"
        else:
            self._postponed_commands.append(cmd)
    
    def _state_is_suitable(self, cmd):
        if isinstance(cmd, ToplevelCommand):
            return (self.get_state() == "waiting_toplevel_command"
                    or cmd.command in ["Reset", "Run", "Debug"])
            
        elif isinstance(cmd, DebuggerCommand):
            return self.get_state() == "waiting_debugger_command"
        
        elif isinstance(cmd, InlineCommand):
            # UI may send inline commands in any state,
            # but some backends don't accept them in some states
            return self.get_state() in self._proxy.allowed_states_for_inline_commands()
        
        else:
            raise RuntimeError("Unknown command class: " + str(type(cmd)))
    
    def _send_postponed_commands(self):
        remaining = []
        
        for cmd in self._postponed_commands:
            if self._state_is_suitable(cmd):
                logging.debug("Sending postponed command", cmd)
                self.send_command(cmd)
            else:
                remaining.append(cmd)
        
        self._postponed_commands = remaining
        
    
    def _poll_vm_messages(self):
        """I chose polling instead of event_generate in listener thread,
        because event_generate across threads is not reliable
        http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        """
        try:
            initial_state = self.get_state()
            
            while self._proxy is not None:
                try:
                    msg = self._proxy.fetch_next_message()
                    if not msg:
                        break
                except BackendTerminatedError as exc:
                    self._report_backend_crash(exc)
                    self.reset_backend()
                    return
                
                if msg.get("SystemExit", False):
                    self.reset_backend()
                    return
                
                # change state
                if "command_context" in msg:
                    # message_context shows the state where corresponding command was handled in the backend
                    # Now we got the response and we're return to that state
                    self._set_state(msg["command_context"])
                elif msg["message_type"] == "ToplevelResult":
                    # some ToplevelResult-s don't have command_context
                    self._set_state("waiting_toplevel_command")
                elif msg["message_type"] == "InputRequest":
                    self._set_state("waiting_input")
                else:
                    "other messages don't affect the state"
                
                if msg["message_type"] == "ToplevelResult":
                    self._current_toplevel_command = None
    
                #logging.debug("Runner: State: %s, Fetched msg: %s" % (self.get_state(), msg))
                get_workbench().event_generate(msg["message_type"], **msg)
                
                # TODO: maybe distinguish between workbench cwd and backend cwd ??
                get_workbench().set_option("run.working_directory", self.get_cwd())
                
                # TODO: is it necessary???
                # https://stackoverflow.com/a/13520271/261181
                #get_workbench().update() 
                
            if self.get_state() != initial_state:
                self._send_postponed_commands()
                
        finally:
            get_workbench().after(50, self._poll_vm_messages)
    
    def _report_backend_crash(self, exc):
        err = "Backend terminated (returncode: %s)\n" % exc.returncode
        
        try:
            faults_file = os.path.join(THONNY_USER_DIR, "backend_faults.log")
            if os.path.exists(faults_file):
                with open(faults_file, encoding="ASCII") as fp:
                    err += fp.read()
        except:
            logging.exception("Failed retrieving backend faults")
                
        err = err.strip() + "\nResetting ...\n"
        
        get_workbench().event_generate("ProgramOutput",
                                       stream_name="stderr",
                                       data=err)
        
        get_workbench().become_topmost_window()
        
    
    def reset_backend(self):
        self.kill_backend()
        configuration = get_workbench().get_option("run.backend_configuration")
        backend_name, configuration_option = parse_configuration(configuration)
        if backend_name not in get_workbench().get_backends():
            raise UserError("Can't find backend '{}'. Please select another backend from options"
                            .format(backend_name))
        
        backend_class = get_workbench().get_backends()[backend_name]
        self._set_state("running")
        self._proxy = None
        self._proxy = backend_class(configuration_option)
    
    def interrupt_backend(self):
        if self._proxy is not None:
            self._proxy.interrupt()
        else:
            logging.warning("Interrupting without proxy")
    
    def kill_backend(self):
        self._current_toplevel_command = None
        self._current_command = None
        self._postponed_commands = []
        if self._proxy:
            self._proxy.kill_current_process()
            self._proxy = None

    def get_interpreter_command(self):
        return self._proxy.get_interpreter_command()
    
    def get_backend_description(self):
        return self._proxy.get_description()

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
            return []
        else:
            return self._proxy.supported_features()
            
            
    def get_frontend_python(self):
        return sys.executable.replace("thonny.exe", "python.exe")
    
    def using_venv(self):
        return isinstance(self._proxy,  CPythonProxy) and self._proxy.in_venv

class BackendProxy:
    """Communicates with backend process.
    
    All communication methods must be non-blocking, 
    ie. suitable for calling from GUI thread."""
    
    def __init__(self, configuration_option):
        """Initializes (or starts the initialization of) the backend process.
        
        Backend is considered ready when the runner gets a ToplevelResult
        with attribute "welcome_text" from fetch_next_message.
        
        param configuration_option:
            If configuration is "Foo (bar)", then "Foo" is backend descriptor
            and "bar" is the configuration option"""
    
    @classmethod
    def get_configuration_options(cls):
        """Returns a list strings for populating interpreter selection dialog.
        The strings are without backend descriptor"""
        raise NotImplementedError()
    
    def get_description(self):
        """Returns a string that describes the backend"""
        raise NotImplementedError()        

    def send_command(self, cmd):
        """Send the command to backend"""
        raise NotImplementedError()
    
    def allowed_states_for_inline_commands(self):
        return ["waiting_toplevel_command"]

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
        self.kill_current_process()
    
    def kill_current_process(self):
        """Kill the backend.
        
        Is called when Thonny no longer needs this backend 
        (Thonny gets closed or new backend gets selected)
        """
        pass
    
    def get_interpreter_command(self):
        """Return system command for invoking current interpreter"""
        raise NotImplementedError()
    
    def supported_features(self):
        return ["run"]

    

class CPythonProxy(BackendProxy):
    @classmethod
    def get_configuration_options(cls):
        return ([DEFAULT_CPYTHON_INTERPRETER, SAME_AS_FRONTEND_INTERPRETER] 
                + CPythonProxy._get_interpreters())
        
    def __init__(self, configuration_option):
        if configuration_option == DEFAULT_CPYTHON_INTERPRETER:
            self._prepare_private_venv()
            self._executable = get_private_venv_executable()
        elif configuration_option == SAME_AS_FRONTEND_INTERPRETER:
            self._executable = get_runner().get_frontend_python()
        elif configuration_option.startswith("."):
            # Relative paths are relative to front-end interpretator directory
            # (This must be written directly to conf file, as it can't be selected from Options dialog)  
            self._executable = os.path.normpath(os.path.join(os.path.dirname(sys.executable), 
                                                             configuration_option)) 
        else:
            self._executable = configuration_option
            
            # Rembember the usage of this non-default interpreter
            used_interpreters = get_workbench().get_option("run.used_interpreters")
            if self._executable not in used_interpreters:
                used_interpreters.append(self._executable)
            get_workbench().set_option("run.used_interpreters", used_interpreters)
            
        
        cwd = get_workbench().get_option("run.working_directory")
        if os.path.exists(cwd):
            self.cwd = cwd
        else:
            self.cwd = os.path.expanduser("~")
            
        self._proc = None
        self._message_queue = None
        self._sys_path = []
        self._tkupdate_loop_id = None
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
        if "tkinter_is_active" in msg:
            self._update_tkupdating(msg)
        
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
    
    def get_description(self):
        # TODO: show backend version and interpreter path
        return "Python (current dir: {})".format(self.cwd)
        
        
    def send_command(self, cmd):
        if isinstance(cmd, ToplevelCommand) and cmd.command in ("Run", "Debug", "Reset"):
            self.kill_current_process()
            self._start_new_process(cmd)
             
        self._proc.stdin.write(serialize_message(cmd) + "\n")
        self._proc.stdin.flush()
        return True 
    
    def send_program_input(self, data):
        self.send_command(InputSubmission(data=data))
        
    def allowed_states_for_inline_commands(self):
        return ["waiting_toplevel_command", "waiting_debugger_command", 
                "waiting_input"]

    def get_sys_path(self):
        return self._sys_path
    
    def interrupt(self):
        
        def do_kill():
            self._proc.kill()
            get_workbench().event_generate("ProgramOutput",
                                           stream_name="stderr",
                                           data="KeyboardInterrupt: Forced reset")
            get_runner().reset_backend()
        
        if self._proc is not None:
            if self._proc.poll() is None:
                command_to_interrupt = get_runner().get_current_toplevel_command()
                if running_on_windows():
                    try:
                        os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                    except:
                        logging.exception("Could not interrupt backend process")
                else:
                    self._proc.send_signal(signal.SIGINT)
            
                # Tkinter programs can't be interrupted so easily:
                # http://stackoverflow.com/questions/13784232/keyboardinterrupt-taking-a-while
                # so let's chedule a hard kill in case the program refuses to be interrupted
                def go_hard():
                    if (get_runner().get_state() != "waiting_toplevel_command"
                        and get_runner().get_current_toplevel_command() == command_to_interrupt): # still running same command
                        do_kill()
                
                # 100 ms was too little for Mac
                # 250 ms was too little for one of the Windows machines
                get_workbench().after(500, go_hard)
            else:
                do_kill()
            
                    
    
    def kill_current_process(self):
        if self._proc is not None and self._proc.poll() is None: 
            self._proc.kill()
            
        self._proc = None
        self._message_queue = None
    
    def _prepare_jedi(self):
        """Make jedi available for the backend"""
        
        # Copy jedi
        import jedi
        dirname = os.path.join(THONNY_USER_DIR, "jedi_" + str(jedi.__version__))
        if not os.path.exists(dirname):
            shutil.copytree(jedi.__path__[0], os.path.join(dirname, "jedi"))
        return dirname
    
        # TODO: clean up old versions
    
    def _start_new_process(self, cmd=None):
        this_python = get_runner().get_frontend_python()
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
        
        # If the back-end interpreter is something else than front-end's one,
        # then it may not have jedi installed. 
        # In this case fffer front-end's jedi for the back-end
        if self._executable != get_runner().get_frontend_python(): 
            # I don't want to use PYTHONPATH for making jedi available
            # because that would add it to the front of sys.path
            my_env["JEDI_LOCATION"] = self._prepare_jedi()
        
        if not os.path.exists(self._executable):
            raise UserError("Interpreter (%s) not found. Please recheck corresponding option!"
                            % self._executable)
        
        
        import thonny.shared.backend_launcher
        cmd_line = [
            self._executable, 
            '-u', # unbuffered IO (neccessary in Python 3.1)
            '-B', # don't write pyo/pyc files 
                  # (to avoid problems when using different Python versions without write permissions)
            thonny.shared.backend_launcher.__file__
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
        
        debug("Starting the backend: %s %s", cmd_line, self.cwd)
        self._proc = subprocess.Popen (
            cmd_line,
            #bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=my_env,
            universal_newlines=True,
            creationflags=creationflags
        )
        
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
                msg = parse_message(data)
                if "cwd" in msg:
                    self.cwd = msg["cwd"]
                    
                # TODO: it was "with self._state_lock:". Is it necessary?
                self._message_queue.append(msg)
                
                if len(self._message_queue) > 100:
                    # Probably backend runs an infinite/long print loop.
                    # Throttle message thougput in order to keep GUI thread responsive.
                    sleep(0.1)

    def _listen_stderr(self):
        # stderr is used only for debugger debugging
        while True:
            data = self._proc.stderr.readline()
            if data == '':
                break
            else:
                debug("### BACKEND ###: %s", data.strip())
        


    @classmethod
    def _get_interpreters(cls):
        result = set()
        
        if running_on_windows():
            # registry
            result.update(CPythonProxy._get_interpreters_from_windows_registry())
            
            # Common locations
            for dir_ in ["C:\\Python34",
                         "C:\\Python35",
                         "C:\\Program Files\\Python 3.5",
                         "C:\\Program Files (x86)\\Python 3.5",
                         "C:\\Python36",
                         "C:\\Program Files\\Python 3.6",
                         "C:\\Program Files (x86)\\Python 3.6",
                         ]:
                path = os.path.join(dir_, WINDOWS_EXE)
                if os.path.exists(path):
                    result.add(os.path.realpath(path))  
        
        else:
            # Common unix locations
            for dir_ in ["/bin", "/usr/bin", "/usr/local/bin",
                         os.path.expanduser("~/.local/bin")]:
                for name in ["python3", "python3.4", "python3.5", "python3.6"]:
                    path = os.path.join(dir_, name)
                    if os.path.exists(path):
                        result.add(path)  
        
        if running_on_mac_os():
            for version in ["3.4", "3.5", "3.6"]:
                dir_ = os.path.join("/Library/Frameworks/Python.framework/Versions",
                                    version, "bin")
                path = os.path.join(dir_, "python3")
                
                if os.path.exists(path):
                    result.add(path)
        
        for command in ["pythonw", "python3", "python3.4", "python3.5", "python3.6"]:
            path = which(command)
            if path is not None and os.path.isabs(path):
                result.add(path)
        
        current_configuration = get_workbench().get_option("run.backend_configuration")
        backend, configuration_option = parse_configuration(current_configuration)
        if backend == "Python" and configuration_option and os.path.exists(configuration_option):
            result.add(os.path.realpath(configuration_option))
        
        for path in get_workbench().get_option("run.used_interpreters"):
            if os.path.exists(path):
                result.add(os.path.realpath(path))
        
        return sorted(result)
    
    
    @classmethod
    def _get_interpreters_from_windows_registry(cls):
        import winreg
        result = set()
        for key in [winreg.HKEY_LOCAL_MACHINE,
                    winreg.HKEY_CURRENT_USER]:
            for version in ["3.4",
                            "3.5", "3.5-32", "3.5-64",
                            "3.6", "3.6-32", "3.6-64"]:
                try:
                    for subkey in [
                        'SOFTWARE\\Python\\PythonCore\\' + version + '\\InstallPath',
                        'SOFTWARE\\Python\\PythonCore\\Wow6432Node\\' + version + '\\InstallPath'
                                 ]:
                        dir_ = winreg.QueryValue(key, subkey)
                        if dir_:
                            path = os.path.join(dir_, WINDOWS_EXE)
                            if os.path.exists(path):
                                result.add(path)
                except:
                    pass
        
        return result
    
    def get_interpreter_command(self):
        return self._executable
    
    
    def _update_tkupdating(self, msg):
        """Enables running Tkinter programs which doesn't call mainloop. 
        
        When mainloop is omitted, then program can be interacted with
        from the shell after it runs to the end.
        
        Each ToplevelResponse is supposed to tell, whether tkinter window
        is open and needs updating.
        """
        if not "tkinter_is_active" in msg:
            return
        
        if msg["tkinter_is_active"] and self._tkupdate_loop_id is None:
            # Start updating
            self._tkupdate_loop_id = self._loop_tkupdate(True)
        elif not msg["tkinter_is_active"] and self._tkupdate_loop_id is not None:
            # Cancel updating
            try:
                get_workbench().after_cancel(self._tkupdate_loop_id)
            finally:
                self._tkupdate_loop_id = None
    
    def _loop_tkupdate(self, force=False):
        if force or get_runner().get_state() == "waiting_toplevel_command":
            self.send_command(InlineCommand("tkupdate"))
            self._tkupdate_loop_id = get_workbench().after(50, self._loop_tkupdate)
        else:
            self._tkupdate_loop_id = None
        

    def _prepare_private_venv(self):
        path = _get_private_venv_path()
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

    def supported_features(self):
        return ["run", "debug", "pip_gui", "system_shell"]


def parse_configuration(configuration):
    """
    "Python (C:\Python34\python.exe)" becomes ("Python", "C:\Python34\python.exe")
    "BBC micro:bit" becomes ("BBC micro:bit", "")
    """
    
    parts = configuration.split("(", maxsplit=1)
    if len(parts) == 1:
        return configuration, ""
    else:
        return parts[0].strip(), parts[1].strip(" )")


    
    
def _get_private_venv_path():
    if "thonny" in sys.executable.lower():
        prefix = "BundledPython"
    else:
        prefix = "Python" 
    return os.path.join(THONNY_USER_DIR, prefix + "%d%d" % (sys.version_info[0], sys.version_info[1]))

def get_private_venv_executable():
    venv_path = _get_private_venv_path()
    
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
