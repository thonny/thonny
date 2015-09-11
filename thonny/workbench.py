# -*- coding: utf-8 -*-

from distutils.version import StrictVersion
import gettext
import importlib
from logging import exception, info, warning
import os.path
import sys
from tkinter import ttk
import traceback

from thonny import misc_utils
from thonny import ui_utils
from thonny.code import EditorNotebook
from thonny.common import Record, ToplevelCommand
from thonny.config import ConfigurationManager
from thonny.misc_utils import running_on_mac_os
from thonny.ui_utils import sequence_to_accelerator, AutomaticPanedWindow, AutomaticNotebook
import tkinter as tk
import tkinter.font as tk_font
import tkinter.messagebox as tk_messagebox
from thonny.running import Runner
import thonny.globals
import logging
from thonny.globals import register_runner, get_runner
from pkgutil import get_data

class Workbench(tk.Tk):
    """
    Thonny's main window and communication hub.
    
    Is responsible for:
    
        * creating the main window
        * maintaining layout (_init_containers)
        * loading plugins (_init_plugins, add_view, add_command)        
        * providing references to main components (editor_notebook and runner)
        * communication between other components (see event_generate and bind)
        * configuration services (get_option, set_option, add_defaults)
        * loading translations
        * maintaining fonts (get_font, increasing and decreasing font size)
    
    After workbench and plugins get loaded, 3 kinds of events start happening:
        
        * User events (keypresses, mouse clicks, menu selections, ...)
        * Virtual events (mostly via get_workbench().event_generate). These include:
          events reported via and dispatched by Tk event system;
          WorkbenchEvent-s, reported via and dispatched by enhanced get_workbench().event_generate.
        * Events from the background process (program output notifications, input requests,
          notifications about debugger's progress)
          
    """
    def __init__(self, main_dir):
        tk.Tk.__init__(self)
        tk.Tk.report_callback_exception = self._on_tk_exception
        self._event_handlers = {}
        
        thonny.globals.register_workbench(self)
        
        self._main_dir = main_dir 
        self._configuration_manager = ConfigurationManager(os.path.expanduser(os.path.join("~", ".thonny", "preferences.ini")))
        
        self._init_diagnostic_logging()
        self._init_translation()
        self._init_fonts()
        self._init_window()
        self._init_menu()
        
        self.title("Thonny")
        self.bind("BackendMessage", self._update_title, True)
        
        self._init_containers()
        register_runner(Runner())
        self._init_commands()
        self._editor_notebook.focus_set()
        
        self._load_plugins()
        
        get_runner().send_command(ToplevelCommand(command="Reset"))
        self.mainloop()
    
    def _init_diagnostic_logging(self):
        self.add_option("debug_mode", False)
        logging.basicConfig(format='%(levelname)s:%(message)s',
            level=logging.DEBUG if self.get_option("debug_mode") else logging.INFO)
    
    def _init_window(self):
        
        self.add_option("layout.zoomed", False)
        self.add_option("layout.top", 15)
        self.add_option("layout.left", 150)
        self.add_option("layout.width", 700)
        self.add_option("layout.height", 650)
        self.add_option("layout.w_width", 200)
        self.add_option("layout.e_width", 200)
        self.add_option("layout.s_height", 200)
        
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
        
    def _init_menu(self):
        self.option_add('*tearOff', tk.FALSE)
        self._menubar = tk.Menu(self)
        self["menu"] = self._menubar
        self._menus = {}
        
        # create standard menus in correct order
        if running_on_mac_os():
            self.get_menu("Thonny")
            
        self.get_menu("file", _("File"))
        self.get_menu("edit", _("Edit"))
        self.get_menu("view", _("View"))
        self.get_menu("run", _("Run"))
        self.get_menu("help", _("Help"))
        
    def _load_plugins(self):
        plugin_names = self._find_plugins(
                            os.path.join(self._main_dir, "thonny", "plugins"),
                            "thonny.plugins.")
        
        for plugin_name in sorted(plugin_names):
            try:
                m = importlib.import_module(plugin_name)
                if hasattr(m, "load_plugin"):
                    m.load_plugin()
            except:
                exception("Failed loading plugin '" + plugin_name + "'")
    
    def _find_plugins(self, extension_dir, module_name_prefix):
        result = set()
        
        for item in os.listdir(extension_dir):
            item_path = os.path.join(extension_dir, item)
            # TODO: support zipped packages
            if (os.path.isfile(item_path)
                    and item.endswith(".py")
                    and not item.endswith("__.py")
                or os.path.isdir(item_path)
                    and os.path.isfile(os.path.join(item_path, "__init__.py"))):
                    result.add(module_name_prefix 
                               + os.path.splitext(item)[0])
        
        return result
                                
    def _init_fonts(self):
        self.add_option("view.editor_font_family", None)
        self.add_option("view.editor_font_size", None) # 15 if running_on_mac_os() else 10,
        
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
        self.add_option("general.language", "en")
        
        gettext.translation('thonny',
                    os.path.join(self._main_dir, "thonny", "locale"), 
                    languages=[self.get_option("general.language"), "en"]).install()
                                
    
    def _init_commands(self):
        
        self.add_command("exit", "file", "Exit",
            self.destroy, 
            default_sequence="<Alt-F4>")
        
        self.add_separator("view")
        
        self.add_command("increase_font_size", "view", "Increase font size",
            lambda: self._change_font_size(1),
            default_sequence="<Control-plus>")
                
        self.add_command("decrease_font_size", "view", "Increase font size",
            lambda: self._change_font_size(-1),
            default_sequence="<Control-minus>")
        
        self.add_command("focus_editor", "view", "Focus editor",
            self._cmd_focus_editor,
            default_sequence="<F11>")
                
        self.add_command("focus_shell", "view", "Focus shell",
            self._cmd_focus_shell,
            default_sequence="<F12>")
        
        #self.add_command("help", "help", "Thonny help",
        #    self._cmd_help)
            
    def _init_containers(self):
        
        main_frame= ttk.Frame(self) # just a backgroud behind padding of main_pw, without this OS X leaves white border 
        main_frame.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.toolbar = ttk.Frame(main_frame, padding=0) # TODO: height=30 ?
        self.toolbar.grid(column=0, row=0, sticky=tk.NSEW, padx=10)
        self._init_toolbar()
        
        main_pw   = AutomaticPanedWindow(main_frame, orient=tk.HORIZONTAL)
        main_pw.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        self._west_pw   = AutomaticPanedWindow(main_pw, 1, orient=tk.VERTICAL)
        self._center_pw = AutomaticPanedWindow(main_pw, 2, orient=tk.VERTICAL)
        self._east_pw   = AutomaticPanedWindow(main_pw, 3, orient=tk.VERTICAL)
        
        self._view_records = {}
        self._view_notebooks = {
            'nw' : AutomaticNotebook(self._west_pw, 1),
            'w'  : AutomaticNotebook(self._west_pw, 2),
            'sw' : AutomaticNotebook(self._west_pw, 3),
            
            's'  : AutomaticNotebook(self._center_pw, 3),
            
            'ne' : AutomaticNotebook(self._east_pw, 1),
            'e'  : AutomaticNotebook(self._east_pw, 2),
            'se' : AutomaticNotebook(self._east_pw, 3),
        }

        self._editor_notebook = EditorNotebook(self._center_pw)
        self._editor_notebook.position_key = 1
        self._center_pw.insert("auto", self._editor_notebook)


    def _init_toolbar(self): 
        def on_kala_button():
            self._editor_notebook.demo_editor.set_read_only(not self._editor_notebook.demo_editor.read_only)
        
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
        
        
    def add_command(self, command_id, menu_name, command_label, handler,
                    tester=None,
                    default_sequence=None,
                    flag_name=None,
                    skip_sequence_binding=False,
                    _index="end"):
        """Adds an item to specified menu.
        
        Args:
            menu_name: Name of the menu the command should appear in.
                Standard menu names are "file", "edit", "run", "view", "help" 
                (these menu names are not transalted, but labels are).
                If a menu with given name doesn't exist, then new menu is created
                (with label=name).
            command_label: Label for this command
            handler: Function to be called when the command is invoked. 
                Should be callable with one argument (the event or None).
            tester: Function to be called for determining if command is available or not.
                Should be callable with one argument (the event or None).
                Should return True or False.
                If None then command is assumed to be always available.
            default_sequence: Default shortcut (Tk style)
            flag_name: Used for toggle commands. Indicates the name of the boolean option.
        
        Returns:
            None
        """     
        
        def dispatch(event=None):
            if not tester or tester():
                denied = False
                handler()
            else:
                denied = True
                info("Command '" + command_id + "' execution denied")
                self.bell()
                
            self.event_generate("Command", command_id=command_id, denied=denied)
        
        sequence_option_name = "shortcuts." + command_id
        self.add_option(sequence_option_name, default_sequence)
        sequence = self.get_option(sequence_option_name) 
        
        if sequence and not skip_sequence_binding:
            self.bind_all(sequence, dispatch, True)
        
        
        def dispatch_from_menu():
            # I don't like that Tk menu toggles checbutton variable
            # automatically before calling the handler.
            # So I revert the toggle before calling the actual handler.
            # This way the handler doesn't have to worry whether it
            # needs to toggle the variable or not, and it can choose to 
            # decline the toggle.
            if flag_name is not None:
                var = self.get_variable(flag_name)
                var.set(not var.get())
                
            dispatch(None)
            
        self.get_menu(menu_name).insert(
            _index,
            "checkbutton" if flag_name else "command",
            label=command_label,
            accelerator=sequence_to_accelerator(sequence),
            variable=self.get_variable(flag_name) if flag_name else None,
            command=dispatch_from_menu)
    
    def add_separator(self, menu_label):
        # TODO: don't add separator as first item in the menu
        pass
    
    def add_view(self, class_, label, default_location,
                visible_by_default=False,
                default_position_key=None):
        """Adds item to "View" menu for showing/hiding given view. 
        
        Args:
            view_class: Class or constructor for view. Should be callable with single
                argument (the master of the view)
            label: Label of the view tab
            location: Location descriptor. Can be "nw", "sw", "s", "se", "ne"
        
        Returns: None        
        """
        view_id = class_.__name__
        if default_position_key == None:
            default_position_key = label
        
        self.add_option("view." + view_id + ".visible" , visible_by_default)
        self.add_option("view." + view_id + ".location", default_location)
        self.add_option("view." + view_id + ".position_key", default_position_key)
        
        self._view_records[view_id] = {
            "class" : class_,
            "label" : label,
            "location" : self.get_option("view." + view_id + ".location"),
            "position_key" : self.get_option("view." + view_id + ".position_key")
        }
        
        visibility_flag = self.get_variable("view." + view_id + ".visible")
        
        # handler
        def toggle_view_visibility():
            if visibility_flag.get():
                self.hide_view(view_id)
            else:
                self.show_view(view_id, True)
        
        # Menu items are positioned alphabetically 
        # in first section (ie. before first separator) of View menu.
        # Find correct position for this label
        view_menu = self.get_menu("View")
        for i in range(0, 999):
            if ("label" not in view_menu.entryconfigure(i) # separator
                or view_menu.entrycget(i, "label") > label):
                index = i
                break
        else:
            index = "end"
            
            
        self.add_command("toggle_" + view_id, menu_name="view",
            command_label=label,
            handler=toggle_view_visibility,
            flag_name="view." + view_id + ".visible",
            _index=index)
        
        if visibility_flag.get():
            self.show_view(view_id, False)
        
        
    def get_option(self, name):
        return self._configuration_manager.get_option(name)
    
    def set_option(self, name, value, save_now=True):
        self._configuration_manager.set_option(name, value, save_now)
        
    def add_option(self, name, default_value):
        """Registers a new option.
        
        If the name contains a period, then the part left to the (first) period
        will become the section of the option and rest will become name under that 
        section.
        
        If the name doesn't contain a period, then it will be added under section 
        "general".
         
        Don't confuse this method with Tkinter's option_add!
        """
        self._configuration_manager.add_option(name, default_value)
    
    def get_variable(self, name):
        return self._configuration_manager.get_variable(name)
    
    def get_font(self, name):
        """
        Supported names are EditorFont and BoldEditorFont
        """
        return self._fonts[name]
    
    
    def get_menu(self, name, label=None):
        """Gives the menu with given name. Creates if not created yet.
        
        Args:
            name: meant to be used as not translatable menu name
            label: translated label, used only when menu with given name doesn't exist yet
        """
        if name not in self._menus:
            menu = tk.Menu(self._menubar)
            menu["postcommand"] = lambda: self._update_menu(name, menu)
            self._menubar.add_cascade(label=label if label else name, menu=menu)
            
            self._menus[name] = menu
            if label:
                self._menus[label] = menu
                
        return self._menus[name]
    
    def get_view(self, view_id, create=True):
        if "instance" not in self._view_records[view_id]:
            if not create:
                return None
            
            # create the view
            class_ = self._view_records[view_id]["class"]
            location = self._view_records[view_id]["location"]
            master = self._view_notebooks[location]
            view = class_(master)
            view.position_key = self._view_records[view_id]["position_key"]
            self._view_records[view_id]["instance"] = view
            
        return self._view_records[view_id]["instance"]
    
    def get_current_editor(self):
        return self._editor_notebook.get_current_editor()
    
    def get_editor_notebook(self):
        return self._editor_notebook
    
    def get_installation_dir(self):
        """Returns Thonny installation directory"""
        return self._main_dir
    
    def get_resource_dir(self):
        """Returns directory with icon and other image files"""
        return os.path.join(self._main_dir, "thonny", "res")
                      
    def show_view(self, view_id, set_focus=True):
        """View must be already registered.
        
        Args:
            view_id: View class name 
            without package name (eg. 'ShellView') """
        
        # get or create
        view = self.get_view(view_id)
        notebook = view.master
        
        if not view.winfo_ismapped():
            notebook.insert("auto", view, text=self._view_records[view_id]["label"])
        
        # switch to the tab
        notebook.select(view)
        
        # add focus
        if set_focus:
            view.focus_set()
        
        self.set_option("view." + view_id + ".visible", True)
        self.event_generate("ShowView", view=view)
    
    def hide_view(self, view_id):
        if "instance" in self._view_records[view_id]:
            view = self._view_records[view_id]["instance"]
            view.master.forget(view)
            
            self.set_option("view." + view_id + ".visible", False)
            self.event_generate("HideView", view=view)
        

    def event_generate(self, sequence, **kwargs):
        """Uses custom event handling when sequence doesn't start with <.
        In this case arbitrary attributes can be added to the event.
        Otherwise forwards the call to Tk's event_generate"""
        if sequence.startswith("<"):
            tk.Tk.event_generate(self, sequence, **kwargs)
        else:
            if sequence in self._event_handlers:
                for handler in self._event_handlers[sequence]:
                    try:
                        # Yes, I'm creating separate event object for each handler
                        # so that they can't misuse the mutabilty
                        event = WorkbenchEvent(sequence, **kwargs)
                        handler(event)
                    except:
                        exception("Problem when handling '" + sequence + "'")
                
    def bind(self, sequence, func, add=None):
        """Uses custom event handling when sequence doesn't start with <.
        Otherwise forwards the call to Tk's bind"""
        
        if not add:
            warning("Workbench.bind({}, ..., add={}) -- did you really want to replace existing bindings?".format(sequence, add))
        
        if sequence.startswith("<"):
            tk.Tk.bind(self, sequence, func, add)
        else:
            if sequence not in self._event_handlers or not add:
                self._event_handlers[sequence] = set()
                
            self._event_handlers[sequence].add(func)

    def get_version(self):
        try:
            with open(os.path.join(os.path.dirname(__file__), "VERSION")) as fp:
                return StrictVersion(fp.read().strip())
        except:
            return StrictVersion("0.0")
      
    
    def in_heap_mode(self):
        # TODO: add a separate command for enabling the heap mode 
        # untie the mode from HeapView
        return (self._configuration_manager.has_option("view.heap.visible")
            and self.get_option("view.heap.visible"))
        
    def _update_toolbar(self):
        "TODO:"
    
    
    def _change_font_size(self, delta):
        for f in self._fonts:
            f.configure(size=f.cget("size") + delta)
        
        # TODO: save conf?
    
    def _check_update_window_width(self, delta):
        if not ui_utils.get_zoomed(self):
            self.update_idletasks()
            # TODO: shift to left if right edge goes away from screen
            # TODO: check with screen width
            new_geometry = "{0}x{1}+{2}+{3}".format(self.winfo_width() + delta,
                                                   self.winfo_height(),
                                                   self.winfo_x(), self.winfo_y())
            
            self.geometry(new_geometry)
            

    
    def _cmd_focus_editor(self):
        self._editor_notebook.focus_set()
    
    def _cmd_focus_shell(self):
        self.show_view("ShellView", True)
    
    
    
    def _update_menu(self, name, menu_widget):
        return
        # TODO:
        """
        for menu_name, _, items in self._menus:
            if menu_name == name:
                for item in items:
                    if isinstance(item, Command):
                        if item.is_enabled():
                            menu_widget.entryconfigure(item.label, state=tk.NORMAL)
                        else:
                            menu_widget.entryconfigure(item.label, state=tk.DISABLED)
        """            
                    
        
    
            
            
            

    
    def _on_close(self):
        if not self._editor_notebook.check_allow_closing():
            return
        
        try:
            self._save_layout()
            #self.user_logger.save()
            #ui_utils.delete_images()
        except:
            self.report_internal_error()

        self.destroy()
        
    def _on_tk_exception(self, exc, val, tb):
        # copied from tkinter.Tk.report_callback_exception with modifications
        # Aivar: following statement kills the process when run with pythonw.exe
        # http://bugs.python.org/issue22384
        #sys.stderr.write("Exception in Tkinter callback\n")
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        self.report_internal_error()
    
    def report_internal_error(self):
        exception("Internal error")
        tk_messagebox.showerror("Internal error. Use {} to copy"
                                .format("Command+C" if running_on_mac_os() else "Ctrl+C"),
                                traceback.format_exc())
    
        
    def _save_layout(self):
        self.update_idletasks()
        
        self.set_option("layout.zoomed", ui_utils.get_zoomed(self), False)
        
        def save_width(widget, name):
            #TODO:
            assert (isinstance(widget, AutomaticPanedWindow)
                or isinstance(widget, AutomaticNotebook))
            
            if widget.last_width:
                self.set_
                
                
        if self._west_pw.winfo_ismapped():
            self.set_option("layout.west_width", self._west_pw.winfo_width(), False)
        if self._center_pw.winfo_ismapped():
            self.set_option("layout.center_width", self._center_pw.winfo_width(), False)
        if self._west_pw.winfo_ismapped():
            self.set_option("layout.east_width", self._west_pw.winfo_width(), False)
            # TODO: heigths
        
        if not ui_utils.get_zoomed(self):
            self.set_option("layout.top", self.winfo_y(), False)
            self.set_option("layout.left", self.winfo_x(), False)
            self.set_option("layout.width", self.winfo_width(), False)
            self.set_option("layout.height", self.winfo_height(), False)
        
        self._configuration_manager.save()
        
    def _update_title(self, event):
        self.title("Thonny  -  Python {1}.{2}.{3}  -  {0}".format(self._runner.get_cwd(), *sys.version_info))
    

class WorkbenchEvent(Record):
    def __init__(self, sequence, **kwargs):
        Record.__init__(self, **kwargs)
        self.sequence = sequence
        
