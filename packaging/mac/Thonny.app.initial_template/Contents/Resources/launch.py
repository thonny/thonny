# inspired by IDLE.app/Contents/IDLE

import sys
import os.path

execdir = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), "MacOS")
executable = os.path.join(execdir, "Python")
resdir = os.path.join(os.path.dirname(execdir), "Resources")
libdir = os.path.join(os.path.dirname(execdir), "Frameworks/Python.framework/Versions/3.10/lib")
ssl_cert_dir = libdir + "/python3.10/site-packages/certifi"
mainprogram = os.path.join(resdir, "thonnymain.py")

sys.argv.insert(1, mainprogram)
sys.argv.insert(1, "-I")

os.environ["PYTHON_SYS_EXECUTABLE"] = executable
os.environ["SSL_CERT_DIR"] = ssl_cert_dir
os.environ["SSL_CERT_FILE"] = ssl_cert_dir + "/cacert.pem"
os.environ["TCL_LIBRARY"] = libdir + "/tcl8.6"
os.environ["TK_LIBRARY"] = libdir + "/tk8.6"

os.execve(executable, sys.argv, os.environ)
