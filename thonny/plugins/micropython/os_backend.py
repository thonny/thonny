from thonny.plugins.micropython.backend import MicroPythonBackend

FALLBACK_BUILTIN_MODULES = [
    "cmath",
    "gc",
    "math",
    "sys",
    "array",
    # "binascii", # don't include it, as it may give false signal for reader/writer
    "collections",
    "errno",
    "hashlib",
    "heapq",
    "io",
    "json",
    "os",
    "re",
    "select",
    "socket",
    "ssl",
    "struct",
    "time",
    "zlib",
    "_thread",
    "btree",
    "micropython",
    "cryptolib",
    "ctypes",
]


class MicroPythonOsBackend(MicroPythonBackend):
    def _process_until_initial_prompt(self, clean):
        raise NotImplementedError()

    def _fetch_welcome_text(self):
        raise NotImplementedError()

    def _fetch_builtin_modules(self):
        return FALLBACK_BUILTIN_MODULES

    def _fetch_cwd(self):
        raise NotImplementedError()

    def _soft_reboot(self, side_command):
        raise NotImplementedError()

    def _execute(self, script, timeout, capture_stdout):
        """Ensures prompt and submits the script.
        Returns (out, value_repr, err) if there are no problems, ie. all parts of the 
        output are present and it reaches active prompt.
        Otherwise raises ProtocolError.
        
        The execution may block. In this case the user should do something (eg. provide
        required input or issue an interrupt). The UI should remind the interrupt in case
        of Thonny commands.
        """
        raise NotImplementedError()

    def _forward_output_until_active_prompt(self, stream_name="stdout"):
        """Used for finding initial prompt or forwarding problematic output 
        in case of protocol errors"""
        raise NotImplementedError()

    def _forward_unexpected_output(self, stream_name="stdout"):
        "Invoked between commands"
        raise NotImplementedError()

    def _cmd_cd(self, cmd):
        raise NotImplementedError()

    def _cmd_execute_system_command(self, cmd):
        raise NotImplementedError()

    def _cmd_get_fs_info(self, cmd):
        raise NotImplementedError()

    def _cmd_write_file(self, cmd):
        raise NotImplementedError()

    def _cmd_delete(self, cmd):
        raise NotImplementedError()

    def _cmd_read_file(self, cmd):
        raise NotImplementedError()

    def _cmd_mkdir(self, cmd):
        raise NotImplementedError()

    def _upload_file(self, source, target, notifier):
        raise NotImplementedError()

    def _download_file(self, source, target, notifier=None):
        raise NotImplementedError()

