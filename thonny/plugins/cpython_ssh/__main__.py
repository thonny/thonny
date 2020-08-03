import sys
import ast

from thonny.plugins.cpython_ssh.cpython_ssh_backend import CPythonSshBackend

args = ast.literal_eval(sys.argv[1])
backend = CPythonSshBackend(**args)
backend.mainloop()
