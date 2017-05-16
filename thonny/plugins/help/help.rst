===========
Thonny help
===========



Running programs step-wise
==========================
If you want to see how Python executes your program step-by-step then you should run it in *debug-mode*.

Start by selecting *Debug current script* from the *Run* menu or by pressing Ctrl+F5. You'll see that first statement of the program gets highlighted and nothing more happens. In this mode you need to notify Thonny that you're ready to let Python make the next step. For this you have two main options:

* *Run → Step over* (or F6) makes big steps, ie. it executes the highlighted code and highlights the next part of the code.
* *Run → Step into* (or F7) tries to make smaller steps. If the highlighted code is made of smaller parts (statements or expressions), then first of these gets highlighted and Thonny waits for next command. If you have reached to a program component which doesn't have any sub-parts (eg. variable name) then *Step into* works like *Step over*, ie. executes (or evaluates) the code.

If you have stepped into the depths of a statement or expression and want to move on faster, then you can use *Run → Step out* (or F8), which executes currently highlighted code and all following program parts on the same level.

If you want to reach a specific part of the code, then you can speed up the process by placing your cursor on that line and selecting *Run → Run to cursor*. This makes Thonny automatically step until this line. You can take the command from there.

Installing 3rd party packages
==============================
Thonny has two options for installing 3rd party libraries.

With pip-GUI
-------------
From "Tools" menu select "Manage packages..." and follow the instructions.

.. image:: https://bitbucket.org/repo/gXnbod/images/2226680569-pipgui_big.png
   :alt: pipgui_big.png

With pip on command line
------------------------
#. From "Tools" menu select "Open system shell...". You should get a new terminal window stating the correct name of *pip* command (usually ``pip`` or ``pip3``). In the following I've assumed the command name is ``pip``.
#. Enter ``pip install <package name>`` (eg. ``pip install pygame``) and press ENTER. You should see *pip* downloading and installing the package and printing a success message.
#. Close the terminal (optional)
#. Return to Thonny
#. Reset interpreter by selecting "Stop/Reset" from "Run menu" (this is required only first time you do pip install)
#. Start using the package

.. image:: https://bitbucket.org/repo/gXnbod/images/1183520217-pipinstall_cmdline.png
   :alt: pipinstall_cmdline.png


Using scientific Python packages
================================
Python distribution coming with Thonny doesn't contain scientific programming libraries (eg. `NumPy <http://numpy.org/>`_  and `Matplotlib <http://matplotlib.org/>`_). 

Recent versions of most popular scientific Python packages (eg. numpy, pandas and matplotlib) have wheels available for popular platforms so you can most likely install them with pip but in case you have troubles, you could try using Thonny with separate Python distribution meant for scientific computing (eg. `Anaconda <https://www.continuum.io/downloads>`_, `Canopy <https://www.enthought.com/products/canopy/>`_ or `Pyzo <http://www.pyzo.org/>`_).


Example: Using Anaconda
------------------------------------
Go to https://www.continuum.io/downloads and download a suitable binary distribution for your platform. Most likely you want graphical installer and 64-bit version (you may need 32-bit version if you have very old system). **Note that Thonny supports only on Python 3, so make sure you choose Python 3 version of Anaconda.**

Install it and find out where it puts Python executable (*pythonw.exe* in Windows and *python3* or *python* in Linux and Mac). For example in Windows the full path is by default ``c:\anaconda\pythonw.exe``.

In Thonny open "Tools" menu and select "Options...". In the options dialog open "Intepreter" tab, click "Select executable" and show the location of Anaconda's Python executable.

After you have done this, next time you run your program, it will be run through Anaconda's Python and all the libraries installed there are available.