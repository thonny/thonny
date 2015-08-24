# -*- coding: utf-8 -*-

from _thread import start_new_thread
import collections
from logging import info, debug
import os.path
import subprocess
import sys
import threading

from thonny.common import parse_message, serialize_message, ToplevelCommand, PauseMessage, \
    ActionCommand, OutputEvent, quote_path_for_shell, \
    InlineCommand, parse_shell_command, unquote_path,\
    CommandSyntaxError
from thonny.shell import ShellView
from thonny.globals import get_workbench
import shlex


COMMUNICATION_ENCODING = "UTF-8"

class Runner:
    def __init__(self):
        
        get_workbench().add_option("run.working_directory", os.path.expanduser("~"))
        get_workbench().add_option("run.auto_cd", True)
        
        self._proxy = _BackendProxy(get_workbench().get_option("run.working_directory"),
            get_workbench().get_installation_dir())
        
        get_workbench().add_view(ShellView, "Shell", "s",
            visible_by_default=True,
            default_position_key='A')
        
        self._shell = get_workbench().get_view("ShellView")
        self._shell.add_command("Run", self._handle_magic_command_from_shell)
        self._shell.add_command("Reset", self._handle_magic_command_from_shell)
        self._shell.add_command("cd", self._handle_magic_command_from_shell)
        
        self._init_commands()
        
        self._poll_vm_messages()
        self._advance_background_tk_mainloop()
    
    def _init_commands(self):
        get_workbench().add_command('run_current_script', "run", 'Run current script',
            handler=self._cmd_run_current_script,
            default_sequence="<F5>",
            tester=self._cmd_run_current_script_enabled)
        
        get_workbench().add_command('reset', "run", 'Stop/Reset',
            handler=self._cmd_reset,
            default_sequence=None # TODO:
            )
        
    def get_cwd(self):
        return self._proxy.cwd
    
    def get_state(self):
        return self._proxy.get_state()
    
    def send_command(self, cmd):
        self._proxy.send_command(cmd)
    
    def execute_current(self, mode):
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
        
        # changing dir may be required
        script_dir = os.path.dirname(filename)
        
        if (get_workbench().get_option("run.auto_cd") and mode[0].isupper()
            and self._proxy.cwd != script_dir):
            # create compound command
            # start with %cd
            cmd_line = "%cd " + quote_path_for_shell(script_dir) + "\n"
            next_cwd = script_dir
        else:
            # create simple command
            cmd_line = ""
            next_cwd = self._proxy.cwd
        
        # append main command (Run, run, Debug or debug)
        rel_filename = os.path.relpath(filename, next_cwd)
        cmd_line += "%" + mode + " " + quote_path_for_shell(rel_filename) + "\n"
        
        # submit to shell (shell will execute it)
        get_workbench().get_view("ShellView").submit_command(cmd_line)
        
    def _cmd_run_current_script_enabled(self):
        return (self._proxy.get_state() == "toplevel"
                and get_workbench().get_editor_notebook().get_current_editor() is not None)
    
    def _cmd_run_current_script(self):
        self.execute_current("Run")
    

    def _handle_magic_command_from_shell(self, cmd_line):
        command, arg_str = parse_shell_command(cmd_line)
        assert command in ["Run", "Reset", "cd"] 

        args = shlex.split(arg_str.strip(), posix=False)
        
        if command == "Reset":
            if len(args) == 0:
                self.send_command(ToplevelCommand(command="Reset"))
            else:
                raise CommandSyntaxError("Command 'Reset' doesn't take arguments")
                
        elif command == "cd":
            if len(args) == 1:
                self.send_command(ToplevelCommand(command="cd", path=unquote_path(args[0])))
            elif len(args) > 1:
                # extra flexibility for those who forgot the quotes
                self.send_command(ToplevelCommand(command="cd", 
                                       path=unquote_path(arg_str)))
            else:
                raise CommandSyntaxError("Directory missing in '{0}'".format(cmd_line))
                
                
        elif command == "Run":
            if len(args) >= 1:
                get_workbench().get_editor_notebook().save_all_named_editors()
                
                self.send_command(ToplevelCommand(command=command,
                                   filename=unquote_path(args[0]),
                                   args=args[1:],
                                   id=self._shell.get_last_command_id()))
            else:
                raise CommandSyntaxError("Filename missing in '{0}'".format(cmd_line))

    
    def _cmd_reset(self):
        self._shell.submit_command("%Reset\n")
    

            
    def _advance_background_tk_mainloop(self):
        """Enables running Tkinter programs which doesn't call mainloop. 
        
        When mainloop is omitted, then program can be interacted with
        from the shell after it runs to the end.
        """
        if self._proxy.get_state() == "toplevel":
            self._proxy.send_command(InlineCommand(command="tkupdate"))
        get_workbench().after(50, self._advance_background_tk_mainloop)
        
    def _poll_vm_messages(self):
        """I chose polling instead of event_generate
        because event_generate across threads is not reliable
        http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        """
        while True:
            msg = self._proxy.fetch_next_message()
            if not msg:
                break
            
            if hasattr(msg, "success") and not msg.success:
                info("_poll_vm_messages, not success")
            
            get_workbench().event_generate("BackendMessage", message=msg)
            get_workbench().set_option("run.working_directory", self._proxy.cwd, save_now=False)
            get_workbench().update_idletasks()
            
        get_workbench().after(50, self._poll_vm_messages)
    

class _BackendProxy:
    def __init__(self, default_cwd, main_dir):
        global _CURRENT_VM
        
        if os.path.exists(default_cwd):
            self.cwd = default_cwd
        else:
            self.cwd = os.path.expanduser("~")
            
        self.thonny_dir = main_dir
        self._proc = None
        self._state_lock = threading.RLock()
        self.send_command(ToplevelCommand(command="Reset"))
        
        _CURRENT_VM = self
        
    def get_state(self):
        with self._state_lock:
            if self._current_pause_msg is None:
                return "busy"
            else: # "toplevel", "debug" or "input"
                return self._current_pause_msg.vm_state
    
    def get_state_message(self):
        with self._state_lock:
            return self._current_pause_msg
    
    def fetch_next_message(self):
        # combine available output messages to one single message, 
        # in order to put less pressure on UI code
        if not self._message_queue or len(self._message_queue) == 0:
            return None
        
        msg = self._message_queue.popleft()
        if isinstance(msg, OutputEvent):
            stream_name = msg.stream_name
            data = msg.data
            
            while True:
                if len(self._message_queue) == 0:
                    return OutputEvent(stream_name=stream_name, data=data)
                else:
                    msg = self._message_queue.popleft()
                    if isinstance(msg, OutputEvent) and msg.stream_name == stream_name:
                        data += msg.data
                    else:
                        # not same type of message, put it back
                        self._message_queue.appendleft(msg)
                        return OutputEvent(stream_name=stream_name, data=data)
            
        else: 
            return msg
    
    def send_command(self, cmd):
        with self._state_lock:
            if isinstance(cmd, ActionCommand):
                self._current_pause_msg = None
            
            if (isinstance(cmd, ToplevelCommand) and cmd.command in ("Run", "Debug", "Reset")):
                self._kill_current_process()
                self._start_new_process(cmd)
                 
            self._proc.stdin.write((serialize_message(cmd) + "\n").encode(COMMUNICATION_ENCODING))
            self._proc.stdin.flush() # required for Python 3.1
            #debug("sent a command: %s", cmd)
    
    def send_program_input(self, data):
        with self._state_lock:
            assert self.get_state() == "input"
            self._proc.stdin.write(data.encode(COMMUNICATION_ENCODING))
            self._proc.stdin.flush()
    
    def _kill_current_process(self):
        if self._proc is not None and self._proc.poll() is None: 
            self._proc.kill()
            self._proc = None
            self._message_queue = None
        
    def _start_new_process(self, cmd):
        self._message_queue = collections.deque()
    
        # create new backend process
        # -u means unbuffered IO (neccessary for Python 3.1)
        my_env = os.environ.copy()
        my_env["PYTHONIOENCODING"] = COMMUNICATION_ENCODING
        
        launcher = os.path.join(self.thonny_dir, "thonny", "backend")
        cmd_line = [sys.executable, '-u', launcher]
        
        if hasattr(cmd, "filename"):
            cmd_line.append(cmd.filename)
            if hasattr(cmd, "args"):
                cmd_line.extend(cmd.args)
            
        
        info("VMProxy: starting the backend: %s %s", cmd_line, self.cwd)
        self._proc = subprocess.Popen (
            cmd_line,
            #bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=my_env
        )
        debug("Done starting backend") 
        
        # setup asynchronous output listeners
        start_new_thread(self._listen_stdout, ())
        start_new_thread(self._listen_stderr, ())
    
    def _listen_stdout(self):
        #debug("... started listening to stdout")
        # will be called from separate thread
        while True:
            data = self._proc.stdout.readline().decode(COMMUNICATION_ENCODING)
            #debug("... read some stdout data", repr(data))
            if data == '':
                break
            else:
                #print("MSG", data)
                msg = parse_message(data)
                if hasattr(msg, "cwd"):
                    self.cwd = msg.cwd
                with self._state_lock:
                    self._message_queue.append(msg)
                    if isinstance(msg, PauseMessage):
                        self._current_pause_msg = msg

    def _listen_stderr(self):
        # stderr is used only for debugger debugging
        while True:
            data = self._proc.stderr.readline().decode(COMMUNICATION_ENCODING)
            if data == '':
                break
            else:
                print("BACKEND:", data.strip(), end="\n")
        
            
