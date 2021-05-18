===============
Version history
===============

3.3.8 (2021-05-18)
==================
* Support installing regular pip-compatible packages to MicroPython or CircuitPython (so far only upip-compatible packages were supported), #1541
* Fix "error 403" problems when installing MicroPython packages from PyPI, #1822
* Fix error when Object inspector is open and a MicroPython object can't be found by id, #1796
* Reduce memory usage by Thonny's MicroPython helper (store last REPL value in global _ instead of storing N last values in a list), #1797, #1798
* Upgraded several dependencies in binary bundles

3.3.7 (2021-04-30)
==================
* Make confugration dialog larger to find French strings, by sourceperl, #1694
* Fix "_prepare_after_soft_reboot" error in Unix MicroPython mode, #1715
* Support interactive programs with Unix MicroPython, #1725
* Fix read-only filesystem error for CircuitPython in non-English variants of CircuitPython, #1662
* Fix error on right clicking in local file explorer with Italian translation, #1713
* Fix back-end switcher menu position and theme, #1719, #1720
* Fix "pop from empty list" error when MicroPython is having problems, #1586
* Fix MYPYPATH / MyPy not working, #1124
* Highlight unclosed strings even inside unclosed parens, #1770
* Fix problem running code via WebREPL, #1762
* Make Outline show also async, defs #1787
* Don't show full error info when ManagementError doesn't seem to be Thonny's fault, #1788
* Don't show error dialog when querying globals fails (error is shown on the variables table instead), #1789
* Recover from corrupted rpc.sock ("invalid literal for int() with base 10" error), #1745
* Add 3 translated Help files for Spanish, by José Carlos García, #1759
* Add Korean translations of Help files, by Hyungseok Choi, #1758
* Add first version of Finnish translation by Lrasinen
* Update translations for Albanian, French, Korean

3.3.6 (2021-03-03)
==================
* Fix crash in Shell when negative int-s are evaluated in MicroPython (regression introduced in 3.3.4), #1670
* Fix problems with wm_overrideredirect on macOS with Tk 8.6.11, #1659
* Fix crash in Plotter when more than 10 numbers are plotted, #1648
* Hide unsuitable PYTHONPATH environment variable in macOS, #1651

3.3.5 (2021-02-22)
==================
* Fix too short reprs at MicroPython REPL (regression introduced in 3.3.4), #1627
* Fix incorrect presentation of long output lines, #1628
* Fix error in nicer debugger when stepping in generators, #1631
* Fix infinite recursion error when evaluating `globals()` in MicroPython REPL while object inspector is open, #1641
* Update Greek translation

3.3.4 (2021-02-17)
==================
* CHANGED: MicroPython time synchronization now sets RTC to local time instead of UTC. This can be changed via a hidden configuration option (https://github.com/thonny/thonny/wiki/MicroPython#advanced-configuration), #1603
* Add time synchronization for RaspberryPi Pico, #1563, #1592
* Skip loading obsolete thonny-pico plug-in, which is now built in, #1575
* Get rid of misleading SSL warning in micropip.py and show a warning about non-MicroPython packages, #1621
* Fix WebREPL connection for MicroPython 1.14 by using regular paste mode instead of the new raw-paste mode, #1613
* Delay importing jedi and asttokens for improved performance, #1556
* Don't assume "dialout" group is required when MicroPython connection fails with permission error, #1286
* Reduce the memory usage of showing global variables by capping object representations to 50 first characters in MicroPython, #1582
* Add Hungarian translation (by Laszlo Kocsis)
* Updated translations for German, Korean, Italian, Dutch (by various authors)


3.3.3 (2021-01-21)
==================
* Add MicroPython support for Raspberry Pi Pico (https://www.raspberrypi.org/blog/raspberry-pi-silicon-pico-now-on-sale/)
* Better support for MicroPython daily builds, #1545, #1553
* Automatically prepend relevant Anaconda directories to PATH. Fixes problem with importing Anaconda's numpy, #1522
* Make custom Python chooser see more interpreters, #1522
* Fix several spelling mistakes, by freddii, #1534
* Update toolbar buttons, when another editor gets selected, fixes wrong button states, #1536
* Catch errors when opening file in system app, #1526
* Fix internal error while using Outline View, #1543
* Fix truncated System Shell environment on macOS, #1529
* Add /usr/local/bin to the PATH of the back-end process if missing, #1131
* Fix error while parsing Pygame Zero error, #1535
* Fix MicroPython completion errors with jedi 0.18, #1560
* Add incomplete Korean language by Augene J. Pak, Fabianus.c, Suk-Hyung Hwang, YEON, $1531
* Add incomplete Albanian translation by Algent Albrahimi
* [Technical] Allow older Send2Trash (Fedora doesn't have version 1.5 of this)
* [Technical] Remove erroneous executable flags from some files

3.3.2 (2021-01-06)
==================
* Fix the problem of missing docstrings, #1481
* Fix MicroPython management error after executing machine.reset(), #1492
* Add support for MicroPython raw paste mode (usable in MicroPython 1.14+), #1498
* Restore MicroPython raw mode as fallback, should fix problems with M5Stick and W600, #1516
* Add syntax highlighting for non-decimal number literals and support underscores, #1482 by Stefan Rothe
* Make sure all output from the program gets presented, #1504
* Interrupt current program when running a MicroPython script, #1512
* Add support for Jedi 0.18, #1497
* Fix arguments completions for jedi 0.16+, #1511
* Make micro:bit support a bit more robust, #1515
* Add Persian (Farsi) translation by Farshid Meidani
* Add Slovak translation by jose1711
* Add Armenian translation by Avag. sayan
* Update Italian and Chinese (TW) translations


3.3.1 (2020-12-06)
==================
* Allow installing MicroPython to micro:bit v2
* Fix problem with MicroPython programs creating lot of output very quickly, #1419
* Fix wrong message when saving to MP and device is busy, #1437
* Bump Pyserial version from 3.5b1 to 3.5, fix problem with some ESP devices, #1443
* Fix error when trying to download file from microbit, #1440
* Don't assume anything about conf files in Pi theme, #1436
* Fix error on reseting MicroPython device, #1442
* Fix unwanted output from expession statements in MicroPython, #1441
* Treat double-click in the remote file dialog differently from double-click in the Files view, #1432
* Fix error when closing MP file dialog without name, #1431
* Refactor "File => Rename" command (new label "Move / rename" and you can't "rename" a file on MP device to a file on local disc and vice versa), #1446
* Fix broken links in help pages, #1447
* Use THONNY_USER_DIR/temp for temp files. Fixes printing when default browser is Snap Chrome, #1435
* Fix error when clicking on "Attributes" tab on Object Inspector when no object is selected (MP) #1450
* Updated translations (Spanish an Brasilian Portuguese)
* Allow specifying DTR/RTS for serial connection (to avoid restarting ESP on connect), #1462
* Open log window automatically if work dialog encounters error, #1466
* Don't close work dialog automatically if log window is opened, #1465
* Fix dummy MicroPython packages giving ugly errors, #1464
* Fix crashes in Assistant view with Dracula theme, #1463
* Work around Caps lock problem when binding command shortcuts, #1347


3.3.0 (2020-11-15)
==================

New & changed
-------------
* Removed automatic tabs => spaces conversion and its confirmation dialog, #599
* Added command for replacing tabs with spaces, #1411
* Added option for highlighting tabs (Tools => Options => Editor), #1409
* Added option for indenting with tabs (Tools => Options => Editor), #599
* Add an option to use Tk file dialogs instead of Zenity in Linux, #1404
* Reduce max repr length for MicroPython (1000 instead of 5000)
* Forward https_proxy or http_proxy variable to pip, #535
* Allow specifying environment variables for the UI process, #1421
* Remove special support for Friendly-traceback, #1416
* Use exclusive access when connecting to a MP device over a serial port, #1418

Fixes
-----
* Make sure expression box for while/for test is located properly, #1134
* In MicroPython backends only warn about failed epoch dectection if sync or validation is required
* Don't show ugly traceback in debug mode
* Internal error while debugging exceptions, #1403
* Automatically create Thonny user dir in remote machine, #1365
* Fix MicroPython uploading/downloading when started from an expanded dir, #1398
* Fix unrensponsive UI when MicroPython is printing in infinite loop, #1419
* Fix ugly stacktrace, when MicroPython device is disconnected during processing a command, #1420

New and updated translations
----------------------------
* Czech by Petr. moses and Radim
* Romanian by Pop Vasile Alexandru
* Norwegian (Bokmål and Nynorsk) by Gabriel Slørdahl
* Updated Portuguese (BR) by Marcelo de Gomensoro Malheiros
* Updated French, Polish, Greek, Spanish, Italian



3.3.0b7 (2020-11-01)
====================
* Add default black fg color to tooltips, #1381, by adzierzanowski
* Use paste-mode instead of raw repl for executing code on MP devices, #1386
* Use WebREPL file protocol for uploading files, #1387
* Hide underscored names from autocomplete suggestions unless user already typed '_', #1382, by adzierzanowski
* Add command to filebrowser menu for toggling hidden files, #1292
* Fix Unconnected network drive shorcuts make Files explorer broken #1333
* Don't allow save as a file which is already opened, #1310
* Color self and cls like builtins, #1080
* Soft-reboot MicroPython before "Run current script", #1393
* Fix error in clearing squeezed boxes, #1091
* Enhance upload/download dialogs, #1395
* Make "Open System shell" open ssh with remote back-ends
* Make "Open System shell" open miniterm with MicroPython back-ends, #1287
* Better interrupt for download, #1320

3.3.0b6 (2020-10-19)
====================

* Clean up backend-switcher menu.

3.3.0b5 (2020-10-19)
====================

* Fixed a regression introduced in b4 -- Thonny crashed on launch when data directory didn't exist yet.

3.3.0b4 (2020-10-18)
====================

New
---
* Statusbar with backend switcher, #1356
* Firmware flasher for CircuitPython, #1375, #1351
* Updated firmware flasher for micro:bit, #1351

Changed
-------
* Refactor alternative interpreter configuration page, #1079

Fixed
-----
* Don't choke when MP management output is wrapped between user input, #1346
* Include ampersand in URL regex in the Shell, #1323
* Dialogs may end up behind the main window, #1158, #1133
* Augment LD_LIBRARY_PATH instead of replacing it, #1008
* Fix "Install from requirements.txt" error, #1344
* File dialog should scroll to top when new folder gets selected, #1345
* Improve MicroPython file write reliability, #1355
* Fix CircuitPython directory creation
* Allow selecting venv 'activate' instead of interpreter symlink in the interpreter configuration page, #1079

Technical
---------
Improve diagnostic logging, #569

3.3.0b3 (2020-09-07)
====================
* Stop/Restart command now soft-reboots MicroPython device after reaching the prompt
* Fixed problem with saving SSH password

3.3.0b2 (2020-09-03)
====================
* Fixed problem with circular imports affecting Python 3.7
* Restored Python 3.5 compatibility

3.3.0b1 (2020-09-03)
====================

New
---
* Back-end for remote Python over SSH (try editing and running remote and local scripts and upload/download in the file browser; package manager, system shell, and debuggers don't work yet)
* Back-end for remote Unix MicroPython over SSH
* Back-end for local Unix MicroPython
* Package manager for MicroPython (using micropip.py by Peter Hinch), #1299, see https://forum.micropython.org/viewtopic.php?f=15&t=8787&start=14
* Support Object inspector with MicroPython back-ends, #1309
* Thonny now synchronizes real-time clock of MicroPython devices on connect and before each file operation, #1004
* Allow editing any file as plain text, #1305
* File browser now allows setting default action by extension (open in system default app or in Thonny's editor), #1305
* ESP flash dialog now allows selecting flash mode, #1056 by Rune Langøy
* "Save all" command, #1053 by Syed Nasim
* Clicking on a value in the Shell selects it and opens in the Object inspector. 
* By default, after evaluating an expression in the Shell the value will be automatically shown in the Object inspector (if open). See Options => Shell to turn it off.
* Object inspector now display more information about numbers (try 1024 or 0.1), #1230
* Support evaluating several expressions at once in the Shell (just like official Python REPL), #795
* Include esptool in binary bundles

Changed
-------
* Package manager now searches PyPI instead of requiring exact package name, #1300
* File browser now shows remote files below local files. This way local pane won't jump around when switching between local and remote back-ends.
* TECHNICAL: Versions of serveral dependencies were updated

Fixed
-----
* Several intermittent bugs related to fragility of the communication with MicroPython REPL, #1103, #1147
* #1138: Allow semicolon in Shell input with Python 3.8
* #1129: Support terminator as system shell
* #772: Allow invoking interrupt command from the menu when the editor has text selected (Ctrl+C would copy then)
* #1146, #1159: "No module named pwd" error
* #1283: Disable save button after save
* Make Replayer work with timestamps without fractional part, #1116
* Don't raise exception when hitting end of undo/redo stack, #1211 by Andrew Scheller
* Fix a typo in the code to display dialog. (#1260 by Ankith)

Enhanced
--------
* Convert keypad movement events to equivalent non-keypad ones, #1107 by Eliot Blennerhassett
* Start file-open-dialog in same dir as current file, #1209 by Andrew Scheller
* Bash install - do everything inside a new directory (#1203 by Andrew Scheller)
* #1145: Provide understandable error message, when Linux installer downloader is run on a non-supported platform (by Andrew Scheller)



3.2.7 (2020-01-22)
==================
* TECHNICAL: Skip name hilighter tests for recent Jedi versions

3.2.6 (2020-01-01)
==================
* FIXED #1035: Make highlight names work with recent Jedi versions 
* FIXED #1043: Can't load files from MicroPython device (regression introduced in 3.2.5)
* FIXED: Missing "Local files" label on save target selection dialog

3.2.5 (2019-12-25)
==================
* CHANGED: Python version in binary bundles upgraded from 3.7.5 to 3.7.6
* CHANGED: MyPy checks are now enabled by default (Tools => Options => Assistant)
* CHANGED: New Pylint checks are enabled
* UPDATED #32: Thonny can now display/copy/paste Unicode emojis with Python 3.7.6+ / 3.8.1+ in Windows and Linux. Selection can be still wonky, though and emojis can freeze Thonny on macOS. Fixed by https://github.com/python/cpython/pull/16545
* FIXED #815: "Open System Shell" fails when no script is open
* FIXED #973: Scrollbar in Help and Assistant acts funny
* FIXED #1019: Crash on startup when Shell gets text inserted too soon
* FIXED #1023: Accept code completions without parent and full_name 
* FIXED #1025: Extra imports by Thonny's back-end make stdlib name shadowing more troublesome
* FIXED #1026: Allow '+' in image data URI chars in Shell
* FIXED #1028: Thonny now has preliminary support for `Friendly Traceback <https://github.com/aroberge/friendly-traceback>`_. 
* FIXED: Allow larger images in shell (don't squeeze image URI-s), #401
* FIXED: Fallback to English, when configured language can't be loaded
* FIXED: Problem using esptool on PATH


3.2.4 (2019-12-07)
==================
* NEW: Turkish translation by M. Burak Kalkan
* NEW: Polish translation by Jarek Miszczak
* NEW: Partial Italian translation by sailslack
* UPDATED: Greek and Spanish translations
* CHANGED: XXL bundle now includes also pandas
* CHANGED: Make faster tracer show exceptions only with step_over and step_into
* CHANGE #1018: Use traditional stack view by default in Simple mode
* ENHANCEMENT: Improved performance for Faster debugger (proposed and supported by Raspberry Pi)
* FIXED #975: Fix stepping through lambdas with faster debugger
* FIXED #977: Don't report certain exceptions in faster debugger
* FIXED #983: Propose replacing tabs with spaces only in the editor (not in debugger frames)
* FIXED #986: Nicer debugger fails when run with breakpoints only in secondary files
* FIXED #987: MicroPython autocomplete problems by adzierzanowski
* FIXED #1003: Wrong interpretation of MicroPython file timestamps
* FIXED #1005: Avoid testing included MicroPython stubs
* FIXED #1015: Indicate disabled toolbar buttons on macOS


3.2.3 (2019-11-03)
==================
* NEW: Greek translation by Nikos
* UPDATE: Updated several translations (by Vytenis, rnLIKEm, Dleta, Alex ANDRÉ, NathanBnm, LionelVaux, Paul, Eric W, Frank Stengel,  ...)
* UPDATE: Propose opening files via dialog in case of macOS Catalina permission error (#813).

3.2.2 (2019-11-01)
==================
* NEW: ESP plug-in has been merged into main Thonny package
* FIXED #219: Implement sending EOF / restart for CPython
* FIXED #873: More robust color preference loading in Pi theme
* FIXED #876: Don't step into comprehension calls
* FIXED #897: Redo shortcut not working in Linux and Mac
* FIXED #899: Can't set THONNY_USER_DIR in customize.py
* FIXED #904: Don't show remote MicroPython dialogs when device is busy
* FIXED #905: Problems with Thonny menu on Mac after closing a dialog
* FIXED #911: Allow restoring default scaling factor
* FIXED #921: Make MicroPython backend play nicer with device resets
* FIXED #923: CircuitPython on Trinket m0 gives small int overflow when listing files
* FIXED #925: Save or open problem with network paths
* FIXED #927: Visual glitch / ghosting in Expression Box in macOS
* FIXED #928: Tooltips stay on top in macOS
* FIXED #929: Indicate dirty state in macOS close button
* FIXED #933: Scaling doesn't work right for Treeviews (Files, Variables)
* FIXED #934: Pad button captions for certain languages
* FIXED #936: Problem uploading files to some STM boards
* FIXED #939: More robust handling of different line endings
* FIXED #943: Wrong syntax highlighting with triple quoted string
* FIXED #946: Handle broken UTF-8 codepoints in MicroPython output
* FIXED #951: Use standard tabstops for program output
* FIXED #953: Allow running system commands with MP back-end
* FIXED #957: Wrong encoding in multiprocessing output
* FIXED #960: File browser is not working in replayer
* FIXED #966: Thonny encounters "internal error" in programs calling exit()
* FIXED #969: Provide nicer message, when MicroPython backend can't get to the REPL
* FIXED: Don't apply theming to menu in macOS (menu items were dull with dark themes)


3.2.1 (2019-09-06)
==================
* NEW: Add European Portuguese translation (by Emanuel Angelo)
* NEW: Add Lithuanian translation (by Vytenis)
* NEW: Add Ukrainian translation (by borpol)
* FIXED #802: Avoid scary traceback on MicroPython disconnect
* FIXED #840: Problems with file dialogs in macOS 10.15
* FIXED #843: Make right-click select items in Files view in macOS
* FIXED #845: Crash with older ESP plug-in
* FIXED #851: Ignore warnings when exporting variables
* FIXED #854: Make single instance mode work in multi-user systems
* FIXED #855: Wrong coloring with paren matching
* FIXED #859: Support relative paths when opening files with Thonny from command line
* FIXED #874: Multiline strings break stepping focus background
* FIXED: Dutch translation was inproperly set up
* FIXED: Internal error in Object Inspector (by Emanuel Angelo)
* FIXED: Problem with compacting user event logs
* TECHNICAL: Make tests run with Python 3.8

3.2.0 (2019-08-12)
==================
* FIXED #849: Uploading single file to MicroPython doesn't work
* UPDATE: Updated translations

3.2.0rc1 (2019-08-09)
=====================
* NEW: Several new commands for Files view (New directory, Move to Trash, Delete, Upload (to MicroPython device), Download (from MicroPython device), ...)
* CHANGED: MicroPython files are now displayed in the upper pane of Files view
* CHANGED: Saving or loading editor content to/from MicroPython device displays progress bar
* TECHNICAL: New dependency: Send2Trash

3.2.0b7 (2019-07-19)
====================
* FIXED: Problem with translation markers disturbing import

3.2.0b6 (2019-07-19)
====================
* NEW: BBC micro:bit plug-in has been merged into main Thonny package
* CHANGED: micro:bit flasher now downloads latest MicroPython from GitHub
* FIXED: Problems with micro:bit file browser 
* FIXED #808: multiprocessing doesn't work in Windows
* FIXED #814: Ctrl+V inserts text twice in Windows (regression introduced in previous betas)

3.2.0b5 (2019-07-16)
====================
* FIXED #810: Use regular spacing in simple mode toolbar 

3.2.0b4 (2019-07-14)
====================
* FIXED #809: Advertise indent/dedent in Edit menu
* FIXED: Marked more terms for translation
* FIXED: Updated Estonian translation

3.2.0b3 (2019-07-13)
====================
* FIXED #803: %cd gives error on MP/CP backend
* FIXED #804: Changing directories does not show in FilesView for MP/CP
* FIXED #805: Thonny user dir was not created at startup

3.2.0b2 (2019-07-13)
====================
* NEW: Former thonny-pi plug-in (containing Raspberry Pi theme) is now part of main Thonny package
* NEW: Former thonny-circuitpython plug-in (containing CircuitPython back-end) is now part of main Thonny package
* NEW: pip GUI now allows installing from requirements.txt file
* NEW: Portable/thumbdrive bundles for Windows, macOS and Linux (https://github.com/thonny/thonny/wiki/DeploymentOptions#portable-version)
* FIXED #188: Tkinter windows won't close on macOS
* FIXED #361: Include Python development files in binary bundles
* FIXED #488: Modal dialogs may get stuck
* FIXED #639: Unset misleading environment variables in Windows launcher
* FIXED #676: Can't close matplotlib window when MacOSX backend is used
* FIXED #706: In Linux Thonny hangs on close sometimes 
* FIXED #800: Can't load large files
* FIXED: Plotter now listens for theme changes (ie. changes background without restart)
* CHANGED: Welcome dialog is not show on Raspberry Pi
* CHANGED: Usage event logging is now disabled by default and can be enabled in Tools => Options => General
* CHANGED: MicroPython back-ends don't interrupt running process on connecting
* TECHNICAL: MicroPython back-end got a big refactoring

3.2.0b1 (2019-06-17)
====================
* NEW: [Work in progress] UI and help content can be translated to other languages (big thanks to cspaier, Georges Khaznadar and translators). See docs/translate.md for contrubution instructions.
* NEW: Shell supports ANSI color codes and line overwriting with ``\b`` and ``\r``. See "Help => Shell" for more info.
* NEW: Shell now has extension called "Plotter", which visualizes series of numbers printed to the standard output. See "Help => Plotter" for more info.
* NEW: Shell presents PNG data URL-s printed to stdout as images. Try print("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
* NEW: Automatic change of working directory is now optional (Tools => Options => Run & Debug)
* NEW: Files view now allows setting working directory (double-click on folder name)
* NEW: Files view allows browsing device's filesystem with MicroPython back-ends 
* NEW: Files from MicroPython devices can be opened in the editor and edited directly 
* NEW: You can now choose which debugger is invoked when clicking on the "Debug" toolbar button (Tools => Options => Run & Debug)
* NEW: On first run Thonny presents a dialog for selecting UI language and initial settings ("standard" or "Raspberry Pi"). With Raspberry Pi settings Thonny will start in simple mode, preferred debugger set to "faster" and UI theme set to "Raspberry Pi".
* NEW: Shell IO font can be configured (Tools => Options => Fonts & Themes). By André Roberge 
* NEW: Support for running Flask programs with F5. Also fixed several issues which prevented running and debugging Flask programs. See "Help => Web development with Flask" for more info.
* NEW: "File => Save copy" allows saving current editor content to a different location without changing editor file name.
* FIXED #630: Pressing up then down in shell doesn't leave shell in previous state. Fixed by Chad Purdy    
* FIXED #691: No Show shell on run with no input() prompt. Fixed by Chad Purdy
* FIXED #692: Cancelling Save As dialog causes error. Fixed by Chad Purdy
* FIXED #700: Allow viewing all files in file dialogs in Linux
* FIXED #703: Exception view was not legible with dark theme
* FIXED #704: Suggest current filename with Save As. Fixed by Илья Кругликов
* FIXED #708: Error when stacktrace includes Cython frames.
* FIXED #711: Thonny can now handle UNC paths
* FIXED #719: Buttons are too narrow in Search/Replace dialog
* FIXED #725: When saving a file, respect the original fileformat. By badukaire 
* FIXED #727: Respect fileformat for unix files too. By badukaire 
* FIXED #731: Right click menu disappears immediately and executes unwanted Undo action
* FIXED #738: Window appears lower on each start
* FIXED #749: "Focus shell" should bring you to a new prompt. By Ivoz 
* CHANGED: In order to work around ``tkinter.Text`` performance problems, Shell squeezes very long lines into a button. The button opens a dialog for expanding, viewing or copying those lines. Shell also deletes old output to remain responsive.
* CHANGED: Various changes in simple mode (Zoom and Quit buttons, merging Run and Resume buttons, automatic display of Variables view).
* CHANGED: Disabled Tk clipboard management workaround in Linux (occasionally caused UI freezes). This means clipboard becomes emptied after closing Thonny.
* CHANGED: MicroPython commands from "Device" menu have been redesigned (use Files view instead) or moved to other menus (Run and Tools). The goal is to get rid of Device menu and keep only magic commands which make sense from the back-end perspective. 


Several of these features were proposed and supported by Raspberry Pi Foundation.

3.1.2 (2019-02-13)
==================
* FIXED: Make Terminal features work in Windows again
* FIXED #685: Print cuts lines
* FIXED #686: Stepping over user modules can be too slow
* ENHANCEMENT: Include pip in binary bundles

3.1.1 (2019-02-09)
==================
* FIXED #674: Print doesn't work on Mac
* FIXED #675: Make focus editor / shell shortcuts usable on Mac
* FIXED #677: Debugging fails with extended slice syntax

3.1.0 (2019-01-28)
==================
* NEW: "Run => Pygame Zero mode" allows running Pygame Zero programs with F5 
* NEW: Support for Birdseye debugger (Run => Debug current script (Birdseye)) by Alex Hall
* NEW: Notes view for writing down code snippets, task descriptions, etc.
* NEW: Allow running current script in system terminal
* NEW: "File => Print..." allows printing current script (via default web browser)
* NEW: Shell's context menu now has editing commands
* ENHANCEMENT: Open the Shell window on Run if it is not open
* ENHANCEMENT: More robust support for running system commands in Thonny Shell (with ! prefix)
* ENHANCEMENT: Allow switching off Pylint and/or MyPy checks
* ENHANCEMENT: Make it clear how to exit Heap mode (with notification box in the upper-right corner of the main window)
* FIXED #621: Holding Enter in the Shell causes a crash
* FIXED #623: Parameters code completion error
* FIXED #627: Debugging stops after raise statement
* FIXED #628: Wrong line highlighted when stepping in for-loop
* FIXED #629: Interrupting system command (!) shows ugly traceback
* FIXED #633: pasting can't affect read-only text anymore
* FIXED #641: Better font scaling in Linux (see Tools => Options => General for more control)
* FIXED #646: Simple open file to edit from command line failing
* FIXED #655: Invalid f-string crashes Assistant
* FIXED #666: Make stdin iterable
* FIXED: Solved several problems related to stepping through raising an exception
* FIXED: Issues with automatic indentation (Thanks to Alex Hall!)
* CHANGED: Use Konsole as terminal in KDE
* CHANGED: "Tools => Open system shell" now shows relevant commands differently 
* CHANGED: Make Assistant's MyPy checks disabled by default
* CHANGED: Source code now lives at GitHub (https://github.com/thonny/thonny)


3.0.8 (2018-11-15)
==================
* FIXED #424: Font scaling problems in Linux
* FIXED #584: Guard against bad repr calls
* TECHNICAL: Reduced required pyserial version (Fedora only has 3.1) 

3.0.8 (2018-11-15)
==================
* FIXED #597: The directory with Python scripts may not be in path for executing system commands from shell
* FIXED: Make executing shell commands compatible with Python 3.5
* FIXED: Make MyPy support compatible with older MyPy versions
* FIXED: Make turtle.pyi compatible with Python 3.5 and remove Windows linebreaks
* FIXED: MyPy error col offset

3.0.7 (2018-11-14)
==================
* FIXED #592: MyPy doesn't work when cwd == sys.prefix
* FIXED #593: No-message exceptions crash the Assistant
* FIXED #595: Running system commands causes an error
* FIXED #596: Arguments are ignored when running system commands from shell in Posix

3.0.6 (2018-11-13)
==================
* FIXED #538: Turtle programs may give false warnings (Typeshed stubs were not packaged)
* FIXED #586: Import interception mechanism fails for some modules
* FIXED #591: Assistant fails when filename is missing from error info

3.0.5 (2018-10-26)
==================
* FIXED #573: "Highlight matching names" and "Highlight local variables" makes editor very slow
* FIXED #574: Error in outline
* FIXED #578: resizing local variable pane in debugger causes error

3.0.4 (2018-10-22)
==================
* FIXED #564: In Windows "Highlight local variables" and "Higlight matching names" cause Thonny to load Jedi files

3.0.3 (2018-10-21)
==================
* FIXED: Regression from 3.0.2 (incomplete code refactoring)

3.0.2 (2018-10-21)
==================
* FIXED #563: Problems with HeapView and EventsView
* FIXED #565: Don't replace tabs in shell

3.0.1 (2018-10-17)
==================
* FIXED: Problems with executing "Run" and "Debug" commands together with "cd" command
* FIXED: Editor file name issues
* FIXED: MicroPython %cat command failed over serial 

3.0.0 (2018-10-16)
==================
* CHANGED: Line numbers are now visible by default
* CHANGED: Stack and Assistant views are now in the bottom-right corner
* CHANGED: Shell doesn't show full path of bundled interpreters anymore
* ENHANCEMENT #555: Internal errors are now shown with more suitable dialog
* FIXED #170: Command+k for clearing shell in Mac
* FIXED #547: Recommend "..." button when plug-ins latest stable isn't suitable for this Thonny version
* FIXED #548: Prevent inconsistent use of tabs and spaces error (when pasting or opening text containing tabs, Thonny proposes to replace them with spaces)
* FIXED #557: Default window size too small for simple mode
* FIXED #559: Make text copied to clipboard available even after closing Thonny
* FIXED: Implemented workaround for https://bugs.python.org/issue34927
* TECHNICAL: MicroPython backend now shows the source of failing internal commands 

3.0.0rc1 (2018-10-08)
=====================
* ENHANCEMENT: Documented several features (see Help => Help contents)
* FIXED #523: Open system shell doesn't work with pip 10
* FIXED #534: Add shortcut for step-back
* FIXED #538: Turtle programs give false warnings

3.0.0b6 (2018-09-30)
====================
* CHANGED: In order to avoid pollution of user home directory, the configuration file and logs are now stored in directories recommended by platform style guides (%APPDATA%/Thonny on Windows, ~/Library/Thonny on Mac and ~/.config/Thonny on Linux). Old configuration and user logs will be imported on first run. 
* CHANGED: "Back end" configuration page was renamed to "Interpreter" (as it was in Thonny 2.1)
* CHANGED: Python version in Thonny+Python bundles upgraded to 3.7.1rc1
* NEW: File menu received a submenu for easy opening of recent files. 
* ENHANCEMENT: Add shortcut for clearing shell (Ctrl+L)
* ENHANCEMENT: Warn when script is saved with a common library module name (eg. turtle.py)
* ENHANCEMENT: Allow switching between regular and simple mode (Tools => Options => General)
* FIXED #72: "View => Full screen" (in Expert mode) is now also available on Mac
* FIXED #262: Add ability to select an autocomplete suggestion with TAB
* FIXED #316: Nice debugger doesn't handle named arguments properly
* FIXED #339: Allow disabling sound Tools => Options => General
* FIXED #389: AST marker fails with dict merge
* FIXED #478: Add option to reopen all files on start-up
* FIXED #479: Make Thonny save configuration when "Quit"-ed on Mac
* FIXED #480: Thonny now properly remembers opened files
* FIXED #498: Open System Shell doesn't work on Raspberry
* FIXED #501: Assistant feedback preview link doesn't work on mac
* FIXED #510: Error when listing available interpreters in config page
* FIXED #518: add menu item: "device" / "Upload current script" for MicroPython (by Jens Diemer) 
* FIXED: Object inspector can show images (again)
* FIXED: Pylint and MyPy processes don't hang anymore with large output. 

3.0.0b5 (2018-09-01)
====================
* FIXED: requirements.txt was missing mypy 

3.0.0b4 (2018-08-31)
====================
* NEW: When program has syntax error or crashes with an exception, Assistant pane opens and tries to help diagnose the problem. Uses Pylint, MyPy and custom dynamic analysis under the hood. (Big "Thank you!" to Raspberry Pi Foundation for the support!) 

* ENHANCEMENT: Resizing the main window doesn't mess up views' layout anymore.
* ENHANCEMENT: Better support for debugging f-strings.
* ENHANCEMENT: Nice debugger now recovers better when it is not able to understand a program.
* FIXED #496: Regression which caused Variables view to skip variables updates during "nicer debugging".
* FIXED #440: Copy&paste over a selection will now delete the text selection first (was problem for some Linuxes)
* FIXED: Removed a nasty debugging statement left into b3, which may cause a crash in the end of debugging.

3.0.0b3 (2018-08-11)
====================
* FIXED: Various problems with pip GUI
* FIXED: Variables view misses events 
* FIXED: Error when last back-end was not available anymore
* TECHNICAL: Implemented ChoiceDialog 

3.0.0b2 (2018-08-11)
====================
* FIXED: problems with pip GUI in virtualenv

3.0.0b1 (2018-08-11)
====================

Note: This version is successor of 2.2.0b4 and 2.1.21. Stable release of 2.2.0 was skipped. 
(Incrementing the major version felt more appropriate considering the amount of new and changed features.)

* NEW: Thonny now has two debug modes: beside original AST based debug mode (the "nicer" one, Ctrl+F5) there is now also line-based mode (the "faster" one, Shift+F5), which is not so intuitive but much more efficient. 
* NEW: Both debug modes now support breakpoints (switch on line numbers and double-click on the margin). Big thanks to Raspberry Pi Foundation for the support! 
* NEW: Alternative presentation for call stack (in single window, just like in most debuggers; see Tools => Options => Debugger) 
* NEW: Clicking on the links in stacktrace now shows the variables of those frames.
* NEW: You can re-run your changed program without closing it first (relevant for graphical programs).   
* NEW: Checking "Run => Dock user windows" makes your Tkinter windows stay on top and appear always on the same location. This allows tweaking your turtle programs while looking at current output.
* NEW: "View => Program arguments" opens a box where you can write the argument string for your program   
* NEW: "Tools => Options => Backend => Custom Python interpreter" now allows creating virtual environments   
* NEW: "Tools => Manage packages" now allows installing new packages with all CPython backends, not only virtual environments. If the backend is not a virtual environment it installs to user site packages (with `pip install --user`)
* NEW: Thonny now includes basic support for MicroPython (former `thonny_microbit` plug-in). See https://bitbucket.org/plas/thonny/wiki/MicroPython for more info.
* CHANGED: Upgraded Python to version 3.7.0 in Thonny+Python bundles 
* CHANGED: Dropped support for Python 3.4 (both for front-end and back-end)
* CHANGED: Dropped support for Tk 8.5. All bundles (including Mac's) now come with Tk 8.6.8
* CHANGED: Default back-end is now "Same as front-end" (was "A special virtual environment"). This makes deployment easier in classroom setting and it is simpler scheme in general. "Special virtual environment" backend may be removed in future versions.
* CHANGED: Plug-ins will be now installed to regular user site packages directory (was ~/.thonny/plugins)
* CHANGED: If Thonny (front-end) is run from a virtual environment, user directory (with configuration.ini and logs) will be .thonny under virtual environment's root directory (instead of usual ~/.thonny).  
* ENHANCEMENT: Better Windows installer (run as administrator for all-users install)
* ENHANCEMENT: thonny.exe is now digitally signed
* ENHANCEMENT: On Linux Thonny now uses native file dialogs (via zenity)   
* ENHANCEMENT: Nicer debugger can now step into your functions defined in other modules   
* ENHANCEMENT: Nicer debugger can now stop before the assignement of loop variable in for-loops   
* ENHANCEMENT: "Run to cursor" can be called by right-clicking desired line in the editor and selecting the command from context menu   
* ENHANCEMENT: Great time and memory optimizations in nicer debug mode. The ability to step back in time is not so expensive anymore.  
* ENHANCEMENT: Thonny now detects external file modifications and proposes to reload 
* ENHANCEMENT: New Windows installer (run as administrator for all-users install)
* FIXED #163: Uninstaller now correctly removes "Open with Thonny" context menu entry
* FIXED #340: Validate geometry before loading
* FIXED #358: sys.exit() in user programs doesn't show stacktrace anymore
* FIXED #363: subprocess.run causes Thonny backend to hang
* FIXED #375: Files are now saved with linebreaks suitable for current platform
* FIXED #419: logging doesn't work in user programs
* FIXED #422: Make Ctrl+C, Ctrl+V etc. work on Greek keyboard
* FIXED #440: In Linux paste over selection doesn't remove the selection
* FIXED #450: Locals marker doesn't work with jedi 0.12
* FIXED #468: Problem with changing backend interpreter
* FIXED #471: Problem when Thonny uses jedi 0.11 or newer
* FIXED #475: Heap view misbehaving on startup
* FIXED: "Run => Run to cursor" works again 
* FIXED: Thonny now honors PEP 263 style encoding markers when saving files. (UTF-8 is still the default) 
* FIXED: Problem when jedi 0.10 and parso are both installed
* TECHNICAL: Plug-in writers can now control each import in user programs (thonny.backend.VM.add_import_handler)
* TECHNICAL: Communication messages between back-end and front-end were changed
* TECHNICAL: Thonny doesn't tweak PYTHONUSERBASE anymore to put plugins under ~/.thonny. Regular user site packages is used instead 
* TECHNICAL: Dependency to "packaging" introduced in 2.2 betas is now replaced with "setuptools" 

2.2.0b4 (2018-06-05)
====================
* FIXED: Couldn't open menus with None backend

2.2.0b3 (2018-06-05)
====================
* FIXED #425: Too big automatic scaling
* FIXED #427: Can't run files with spaces in filename
* FIXED: Fixed a bug when debugging and encountering an exception (by Alar Leemet)
* ENHANCEMENT: Show indicator about stepping in the past in the text of editor tabs
* ENHANCEMENT: Added Thonny version guards for installing plug-ins
* EXPERIMENTAL: Preliminary support for running system commands in Thonny shell (eg. `!ls` or `!dir`)
* TECHNICAL: thonny.exe in Windows bundle is now signed
* TECHNICAL: Delay starting of Runner until UI is shown
* TECHNICAL: Various enhancements to support MicroPython plug-ins 


2.2.0b2 (2018-05-04)
====================
* FIXED: Options dialog crashes when Variables view hasn't been created yet

2.2.0b1 (2018-05-04)
====================
* NEW: Added support for stepping back in time during debugging (Run => Step back) by Alar Leemet. If you accidentally stepped over an interesting part of code, then now you can step back and step into.
* NEW: Added support for UI and syntax theming (https://bitbucket.org/plas/thonny/wiki/Theming)
* NEW: Added several built-in dark themes
* NEW: Added support for display scaling / high-DPI screens (Tools => Options => General)
* NEW: Added closing buttons to the tabs of all views 
* NEW: Added support for (CPython) back-end plug-ins (https://bitbucket.org/plas/thonny/wiki/Plugins)
* NEW: Current editor line can be highlighted (Tools => Options => Editor)
* NEW: Thonny can be started in simple mode (https://bitbucket.org/plas/thonny/wiki/Modes) 
* NEW: Variables view now allows viewing variables from other modules beside __main__  (Tools => Options => General)
* CHANGED: Dropped support for Python 3.4 (both for front-end and back-end)
* CHANGED: Reorganized back-end configuration ("Tools => Options => Back-end" instead of "Tools => Options => Interpreter")
* CHANGED: The roles of Interrupt and Stop commands are now more clear: Stop always restarts the backend and Interrupt only tries to interrupt 
* CHANGED: Editing the running program doesn't interrupt it anymore.  
* CHANGED: Object inspector now shows attributes and object overview on different tabs
* CHANGED: Can't set thonny.THONNY_USER_DIR directly in customize.py anymore (https://bitbucket.org/plas/thonny/wiki/DeploymentOptions)
* CHANGED: For plug-in writers: Unified early and late plug-ins (load_early_plugin should be renamed to load_plugin)
* CHANGED: For plug-in writers: get_workbench and get_runner moved from thonny.globals to thonny
* FIXED #358: Hide the stacktrace of SystemExit
* FIXED #368: "Open system shell" doesn't work in Xfce (fix by Miro Hrončok) 
* FIXED #370: Made zooming with Ctrl++ / Ctrl+- work on the numpad on Linux
* FIXED #372: Now it's possible to specify a link as backend interpreter (fix by Miro Hrončok)
* FIXED #396: exec causes range marker to crash
* FIXED #403: Window width may become negative
* TECHNICAL: Changed the location and sharing of backend.py, common.py, ast_utils.py
* TECHNICAL: Cleaner approach for sharing jedi with the back-end
* TECHNICAL: Package manager now uses pypi.org instead of pypi.python.org
* TECHNICAL: Several changes in Runner and BackendProxy interface
* TECHNICAL: Saving an editor now forces writing to disk (see https://learn.adafruit.com/adafruit-circuit-playground-express/creating-and-editing-code#1-use-an-editor-that-writes-out-the-file-completely-when-you-save-it)

2.1.22 (2018-08-20)
===================
Happy re-independence day to Estonia!

* ENHANCEMENT: Less intrusive logging for AST marking problems
* FIXED #340: Validate geometry before loading
* FIXED #363: subprocess.run causes Thonny backend to hang
* FIXED #419: logging doesn't work in user programs
* FIXED #440: In Linux paste over selection doesn't remove the selection
* FIXED #487: Use PyPI.org and turn off pip warnings in package manager
* FIXED #490: Debugger gets confused with f-strings
* FIXED: In case of back-end problems, kill backend instead of resetting
* FIXED: Colorize f-string prefixes

2.1.21 (2018-07-17)
===================
* FIXED #471: Another problem when Thonny uses jedi 0.11 or newer

2.1.20 (2018-07-16)
===================
* FIXED: Problem when jedi 0.10 and parso are both installed

2.1.19 (2018-07-16)
===================
Updates in this version are relevant only on Windows

* FIXED #467: Error when running Thonny with pythonw on Windows (regression from 2.1.18)
* ENHANCEMENT: New Windows installer (run as administrator for all-users install)
* ENHANCEMENT: Upgraded Python to version 3.6.6 in Thonny+Python bundles 

2.1.18 (2018-06-22)
===================
* FIXED #450: Locals marker doesn't work with jedi 0.12

2.1.17 (2018-03-21)
===================
* FIXED #409: Package manager crashed after release of pip 9.0.2

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
See https://github.com/thonny/thonny/issues and https://github.com/thonny/thonny/commits  
