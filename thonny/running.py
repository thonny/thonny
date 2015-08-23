# -*- coding: utf-8 -*-

from _thread import start_new_thread
import collections
from logging import info, debug
import os.path
import subprocess
import sys
import threading

from thonny.common import parse_message, serialize_message, ToplevelCommand, PauseMessage, \
    ActionCommand, OutputEvent, quote_path_for_shell, DebuggerResponse, \
    DebuggerCommand, InlineCommand
from thonny.shell import ShellView
from thonny.globals import get_workbench


COMMUNICATION_ENCODING = "UTF-8"

class Runner:
    def __init__(self):
        
        get_workbench().add_defaults({
            "run.working_directory" : os.path.expanduser("~"),
            "run.auto_cd" : True, 
        })
        
        self._proxy = _BackendProxy(get_workbench().get_option("run.working_directory"),
            get_workbench().get_installation_dir())
        
        get_workbench().add_view(ShellView, "Shell", "s",
            visible_by_default=True,
            default_position_key='A')
        
        self._init_commands()
        
        self._poll_vm_messages()
        #self._advance_background_tk_mainloop()
    
    def _init_commands(self):
        
        
        get_workbench().add_command('run_current_script', "run", 'Run current script',
            handler=self._cmd_run_current_script,
            default_sequence="<F5>",
            tester=self._cmd_run_current_script_enabled)
        
        """
        get_workbench().add_command('debug_current_script', "run", 'Debug current script',
            handler=self._cmd_debug_current_script,
            default_sequence="<Control-F5>",
            tester=self._cmd_debug_current_script_enabled)
        """
        
        get_workbench().add_command('reset', "run", 'Stop/Reset',
            handler=self._cmd_reset,
            default_sequence=None # TODO:
            )
        
        """
        get_workbench().add_separator("run")
        
        get_workbench().add_command('step_over', "run", 'Step over',
            handler=self._cmd_step_over,
            default_sequence="<F7>",
            tester=self._cmd_step_over_enabled)
        
        get_workbench().add_command('step_into', "run", 'Step into',
            handler=self._cmd_step_into,
            default_sequence="<F8>",
            tester=self._cmd_step_into_enabled)
        
        """
        """
                "---", 
                Command('set_auto_cd', 'Auto-cd to script dir',  None, self,
                        kind="checkbutton", variable_name="run.auto_cd"),
        """
        
    def get_cwd(self):
        return self._proxy.cwd
    
    def request_locals(self, frame_id):
        "TODO: "
    
    def request_globals(self, module_id):
        "TODO: "
    
    def request_object_info(self, object_id):
        "TODO: "
    
    def request_reset(self, object_id):
        "TODO: "
    
    def get_state(self):
        return self._proxy.get_state()
    
    def send_command(self, cmd):
        self._proxy.send_command(cmd)
    
    def _cmd_run_current_script_enabled(self):
        return (self._proxy.get_state() == "toplevel"
                and get_workbench().get_editor_notebook().get_current_editor() is not None)
    
    def _cmd_run_current_script(self):
        self.execute_current("Run")
    
    def _cmd_debug_current_script_enabled(self):
        return self._cmd_run_current_script_enabled()
    
    def _cmd_debug_current_script(self):
        self.execute_current("Debug")
        
    def _cmd_run_current_file_enabled(self):
        return self._cmd_run_current_script_enabled()
    
    def _cmd_run_current_file(self):
        self.execute_current("run")
    
    def _cmd_debug_current_file_enabled(self):
        return self._cmd_run_current_script_enabled()
    
    def _cmd_debug_current_file(self):
        self.execute_current("debug")
    
    def execute_current(self, cmd_name, text_range=None):
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
        
        if (get_workbench().get_option("run.auto_cd") and cmd_name[0].isupper()
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
        cmd_line += "%" + cmd_name + " " + quote_path_for_shell(rel_filename) + "\n"
        if text_range is not None:
            "TODO: append range indicators" 
        
        # submit to shell (shell will execute it)
        get_workbench().get_view("ShellView").submit_magic_command(cmd_line)
        
        self.step_over = False
    
    
    def _cmd_reset(self):
        self._proxy.send_command(ToplevelCommand(command="Reset", globals_required="__main__"))
    
    def _cmd_step_into_enabled(self):
        #self._check_issue_goto_before_or_after()
        msg = self._proxy.get_state_message()
        # always enabled during debugging
        return (isinstance(msg, DebuggerResponse)) 
    
    def _cmd_step_into(self, automatic=False):
        if not automatic:
            self.step_over = False
        self._check_issue_debugger_command(DebuggerCommand(command="step"))
    
    def _cmd_step_over_enabled(self):
        return self._cmd_step_enabled()
        #self._check_issue_goto_before_or_after()
        #msg = self._proxy.get_state_message()
        #return (isinstance(msg, DebuggerResponse) 
        #        and msg.state in ("before_expression", "before_expression_again",
        #                          "before_statement", "before_statement_again")) 
    
    def _cmd_step_over(self):
        self.step_over = True
        self._cmd_step(True)

    def _check_issue_debugger_command(self, cmd, automatic=False):
        if isinstance(self._proxy.get_state_message(), DebuggerResponse):
            self._issue_debugger_command(cmd, automatic)
            # TODO: notify memory panes and editors? Make them inactive?
    
    def _issue_debugger_command(self, cmd, automatic=False):
        debug("_issue", cmd, automatic)
        
        last_response = self._proxy.get_state_message()
        # tell VM the state we are seeing
        cmd.setdefault (
            frame_id=last_response.frame_id,
            state=last_response.state,
            focus=last_response.focus
        )
        
        if not automatic:
            self.last_manual_debugger_command_sent = cmd    # TODO: hack
        self._proxy.send_command(cmd)
        # TODO: notify memory panes and editors? Make them inactive?
            
    def _cmd_set_auto_cd(self):
        print(self._auto_cd.get())
        
    def stop_debugging(self):
        self.editor_notebook.stop_debugging()
        self._shell.stop_debugging()
        self.globals_frame.stop_debugging()
        self.builtins_frame.stop_debugging()
        self.heap_frame.stop_debugging()
        self._proxy.reset()
    
    def start_debugging(self, filename=None):
        self.editor_notebook.start_debugging(self._proxy, filename)
        self._shell.start_debugging(self._proxy, filename)
        self._proxy.start()
    
    def _advance_background_tk_mainloop(self):
        if self._proxy.get_state() == "toplevel":
            self._proxy.send_command(InlineCommand(command="tkupdate"))
        self.after(50, self._advance_background_tk_mainloop)
        
    def _poll_vm_messages(self):
        # I chose polling instead of event_generate
        # because event_generate across threads is not reliable
        # http://www.thecodingforums.com/threads/more-on-tk-event_generate-and-threads.359615/
        while True:
            msg = self._proxy.fetch_next_message()
            if not msg:
                break
            
            # skip some events
            if (isinstance(msg, DebuggerResponse) 
                and hasattr(msg, "tags") 
                and "call_function" in msg.tags
                and not self.get_option("debugging.expand_call_functions")):
                
                self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
                continue
                
            if hasattr(msg, "success") and not msg.success:
                print("_poll_vm_messages, not success")
                self.bell()
            
            # publish event
            get_workbench().event_generate("BackendMessage", message=msg)
            get_workbench().set_option("run.working_directory", self._proxy.cwd, save_now=False)
            
            self._update_title()
            
            # automatically advance from some events
            # TODO:
            """
            if (isinstance(msg, DebuggerResponse) 
                and msg.state in ("after_statement", "after_suite", "before_suite")
                and not self.get_option("debugging.detailed_steps")
                or self.continue_with_step_over(self.last_manual_debugger_command_sent, msg)):
                
                self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
            """
            get_workbench().update_idletasks()
            
        get_workbench().after(50, self._poll_vm_messages)
    
    def _update_title(self):
        get_workbench().title("Thonny  -  Python {1}.{2}.{3}  -  {0}".format(self.get_cwd(), *sys.version_info))
        
    def continue_with_step_over(self, cmd, msg):
        if not self.step_over:
            print("Not step_over")
            return False
        
        if not isinstance(msg, DebuggerResponse):
            return False
        
        if cmd is None:
            return False
        
        if msg.state not in ("before_statement", "before_expression", "after_expression"):
            # TODO: hack, may want after_statement
            return True
        
        if msg.frame_id != cmd.frame_id:
            return True
        
        if msg.focus.is_smaller_in(cmd.focus):
            print("smaller")
            return True
        else:
            print("outside")
            return False
        
    
    

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
        self.send_command(ToplevelCommand(command="Reset", globals_required="__main__"))
        
        _CURRENT_VM = self
        
    def get_state(self):
        with self._state_lock:
            if self._current_pause_msg is None:
                return "busy"
            else: # "toplevel", "debug" or "input"
                return self._current_pause_msg.vm_state
    
    def get_state_message(self):
        # TODO: create separate class for expressing backend state
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
            debug("sent a command: %s", cmd)
    
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
        
            
