import ast
import sys

import thonny
from thonny.plugins.cpython_ssh.ssh_cpython_backend import SshCPythonBackend

thonny.configure_backend_logging()
args = ast.literal_eval(sys.argv[1])
backend = SshCPythonBackend(**args)
backend.mainloop()
