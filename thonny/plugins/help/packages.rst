Installing 3rd party packages
==============================
Thonny has two options for installing 3rd party libraries.

With pip-GUI
-------------
From "Tools" menu select "Manage packages..." and follow the instructions.

With pip on command line
------------------------
#. From "Tools" menu select "Open system shell...". You should get a new terminal window stating the correct name of *pip* command (usually ``pip`` or ``pip3``). In the following I've assumed the command name is ``pip``.
#. Enter ``pip install <package name>`` (eg. ``pip install pygame``) and press ENTER. You should see *pip* downloading and installing the package and printing a success message.
#. Close the terminal (optional)
#. Return to Thonny
#. Reset interpreter by selecting "Stop/Reset" from "Run menu" (this is required only first time you do pip install)
#. Start using the package


Using scientific Python packages
================================
Python distribution coming with Thonny doesn't contain scientific programming libraries 
(eg. `NumPy <http://numpy.org/>`_  and `Matplotlib <http://matplotlib.org/>`_). 

Recent versions of most popular scientific Python packages (eg. numpy, pandas and 
matplotlib) have wheels available for popular platforms so you can most likely install 
them with pip but in case you have troubles, you could try using Thonny with separate 
Python distribution meant for scientific computing 
(eg. `Anaconda <https://www.anaconda.com>`_
or `Pyzo <http://www.pyzo.org/>`_).


Example: Using Anaconda
------------------------------------
Go to https://www.anaconda.com/products/individual and download a suitable binary distribution for
your platform. Most likely you want graphical installer and 64-bit version (you may need 
32-bit version if you have very old system).

Install it and find out where it puts Python executable (*pythonw.exe* in Windows and 
*python3* or *python* in Linux and Mac).

In Thonny open "Tools" menu and select "Options...". In the options dialog open "Interpreter" 
tab, click "Select executable" and show the location of Anaconda's Python executable.

After you have done this, next time you run your program, it will be run through Anaconda's 
Python and all the libraries installed there are available.
