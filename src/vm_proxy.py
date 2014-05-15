# -*- coding: utf-8 -*-
from __future__ import print_function, division 

import subprocess
import sys
import os.path
import logging

try:
    from _thread import start_new_thread
    from queue import Queue
except ImportError:
    from thread import start_new_thread
    from Queue import Queue

import threading

from common import parse_message, serialize_message, ToplevelCommand, PauseMessage,\
    ActionCommand

COMMUNICATION_ENCODING = "UTF-8"

logger = logging.getLogger("thonny.vmproxy")
logger.addHandler(logging.StreamHandler(sys.stdout))

_CURRENT_VM = None

class VMProxy:
    def __init__(self, default_cwd, backend_dir):
        global _CURRENT_VM
        
        if os.path.exists(default_cwd):
            self.cwd = default_cwd
        else:
            self.cwd = os.path.expanduser("~")
            
        self.backend_dir = backend_dir
        self._proc = None
        self._state_lock = threading.RLock()
        self.message_queue = Queue()
        self.send_command(ToplevelCommand(command="Reset", globals_required="__main__"))
        
        _CURRENT_VM = self
        
    def get_state(self):
        with self._state_lock:
            if self._current_pause_msg == None:
                return "busy"
            else: # "toplevel", "debug" or "input"
                return self._current_pause_msg.vm_state
    
    def get_state_message(self):
        with self._state_lock:
            return self._current_pause_msg
    
    def send_command(self, cmd):
        with self._state_lock:
            if isinstance(cmd, ActionCommand):
                self._current_pause_msg = None
            
            if (isinstance(cmd, ToplevelCommand) and cmd.command in ("Run", "Debug", "Reset")):
                self._kill_current_process()
                self._start_new_process(cmd)
                 
            self._proc.stdin.write((serialize_message(cmd) + "\n").encode(COMMUNICATION_ENCODING))
            self._proc.stdin.flush() # required for Python 3.1
            logger.debug("sent a command: %s", cmd)
    
    def send_program_input(self, data):
        with self._state_lock:
            assert self.get_state() == "input"
            self._proc.stdin.write(data.encode(COMMUNICATION_ENCODING))
            self._proc.stdin.flush()
    
    def _kill_current_process(self):
        if self._proc != None and self._proc.poll() == None: 
            self._proc.kill()
            self._proc = None
        
    def _start_new_process(self, cmd):
        self._output_queue = Queue() # discard current output queue
    
        # create new backend process
        # -u means unbuffered IO (neccessary for Python 3.1)
        my_env = os.environ
        my_env["PYTHONIOENCODING"] = COMMUNICATION_ENCODING
        
        launcher = os.path.join(self.backend_dir, "backlaunch.py")
        cmd_line = [sys.executable, '-u', launcher]
        
        if hasattr(cmd, "filename"):
            cmd_line.append(cmd.filename)
            if hasattr(cmd, "args"):
                cmd_line.extend(cmd.args)
            
        
        logger.info("VMProxy: starting the backend: %s %s", cmd_line, self.cwd)
        self._proc = subprocess.Popen (
            cmd_line,
            #bufsize=0,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.cwd,
            env=my_env
        )
        logger.debug("Done starting backend") 
        
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
                msg = parse_message(data)
                if hasattr(msg, "cwd"):
                    self.cwd = msg.cwd
                with self._state_lock:
                    self.message_queue.put(msg)
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
        
            
def send_command(cmd):
    _CURRENT_VM.send_command(cmd)