"""Intermediate process for communicating with the remote Python via SSH"""
import sys

from thonny.backend import SshBackend
from thonny.common import parse_message


class CPythonSshBackend(SshBackend):
    def __init__(self, host, user, password):
        self._init_client(host, user, password)

    def mainloop(self):
        while True:
            line = sys.stdin.readline()
            cmd = parse_message(line)
