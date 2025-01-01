#!/usr/bin/env python3

import os.path
import subprocess
import sys
import select
from datetime import datetime


class SimpleIOLogger:
    def __init__(self, command, logfile):
        """
        Initialize logger with command to run and logfile path.

        Args:
            command (list): Command and arguments to execute
            logfile (str): Path to the log file
        """
        self.command = command
        self.logfile = logfile

    def _log(self, data, sender):
        """Log data with timestamp and direction indicator."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with open(self.logfile, 'a') as f:
            f.write(data)
            f.write(f"{sender}!!!!!")
            #f.write(f"[{timestamp}] {'>' if direction == 'input' else '<'}\n{data}")

    def run(self):
        """Run the process with logged I/O."""
        process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0  # Unbuffered
        )

        try:
            # Make stdout non-blocking
            import fcntl, os
            fl = fcntl.fcntl(process.stdout, fcntl.F_GETFL)
            fcntl.fcntl(process.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            while True:
                reads = [sys.stdin, process.stdout]
                writes = []

                # Check if process has terminated
                if process.poll() is not None:
                    break

                readable, writable, _ = select.select(reads, writes, [], 0.1)

                for fd in readable:
                    if fd is process.stdout:
                        try:
                            chunk = os.read(process.stdout.fileno(), 4096)
                            if chunk:
                                decoded = chunk.decode('utf-8', errors='replace')
                                self._log(decoded, 'SERVER')
                                sys.stdout.buffer.write(chunk)
                                sys.stdout.buffer.flush()
                        except BlockingIOError:
                            continue

                    elif fd is sys.stdin:
                        chunk = os.read(sys.stdin.fileno(), 4096)
                        if chunk:
                            self._log(chunk.decode('utf-8', errors='replace'), 'CLIENT')
                            process.stdin.write(chunk)
                            process.stdin.flush()
                        else:
                            # EOF on stdin
                            process.stdin.close()
                            reads.remove(sys.stdin)

        finally:
            if process.stdin:
                process.stdin.close()
            process.stdout.close()
            if process.poll() is None:
                process.terminate()
                process.wait()


if __name__ == "__main__":
    command = [os.path.expanduser("~/python_stuff/uv1/hxvenv/bin/basedpyright-langserver-orig"), "--stdio"]

    logfile = "out.log"

    logger = SimpleIOLogger(command, logfile)
    logger.run()
