===============
Version history
===============

Unreleased
==========

* NEW: Dialog for managing 3rd party packages / a simple pip GUI. Check it out: "Tools => Manage packages"
* NEW: Window title now shows full path and cursor location of current file. 
* NEW: Editor lines can be selected by clicking and/or dragging on line-number margin (thanks to Sven).
* ENHANCEMENT: Recommended pip-command now appears faster in System Shell.
* EXPERIMENTAL: Ctrl-click on a name in code tries to locate its definition. NB! Not finished yet!
* CHANGED: Bundled Python version has been upgraded to 3.6.1
* CHANGED: Bundled Python in Mac and Linux new uses SSL certs from `certifi project
<https://pypi.python.org/pypi/certifi>`_.
* REMOVED: Moved incomplete Exercise system to a separate plugin (https://bitbucket.org/plas/thonny-exersys). With this got rid of tkinterhtml, requests and beautifulsoup4 dependencies.
* FIXED #98: Nested functions crashed the debugger.
* FIXED #114: Crash when trying to change interpreter in macOS.
* FIXED #142: "Open system shell" failed when Thonny path had spaces in it. Paths are now properly quoted.
* FIXED #159: Debugging list or set comprehension caused crash
* FIXED #187: Main modules launched by Thonny were missing `__spec__` attribute.
* FIXED #195: Debugger crashes when using generators.
* FIXED #201: "Tools => Open Thonny data folder" now works also in macOS.
* FIXED #211: Linux installer was failing when using `xdg-user-dir` (thanks to Ryan McQuen)
* FIXED: Event logger did not save filenames (eb34c5d).
* FIXED: Problem in replayer (db78855).
* TECHNICAL: Bundled Jedi version has been upgraded to 0.10.0.
* TECHNICAL: 3rd party Thonny plugins must now be under `thonnycontrib` namespace package.
* TECHNICAL: Introduced the concept of "eary plugins" (plugins, which get loaded before initializing the runner).
* TECHNICAL: Refactored the interface between GUI and backend to allow different backend implementations
* TECHNICAL: Previously, with bundled Python, Thonny was using nasty tricks to force pip install packages install under ~/.thonny. Now it creates a proper virtual environment under ~/.thonny and uses this as the backend by default (instead of using interpreter running the GUI directly).

2.0.7 (2017-01-06)
==================

* FIXED: Making font size too small would crash Thonny.
* FIXED: Another take on configuration file corruption. 
* FIXED: Shift-Tab wasn’t working in some cases.
* FIXED #165: "Open system shell" did not add Scripts dir to PATH in Windows. 
* FIXED #183: `from __future__ import` crashed the debugger.

2.0.6 (2017-01-06)
==================
* FIXED: a bug in Linux installer (configuration file wasn’t created in new installations)

2.0.5 (2016-11-30)
==================
* FIXED: Corrected shift key detection (a82bd4d)

2.0.4 (2016-10-26)
==================
* FIXED: Configuration file was occasionally getting corrupted (for mysterious reasons, maybe a bug in Python’s configparser)

2.0.3 (2016-09-30)
==================
See https://bitbucket.org/plas/thonny/issues/ and https://bitbucket.org/plas/thonny/commits/ for details 