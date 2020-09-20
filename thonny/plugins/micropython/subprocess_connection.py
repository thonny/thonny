import signal
import sys

from thonny.plugins.micropython.connection import MicroPythonConnection


class SubprocessConnection(MicroPythonConnection):
    def __init__(self, executable, args=[]):
        import threading

        try:
            import ptyprocess
        except ImportError:
            print(
                "ERROR: This back-end requires a Python package named 'ptyprocess'.\n"
                + "Install it via system package manager or 'Tools => Manage plug-ins'."
            )
            sys.exit(1)

        super().__init__()
        cmd = [executable] + args
        self._proc = ptyprocess.PtyProcessUnicode.spawn(cmd, echo=False)
        # print(dir(self._proc))
        # self._poll = select.poll()
        # self._poll.register(self._proc, select.POLLIN)

        # self._stdout = self._proc.stdout

        self._reading_thread = threading.Thread(target=self._listen_output, daemon=True)

        self._reading_thread.start()

    def write(self, data):
        if isinstance(data, (bytes, bytearray)):
            data = data.decode(self.encoding)
        self._proc.write(data)
        self._proc.flush()
        return len(data)

    def _listen_output(self):
        "NB! works in background thread"
        try:
            while True:
                chars = self._proc.read(1)
                if len(chars) > 0:
                    as_bytes = chars.encode(self.encoding)
                    self._make_output_available(as_bytes)
                else:
                    self._error = "EOF"
                    break

        except Exception as e:
            self._error = str(e)

    def close(self):
        if self._proc is not None:
            self._proc.kill(signal.SIGKILL)
            # self._reading_thread.join() # 0.2 secs!
            self._proc = None
            self._reading_thread = None
