import subprocess
import pty
import os


from thonny.plugins.micropython.connection import MicroPythonConnection
import threading


class SerialConnection(MicroPythonConnection):
    def __init__(self, executable, args, env):
        master, slave = pty.openpty()
        self._proc = subprocess.Popen(
            [executable] + args,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=slave,
            universal_newlines=True,
        )

        self._stdin = os.fdopen(master, 'w')    
            
        self._reading_thread = threading.Thread(target=self._listen_serial, daemon=True)
        self._reading_thread.start()
