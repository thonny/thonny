#! /usr/bin/python3
# -*- coding: utf-8 -*-

"""
Thonny, Python IDE for beginners Copyright (C) 2014 Aivar Annamaa

This program is free software: you can redistribute it and/or modify it under the 
terms of the GNU General Public License as published by the Free Software Foundation, 
either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. 
If not, see <http://www.gnu.org/licenses/>.
"""

import sys
import traceback
import os.path
from distutils.version import StrictVersion
from logging import info, debug
import time
import gettext
import re
import tkinter as tk
from tkinter import ttk
import tkinter.font as tk_font
import importlib
import tkinter.messagebox as tkMessageBox

from thonny import ui_utils
from thonny import stack
from thonny import vm_proxy
from thonny.config import ConfigurationManager
from thonny.about import AboutDialog
from thonny.code import EditorNotebook, Editor
from thonny.shell import ShellFrame
from thonny.memory import GlobalsFrame, HeapFrame, ObjectInspector
from thonny.common import DebuggerCommand, ToplevelCommand, DebuggerResponse,\
    InlineCommand, quote_path_for_shell
from thonny.ui_utils import Command, CLAM_BACKGROUND, SASHTHICKNESS,\
    insert_to_notebook
from thonny import user_logging
from thonny import misc_utils
import thonny.refactor
import subprocess
import thonny.outline
from thonny.misc_utils import running_on_mac_os, running_on_linux,\
    running_on_windows


class Workbench(tk.Tk):
    def __init__(self, main_dir):
        
        self._main_dir = main_dir # the directory containing eg. "thonny" package
        
        self._init_configuration()
        self._init_translation()
        self._init_user_logging()
        self._init_backend()
        
        tk.Tk.__init__(self)
        tk.Tk.report_callback_exception = self._on_tk_exception
        self._init_window()
        self._init_style()
        
        self._views = {}
        self._init_widgets()
        self._init_commands()
        self._load_plugins()
        
        # There are 3 kinds of events:
        #    - commands from user (menu and toolbar events are bound in respective methods)
        #    - notifications about asynchronous debugger responses 
        #    - notifications about new output from the running program
        
        self.last_manual_debugger_command_sent = None # TODO: hack
        self.step_over = False
        
        self.editor_book.load_startup_files()
        self.editor_book.focus_current_editor()
    
    def _init_window(self):
        self._update_title()
        self.geometry("{0}x{1}+{2}+{3}".format(self.get_option("layout.width"),
                                            self.get_option("layout.height"),
                                            self.get_option("layout.left"),
                                            self.get_option("layout.top")))
        
        if self.get_option("layout.zoomed"):
            ui_utils.set_zoomed(self, True)
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Try set icon
        try:
            self.iconbitmap(default=os.path.join(self._main_dir, "res", "thonny.ico"))
        except:
            pass
        
        
        self.bind("<FocusIn>", self._on_get_focus, "+")
        self.bind("<FocusOut>", self._on_lose_focus, "+")
        
        if ui_utils.running_on_mac_os:
            self._set_up_mac_specific_stuff()
    
    def _init_menu(self):
        self._menubar = tk.Menu(self)
        self["menu"] = self._menubar
        self._menus = {}
        
        # create standard menus in correct order
        self._get_menu("File")
        self._get_menu("Edit")
        self._get_menu("View")
        self._get_menu("Run")
        self._get_menu("Help")
        
        
    def _init_style(self):
        style = ttk.Style()
    
        if 'xpnative' in style.theme_names():
            # gives better scrollbars in empty editors
            theme = 'xpnative'
        elif 'aqua' in style.theme_names():
            theme = 'clam'
        elif 'clam' in style.theme_names():
            theme = 'clam'
        else:
            theme = style.theme_use()
            
        style.theme_use(theme)
        
        style.configure("Sash", sashthickness=SASHTHICKNESS)
        
        # get rid of Treeview borders
        style.layout("Treeview", [
            ('Treeview.treearea', {'sticky': 'nswe'})
        ])
        
        # necessary for Python 2.7 TODO: doesn't help for aqua
        style.configure("Treeview", background="white")
        
        
        """
        _images[1] = tk.PhotoImage("img_close",
            file=os.path.join(imgdir, '1x1_white.gif'))
        _images[2] = tk.PhotoImage("img_closeactive",
            file=os.path.join(imgdir, 'close_active.gif'))
        _images[3] = tk.PhotoImage("img_closepressed",
            file=os.path.join(imgdir, 'close_pressed.gif'))
            
        style.element_create("close", "image", "img_close",
            ("active", "pressed", "!disabled", "img_closepressed"),
            ("active", "!disabled", "img_closeactive"), border=8, sticky='')
        """
        
        global _IMG_GRAY_LINE # Saving the reference, otherwise Tk will garbage collect the images 
        _IMG_GRAY_LINE = tk.PhotoImage("gray_line", file=os.path.join(self._get_image_dir(), 'gray_line.gif'))
        style.element_create("gray_line", "image", "gray_line",
                                   ("!selected", "gray_line"), 
                                   height=1, width=10, border=1)
        
        
        if theme == "xpnative":
            # add a line below active tab to separate it from content
            style.layout("Tab", [
                ('Notebook.tab', {'sticky': 'nswe', 'children': [
                    ('Notebook.padding', {'sticky': 'nswe', 'children': [
                        ('Notebook.focus', {'sticky': 'nswe', 'children': [
                            ('Notebook.label', {'sticky': '', 'side': 'left'}),
                            #("close", {"side": "left", "sticky": ''})
                        ], 'side': 'top'})
                    ], 'side': 'top'}),
                    ('gray_line', {'sticky': 'we', 'side': 'bottom'}),
                ]}),
            ])
            
            style.configure("Tab", padding=(4,1,0,0))
            
        elif theme == "aqua":
            style.map("TNotebook.Tab", foreground=[('selected', 'white'), ('!selected', 'black')])
            
            
            
        
        """
        ################
        #print(style.layout("TMenubutton"))
        style.layout("TMenubutton", [
            ('Menubutton.dropdown', {'side': 'right', 'sticky': 'ns'}),
            ('Menubutton.button', {'children': [
                #('Menubutton.padding', {'children': [
                    ('Menubutton.label', {'sticky': ''})
                #], 'expand': '1', 'sticky': 'we'})
            ], 'expand': '1', 'sticky': 'nswe'})
        ])
        
        style.configure("TMenubutton", padding=14)
        """
        
        
        #print(style.map("Treeview"))
        #print(style.layout("Treeview"))
        #style.configure("Treeview.treearea", font=TREE_FONT)
        # NB! Some Python or Tk versions (Eg. Py 3.2.3 + Tk 8.5.11 on Raspbian)
        # can't handle multi word color names in style.map  
        light_blue = "#ADD8E6" 
        light_grey = "#D3D3D3"
        if running_on_linux():
            style.map("Treeview",
                  background=[('selected', 'focus', light_blue),
                              ('selected', '!focus', light_grey),
                              ],
                  foreground=[('selected', 'black'),
                              ],
                  )
        else:
            style.map("Treeview",
                  background=[('selected', 'focus', 'SystemHighlight'),
                              ('selected', '!focus', light_grey),
                              ],
                  foreground=[('selected', 'SystemHighlightText')],
                  )
        
    def _init_user_logging(self):
        # generate log filename
        folder = os.path.expanduser(os.path.join("~", ".thonny", "user_logs"))
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        i = 0
        while True: 
            filename = os.path.join(folder, time.strftime("%Y-%m-%d_%H-%M-%S_{}.txt".format(i)));
            if os.path.exists(filename):
                i += 1;  
            else:
                return filename
        
        # create logger
        self._user_logger = user_logging.UserEventLogger(filename)
        
    def _load_plugins(self):
        plugin_names = self._find_plugins(
                            os.path.join(self._main_dir, "thonny", "plugins"),
                            "thonny.plugins.")
        
        for plugin_name in sorted(plugin_names):
            m = importlib.import_module(plugin_name)
            m.load_plugin(self)
    
    def _find_plugins(self, extension_dir, module_name_prefix):
        result = set()
        
        for item in os.listdir(extension_dir):
            item_path = os.path.join(extension_dir, item)
            # TODO: support zipped packages
            if (os.path.isfile(item_path)
                    and item.endswith(".py")
                    and not item.endswith("__.py")
                or os.path.isdir(item_path)
                    and os.path.isfile(os.path.join(item, "__init__.py"))):
                    result.add(module_name_prefix 
                               + os.path.splitext(item)[0])
        
        return result
                                
    def _init_fonts(self):
        if self.get_option("view.editor_font_family"):
            editor_font = tk_font.Font(family=self.get_option("view.editor_font_family"))
        else:
            editor_font = tk_font.nametofont("TkFixedFont")
            
        if self.get_option("view.editor_font_size"):
            editor_font.configure(size=self.get_option("view.editor_font_size"))
        
        self._fonts = {
            'EditorFont' : editor_font,
            'BoldEditorFont' : tk_font.Font(family=editor_font.actual()["family"],
                                    size=editor_font.actual()["size"],
                                    weight="bold"),
            'IOFont' : tk_font.Font(family=editor_font.actual()["family"],
                                    size=editor_font.actual()["size"]-2)
        }

    def _init_translation(self):
        gettext.translation('thonny',
                    os.path.join(self._main_dir, "thonny", "locale"), 
                    languages=[self.get_option("general.language"), "en"]).install()
                                
    
    def _init_configuration(self):
        self._configuration = ConfigurationManager(os.path.expanduser(os.path.join("~", ".thonny", "preferences.ini")))
        self._configuration.set_defaults({
            "general.language" : "en",
            "layout.zoomed" : False,
            "layout.top" : 15,
            "layout.left" : 150,
            "layout.width" : 700,
            "layout.height" : 650,
            "layout.w_width" : 200,
            "layout.e_width" : 200,
            "layout.s_height" : 200,
            
            "file.recent_files" : [],
            "file.last_browser_folder" : None,
            
            "run.working_directory" : os.path.expanduser("~"),
            "run.auto_cd" : True, 
            
            "edit.enable_autocomplete" : True,
            
            "view.editor_font_family" : None,
            "view.editor_font_size" : None, # 15 if running_on_mac_os() else 10,

            # TODO: view defaults should appear automatically
            "view.filebrowser" : False,
            "view.variables" : False,
            "view.heap" : False,
        })
         
    def _init_commands(self):
        
        # TODO: see idlelib.macosxSupports
        self.createcommand("tkAboutDialog", self.cmd_about)
        # https://www.tcl.tk/man/tcl8.6/TkCmd/tk_mac.htm
        self.createcommand("::tk::mac::ShowPreferences", lambda: print("Prefs"))

        
        # declare menu structure
        self._menus = [
            ('file', 'File', [
                Command('new_file',     _('New'),         'Ctrl+N',       self.editor_book),
                Command('open_file',    _('Open...'),     'Ctrl+O',       self.editor_book),
                Command('close_file',   _('Close'),       'Ctrl+W',       self.editor_book),
                "---",
                Command('save_file',    'Save',        'Ctrl+S',       self.editor_book.get_current_editor),
                Command('save_file_as', 'Save as...',  'Shift+Ctrl+S', self.editor_book.get_current_editor),
#                 "---",
#                 Command('print',    'Print (via browser)',        'Ctrl+P',       self.editor_book.get_current_editor),
#                 "---",
#                 Command('TODO:', '1 prax11/kollane.py', None, None),
#                 Command('TODO:', '2 kodutööd/vol1_algne.py', None, None),
#                 Command('TODO:', '3 stat.py', None, None),
#                 Command('TODO:', '4 praxss11/kollane.py', None, None),
#                 Command('TODO:', '5 koduqwertööd/vol1_algne.py', None, None),
#                 Command('TODO:', '6 stasst.py', None, None),
#                 "---",
                Command('exit', 'Exit', None, self),
            ]),
            ('edit', 'Edit', [
                Command('undo',         'Undo',         'Ctrl+Z', self._find_current_edit_widget, system_bound=True), 
                Command('redo',         'Redo',         'Ctrl+Y', self._find_current_edit_widget, system_bound=True),
                "---", 
                Command('cut',          'Cut',          'Ctrl+X', self._find_current_edit_widget, system_bound=True), 
                Command('copy',         'Copy',         'Ctrl+C', self._find_current_edit_widget, system_bound=True), 
                Command('paste',        'Paste',        'Ctrl+V', self._find_current_edit_widget, system_bound=True),
                "---", 
                Command('select_all',   'Select all',   'Ctrl+A', self._find_current_edit_widget),
#                 "---",        
#                 Command('find_next',    'Find next',    'F3',     self._find_current_edit_widget),
                 
            ]),
            ('view', 'View', [
                Command('update_browser_visibility', 'Show browser',  None, self,
                        kind="checkbutton", variable_name="layout.browser_visible"),
                Command('update_memory_visibility', 'Show variables',  None, self,
                        kind="checkbutton", variable_name="layout.memory_visible"),
                Command('update_inspector_visibility', 'Show object inspector',  None, self,
                        kind="checkbutton", variable_name="layout.inspector_visible"),
                "---",
                Command('increase_font_size', 'Increase font size', 'Ctrl++', self),
                Command('decrease_font_size', 'Decrease font size', 'Ctrl+-', self),
                "---",
                Command('update_memory_model', 'Show values in heap',  None, self,
                        kind="checkbutton", variable_name="view.values_in_heap"),
                "---",
                Command('focus_editor', "Focus editor", "F11", self),
                Command('focus_shell', "Focus shell", "F12", self),
                Command('show_replayer', "Show Replayer", None, self),
                Command('preferences', 'Preferences', None, self) 
            ]),
#             ('code', 'Code', [
#                 Command('TODO:', 'Indent selection',         "Tab", self.editor_book.get_current_editor), 
#                 Command('TODO:', 'Dedent selection',         "Shift+Tab", self.editor_book.get_current_editor),
#                 "---", 
#                 Command('TODO:', 'Comment out selection',    "Ctrl+3", self.editor_book.get_current_editor), 
#                 Command('TODO:', 'Uncomment selection',      "Shift+Ctrl+3", self.editor_book.get_current_editor), 
#             ]),
            ('run', 'Run', [
                Command('run_current_script',       'Run current script',        'F5',  self), 
                Command('debug_current_script',     'Debug current script',  'Ctrl+F5', self),
#                 Command('run_current_file',         'Run current file',        None,  self), 
#                 Command('debug_current_file',       'Debug current file',  None, self), 
#                 "---", 
#                 Command('run_current_cell',         'Run current cell',        None,  self), 
#                 Command('debug_current_cell',       'Debug current cell',  None, self), 
#                 "---", 
#                 Command('run_current_selection',    'Run current selection',        None,  self), 
#                 Command('debug_current_selection',  'Debug current selection',  None, self), 
#                 "---", 
#                 Command('run_main_script',          'Run main script',        'Shift+F5',  self), 
#                 Command('debug_main_script',        'Debug main script',  'Ctrl+Shift+F5', self), 
#                 Command('run_main_file',            'Run main file',        None,  self), 
#                 Command('debug_main_file',          'Debug main file',  None, self), 
#                 "---", 
                Command('reset',                 'Stop/Reset',       None, self),
                "---", 
                Command('exec',                 'Step over', "F7", self),
#                Command('zoom',                 'Zoom in',               "F8", self),
                Command('step',                 'Step',                  "F9", self),
                "---", 
                Command('set_auto_cd', 'Auto-cd to script dir',  None, self,
                        kind="checkbutton", variable_name="run.auto_cd"),
            ]),
            ('misc', 'Misc', [
                Command('open_user_dir',   'Open Thonny user folder',        None, self), 
            ]),
            ('help', 'Help', [
                Command('help',             'Thonny help',        None, self), 
            ]),
        ]

        self._menus[1][2].append("---");
        self._menus[1][2].append(Command('find',         'Find & Replace',         'Ctrl+F', self._find_current_edit_widget));

        self._menus[1][2].append("---");
        self._menus[1][2].append(Command('autocomplete',         'Autocomplete',         'Ctrl+space', self._find_current_edit_widget));            

        self._menus[2][2].append("---");
        self._menus[2][2].append(Command('update_outline_visibility',         'Show outline',         None, self,  kind="checkbutton", variable_name="layout.outline_visible"));

        self._menus[1][2].append("---");
        self._menus[1][2].append(Command('refactor_rename',         'Rename identifier',         None, self)); 

        self._menus[1][2].append("---");
        self._menus[1][2].append(Command('comment_in',         'Comment in',         'Ctrl+Key-3', self._find_current_edit_widget)); 
        self._menus[1][2].append(Command('comment_out',         'Comment out',         'Ctrl+Key-4', self._find_current_edit_widget));
                
        # TODO:
        """
        if misc_utils.running_on_mac_os():
            self.menus[-2][2].append (
                Command('mac_add_download_assessment',   'Allow opening py files from browser ...',        None, self)
            )
        """
        
        
        ## make plaftform specific tweaks
        if misc_utils.running_on_mac_os():
            # insert app menu with "about" and "preferences"
            self._menus.insert(0, ('apple', 'Thonny', [
                Command('about', 'About Thonny', None, self),
                # TODO: tkdocs says preferences are added automatically.
                # How can I connect with it?
            ]))
            
            # use Command instead of Ctrl in accelerators
            for __, __, items in self._menus:
                for item in items:
                    if isinstance(item, Command) and isinstance(item.accelerator, str):
                        item.accelerator = item.accelerator.replace("Ctrl", "Command") 
        else:
            # insert "about" to Help (last) menu ...
            self._menus[-1][2].append(Command('about', 'About Thonny', None, self))
            

        # create actual widgets and bind the shortcuts
        self.option_add('*tearOff', tk.FALSE)
        menubar = tk.Menu(self)
        self['menu'] = menubar
        
        for name, label, items in self._menus:
            menu = tk.Menu(menubar, name=name)
            menubar.add_cascade(menu=menu, label=label)
            menu["postcommand"] = lambda name=name, menu=menu: self._update_menu(name, menu)
            
            for item in items:
                if item == "---":
                    menu.add_separator()
                elif isinstance(item, Command):
                    accelerator_name = item.accelerator
                    if accelerator_name is not None: 
                        accelerator_name = accelerator_name.replace("Key-", "")
                    menu.add(item.kind,
                        label=item.label,
                        accelerator=accelerator_name,
                        value=item.value,
                        variable=item.variable,
                        command=lambda cmd=item: cmd.execute())
                    
                    if (item.accelerator is not None and not item.system_bound):
                        # create event sequence out of accelerator 
                        # tk wants Control, not Ctrl
                        sequence = item.accelerator.replace("Ctrl", "Control")
                        
                        sequence = sequence.replace("+-", "+minus")
                        sequence = sequence.replace("++", "+plus")
                        
                        # it's customary to show keys with capital letters
                        # but tk would treat this as pressing with shift
                        parts = sequence.split("+")
                        if len(parts[-1]) == 1:
                            parts[-1] = parts[-1].lower()
                        
                        # tk wants "-" between the parts 
                        sequence = "-".join(parts)
                        
                        # bind the event
                        try:
                            self.bind_all("<"+sequence+">", lambda e, cmd=item: cmd.execute(e), "+")
                        except:
                            # TODO: Command+C for Mac
                            # TODO: refactor
                            tk.messagebox.showerror("Internal error. Use Ctrl+C to copy",
                                traceback.format_exc())
                            
                        
                        # TODO: temporary extra key for step
                        if item.cmd_id == "step":
                            self.bind_all("<Control-t>", lambda e, cmd=item: cmd.execute(e), "+")


        
        
        
        #variables_var = tk.BooleanVar()
        #variables_var.set(True)
        #var_menu = view_menu.add_checkbutton(label="Variables", value=1, variable=variables_var, command=showViews)
        #def showViews():
        #    if variables_var.get():
        #        memory_pw.remove(globals_frame)
        #    else:
        #        memory_pw.pane

    
    def _init_widgets(self):
        
        main_frame= ttk.Frame(self) # just a backgroud behind padding of main_pw, without this OS X leaves white border 
        main_frame.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.toolbar = ttk.Frame(main_frame, padding=0) # TODO: height=30 ?
        self.toolbar.grid(column=0, row=0, sticky=tk.NSEW, padx=10)
        self._init_populate_toolbar()
        
        main_pw   = ui_utils.OrderedPanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_pw.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        west_pw   = ui_utils.OrderedPanedWindow(main_pw, orient=tk.VERTICAL)
        center_pw = ui_utils.OrderedPanedWindow(main_pw, orient=tk.VERTICAL)
        east_pw   = ui_utils.OrderedPanedWindow(main_pw, orient=tk.VERTICAL)
        
        self.view_notebooks = {
            'nw' : ui_utils.OrderedNotebook(west_pw),
            'w'  : ui_utils.OrderedNotebook(west_pw),
            'sw' : ui_utils.OrderedNotebook(west_pw),
            
            's'  : ui_utils.OrderedNotebook(center_pw),
            
            'ne' : ui_utils.OrderedNotebook(east_pw),
            'e'  : ui_utils.OrderedNotebook(east_pw),
            'se' : ui_utils.OrderedNotebook(east_pw),
        }

        self.editor_book = EditorNotebook(self.center_pw)
        center_pw.add(self.editor_book, position_key=1)
        


    def _init_backend(self):
        self._vm = vm_proxy.VMProxy(self.get_option("run.working_directory"), self._main_dir)
        self._poll_vm_messages()
        self._advance_background_tk_mainloop()


    def _init_populate_toolbar(self): 
        def on_kala_button():
            self.editor_book.demo_editor.set_read_only(not self.editor_book.demo_editor.read_only)
        
        top_spacer = ttk.Frame(self.toolbar, height=5)
        top_spacer.grid(row=0, column=0, columnspan=100)
        
        self.images = {}
        self.toolbar_buttons = {}
        col = 1
        
        for name in ('file.new_file', 'file.open_file', 'file.save_file', 
                     '-', 'run.run_current_script',
                          'run.debug_current_script',
                          'run.step',
                          'run.reset'):
            
            if name == '-':
                hor_spacer = ttk.Frame(self.toolbar, width=15)
                hor_spacer.grid(row=0, column=col)
            else:
                img = tk.PhotoImage(file=misc_utils.get_res_path(name + ".gif"))
            
                btn = ttk.Button(self.toolbar, 
                                 #command=on_kala_button, 
                                 image=img, 
                                 text="?",
                                 style="Toolbutton",
                                 state=tk.NORMAL)
                btn.grid(row=1, column=col, padx=0, pady=0)
            
                self.images[name] = img
                self.toolbar_buttons[name] = btn
                
            col += 1 
        
    def _set_up_mac_specific_stuff(self):
        def mac_open_document(self, *args):
            # TODO:
            #showinfo("open doc", str(args))
            pass
        
        def mac_open_application(self, *args):
            #showinfo("open app", str(args))
            pass
        
        def mac_reopen_application(self, *args):
            #showinfo("reopen app", str(args))
            pass
        
        self.createcommand("::tk::mac::OpenDocument", mac_open_document)
        self.createcommand("::tk::mac::OpenApplication", mac_open_application)
        self.createcommand("::tk::mac::ReopenApplication", mac_reopen_application)
        
    def _get_image_dir(self):
        return os.path.join(self._main_dir, "thonny", "res")
    
    def _get_menu(self, label):
        if label not in self._menus:
            self._menus[label] = tk.Menu(self._menubar)
            self._menubar.add_cascade(label=label, menu=self._menus[label])
            
        return self._menus[label]
                      
    def get_option(self, name):
        return self._configuration.get_option(name)
    
    def set_option(self, name, value, save_now=True):
        self._configuration.set_option(name, value, save_now)
        
    def add_defaults(self, defaults):
        self._configuration.set_defaults(defaults)
    
    def get_variable(self, name):
        return self._configuration.get_variable(name)
    
    def get_font(self, name):
        """
        Supported names are EditorFont and BoldEditorFont
        """
        return self._fonts[name]
    
    def _get_view(self, view_id):
        if "instance" not in self._views[view_id]:
            # create the view
            class_ = self._view_records[view_id]["class"]
            location = self._view_records[view_id]["location"]
            master = self._view_notebooks[location]
            view = class_(master)
            self._views[view_id]["instance"] = view
            
        return self._views[view_id]["instance"]
    
    
    def _show_view(self, view_id, set_focus):
        # get or create
        view = self._get_view(view_id)
        notebook = view.master
        
        if not view.winfo_ismapped():
            # insert to correct position
            position_key = self._views[view_id]["position_key"] 
            for sibling in map(notebook.nametowidget, notebook.tabs()):
                sibling_id = sibling.__class__.__name__
                sibling_position_key = self._views[sibling_id]["position_key"]
                if sibling_position_key > position_key:
                    where = sibling
                    break
            else:
                where = "end"
            
            notebook.insert(where, view, text=self._views[view_id]["label"])
        
        # switch to the tab
        notebook.select(view)
        
        # add focus
        if set_focus:
            view.focus_set()
    
    def _hide_view(self, view_id):
        if "instance" in self._views[view_id]:
            view = self._views[view_id]["instance"]
            view.master.remove(view)
        
        # TODO: update master visibility
        
    
    def register_view(self, class_, label, default_location):
        """Adds item to "View" menu for showing/hiding given view. 
        
        Args:
            view_class: Class or constructor for view. Should be callable with single
                argument (the master of the view)
            label: Label of the view tab
            location: Location descriptor. Can be "nw", "sw", "s", "se", "ne"
        
        Returns: None        
        """
        view_id = class_.__name__
        
        self.add_defaults({
            "view." + view_id + ".visible"  : False,
            "view." + view_id + ".location" : default_location,
            "view." + view_id + ".position_key" : label
        })
        
        self._view_records[view_id] = {
            "class" : class_,
            "label" : label,
            "location" : self.get_option("view." + view_id + ".location"),
            "position_key" : self.get_option("view." + view_id + ".position_key")
        }
            
        def toggle_view():
            # find or create view
            master = self._view_notebooks[self.get_option("view." + view_id + ".location")] 
            for child in master.winfo_children():
                if isinstance(child, view_class):
                    view = child
                    break
            else:
                view = view_class(master)
                view.position_key = self.get_option("view." + view_id + ".position_key")
            
            # show or hide
            visibility_flag = self.get_variable("view." + view_id + ".visible") 
            if visibility_flag.get():
                master.remove(view)
                if len(master.panes()) == 0:
                    
            else:
                # find correct position
                for name in master.tabs():
                    where = master.nametowidget(name)
                    if where.position_key > view.position_key:
                        break
                else:
                    where = "end"
                
                # insert
                master.insert(where, view, text=label)
            
            # toggle the flag
            visibility_flag.set(not visibility_flag.get())
        
        
        # Menu items are positioned alphabetically 
        # in first section (ie. before first separator) of View menu.
        # Find correct position for this label
        view_menu = self._get_menu("View")
        for i in range(0, view_menu.index("end")+1):
            if ("label" not in view_menu.entryconfigure(i) # separator
                or view_menu.entrycget(i, "label") > label):
                index = i
                break
        else:
            index = None
            
            
        self.add_command(
            menu_label="View",
            command_label=label,
            handler=toggle_view,
            flag_name="view." + view_id + ".visible",
            index=index)
        
        
    def add_command(self, menu_label, command_label, handler,
                    tester=None,
                    default_accelerator=None,
                    flag_name=None,
                    _index="end"):
        """Adds an item to specified menu.
        
        Args:
            menu_label: Label of the menu the command should appear in.
            command_label: Label for this command
            handler: Function to be called when the command is invoked. 
                Should be callable with one argument (the event or None).
            tester: Function to be called for determining if command is available or not.
                Should be callable with one argument (the event or None).
                Should return True or False.
                If None then command is assumed to be always available.
            default_accelerator: Windows style keyboard shortcut string. 
                Will be translated on Mac
            flag_name: Used for toggle commands. Indicates the name of the boolean option.
        
        Returns:
            None
        """     
        
        def dispatch(event=None):
            if tester and tester(event):
                # TODO: what about executing via shortcut and option variable?
                handler(event)
            else:
                self.bell()
                
        # select actual accelerator according to user settings
        """TODO:
        accelerator = ...
        
        if accelerator:
            # Tweak the appearance of the accelerator
            accelerator = accelerator.replace("Key-", "")
            if misc_utils.running_on_mac_os():
                accelerator = accelerator.replace("Ctrl", "Command")
            
            # Convert visible accelerator string to Tk-s sequence 
            sequence = accelerator.replace("Ctrl", "Control")
            sequence = sequence.replace("+-", "+minus")
            sequence = sequence.replace("++", "+plus")
            
            # it's customary to show keys with capital letters
            # but tk would treat this as pressing with shift
            parts = sequence.split("+")
            if len(parts[-1]) == 1:
                parts[-1] = parts[-1].lower()
            
            # tk wants "-" between the parts 
            sequence = "-".join(parts)
    
            self.bind_all('<' + sequence + '>', dispatch, True)
        """
        
        self._get_menu(menu_label).insert(
            _index,
            "checkbutton" if flag_name else "command",
            label=command_label,
            #accelerator=accelerator,
            variable=self.get_variable(flag_name),
            command=dispatch)
    
    def log_user_event(self, event):
        self._user_logger.log_micro_event(event)

    
    def _update_toolbar(self):
        "TODO:"
    
    
    def _advance_background_tk_mainloop(self):
        if self._vm.get_state() == "toplevel":
            self._vm.send_command(InlineCommand(command="tkupdate"))
        self.after(50, self._advance_background_tk_mainloop)
        
    def _poll_vm_messages(self):
        # I chose polling instead of event_generate
        # because event_generate across threads is not reliable
        while True:
            msg = self._vm.fetch_next_message()
            if not msg:
                break
            
            # skip some events
            if (isinstance(msg, DebuggerResponse) 
                and hasattr(msg, "tags") 
                and "call_function" in msg.tags
                and not self.get_option("debugging.expand_call_functions")):
                
                self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
                continue
                
            if hasattr(msg, "success") and not msg.success:
                print("_poll_vm_messages, not success")
                self.bell()
            
            self.shell.handle_vm_message(msg)
            self.stack.handle_vm_message(msg)
            self.editor_book.handle_vm_message(msg)
            self.globals_frame.handle_vm_message(msg)
            self.heap_frame.handle_vm_message(msg)
            self.inspector_frame.handle_vm_message(msg)
            
            self.set_option("run.working_directory", self._vm.cwd)
            self._update_title()
            
            # automatically advance from some events
            if (isinstance(msg, DebuggerResponse) 
                and msg.state in ("after_statement", "after_suite", "before_suite")
                and not self.get_option("debugging.detailed_steps")
                or self.continue_with_step_over(self.last_manual_debugger_command_sent, msg)):
                
                self._check_issue_debugger_command(DebuggerCommand(command="step"), automatic=True)
            
            self.update_idletasks()
            
        self.after(50, self._poll_vm_messages)
    
    def continue_with_step_over(self, cmd, msg):
        if not self.step_over:
            print("Not step_over")
            return False
        
        if not isinstance(msg, DebuggerResponse):
            return False
        
        if cmd is None:
            return False
        
        if msg.state not in ("before_statement", "before_expression", "after_expression"):
            # TODO: hack, may want after_statement
            return True
        
        if msg.frame_id != cmd.frame_id:
            return True
        
        if msg.focus.is_smaller_in(cmd.focus):
            print("smaller")
            return True
        else:
            print("outside")
            return False
        
    
    def cmd_about(self):
        AboutDialog(self, self._get_version())
    
    def cmd_run_current_script_enabled(self):
        return (self._vm.get_state() == "toplevel"
                and self.editor_book.get_current_editor() is not None)
    
    def cmd_run_current_script(self):
        self._execute_current("Run")
    
    def cmd_debug_current_script_enabled(self):
        return self.cmd_run_current_script_enabled()
    
    def cmd_debug_current_script(self):
        self._execute_current("Debug")
        
    def cmd_run_current_file_enabled(self):
        return self.cmd_run_current_script_enabled()
    
    def cmd_run_current_file(self):
        self._execute_current("run")
    
    def cmd_debug_current_file_enabled(self):
        return self.cmd_run_current_script_enabled()
    
    def cmd_debug_current_file(self):
        self._execute_current("debug")
    
    def cmd_increase_font_size(self):
        self._change_font_size(1)
    
    def cmd_decrease_font_size(self):
        self._change_font_size(-1)
    
    def _change_font_size(self, delta):
        self.shell.change_font_size(delta)
        self.editor_book.change_font_size(delta)
        self.globals_frame.change_font_size(delta)
        # TODO:
        #self.builtins_frame.change_font_size(delta)
        self.heap_frame.change_font_size(delta)
    
    def _execute_current(self, cmd_name, text_range=None):
        """
        This method's job is to create a command for running/debugging
        current file/script and submit it to shell
        """
        
        editor = self.editor_book.get_current_editor()
        if not editor:
            return

        filename = editor.get_filename(True)
        if not filename:
            return
        
        # changing dir may be required
        script_dir = os.path.dirname(filename)
        
        if (self.get_option("run.auto_cd") and cmd_name[0].isupper()
            and self._vm.cwd != script_dir):
            # create compound command
            # start with %cd
            cmd_line = "%cd " + quote_path_for_shell(script_dir) + "\n"
            next_cwd = script_dir
        else:
            # create simple command
            cmd_line = ""
            next_cwd = self._vm.cwd
        
        # append main command (Run, run, Debug or debug)
        rel_filename = os.path.relpath(filename, next_cwd)
        cmd_line += "%" + cmd_name + " " + quote_path_for_shell(rel_filename) + "\n"
        if text_range is not None:
            "TODO: append range indicators" 
        
        # submit to shell (shell will execute it)
        self.shell.submit_magic_command(cmd_line)
        self.step_over = False
    
    
    def cmd_reset(self):
        self._vm.send_command(ToplevelCommand(command="Reset", globals_required="__main__"))
    
    def cmd_update_browser_visibility(self, adjust_window_width=True):
        if self.get_option("layout.browser_visible") and not self.w_book.winfo_ismapped():
            if adjust_window_width:
                self._check_update_window_width(+self.get_option("layout.w_width")+SASHTHICKNESS)
            self.main_pw.add(self.w_book, minsize=150, 
                             width=self.get_option("layout.w_width"),
                             before=self.center_pw)
        elif not self.get_option("layout.browser_visible") and self.w_book.winfo_ismapped():
            if adjust_window_width:
                self._check_update_window_width(-self.get_option("layout.w_width")-SASHTHICKNESS)
            self.main_pw.remove(self.w_book)

            self.step_over = False

    def cmd_update_memory_visibility(self, adjust_window_width=True):
        # TODO: treat variables frame and memory pane differently

        if self.get_option("layout.memory_visible"):
            self.right_pw.add(self.globals_book, minsize=50)
        else:
            self.right_pw.remove(self.globals_book)

    def cmd_update_inspector_visibility(self):
        if self.get_option("layout.inspector_visible"):
            self.right_pw.add(self.info_book, minsize=50)
        else:
            self.right_pw.remove(self.info_book)

    def cmd_update_outline_visibility_enabled(self):
        return self.editor_book.get_current_editor() is not None

    def cmd_update_outline_visibility(self): 
        if not self.get_option("layout.outline_visible"): 
            self.outline_frame.prepare_for_removal()
            self.right_pw.remove(self.outline_book)
        else:
            self.outline_frame.register_notebook_listener()
            if self.editor_book.get_current_editor() != None:
                self.outline_frame.parse_and_display_module(self.editor_book.get_current_editor()._code_view)
            self.right_pw.add(self.outline_book, minsize=50)
            self.log_user_event(thonny.outline.OutlineOpenEvent(self.editor_book.get_current_editor()))

    def cmd_refactor_rename_enabled(self):
        return self.editor_book.get_current_editor() is not None

    def cmd_refactor_rename(self):
        self.log_user_event(thonny.refactor.RefactorRenameStartEvent(self.editor_book.get_current_editor()))
        if not self.editor_book.get_current_editor():
            self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
            errorMessage = tkMessageBox.showerror(
                           title="Rename failed",
                           message="Rename operation failed (no active editor tabs?).", #TODO - more informative text needed
                           master=self)
            return

        #create a list of active but unsaved/modified editors)
        unsaved_editors = [x for x in self.editor_book.winfo_children() if type(x) == Editor and x.cmd_save_file_enabled()]

        if len(unsaved_editors) != 0:
            #confirm with the user that all open editors need to be saved first
            confirm = tkMessageBox.askyesno(
                      title="Save Files Before Rename",
                      message="All modified files need to be saved before refactoring. Do you want to continue?",
                      default=tkMessageBox.YES,
                      master=self)

            if not confirm:
                self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_book.get_current_editor()))
                return #if user doesn't want it, return

            for editor in unsaved_editors:                     
                if not editor.get_filename():
                    self.editor_book.select(editor) #in the case of editors with no filename, show it, so user knows which one they're saving
                editor.cmd_save_file()
                if editor.cmd_save_file_enabled(): #just a sanity check - if after saving a file still needs saving, something is wrong
                    self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
                    errorMessage = tkMessageBox.showerror(
                                   title="Rename failed",
                                   message="Rename operation failed (saving file failed).", #TODO - more informative text needed
                                   master=self)
                    return

        filename = self.editor_book.get_current_editor().get_filename()

        if filename == None: #another sanity check - the current editor should have an associated filename by this point 
            self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
            errorMessage = tkMessageBox.showerror(
                           title="Rename failed",
                           message="Rename operation failed (no filename associated with current module).", #TODO - more informative text needed
                           master=self)
            return

        identifier = re.compile(r"^[^\d\W]\w*\Z", re.UNICODE) #regex to compare valid python identifiers against

        while True: #ask for new variable name until a valid one is entered
            renameWindow = thonny.refactor.RenameWindow(self)
            newname = renameWindow.refactor_new_variable_name
            if newname == None:
                self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_book.get_current_editor()))
                return #user canceled, return

            if re.match(identifier, newname):
                break #valid identifier entered, continue

            errorMessage = tkMessageBox.showerror(
                           title="Incorrect identifier",
                           message="Incorrect Python identifier, please re-enter.",
                           master=self)

        try: 
            #calculate the offset for rope
            offset = thonny.refactor.calculate_offset(self.editor_book.get_current_editor()._code_view.text)
            #get the project handle and list of changes
            project, changes = thonny.refactor.get_list_of_rename_changes(filename, newname, offset)
            #if len(changes.changes == 0): raise Exception

        except Exception:
            try: #rope needs the cursor to be AFTER the first character of the variable being refactored
                 #so the reason for failure might be that the user had the cursor before the variable name
                offset = offset + 1
                project, changes = thonny.refactor.get_list_of_rename_changes(filename, newname, offset)
                #if len(changes.changes == 0): raise Exception

            except Exception: #couple of different reasons why this could happen, let's list them all in the error message
                self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
                message = 'Rename operation failed. A few possible reasons: \n'
                message += '1) Not a valid Python identifier selected \n'
                message += '2) The current file or any other files in the same directory or in any of its subdirectores contain incorrect syntax. Make sure the current project is in its own separate folder.'
                errorMessage = tkMessageBox.showerror(
                               title="Rename failed",
                               message=message, #TODO - maybe also print stack trace for more info?
                               master=self)               
                return

        description = changes.description #needed for logging

        #sanity check
        if len(changes.changes) == 0:
            self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
            errorMessage = tkMessageBox.showerror(
                               title="Rename failed",
                               message="Rename operation failed - no identifiers affected by change.", #TODO - more informative text needed
                               master=self)               
            return

        affected_files = [] #needed for logging
        #show the preview window to user
        messageText = 'Confirm the changes. The following files will be modified:\n'
        for change in changes.changes:
            affected_files.append(change.resource._path)
            messageText += '\n ' + change.resource._path

        messageText += '\n\n NB! This action cannot be undone.'

        confirm = tkMessageBox.askyesno(
                  title="Confirm changes",
                  message=messageText,
                  default=tkMessageBox.YES,
                  master=self)
        
        #confirm with user to finalize the changes
        if not confirm:
            self.log_user_event(thonny.refactor.RefactorRenameCancelEvent(self.editor_book.get_current_editor()))
            thonny.refactor.cancel_changes(project)
            return

        try:
            thonny.refactor.perform_changes(project, changes)
        except Exception:
                self.log_user_event(thonny.refactor.RefactorRenameFailedEvent(self.editor_book.get_current_editor()))
                errorMessage = tkMessageBox.showerror(
                               title="Rename failed",
                               message="Rename operation failed (Rope error).", #TODO - more informative text needed
                               master=self)     
                thonny.refactor.cancel_changes(project)
                return            
  
        #everything went fine, let's load all the active tabs again and set their content
        for editor in self.editor_book.winfo_children():
            try: 
                filename = editor.get_filename()
                source, self.file_encoding = misc_utils.read_python_file(filename)
                editor._code_view.set_content(source)
                editor._code_view.modified_since_last_save = False
                self.editor_book.tab(editor, text=self.editor_book._generate_editor_title(filename))
            except Exception:
                try: #it is possible that a file (module) itself was renamed - Rope allows it. so let's see if a file exists with the new name. 
                    filename = filename.replace(os.path.split(filename)[1], newname + '.py')
                    source, self.file_encoding = misc_utils.read_python_file(filename)
                    editor._code_view.set_content(source)
                    editor._code_view.modified_since_last_save = False
                    self.editor_book.tab(editor, text=self.editor_book._generate_editor_title(filename))
                except Exception: #something went wrong with reloading the file, let's close this tab to avoid consistency problems
                    self.editor_book.forget(editor)
                    editor.destroy()

        self.log_user_event(thonny.refactor.RefactorRenameCompleteEvent(description, offset, affected_files))
        current_browser_node_path = self.file_browser.get_selected_path()
        self.file_browser.refresh_tree()
        if current_browser_node_path != None:
            self.file_browser.open_path_in_browser(current_browser_node_path)

    def _check_update_window_width(self, delta):
        if not ui_utils.get_zoomed(self):
            self.update_idletasks()
            # TODO: shift to left if right edge goes away from screen
            # TODO: check with screen width
            new_geometry = "{0}x{1}+{2}+{3}".format(self.winfo_width() + delta,
                                                   self.winfo_height(),
                                                   self.winfo_x(), self.winfo_y())
            
            self.geometry(new_geometry)
            
    
    def cmd_update_memory_model_enabled(self):
        return self._vm.get_state() == "toplevel"
    
    def cmd_update_memory_model(self):
        if self.get_option("view.heap") and not self.heap_book.winfo_ismapped():
            # TODO: put it before object info block
            self.right_pw.add(self.heap_book, after=self.globals_book, minsize=50)
        elif not self.get_option("view.heap") and self.heap_book.winfo_ismapped():
            self.right_pw.remove(self.heap_book)
        
        self.globals_frame.update_memory_model()
        self.inspector_frame.update_memory_model()
        # TODO: globals and locals
        
        assert self._vm.get_state() == "toplevel"
        # TODO: following command creates an unnecessary new propmpt
        self._vm.send_command(ToplevelCommand(command="pass", heap_required=True))

    def cmd_mac_add_download_assessment(self):
        # TODO:
        """
        Normally Mac doesn't allow opening py files from web directly
        See:
        http://keith.chaos-realm.net/plugin/tag/downloadassessment
        https://developer.apple.com/library/mac/#documentation/Miscellaneous/Reference/UTIRef/Articles/System-DeclaredUniformTypeIdentifiers.html
        
        create file ~/Library/Preferences/com.apple.DownloadAssessment.plist
        with following content:
        
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>LSRiskCategorySafe</key> 
            <dict>
                <key>LSRiskCategoryContentTypes</key>
                <array>
                    <string>public.xml</string>
                </array>
            
                <key>LSRiskCategoryExtensions</key>
                <array>
                    <string>py</string>
                    <string>pyw</string>
                </array>
            </dict>
        </dict>
        </plist>
        """

    def cmd_step_enabled(self):
        #self._check_issue_goto_before_or_after()
        msg = self._vm.get_state_message()
        # always enabled during debugging
        return (isinstance(msg, DebuggerResponse)) 
    
    def cmd_step(self, automatic=False):
        if not automatic:
            self.step_over = False
        self._check_issue_debugger_command(DebuggerCommand(command="step"))
    
    def cmd_zoom_enabled(self):
        #self._check_issue_goto_before_or_after()
        return self.cmd_exec_enabled()
    
    def cmd_zoom(self):
        self._check_issue_debugger_command(DebuggerCommand(command="zoom"))
    
    def cmd_exec_enabled(self):
        return self.cmd_step_enabled()
        #self._check_issue_goto_before_or_after()
        #msg = self._vm.get_state_message()
        #return (isinstance(msg, DebuggerResponse) 
        #        and msg.state in ("before_expression", "before_expression_again",
        #                          "before_statement", "before_statement_again")) 
    
    def cmd_exec(self):
        self.step_over = True
        self.cmd_step(True)
    
    def cmd_focus_editor(self):
        self.editor_book.focus_current_editor()
    
    def cmd_focus_shell(self):
        self.shell.focus_set()
    
    def cmd_open_user_dir(self):
        misc_utils.open_path_in_system_file_manager(os.path.expanduser(os.path.join("~", ".thonny")))
    
    def _check_issue_debugger_command(self, cmd, automatic=False):
        if isinstance(self._vm.get_state_message(), DebuggerResponse):
            self._issue_debugger_command(cmd, automatic)
            # TODO: notify memory panes and editors? Make them inactive?
    
    def _issue_debugger_command(self, cmd, automatic=False):
        print("_issue", cmd, automatic)
        last_response = self._vm.get_state_message()
        # tell VM the state we are seeing
        cmd.setdefault (
            frame_id=last_response.frame_id,
            state=last_response.state,
            focus=last_response.focus,
            heap_required=self.get_option("view.values_in_heap")
        )
        
        if not automatic:
            self.last_manual_debugger_command_sent = cmd    # TODO: hack
        self._vm.send_command(cmd)
        # TODO: notify memory panes and editors? Make them inactive?
            
    def cmd_set_auto_cd(self):
        print(self._auto_cd.get())
        
    def stop_debugging(self):
        self.editor_book.stop_debugging()
        self.shell.stop_debugging()
        self.globals_frame.stop_debugging()
        self.builtins_frame.stop_debugging()
        self.heap_frame.stop_debugging()
        self._vm.reset()
    
    def start_debugging(self, filename=None):
        self.editor_book.start_debugging(self._vm, filename)
        self.shell.start_debugging(self._vm, filename)
        self._vm.start()
    
    
    def _update_menu(self, name, menu_widget):
        for menu_name, _, items in self._menus:
            if menu_name == name:
                for item in items:
                    if isinstance(item, Command):
                        if item.is_enabled():
                            menu_widget.entryconfigure(item.label, state=tk.NORMAL)
                        else:
                            menu_widget.entryconfigure(item.label, state=tk.DISABLED)
                    
                    
        
    
    def _find_current_edit_widget(self):
        ""
        widget = self.focus_get()
        if (isinstance(widget, tk.Text) and widget.cget("undo")):
            return widget.master
            
            
            

    def cmd_show_replayer(self):
        launcher = os.path.join(self._main_dir, "replay")
        cmd_line = [sys.executable, '-u', launcher]
        subprocess.Popen(cmd_line)
    
    def _get_version(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fp:
                return StrictVersion(fp.read().strip())
        except:
            return StrictVersion("0.0")
      
    def _update_title(self):
        self.title("Thonny  -  Python {1}.{2}.{3}  -  {0}".format(self._vm.cwd, *sys.version_info))
    

    
    def _on_close(self):
        if not self.editor_book.check_allow_closing():
            return
        
        try:
            self._save_preferences()
            self.user_logger.save()
            ui_utils.delete_images()
        except:
            tk.messagebox.showerror("Internal error. Use Ctrl+C to copy",
                                traceback.format_exc())
        
        self.destroy()
        
    def _on_get_focus(self, e):
        self.log_user_event(user_logging.ProgramGetFocusEvent());

    def _on_lose_focus(self, e):
        self.log_user_event(user_logging.ProgramLoseFocusEvent());
        
    
    def _on_tk_exception(self, exc, val, tb):
        # copied from tkinter.Tk.report_callback_exception
        # Aivar: following statement kills the process when run with pythonw.exe
        # http://bugs.python.org/issue22384
        #sys.stderr.write("Exception in Tkinter callback\n")
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)
        
        # TODO: Command+C for Mac
        tk.messagebox.showerror("Internal error. Use Ctrl+C to copy",
                                traceback.format_exc())
    
        
    def _save_preferences(self):
        self.update_idletasks()
        
        # update layout prefs
        if self.w_book.winfo_ismapped():
            self.set_option("layout.w_width", self.w_book.winfo_width(), False)
        
        if self.right_pw.winfo_ismapped():
            self.set_option("layout.memory_width", self.right_pw.winfo_width(), False)
            # TODO: heigths
        
        self.set_option("layout.zoomed", ui_utils.get_zoomed(self), False)
        if not ui_utils.get_zoomed(self):
            self.set_option("layout.top", self.winfo_y(), False)
            self.set_option("layout.left", self.winfo_x(), False)
            self.set_option("layout.width", self.winfo_width(), False)
            self.set_option("layout.height", self.winfo_height(), False)
        
        center_width = self.center_pw.winfo_width()
        if center_width > 1:
            self.set_option("layout.center_width", center_width, False)
        
        if self.right_pw.winfo_ismapped():
            self.set_option("layout.memory_width", self.right_pw.winfo_width(), False)
        
        if self.w_book.winfo_ismapped():
            self.set_option("layout.browser_width", self.w_book.winfo_width(), False)
            
        self._configuration.save()
    

