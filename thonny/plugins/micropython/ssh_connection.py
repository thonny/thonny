import shlex

from thonny.plugins.micropython.connection import MicroPythonConnection


class SshProcessConnection(MicroPythonConnection):
    def __init__(self, client, cwd, executable, args):
        super().__init__()
        import threading

        self._client = client

        cmd_line_str = (
            "echo $$ ;"
            + ((" cd %s  2> /dev/null ;" % shlex.quote(cwd) if cwd else ""))
            + (" exec " + " ".join(map(shlex.quote, [executable] + args)))
        )
        self._stdin, self._stdout, _ = self._client.exec_command(
            cmd_line_str, bufsize=0, timeout=None, get_pty=True
        )

        # stderr gets directed to stdout because of pty
        self._pid = self._stdout.readline().strip()

        self._reading_thread = threading.Thread(target=self._listen_output, daemon=True)
        self._reading_thread.start()

    def write(self, data, block_size=255, delay=0.01):
        if isinstance(data, str):
            data = data.encode(self.encoding)
        self._stdin.write(data)
        self._stdin.flush()
        return len(data)

    def _listen_output(self):
        "NB! works in background thread"
        try:
            while not self._reader_stopped:
                data = self._stdout.read(1)
                if len(data) > 0:
                    self._make_output_available(data)
                else:
                    self._error = "EOF"
                    break

        except Exception as e:
            self._error = str(e)

    def close(self):
        self._client.exec_command("kill -s SIGKILL %s" % self._pid)
        self._reading_thread.join()
        self._client = None
        self._reading_thread = None
