import sys
import ast

from thonny.plugins.cpython_ssh.ssh_cpython_backend import SshCPythonBackend

args = ast.literal_eval(sys.argv[1])
backend = SshCPythonBackend(**args)
backend.mainloop()
