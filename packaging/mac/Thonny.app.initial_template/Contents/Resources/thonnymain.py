# Bootstrap script for Thonny as an application bundle.
# Inspired by https://github.com/python/cpython/blob/master/Mac/IDLE/IDLE.app/Contents/Resources/idlemain.py
import os.path
import sys

# Make sure sys.executable points to the python interpreter inside the
# framework, instead of at the helper executable inside the application
# bundle (the latter works, but doesn't allow access to the window server)
#
#  .../Thonny.app/
#       Contents/
#           MacOS/
#               Thonny (a python script)
#               Python{-32} (symlink)
#           Resources/
#               thonnymain.py (this module)
#               ...
#
# ../Thonny.app/Contents/MacOS/Python{-32} is symlinked to
#       ../Frameworks/Python.framework/Versions/m.n
#                   /Resources/Python.app/Contents/MacOS/Python{-32}
#       which is the Python interpreter executable
#
# The flow of control is as follows:
# 1. Thonny.app is launched which starts python running the thonny script
# 2. thonny script exports
#       PYTHONEXECUTABLE = .../Thonny.app/Contents/MacOS/Python{-32}
#           (the symlink to the framework python)
# 3. Thonny script alters sys.argv and uses os.execve to replace itself with
#       thonnymain.py running under the symlinked python.
#       This is the magic step.
#       NB! This seems to enable Thonny menu instead of Python menu
# 4. During interpreter initialization, because PYTHONEXECUTABLE is defined,
#    sys.executable may get set to an unuseful value.
#
# Now fix up the execution environment before importing thonny.

# Reset sys.executable to its normal value, the actual path of
# the interpreter in the framework, by following the symlink
# exported in PYTHONEXECUTABLE.
pyex = os.environ['PYTHON_SYS_EXECUTABLE']
sys.executable = os.path.join(sys.prefix, 'bin', 'python%d.%d'%(sys.version_info[:2]))

# Remove any sys.path entries for the Resources dir in the Thonny.app bundle.
p = pyex.partition('.app')
if p[2].startswith('/Contents/MacOS/Python'):
    sys.path = [value for value in sys.path if
            value.partition('.app') != (p[0], p[1], '/Contents/Resources')]

# Unexport PYTHONEXECUTABLE so that the other Python processes started
# by Thonny have a normal sys.executable.
del os.environ['PYTHON_SYS_EXECUTABLE']

# Look for the -psn argument that the launcher adds and remove it, it will
# only confuse the Thonny startup code.
for idx, value in enumerate(sys.argv):
    if value.startswith('-psn_'):
        del sys.argv[idx]
        break

# Now it is safe to import thonny.
if __name__ == '__main__':
    import thonny
    thonny.launch()
