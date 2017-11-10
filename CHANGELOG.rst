===============
Version history
===============

2.1.16 (2017-11-10)
===================
* Tests moved under thonny package
* Tests included in the source distribution
* More icons included in the source distribution

2.1.15 (2017-11-07)
===================
* Removed StartupNotify from Linux .desktop file (StartupNotify=true leaves cursor spinning in Debian)

2.1.14 (2017-11-02)
===================
* Added some Linux-specific files to source distribution. No new features or fixes.

2.1.13 (2017-10-29)
===================
* Temporary workaround for #351: Locals and name highlighter occasionally make Thonny freeze
* Include only required licenses in source dist

2.1.12 (2017-10-13)
===================
* FIXED #303: Allow specifying same interpreter for backend as frontend uses
* FIXED #304: Allow specifying backend interpreter by relative path
* FIXED #312: Closing unsaved tab causes error    
* FIXED #319: Linux install script needs quoting around the path(s) 
* FIXED #320: Install gets recursive if trying to install within extracted tarball 
* FIXED #321: Linux installer fails if invoked with relative, local user path 
* FIXED #334: init.tcl not found (Better control over back-end environment variables)
* FIXED #343: Thonny now also works with jedi 0.11

2.1.11 (2017-07-22)
===================
* FIXED #31: Infinite print loop freezes Thonny  
* FIXED #285: Previous used interpreters are not shown in options dialog
* FIXED #296: Make it more explicit that pip GUI search box needs exact package name
* FIXED #298: Python crashes keep backend hanging 
* FIXED #305: Variables table doesn't get updated, if it's blocked by another view

2.1.10 (2017-06-09)
===================
* NEW: More flexibility for classroom setups (see https://bitbucket.org/plas/thonny/wiki/ClassroomSetup) 
* FIXED #276: Copy with Ctrl+C causes bell
* FIXED #277: Triple-quoted strings keep keyword coloring
* FIXED #278: Paste in shell causes bell 
* FIXED #281: Wrong unindentation with SHIFT+TAB when last line does not end with linebreak
* FIXED #283: backend.log path doesn't take THONNY_USER_DIR into account
* FIXED #284: Internal error when saving to a read-only folder/file (now proposes to choose another name)

2.1.9 (2017-06-01)
==================
* FIXED #273: Memory leak in editor margin because of undo log
* FIXED #275: Updating line numbers is very inefficient
* FIXED: Pasted text occasionally was hidden below bottom edge of the editor
* FIXED: sys.exit() didn't really close the backend 

2.1.8 (2017-05-28)
==================
* ENHANCEMENT: Code completion with Tab-key is now optional (see Tools => Options => Editor)
* ENHANCEMENT: Clicking on the editor now closes code completion box
* CHANGED: Code completion box doesn't offer names starting with double underscore anymore.
* FIXED: Error caused by too fast typing with open code completions box 
* ENHANCEMENT: Find/Replace dialog can now be operated with F3
* ENHANCEMENT: Find/Replace pre-selects previously used search string
* ENHANCEMENT: Find/Replace dialog doesn't block main window anymore
* FIXED: Find/Replace doesn't ignore spaces in search string anymore 
* FIXED: Closed views reappeared after restart if they were only views in that notebook  
* FIXED #264: Debugger fails with with conditional list comprehension 
* FIXED #265: Error when using two word search string in pip GUI
* FIXED #266: Occasional incorrect line numbering
* FIXED #267: Kivy application main window didn't show in Windows
* TECHNICAL: Better diagnostic logging
 

2.1.7 (2017-05-13)
==================
* CHANGED: pip GUI now works in read-only mode unless backend is a virtual environment
* FIXED: Error when non-default backend was used without previously generated Thonny-private virtual environment

2.1.6 (2017-05-12)
==================
* FIXED #260: Strange behaviour when indenting with TAB 
* FIXED #261: Editing a triple-quoted string breaks coloring in following lines 
* FIXED: Made outdated pip detection more general 

2.1.5 (2017-05-09)
==================
* FIXED: Jedi version checking problem 

2.1.4 (2017-05-09)
==================
(This release is meant for making Thonny work better with system Python 3.4 in Debian Jessie)

* FIXED #254: "Manage plug-ins" now gives instructions for installing pip if system is missing it or it's too old 
* FIXED #255: Name highlighter and locals marker are now quietly disabled when system has too old jedi
* FIXED: Virtual env dialog now closes properly
* TECHNICAL: SubprocessDialog now has more robust returncode checking in Linux


2.1.3 (2017-05-09)
==================
* FIXED #250: Debugger focus was off by one line in function frames
* FIXED #251: Debugger timing issue (wrong command type in the backend)
* FIXED #252: Debugger timing issue (get_globals and debugger commands interfere)
* FIXED #253: Creating default virtual env does not work when using Debian python3 without ensurepip

2.1.2 (2017-05-08)
==================
* FIXED #220 and #237: Icon problems in Linux tasbar.
* FIXED #245: Tooltips not working in Mac
* FIXED #246: Current script did not get executed if cursor was not in the end of the shell 
* FIXED #249: Reset, Run and Debug caused double prompt

2.1.1 (2017-05-03)
==================
* FIXED #241: Some menu items gave errors with micro:bit backend.
* FIXED #242: Focus got stuck on first run (no entry was possible neither in shell nor editor when initialization dialog closed)

2.1.0 (2017-05-02)
==================
* TECHNICAL: Changes in diagnostic logging

2.1.0b11 (2017-04-29)
=====================
* TECHNICAL: Implemented more robust approach for installing Thonny plugins

2.1.0b10 (2017-04-29)
=====================
* CHANGED: Installed plugins now end up under ~/.thonny/plugins
* TECHNICAL: Backend preparation now occurs when main window has been opened

2.1.0b9 (2017-04-28)
====================
* FIXED: Backend related regression introduced in b8

2.1.0b8 (2017-04-27)
====================
* CHANGED: (FIXED #231) Stop/Reset button is now Interrupt/Reset button (tries to interrupt a running command instead of reseting. Resets if pressed in idle state)
* FIXED #232: Ubuntu showed pip GUI captions with too big font
* FIXED #233: Thonny now remembers which view was on top in a panel.
* FIXED #234: Multiline support problems in shell (trailing whitespace was causing trouble)
* FIXED: pip GUI shows latest version number when there is no stable version.
* FIXED: pip GUI now can handle also packages without PyPI presence
* TECHNICAL: Backends are not sent Reset command for initialization anymore.  

2.1.0b7 (2017-04-25)
==================
* FIXED: Removed some circular import to support Python 3.4
* FIXED: pip GUI now also lists installed pre-releases
* EXPERIMENTAL: GUI for installing Thonny plug-ins (Tools => Manage plug-ins...)
* TECHNICAL: Thonny+Python bundles again include pip (needed for installing plug-ins)
* TECHNICAL: Refactored creation of several widgets to support theming
* TECHNICAL: THONNY_USER_DIR environment variable can now specify where Thonny stores user data (conf files, default virtual env, ...)
 

2.1.0b6 (2017-04-19)
==================
* ENHANCEMENT: Shell now shows location of external interpreter as welcome text
* FIXED #224: Tab-indentation didn't work if tail of the text was selected and text didn't end with empty line
* FIXED: Tab with selected text occasionally invoked code-completion
* TECHNICAL: Tweaks in Windows console allocation
* TECHNICAL: Thonny+Python bundles don't include pip anymore (venv gets pip via ensurepip)

2.1.0b5 (2017-04-18)
==================
* FIXED: Typo in pipGUI (regression introduced in b4)

2.1.0b4 (2017-04-18)
====================
* CHANGED: If you want to use Thonny with external Python interpreter, then now you should select python.exe instead of pythonw.exe.
* FIXED #223: Can't interrupt subprocess when Thonny is run via thonny.exe
* FIXED: Private venv didn't find Tcl/Tk in ubuntu (commit 33eabff)
* FIXED: Right-click on editor tabs now also works on macOS.

2.1.0b3 (2017-04-17)
====================
* NEW: Dialog for managing 3rd party packages / a simple pip GUI. Check it out: "Tools => Manage packages"
* NEW: Shell now supports multiline commands
* ENHANCEMENT: Window title now shows full path and cursor location of current file. 
* ENHANCEMENT: Editor lines can be selected by clicking and/or dragging on line-number margin (thanks to Sven).
* ENHANCEMENT: Most programs can now be interrupted by Ctrl+C without restarting the process.
* ENHANCEMENT: You can start editing the code that is still running (the process gets interrupted automatically). This is handy when developing tkinter applications.
* ENHANCEMENT: Tab can be used as alternative code-completion shortcut.
* ENHANCEMENT: Recommended pip-command now appears faster in System Shell.
* ENHANCEMENT: Alternative interpreter doesn't need to have jedi installed in order to provide code-completions (see #171: Code auto-complete error)
* ENHANCEMENT: Double-click on autocomplete list inserts the completion
* EXPERIMENTAL: Ctrl-click on a name in code tries to locate its definition. NB! Not finished yet!
* CHANGED: Bundled Python version has been upgraded to 3.6.1
* CHANGED: Bundled Python in Mac and Linux now uses SSL certs from certifi project (https://pypi.python.org/pypi/certifi).
* REMOVED: Moved incomplete Exercise system to a separate plugin (https://bitbucket.org/plas/thonny-exersys). With this got rid of tkinterhtml, requests and beautifulsoup4 dependencies.
* FIXED #16: Run doesn't clear variables (again?)
* FIXED #98: Nested functions crashed the debugger.
* FIXED #114: Crash when trying to change interpreter in macOS.
* FIXED #142: "Open system shell" failed when Thonny path had spaces in it. Paths are now properly quoted.
* FIXED #154: Problems with Notebook tabs' context menus
* FIXED #159: Debugging list or set comprehension caused crash
* FIXED #166: Can't delete one of two spaces with backspace
* FIXED #180: Right-click doesn't focus editor
* FIXED #187: Main modules launched by Thonny were missing ``__spec__`` attribute.
* FIXED #195: Debugger crashes when using generators.
* FIXED #201: "Tools => Open Thonny data folder" now works also in macOS.
* FIXED #211: Linux installer was failing when using ``xdg-user-dir`` (thanks to Ryan McQuen)
* FIXED #213: In single instance mode new Window doesn't get focus
* FIXED #217: Debugger on Python 3.5 and later can't handle splat operator 
* FIXED #221: Context menus in Linux can now be closed by clicking elsewhere
* FIXED: Event logger did not save filenames (eb34c5d).
* FIXED: Problem in replayer (db78855).
* TECHNICAL: Bundled Jedi version has been upgraded to 0.10.2.
* TECHNICAL: 3rd party Thonny plugins must now be under ``thonnycontrib`` namespace package.
* TECHNICAL: Introduced the concept of "eary plugins" (plugins, which get loaded before initializing the runner).
* TECHNICAL: Refactored the interface between GUI and backend to allow different backend implementations
* TECHNICAL: Previously, with bundled Python, Thonny was using nasty tricks to force pip install packages install under ~/.thonny. Now it creates a proper virtual environment under ~/.thonny and uses this as the backend by default (instead of using interpreter running the GUI directly).
* TECHNICAL: Automatic tkinter updates on the backend are now less invasive

2.0.7 (2017-01-06)
==================
* FIXED: Making font size too small would crash Thonny.
* FIXED: Another take on configuration file corruption. 
* FIXED: Shift-Tab wasn’t working in some cases.
* FIXED #165: "Open system shell" did not add Scripts dir to PATH in Windows. 
* FIXED #183: ``from __future__ import`` crashed the debugger.

2.0.6 (2017-01-06)
==================
* FIXED: a bug in Linux installer (configuration file wasn’t created in new installations)

2.0.5 (2016-11-30)
==================
* FIXED: Corrected shift key detection (a82bd4d)

2.0.4 (2016-10-26)
==================
* FIXED: Configuration file was occasionally getting corrupted (for mysterious reasons, maybe a bug in Python’s configparser)
* FIXED #104: Negative font size crashed Thonny
* FIXED #143: Linux installer fails if desktop isn't named "Desktop". (Later turned out this wasn't fixed for all cases).
* FIXED #134: "Open system shell" doesn't work in Centos 7 KDE 

2.0.3 (2016-09-30)
==================
* FIXED: Quoting in "Open system shell" in Mac. Again. 

2.0.2 (2016-09-30)
==================
* FIXED: Quoting in "Open system shell" in Mac. 

2.0.1 (2016-09-30)
==================
* FIXED #106: Don't let user logs grow too big

2.0.0 (2016-09-29)
==================
* NEW: Added code completion (powered by Jedi: https://github.com/davidhalter/jedi)
* NEW: Added new command "Tools => Open system shell" which opens terminal where current Python is in PATH.
* CHANGED: Single instance mode is now optional (Tools => Options => General)
* FIXED: Many bugs

1.2.0b2 (2016-02-10)
====================
* NEW: Thonny now runs in single instance mode. Previously, when you opened a py file with Thonny, a new Thonny instance (window) was created even if an instance existed already. This became nuisance if you opened several files. Now Thonny works as single instance program, meaning only one instance of Thonny runs at the time. When you open another file, it is opened in existing window.
* NEW: Editor enhancements. Added option to show line numbers and right margin in the editor. In order to keep first impression cleaner, they are disabled by default. See Tools => Options => Editor. Don't forget that you don't need line numbers for locating lines mentioned in error messages -- you can click them and Thonny shows you the line.
* FIXED: Some bugs where Thonny couldn't prepare some programs for debugging.

Older versions
==============
See https://bitbucket.org/plas/thonny/issues/ and https://bitbucket.org/plas/thonny/commits/ for details 
