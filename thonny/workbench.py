# -*- coding: utf-8 -*-

import ast
import collections
import importlib
import logging
import os.path
import pkgutil
import platform
import queue
import re
import socket
import sys
import tkinter as tk
import tkinter.font as tk_font
import tkinter.messagebox as tk_messagebox
import traceback
import webbrowser
from threading import Thread
from tkinter import ttk
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,  # pylint: disable=unused-import
    Sequence,
    Set,       # pylint: disable=unused-import 
    Tuple,     # pylint: disable=unused-import
    Type,
    Union,
    cast,
)  # pylint: disable=unused-import
from warnings import warn

import thonny
from thonny import THONNY_USER_DIR, get_runner, running, ui_utils, assistance
from thonny.code import EditorNotebook
from thonny.common import Record, UserError, normpath_with_actual_case
from thonny.config import try_load_configuration
from thonny.config_ui import ConfigurationDialog
from thonny.misc_utils import running_on_linux, running_on_mac_os, running_on_windows
from thonny.running import BackendProxy, Runner
from thonny.shell import ShellView
from thonny.ui_utils import (
    AutomaticNotebook,
    AutomaticPanedWindow,
    create_tooltip,
    get_style_configuration,
    lookup_style_option,
    register_latin_shortcut,
    select_sequence,
    sequence_to_accelerator,
)

THONNY_PORT = 4957
SERVER_SUCCESS = "OK"
CONFIGURATION_FILE_NAME = os.path.join(THONNY_USER_DIR, "configuration.ini")
SINGLE_INSTANCE_DEFAULT = True
SIMPLE_MODE_VIEWS = ["ShellView", "VariablesView"]

MenuItem = collections.namedtuple("MenuItem", ["group", "position_in_group", "tester"])
BackendSpec = collections.namedtuple(
    "BackendSpec",
    ["name", "proxy_class", "description", "config_page_constructor", "sort_key"],
)

BasicUiThemeSettings = Dict[str, Dict[str, Union[Dict, Sequence]]]
CompoundUiThemeSettings = List[BasicUiThemeSettings]
UiThemeSettings = Union[BasicUiThemeSettings, CompoundUiThemeSettings]
FlexibleUiThemeSettings = Union[UiThemeSettings, Callable[[], UiThemeSettings]]

SyntaxThemeSettings = Dict[str, Dict[str, Union[str, int, bool]]]
FlexibleSyntaxThemeSettings = Union[
    SyntaxThemeSettings, Callable[[], SyntaxThemeSettings]
]


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
        * maintaining fonts (named fonts, increasing and decreasing font size)
    
    After workbench and plugins get loaded, 3 kinds of events start happening:
        
        * User events (keypresses, mouse clicks, menu selections, ...)
        * Virtual events (mostly via get_workbench().event_generate). These include:
          events reported via and dispatched by Tk event system;
          WorkbenchEvent-s, reported via and dispatched by enhanced get_workbench().event_generate.
        * Events from the background process (program output notifications, input requests,
          notifications about debugger's progress)
          
    """

    def __init__(self, server_socket=None) -> None:
        thonny._workbench = self

        self._destroying = False
        self._destroyed = False
        self.initializing = True
        tk.Tk.__init__(self, className="Thonny")
        tk.Tk.report_callback_exception = self._on_tk_exception  # type: ignore
        self._event_handlers = {}  # type: Dict[str, Set[Callable]]
        self._images = (
            set()
        )  # type: Set[tk.PhotoImage] # keep images here to avoid Python garbage collecting them,
        self._default_image_mapping = (
            {}
        )  # type: Dict[str, str] # to allow specify default alternative images
        self._image_mapping_by_theme = (
            {}
        )  # type: Dict[str, Dict[str, str]] # theme-based alternative images
        self._current_theme_name = "clam"  # will be overwritten later
        self._backends = {}  # type: Dict[str, BackendSpec]
        self._commands = []  # type: List[Dict[str, Any]]
        self._view_records = {}  # type: Dict[str, Dict[str, Any]]
        self.content_inspector_classes = []  # type: List[Type]
        self._latin_shortcuts = (
            {}
        )  # type: Dict[Tuple[int,int], List[Tuple[Callable, Callable]]]

        self._init_configuration()
        self._init_diagnostic_logging()

        self._init_scaling()

        self._add_main_backends()
        self._init_theming()
        self._init_window()
        self.add_view(
            ShellView, "Shell", "s", visible_by_default=True, default_position_key="A"
        )
        assistance.init()
        self._runner = Runner()
        self._load_plugins()

        self._editor_notebook = None  # type: Optional[EditorNotebook]
        self._init_fonts()

        self.reload_themes()
        self._init_menu()

        self._init_containers()
        assert self._editor_notebook is not None

        self._init_program_arguments_frame()
        self._init_regular_mode_link()

        self._show_views()

        self._init_commands()
        self._init_icon()
        try:
            self._editor_notebook.load_startup_files()
        except Exception:
            self.report_exception()

        self._editor_notebook.focus_set()
        self._try_action(self._open_views)

        if server_socket is not None:
            self._init_server_loop(server_socket)

        self.bind_class("CodeViewText", "<<CursorMove>>", self.update_title, True)
        self.bind_class("CodeViewText", "<<Modified>>", self.update_title, True)
        self.bind_class("CodeViewText", "<<TextChange>>", self.update_title, True)
        self.get_editor_notebook().bind(
            "<<NotebookTabChanged>>", self.update_title, True
        )
        self.bind_all("<KeyPress>", self._on_all_key_presses, True)
        self.bind("<FocusIn>", self._on_focus_in, True)

        self._publish_commands()
        self.initializing = False
        self.event_generate("<<WorkbenchInitialized>>")
        self.after(
            1, self._start_runner
        )  # Show UI already before waiting for the backend to start

    def _try_action(self, action: Callable) -> None:
        try:
            action()
        except Exception:
            self.report_exception()

    def _init_configuration(self) -> None:
        self._configuration_manager = try_load_configuration(CONFIGURATION_FILE_NAME)
        self._configuration_pages = {}  # type: Dict[str, Type[tk.Widget]]

        self.set_default("general.single_instance", SINGLE_INSTANCE_DEFAULT)
        self.set_default("general.ui_mode", "regular")
        self.set_default("general.debug_mode", False)
        self.set_default("general.disable_notification_sound", False)
        self.set_default("general.scaling", "default")
        self.set_default("run.working_directory", os.path.expanduser("~"))

    def _get_logging_level(self) -> int:
        if self.in_debug_mode():
            return logging.DEBUG
        else:
            return logging.INFO

    def _init_diagnostic_logging(self) -> None:
        logFormatter = logging.Formatter("%(levelname)s: %(message)s")
        root_logger = logging.getLogger()

        log_file = os.path.join(THONNY_USER_DIR, "frontend.log")
        file_handler = logging.FileHandler(log_file, encoding="UTF-8", mode="w")
        file_handler.setFormatter(logFormatter)
        file_handler.setLevel(self._get_logging_level())
        root_logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logFormatter)
        console_handler.setLevel(self._get_logging_level())
        root_logger.addHandler(console_handler)

        root_logger.setLevel(self._get_logging_level())

        import faulthandler

        fault_out = open(os.path.join(THONNY_USER_DIR, "frontend_faults.log"), mode="w")
        faulthandler.enable(fault_out)

    def _init_window(self) -> None:
        self.title("Thonny")

        self.set_default("layout.zoomed", False)
        self.set_default("layout.top", 15)
        self.set_default("layout.left", 150)
        self.set_default("layout.width", 800)
        self.set_default("layout.height", 650)
        self.set_default("layout.w_width", 200)
        self.set_default("layout.e_width", 200)
        self.set_default("layout.s_height", 200)

        # I don't actually need saved options for Full screen/maximize view,
        # but it's easier to create menu items, if I use configuration manager's variables
        self.set_default("view.full_screen", False)
        self.set_default("view.maximize_view", False)

        # In order to avoid confusion set these settings to False
        # even if they were True when Thonny was last run
        self.set_option("view.full_screen", False)
        self.set_option("view.maximize_view", False)

        self.geometry(
            "{0}x{1}+{2}+{3}".format(
                max(self.get_option("layout.width"), 320),
                max(self.get_option("layout.height"), 240),
                min(
                    max(self.get_option("layout.left"), 0),
                    self.winfo_screenwidth() - 200,
                ),
                min(
                    max(self.get_option("layout.top"), 0),
                    self.winfo_screenheight() - 200,
                ),
            )
        )

        if self.get_option("layout.zoomed"):
            ui_utils.set_zoomed(self, True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_configure, True)

    def _init_icon(self) -> None:
        # Window icons
        if running_on_linux() and ui_utils.get_tk_version_info() >= (8, 6):
            self.iconphoto(True, self.get_image("thonny.png"))
        else:
            icon_file = os.path.join(self.get_package_dir(), "res", "thonny.ico")
            try:
                self.iconbitmap(icon_file, default=icon_file)
            except Exception:
                try:
                    # seems to work in mac
                    self.iconbitmap(icon_file)
                except Exception:
                    pass

    def _init_menu(self) -> None:
        self.option_add("*tearOff", tk.FALSE)
        if lookup_style_option("Menubar", "custom", False):
            self._menubar = ui_utils.CustomMenubar(
                self
            )  # type: Union[tk.Menu, ui_utils.CustomMenubar]
            if self.get_ui_mode() != "simple":
                self._menubar.grid(row=0, sticky="nsew")
        else:
            opts = get_style_configuration("Menubar")
            if "custom" in opts:
                del opts["custom"]
            self._menubar = tk.Menu(self, **opts)
            if self.get_ui_mode() != "simple":
                self["menu"] = self._menubar
        self._menus = {}  # type: Dict[str, tk.Menu]
        self._menu_item_specs = (
            {}
        )  # type: Dict[Tuple[str, str], MenuItem] # key is pair (menu_name, command_label)

        # create standard menus in correct order
        self.get_menu("file", "File")
        self.get_menu("edit", "Edit")
        self.get_menu("view", "View")
        self.get_menu("run", "Run")
        self.get_menu("device", "Device")
        self.get_menu("tools", "Tools")
        self.get_menu("help", "Help")

    def _load_plugins(self) -> None:
        # built-in plugins
        import thonny.plugins  # pylint: disable=redefined-outer-name

        self._load_plugins_from_path(
            thonny.plugins.__path__, "thonny.plugins."  # type: ignore
        )

        # 3rd party plugins from namespace package
        try:
            import thonnycontrib  # @UnresolvedImport
        except ImportError:
            # No 3rd party plugins installed
            pass
        else:
            self._load_plugins_from_path(thonnycontrib.__path__, "thonnycontrib.")

    def _load_plugins_from_path(self, path: List[str], prefix: str) -> None:
        load_function_name = "load_plugin"

        for _, module_name, _ in sorted(
            pkgutil.iter_modules(path, prefix), key=lambda x: x[2]
        ):
            try:
                m = importlib.import_module(module_name)
                if hasattr(m, load_function_name):
                    getattr(m, load_function_name)()
            except Exception:
                logging.exception("Failed loading plugin '" + module_name + "'")

    def _init_fonts(self) -> None:
        # set up editor and shell fonts
        self.set_default(
            "view.io_font_family", "Courier" if running_on_mac_os() else "Courier New"
        )

        default_editor_family = "Courier New"
        families = tk_font.families()

        for family in ["Consolas", "Ubuntu Mono", "Menlo", "DejaVu Sans Mono"]:
            if family in families:
                default_editor_family = family
                break

        self.set_default("view.editor_font_family", default_editor_family)
        self.set_default("view.editor_font_size", 14 if running_on_mac_os() else 11)

        default_font = tk_font.nametofont("TkDefaultFont")
        
        if running_on_linux():
            heading_font = tk_font.nametofont("TkHeadingFont")
            heading_font.configure(weight="normal")
            caption_font = tk_font.nametofont("TkCaptionFont")
            caption_font.configure(weight="normal", size=default_font.cget("size"))

        self._fonts = [
            tk_font.Font(name="IOFont", family=self.get_option("view.io_font_family")),
            tk_font.Font(
                name="EditorFont", family=self.get_option("view.editor_font_family")
            ),
            tk_font.Font(
                name="SmallEditorFont",
                family=self.get_option("view.editor_font_family"),
            ),
            tk_font.Font(
                name="BoldEditorFont",
                family=self.get_option("view.editor_font_family"),
                weight="bold",
            ),
            tk_font.Font(
                name="ItalicEditorFont",
                family=self.get_option("view.editor_font_family"),
                slant="italic",
            ),
            tk_font.Font(
                name="BoldItalicEditorFont",
                family=self.get_option("view.editor_font_family"),
                weight="bold",
                slant="italic",
            ),
            tk_font.Font(
                name="TreeviewFont",
                family=default_font.cget("family"),
                size=default_font.cget("size"),
            ),
            tk_font.Font(
                name="BoldTkDefaultFont",
                family=default_font.cget("family"),
                size=default_font.cget("size"),
                weight="bold",
            ),
            tk_font.Font(
                name="ItalicTkDefaultFont",
                family=default_font.cget("family"),
                size=default_font.cget("size"),
                slant="italic",
            ),
            tk_font.Font(
                name="UnderlineTkDefaultFont",
                family=default_font.cget("family"),
                size=default_font.cget("size"),
                underline=1,
            ),
        ]

        self.update_fonts()

    def _add_main_backends(self) -> None:
        self.set_default("run.backend_name", "SameAsFrontend")
        self.set_default("CustomInterpreter.used_paths", [])
        self.set_default("CustomInterpreter.path", "")

        self.add_backend(
            "SameAsFrontend",
            running.SameAsFrontendCPythonProxy,
            "The same interpreter which runs Thonny (default)",
            running.get_frontend_python(),
            "1",
        )

        from thonny import running_config_page

        self.add_backend(
            "CustomCPython",
            running.CustomCPythonProxy,
            "Alternative Python 3 interpreter or virtual environment",
            running_config_page.CustomCPythonConfigurationPage,
            "2",
        )

        self.add_backend(
            "PrivateVenv",
            running.PrivateVenvCPythonProxy,
            "A special virtual environment (deprecated)",
            "This virtual environment is automatically maintained by Thonny.\n"
            "Location: " + running.get_private_venv_path(),
            "z",
        )

    def _start_runner(self) -> None:
        try:
            self.update_idletasks()  # allow UI to complete
            thonny._runner = self._runner
            self._runner.start()
            self._update_toolbar()
        except Exception:
            self.report_exception("Error when initializing backend")

    def _init_server_loop(self, server_socket) -> None:
        """Socket will listen requests from newer Thonny instances,
        which try to delegate opening files to older instance"""
        self._requests_from_socket = queue.Queue()  # type: queue.Queue[bytes]

        def server_loop():
            while True:
                logging.debug("Waiting for next client")
                (client_socket, _) = server_socket.accept()
                try:
                    self._handle_socket_request(client_socket)
                except Exception:
                    traceback.print_exc()

        Thread(target=server_loop, daemon=True).start()
        self._poll_socket_requests()

    def _init_commands(self) -> None:

        self.add_command(
            "exit",
            "file",
            "Exit",
            self._on_close,
            default_sequence=select_sequence("<Alt-F4>", "<Command-q>"),
        )

        self.add_command(
            "show_options", "tools", "Options...", self._cmd_show_options, group=180
        )
        self.createcommand("::tk::mac::ShowPreferences", self._cmd_show_options)
        self.createcommand("::tk::mac::Quit", self._mac_quit)

        self.add_command(
            "increase_font_size",
            "view",
            "Increase font size",
            lambda: self._change_font_size(1),
            default_sequence=select_sequence("<Control-plus>", "<Command-Shift-plus>"),
            extra_sequences=["<Control-KP_Add>"],
            group=60,
        )

        self.add_command(
            "decrease_font_size",
            "view",
            "Decrease font size",
            lambda: self._change_font_size(-1),
            default_sequence=select_sequence("<Control-minus>", "<Command-minus>"),
            extra_sequences=["<Control-KP_Subtract>"],
            group=60,
        )

        self.bind("<Control-MouseWheel>", self._cmd_zoom_with_mouse, True)

        self.add_command(
            "focus_editor",
            "view",
            "Focus editor",
            self._cmd_focus_editor,
            default_sequence="<Alt-e>",
            group=70,
        )

        self.add_command(
            "focus_shell",
            "view",
            "Focus shell",
            self._cmd_focus_shell,
            default_sequence="<Alt-s>",
            group=70,
        )

        if self.get_ui_mode() == "expert":

            self.add_command(
                "toggle_maximize_view",
                "view",
                "Maximize view",
                self._cmd_toggle_maximize_view,
                flag_name="view.maximize_view",
                default_sequence=None,
                group=80,
            )
            self.bind_class("TNotebook", "<Double-Button-1>", self._maximize_view, True)
            self.bind("<Escape>", self._unmaximize_view, True)

            self.add_command(
                "toggle_maximize_view",
                "view",
                "Full screen",
                self._cmd_toggle_full_screen,
                flag_name="view.full_screen",
                default_sequence=select_sequence("<F11>", "<Command-Shift-F>"),
                group=80,
            )

        if self.in_debug_mode():
            self.bind_all(
                "<Control-Shift-Alt-D>", self._print_state_for_debugging, True
            )

    def _print_state_for_debugging(self, event) -> None:
        print(get_runner()._postponed_commands)

    def _init_containers(self) -> None:

        # Main frame functions as
        # - a backgroud behind padding of main_pw, without this OS X leaves white border
        # - a container to be hidden, when a view is maximized and restored when view is back home
        main_frame = ttk.Frame(self)  #
        self._main_frame = main_frame
        main_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._maximized_view = None  # type: Optional[tk.Widget]

        self._toolbar = ttk.Frame(main_frame, padding=0)
        self._toolbar.grid(column=0, row=0, sticky=tk.NSEW, padx=10, pady=(5, 0))

        self.set_default("layout.west_pw_width", self.scale(150))
        self.set_default("layout.east_pw_width", self.scale(150))

        self.set_default("layout.s_nb_height", self.scale(150))
        self.set_default("layout.nw_nb_height", self.scale(150))
        self.set_default("layout.sw_nb_height", self.scale(150))
        self.set_default("layout.ne_nb_height", self.scale(150))
        self.set_default("layout.se_nb_height", self.scale(150))

        self._main_pw = AutomaticPanedWindow(main_frame, orient=tk.HORIZONTAL)

        self._main_pw.grid(column=0, row=1, sticky=tk.NSEW, padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        self._west_pw = AutomaticPanedWindow(
            self._main_pw,
            1,
            orient=tk.VERTICAL,
            preferred_size_in_pw=self.get_option("layout.west_pw_width"),
        )
        self._center_pw = AutomaticPanedWindow(self._main_pw, 2, orient=tk.VERTICAL)
        self._east_pw = AutomaticPanedWindow(
            self._main_pw,
            3,
            orient=tk.VERTICAL,
            preferred_size_in_pw=self.get_option("layout.east_pw_width"),
        )

        self._view_notebooks = {
            "nw": AutomaticNotebook(
                self._west_pw,
                1,
                preferred_size_in_pw=self.get_option("layout.nw_nb_height"),
            ),
            "w": AutomaticNotebook(self._west_pw, 2),
            "sw": AutomaticNotebook(
                self._west_pw,
                3,
                preferred_size_in_pw=self.get_option("layout.sw_nb_height"),
            ),
            "s": AutomaticNotebook(
                self._center_pw,
                3,
                preferred_size_in_pw=self.get_option("layout.s_nb_height"),
            ),
            "ne": AutomaticNotebook(
                self._east_pw,
                1,
                preferred_size_in_pw=self.get_option("layout.ne_nb_height"),
            ),
            "e": AutomaticNotebook(self._east_pw, 2),
            "se": AutomaticNotebook(
                self._east_pw,
                3,
                preferred_size_in_pw=self.get_option("layout.se_nb_height"),
            ),
        }

        for nb_name in self._view_notebooks:
            self.set_default("layout.notebook_" + nb_name + "_visible_view", None)

        self._editor_notebook = EditorNotebook(self._center_pw)
        self._editor_notebook.position_key = 1  # type: ignore
        self._center_pw.insert("auto", self._editor_notebook)

    def _init_theming(self) -> None:
        self._style = ttk.Style()
        self._ui_themes = (
            {}
        )  # type: Dict[str, Tuple[Optional[str], FlexibleUiThemeSettings, Dict[str, str]]] # value is (parent, settings, images)
        self._syntax_themes = (
            {}
        )  # type: Dict[str, Tuple[Optional[str], FlexibleSyntaxThemeSettings]] # value is (parent, settings)
        # following will be overwritten by plugins.base_themes
        self.set_default(
            "view.ui_theme", "xpnative" if running_on_windows() else "clam"
        )
        self.set_default(
            "view.ui_theme", "xpnative" if running_on_windows() else "clam"
        )

    def add_command(
        self,
        command_id: str,
        menu_name: str,
        command_label: str,
        handler: Optional[Callable[[], None]] = None,
        tester: Optional[Callable[[], bool]] = None,
        default_sequence: Optional[str] = None,
        extra_sequences: Sequence[str] = [],
        flag_name: Optional[str] = None,
        skip_sequence_binding: bool = False,
        accelerator: Optional[str] = None,
        group: int = 99,
        position_in_group="end",
        image: Optional[str] = None,
        caption: Optional[str] = None,
        include_in_toolbar: bool = False,
        submenu: Optional[tk.Menu] = None,
        bell_when_denied: bool = True,
    ) -> None:
        """Registers an item to be shown in specified menu.
        
        Args:
            menu_name: Name of the menu the command should appear in.
                Standard menu names are "file", "edit", "run", "view", "help".
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
            group: Used for grouping related commands together. Value should be int. 
                Groups with smaller numbers appear before.
        
        Returns:
            None
        """

        # store command to be published later
        self._commands.append(
            dict(
                command_id=command_id,
                menu_name=menu_name,
                command_label=command_label,
                handler=handler,
                tester=tester,
                default_sequence=default_sequence,
                extra_sequences=extra_sequences,
                flag_name=flag_name,
                skip_sequence_binding=skip_sequence_binding,
                accelerator=accelerator,
                group=group,
                position_in_group=position_in_group,
                image=image,
                caption=caption,
                include_in_toolbar=include_in_toolbar,
                submenu=submenu,
                bell_when_denied=bell_when_denied,
            )
        )

    def _publish_commands(self) -> None:
        for cmd in self._commands:
            self._publish_command(**cmd)

    def _publish_command(
        self,
        command_id: str,
        menu_name: str,
        command_label: str,
        handler: Optional[Callable[[], None]],
        tester: Optional[Callable[[], bool]] = None,
        default_sequence: Optional[str] = None,
        extra_sequences: Sequence[str] = [],
        flag_name: Optional[str] = None,
        skip_sequence_binding: bool = False,
        accelerator: Optional[str] = None,
        group: int = 99,
        position_in_group="end",
        image: Optional[str] = None,
        caption: Optional[str] = None,
        include_in_toolbar: bool = False,
        submenu: Optional[tk.Menu] = None,
        bell_when_denied: bool = True,
    ) -> None:
        def dispatch(event=None):
            if not tester or tester():
                denied = False
                handler()
            else:
                denied = True
                logging.debug("Command '" + command_id + "' execution denied")
                if bell_when_denied:
                    self.bell()

            self.event_generate(
                "UICommandDispatched", command_id=command_id, denied=denied
            )

        sequence_option_name = "shortcuts." + command_id
        self.set_default(sequence_option_name, default_sequence)
        sequence = self.get_option(sequence_option_name)

        if sequence:
            if not skip_sequence_binding:
                self.bind_all(sequence, dispatch, True)
            # register shortcut even without binding
            register_latin_shortcut(self._latin_shortcuts, sequence, handler, tester)

        for extra_sequence in extra_sequences:
            self.bind_all(extra_sequence, dispatch, True)
            if "greek_" not in extra_sequence.lower() or running_on_linux():
                # Use greek alternatives only on Linux
                # (they are not required on Mac
                # and cause double events on Windows)
                register_latin_shortcut(
                    self._latin_shortcuts, sequence, handler, tester
                )

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

        if image:
            _image = self.get_image(image)  # type: Optional[tk.PhotoImage]
        else:
            _image = None

        if _image and lookup_style_option("OPTIONS", "icons_in_menus", True):
            menu_image = _image  # type: Optional[tk.PhotoImage]
        elif flag_name:
            # no image or black next to a checkbox
            menu_image = None
        else:
            menu_image = self.get_image("16x16-blank")

        if not accelerator and sequence:
            accelerator = sequence_to_accelerator(sequence)

        # remember the details that can't be stored in Tkinter objects
        self._menu_item_specs[(menu_name, command_label)] = MenuItem(
            group, position_in_group, tester
        )

        menu = self.get_menu(menu_name)
        menu.insert(
            self._find_location_for_menu_item(menu_name, command_label),
            "checkbutton" if flag_name else "cascade" if submenu else "command",
            label=command_label,
            accelerator=accelerator,
            image=menu_image,
            compound=tk.LEFT,
            variable=self.get_variable(flag_name) if flag_name else None,
            command=dispatch_from_menu if handler else None,
            menu=submenu,
        )

        if include_in_toolbar:
            toolbar_group = self._get_menu_index(menu) * 100 + group
            assert caption is not None
            self._add_toolbar_button(
                _image,
                command_label,
                caption,
                accelerator,
                handler,
                tester,
                toolbar_group,
            )

    def add_view(
        self,
        cls: Type[tk.Widget],
        label: str,
        default_location: str,
        visible_by_default: bool = False,
        default_position_key: Optional[str] = None,
    ) -> None:
        """Adds item to "View" menu for showing/hiding given view. 
        
        Args:
            view_class: Class or constructor for view. Should be callable with single
                argument (the master of the view)
            label: Label of the view tab
            location: Location descriptor. Can be "nw", "sw", "s", "se", "ne"
        
        Returns: None        
        """
        view_id = cls.__name__
        if default_position_key == None:
            default_position_key = label

        self.set_default("view." + view_id + ".visible", visible_by_default)
        self.set_default("view." + view_id + ".location", default_location)
        self.set_default("view." + view_id + ".position_key", default_position_key)

        if self.get_ui_mode() == "simple":
            visibility_flag = tk.BooleanVar(
                value=view_id in SIMPLE_MODE_VIEWS
            )
        else:
            visibility_flag = cast(
                tk.BooleanVar, self.get_variable("view." + view_id + ".visible")
            )

        self._view_records[view_id] = {
            "class": cls,
            "label": label,
            "location": self.get_option("view." + view_id + ".location"),
            "position_key": self.get_option("view." + view_id + ".position_key"),
            "visibility_flag": visibility_flag,
        }

        # handler
        def toggle_view_visibility():
            if visibility_flag.get():
                self.hide_view(view_id)
            else:
                self.show_view(view_id, True)

        self.add_command(
            "toggle_" + view_id,
            menu_name="view",
            command_label=label,
            handler=toggle_view_visibility,
            flag_name="view." + view_id + ".visible",
            group=10,
            position_in_group="alphabetic",
        )

    def add_configuration_page(self, title: str, page_class: Type[tk.Widget]) -> None:
        self._configuration_pages[title] = page_class

    def add_content_inspector(self, inspector_class: Type) -> None:
        self.content_inspector_classes.append(inspector_class)

    def add_backend(
        self,
        name: str,
        proxy_class: Type[BackendProxy],
        description: str,
        config_page_constructor,
        sort_key=None,
    ) -> None:
        self._backends[name] = BackendSpec(
            name,
            proxy_class,
            description,
            config_page_constructor,
            sort_key if sort_key is not None else description,
        )

        # assing names to related classes
        assert proxy_class.backend_name is None
        proxy_class.backend_name = name  # type: ignore
        if not isinstance(config_page_constructor, str):
            if not getattr(config_page_constructor, "backend_name", None):
                config_page_constructor.backend_name = name

    def add_ui_theme(
        self,
        name: str,
        parent: Union[str, None],
        settings: FlexibleUiThemeSettings,
        images: Dict[str, str] = {},
    ) -> None:
        if name in self._ui_themes:
            warn("Overwriting theme '%s'" % name)

        self._ui_themes[name] = (parent, settings, images)

    def add_syntax_theme(
        self, name: str, parent: Optional[str], settings: FlexibleSyntaxThemeSettings
    ) -> None:
        if name in self._syntax_themes:
            warn("Overwriting theme '%s'" % name)

        self._syntax_themes[name] = (parent, settings)

    def get_usable_ui_theme_names(self) -> Sequence[str]:
        return sorted(
            [name for name in self._ui_themes if self._ui_themes[name][0] is not None]
        )

    def get_syntax_theme_names(self) -> Sequence[str]:
        return sorted(self._syntax_themes.keys())

    def get_ui_mode(self) -> str:
        return os.environ.get("THONNY_MODE", self.get_option("general.ui_mode"))

    def scale(self, value: Union[int, float]) -> int:
        if isinstance(value, (int, float)):
            # using int instead of round so that thin lines will stay
            # one pixel even with scaling_factor 1.67
            result = int(self._scaling_factor * value)
            if result == 0 and value > 0:
                # don't lose thin lines because of scaling
                return 1
            else:
                return result
        else:
            raise NotImplementedError("Only numeric dimensions supported at the moment")

    def _register_ui_theme_as_tk_theme(self, name: str) -> None:
        # collect settings from all ancestors
        total_settings = []  # type: List[FlexibleUiThemeSettings]
        total_images = {}  # type: Dict[str, str]
        temp_name = name
        while True:
            parent, settings, images = self._ui_themes[temp_name]
            total_settings.insert(0, settings)
            for img_name in images:
                total_images.setdefault(img_name, images[img_name])

            if parent is not None:
                temp_name = parent
            else:
                # reached start of the chain
                break

        assert temp_name in self._style.theme_names()
        # only root of the ancestors is relevant for theme_create,
        # because the method actually doesn't take parent settings into account
        # (https://mail.python.org/pipermail/tkinter-discuss/2015-August/003752.html)
        self._style.theme_create(name, temp_name)
        self._image_mapping_by_theme[name] = total_images

        # load images
        self.get_image("tab-close", "img_close")
        self.get_image("tab-close-active", "img_close_active")

        # apply settings starting from root ancestor
        for settings in total_settings:
            if callable(settings):
                settings = settings()

            if isinstance(settings, dict):
                self._style.theme_settings(name, settings)
            else:
                for subsettings in settings:
                    self._style.theme_settings(name, subsettings)

    def _apply_ui_theme(self, name: str) -> None:
        self._current_theme_name = name
        if name not in self._style.theme_names():
            self._register_ui_theme_as_tk_theme(name)

        self._style.theme_use(name)

        # https://wiki.tcl.tk/37973#pagetocfe8b22ab
        for setting in [
            "background",
            "foreground",
            "selectBackground",
            "selectForeground",
        ]:
            value = self._style.lookup("Listbox", setting)
            if value:
                self.option_add("*TCombobox*Listbox." + setting, value)
                self.option_add("*Listbox." + setting, value)

        text_opts = self._style.configure("Text")
        if text_opts:
            for key in text_opts:
                self.option_add("*Text." + key, text_opts[key])

        if hasattr(self, "_menus"):
            # if menus have been initialized, ie. when theme is being changed
            for menu in self._menus.values():
                menu.configure(get_style_configuration("Menu"))

        self.update_fonts()

    def _apply_syntax_theme(self, name: str) -> None:
        def get_settings(name):
            try:
                parent, settings = self._syntax_themes[name]
            except KeyError:
                self.report_exception("Can't find theme '%s'" % name)
                return {}

            if callable(settings):
                settings = settings()

            if parent is None:
                return settings
            else:
                result = get_settings(parent)
                for key in settings:
                    if key in result:
                        result[key].update(settings[key])
                    else:
                        result[key] = settings[key]
                return result

        from thonny import codeview

        codeview.set_syntax_options(get_settings(name))

    def reload_themes(self) -> None:
        preferred_theme = self.get_option("view.ui_theme")
        available_themes = self.get_usable_ui_theme_names()

        if preferred_theme in available_themes:
            self._apply_ui_theme(preferred_theme)
        elif "Enhanced Clam" in available_themes:
            self._apply_ui_theme("Enhanced Clam")
        elif "Windows" in available_themes:
            self._apply_ui_theme("Windows")

        self._apply_syntax_theme(self.get_option("view.syntax_theme"))

    def uses_dark_ui_theme(self) -> bool:

        name = self._style.theme_use()
        while True:
            if "dark" in name.lower():
                return True

            name, _, _ = self._ui_themes[name]
            if name is None:
                # reached start of the chain
                break

        return False

    def _init_program_arguments_frame(self) -> None:
        self.set_default("view.show_program_arguments", False)
        self.set_default("run.program_arguments", "")
        self.set_default("run.past_program_arguments", [])

        visibility_var = self.get_variable("view.show_program_arguments")
        content_var = self.get_variable("run.program_arguments")

        frame = ttk.Frame(self._toolbar)
        col = 1000
        self._toolbar.columnconfigure(col, weight=1)

        label = ttk.Label(frame, text="Program arguments:")
        label.grid(row=0, column=0, sticky="nse", padx=5)

        self.program_arguments_box = ttk.Combobox(
            frame,
            width=80,
            height=15,
            textvariable=content_var,
            values=[""] + self.get_option("run.past_program_arguments"),
        )
        self.program_arguments_box.grid(row=0, column=1, sticky="nsew", padx=5)

        frame.columnconfigure(1, weight=1)

        def update_visibility():
            if visibility_var.get():
                if not frame.winfo_ismapped():
                    frame.grid(row=0, column=col, sticky="nse")
            else:
                if frame.winfo_ismapped():
                    frame.grid_remove()

        def toggle():
            visibility_var.set(not visibility_var.get())
            update_visibility()

        self.add_command(
            "viewargs",
            "view",
            "Program arguments",
            toggle,
            flag_name="view.show_program_arguments",
            group=11,
        )
        
        update_visibility()
    
    def _init_regular_mode_link(self):
        if self.get_ui_mode() != "simple":
            return
        
        default_font = tk_font.nametofont("TkDefaultFont") 
        small_font = default_font.copy()
        small_font.configure(size=int(default_font.cget("size") * 0.7), underline=True) 
        label = ttk.Label(
            self._toolbar, 
            text="Switch to\nregular mode", 
            justify="right",
            font=small_font,
            style="Url.TLabel",
            cursor="hand2",
        )
        label.grid(row=0, column=1001, sticky="ne")
        
        def on_click(_):
            self.set_option("general.ui_mode", "regular")
            tk_messagebox.showinfo(
                "Regular mode",
                "Configuration has been updated. "
                + "Restart Thonny to start working in regular mode.\n\n"
                + "(See 'Tools → Options → General' if you change your mind later.)",
                parent=self)
        
        label.bind("<1>", on_click, True)
        

    def log_program_arguments_string(self, arg_str: str) -> None:
        arg_str = arg_str.strip()
        self.set_option("run.program_arguments", arg_str)

        if arg_str == "":
            # empty will be handled differently
            return

        past_args = self.get_option("run.past_program_arguments")

        if arg_str in past_args:
            past_args.remove(arg_str)

        past_args.insert(0, arg_str)
        past_args = past_args[:10]

        self.set_option("run.past_program_arguments", past_args)
        self.program_arguments_box.configure(values=[""] + past_args)

    def _show_views(self) -> None:
        for view_id in self._view_records:
            if self._view_records[view_id]["visibility_flag"].get():
                try:
                    self.show_view(view_id, False)
                except Exception:
                    self.report_exception("Problem showing " + view_id)

    def update_image_mapping(self, mapping: Dict[str, str]) -> None:
        self._default_image_mapping.update(mapping)

    def get_backends(self) -> Dict[str, BackendSpec]:
        return self._backends

    def get_option(self, name: str, default=None) -> Any:
        # Need to return Any, otherwise each typed call site needs to cast
        return self._configuration_manager.get_option(name, default)

    def set_option(self, name: str, value: Any) -> None:
        self._configuration_manager.set_option(name, value)

    def get_cwd(self) -> str:
        cwd = self.get_option("run.working_directory")
        if os.path.exists(cwd):
            return normpath_with_actual_case(cwd)
        else:
            return normpath_with_actual_case(os.path.expanduser("~"))

    def set_cwd(self, value: str) -> None:
        self.set_option("run.working_directory", value)

    def set_default(self, name: str, default_value: Any) -> None:
        """Registers a new option.
        
        If the name contains a period, then the part left to the (first) period
        will become the section of the option and rest will become name under that 
        section.
        
        If the name doesn't contain a period, then it will be added under section 
        "general".
        """
        self._configuration_manager.set_default(name, default_value)

    def get_variable(self, name: str) -> tk.Variable:
        return self._configuration_manager.get_variable(name)

    def get_menu(self, name: str, label: Optional[str] = None) -> tk.Menu:
        """Gives the menu with given name. Creates if not created yet.
        
        Args:
            name: meant to be used as not translatable menu name
            label: translated label, used only when menu with given name doesn't exist yet
        """
        if name not in self._menus:
            menu = tk.Menu(self._menubar, **get_style_configuration("Menu"))
            menu["postcommand"] = lambda: self._update_menu(menu, name)
            self._menubar.add_cascade(label=label if label else name, menu=menu)

            self._menus[name] = menu
            if label:
                self._menus[label] = menu

        return self._menus[name]

    def get_view(self, view_id: str, create: bool = True) -> tk.Widget:
        if "instance" not in self._view_records[view_id]:
            if not create:
                raise RuntimeError("View %s not created" % view_id)
            class_ = self._view_records[view_id]["class"]
            location = self._view_records[view_id]["location"]
            master = self._view_notebooks[location]

            # create the view
            view = class_(
                self
            )  # View's master is workbench to allow making it maximized
            view.position_key = self._view_records[view_id]["position_key"]
            self._view_records[view_id]["instance"] = view

            # create the view home_widget to be added into notebook
            view.home_widget = ttk.Frame(master)
            view.home_widget.columnconfigure(0, weight=1)
            view.home_widget.rowconfigure(0, weight=1)
            view.home_widget.maximizable_widget = view  # type: ignore
            view.home_widget.close = lambda: self.hide_view(view_id)  # type: ignore
            if hasattr(view, "position_key"):
                view.home_widget.position_key = view.position_key  # type: ignore

            # initially the view will be in it's home_widget
            view.grid(row=0, column=0, sticky=tk.NSEW, in_=view.home_widget)
            view.hidden = True

        return self._view_records[view_id]["instance"]

    def get_editor_notebook(self) -> EditorNotebook:
        assert self._editor_notebook is not None
        return self._editor_notebook

    def get_package_dir(self):
        """Returns thonny package directory"""
        return os.path.dirname(sys.modules["thonny"].__file__)

    def get_image(self, filename: str, tk_name: Optional[str] = None) -> tk.PhotoImage:

        if filename in self._image_mapping_by_theme[self._current_theme_name]:
            filename = self._image_mapping_by_theme[self._current_theme_name][filename]

        if filename in self._default_image_mapping:
            filename = self._default_image_mapping[filename]

        # if path is relative then interpret it as living in res folder
        if not os.path.isabs(filename):
            filename = os.path.join(self.get_package_dir(), "res", filename)
            if not os.path.exists(filename):
                if os.path.exists(filename + ".png"):
                    filename = filename + ".png"
                elif os.path.exists(filename + ".gif"):
                    filename = filename + ".gif"

        # are there platform-specific variants?
        plat_filename = filename[:-4] + "_" + platform.system() + ".png"
        if os.path.exists(plat_filename):
            filename = plat_filename

        if self._scaling_factor >= 2.0:
            scaled_filename = filename[:-4] + "_2x.png"
            if os.path.exists(scaled_filename):
                filename = scaled_filename
            else:
                img = tk.PhotoImage(file=filename)
                # can't use zoom method, because this doesn't allow name
                img2 = tk.PhotoImage(tk_name)
                self.tk.call(
                    img2,
                    "copy",
                    img.name,
                    "-zoom",
                    int(self._scaling_factor),
                    int(self._scaling_factor),
                )
                self._images.add(img2)
                return img2

        img = tk.PhotoImage(tk_name, file=filename)
        self._images.add(img)
        return img

    def show_view(self, view_id: str, set_focus: bool = True) -> Union[bool, tk.Widget]:
        """View must be already registered.
        
        Args:
            view_id: View class name 
            without package name (eg. 'ShellView') """

        # NB! Don't forget that view.home_widget is added to notebook, not view directly
        # get or create
        view = self.get_view(view_id)
        notebook = view.home_widget.master  # type: ignore

        if hasattr(view, "before_show") and view.before_show() == False:  # type: ignore
            return False

        if view.hidden:  # type: ignore
            notebook.insert(
                "auto",
                view.home_widget,  # type: ignore
                text=self._view_records[view_id]["label"],
            )
            view.hidden = False  # type: ignore

        # switch to the tab
        notebook.select(view.home_widget)  # type: ignore

        # add focus
        if set_focus:
            view.focus_set()

        self.set_option("view." + view_id + ".visible", True)
        self.event_generate("ShowView", view=view, view_id=view_id)
        return view

    def hide_view(self, view_id: str) -> Union[bool, None]:
        # NB! Don't forget that view.home_widget is added to notebook, not view directly

        if "instance" in self._view_records[view_id]:
            # TODO: handle the case, when view is maximized
            view = self._view_records[view_id]["instance"]
            if view.hidden:
                return

            if hasattr(view, "before_hide") and view.before_hide() == False:
                return False

            view.home_widget.master.forget(view.home_widget)
            self.set_option("view." + view_id + ".visible", False)

            self.event_generate("HideView", view=view, view_id=view_id)
            view.hidden = True

        return None

    def event_generate(
        self, sequence: str, event: Optional[Record] = None, **kwargs
    ) -> None:
        """Uses custom event handling when sequence doesn't start with <.
        In this case arbitrary attributes can be added to the event.
        Otherwise forwards the call to Tk's event_generate"""
        # pylint: disable=arguments-differ
        if sequence.startswith("<"):
            assert event is None
            tk.Tk.event_generate(self, sequence, **kwargs)
        else:
            if sequence in self._event_handlers:
                if event is None:
                    event = WorkbenchEvent(sequence, **kwargs)
                else:
                    event.update(kwargs)

                # make a copy of handlers, so that event handler can remove itself
                # from the registry during iteration
                # (or new handlers can be added)
                for handler in sorted(self._event_handlers[sequence].copy(), key=str):
                    try:
                        handler(event)
                    except Exception:
                        self.report_exception(
                            "Problem when handling '" + sequence + "'"
                        )

        self._update_toolbar()

    def bind(
        self, sequence: str, func: Callable, add: bool = None
    ) -> None:  # type: ignore
        """Uses custom event handling when sequence doesn't start with <.
        Otherwise forwards the call to Tk's bind"""
        # pylint: disable=signature-differs

        if not add:
            logging.warning(
                "Workbench.bind({}, ..., add={}) -- did you really want to replace existing bindings?".format(
                    sequence, add
                )
            )

        if sequence.startswith("<"):
            tk.Tk.bind(self, sequence, func, add)
        else:
            if sequence not in self._event_handlers or not add:
                self._event_handlers[sequence] = set()

            self._event_handlers[sequence].add(func)

    def unbind(self, sequence: str, funcid=None) -> None:
        if sequence.startswith("<"):
            tk.Tk.unbind(self, sequence, funcid=funcid)
        else:
            try:
                self._event_handlers[sequence].remove(funcid)
            except Exception:
                logging.getLogger("thonny").exception(
                    "Can't remove binding for '%s' and '%s'", sequence, funcid
                )

    def in_heap_mode(self) -> bool:
        # TODO: add a separate command for enabling the heap mode
        # untie the mode from HeapView

        return self._configuration_manager.has_option(
            "view.HeapView.visible"
        ) and self.get_option("view.HeapView.visible")

    def in_debug_mode(self) -> bool:
        return os.environ.get("THONNY_DEBUG", False) in [
            "1",
            1,
            "True",
            True,
            "true",
        ] or self.get_option("general.debug_mode", False)

    def _init_scaling(self) -> None:
        self._default_scaling_factor = self.tk.call("tk", "scaling")

        scaling = self.get_option("general.scaling")
        if scaling in ["default", "auto"]:  # auto was used in 2.2b3
            self._scaling_factor = self._default_scaling_factor
        else:
            self._scaling_factor = float(scaling)

        if running_on_mac_os():
            self._scaling_factor *= 1.7

        self.tk.call("tk", "scaling", self._scaling_factor)

        if running_on_linux() and scaling not in ["default", "auto"]:
            # update system fonts which are given in pixel sizes
            for name in tk_font.names():
                f = tk_font.nametofont(name)
                orig_size = f.cget("size")
                if orig_size < 0:
                    # meaning its absolute value means height in pixels
                    f.configure(
                        size=int(
                            orig_size
                            * (self._scaling_factor / self._default_scaling_factor)
                        )
                    )
        elif running_on_mac_os() and scaling not in ["default", "auto"]:
            # TODO: see http://wiki.tcl.tk/44444
            # update system fonts
            for name in tk_font.names():
                f = tk_font.nametofont(name)
                orig_size = f.cget("size")
                assert orig_size > 0
                f.configure(size=int(orig_size * self._scaling_factor / 1.7))

    def update_fonts(self) -> None:
        editor_font_size = self._guard_font_size(
            self.get_option("view.editor_font_size")
        )
        editor_font_family = self.get_option("view.editor_font_family")
        io_font_family = self.get_option("view.io_font_family")

        tk_font.nametofont("IOFont").configure(
            family=io_font_family,
            size=min(editor_font_size - 2, int(editor_font_size * 0.8 + 3)),
        )
        tk_font.nametofont("EditorFont").configure(
            family=editor_font_family, size=editor_font_size
        )
        tk_font.nametofont("SmallEditorFont").configure(
            family=editor_font_family, size=editor_font_size - 2
        )
        tk_font.nametofont("BoldEditorFont").configure(
            family=editor_font_family, size=editor_font_size
        )
        tk_font.nametofont("ItalicEditorFont").configure(
            family=editor_font_family, size=editor_font_size
        )
        tk_font.nametofont("BoldItalicEditorFont").configure(
            family=editor_font_family, size=editor_font_size
        )

        style = ttk.Style()
        if running_on_mac_os():
            treeview_font_size = int(editor_font_size * 0.7 + 4)
            rowheight = int(treeview_font_size * 1.2 + self.scale(4))
        else:
            treeview_font_size = int(editor_font_size * 0.7 + 2)
            rowheight = int(treeview_font_size * 2.5 + self.scale(3))

        tk_font.nametofont("TreeviewFont").configure(size=treeview_font_size)
        style.configure("Treeview", rowheight=rowheight)

        if self._editor_notebook is not None:
            self._editor_notebook.update_appearance()

    def _get_menu_index(self, menu: tk.Menu) -> int:
        for i in range(len(self._menubar.winfo_children())):
            if menu == self._menubar.winfo_children()[i]:
                return i

        raise RuntimeError("Couldn't find menu")

    def _add_toolbar_button(
        self,
        image: Optional[tk.PhotoImage],
        command_label: str,
        caption: str,
        accelerator: Optional[str],
        handler: Callable[[], None],
        tester: Optional[Callable[[], bool]],
        toolbar_group: int,
    ) -> None:

        assert caption is not None and len(caption) > 0, (
            "Missing caption for '%s'. Toolbar commands must have caption."
            % command_label
        )
        slaves = self._toolbar.grid_slaves(0, toolbar_group)
        if len(slaves) == 0:
            group_frame = ttk.Frame(self._toolbar)
            if self.get_ui_mode() == "simple":
                padx = 0  # type: Union[int, Tuple[int, int]]
            else:
                padx = (0, 10)
            group_frame.grid(row=0, column=toolbar_group, padx=padx)
        else:
            group_frame = slaves[0]

        button = ttk.Button(
            group_frame,
            command=handler,
            image=image,
            style="Toolbutton",
            state=tk.NORMAL,
            text=caption,
            compound="top" if self.get_ui_mode() == "simple" else None,
            pad=(10, 0) if self.get_ui_mode() == "simple" else None,
        )
        button.pack(side=tk.LEFT)
        button.tester = tester  # type: ignore
        tooltip_text = command_label
        if self.get_ui_mode() != "simple":
            if accelerator and lookup_style_option(
                "OPTIONS", "shortcuts_in_tooltips", default=True
            ):
                tooltip_text += " (" + accelerator + ")"
            create_tooltip(button, tooltip_text)

    def _update_toolbar(self) -> None:
        if self._destroyed or not hasattr(self, "_toolbar"):
            return

        if self._toolbar.winfo_ismapped():
            for group_frame in self._toolbar.grid_slaves(0):
                for button in group_frame.pack_slaves():
                    if thonny._runner is None or button.tester and not button.tester():
                        button["state"] = tk.DISABLED
                    else:
                        button["state"] = tk.NORMAL

    def _cmd_zoom_with_mouse(self, event) -> None:
        if event.delta > 0:
            self._change_font_size(1)
        else:
            self._change_font_size(-1)

    def _change_font_size(self, delta: int) -> None:

        if delta != 0:
            editor_font_size = self.get_option("view.editor_font_size")
            editor_font_size += delta
            self.set_option(
                "view.editor_font_size", self._guard_font_size(editor_font_size)
            )
            self.update_fonts()

    def _guard_font_size(self, size: int) -> int:
        # https://bitbucket.org/plas/thonny/issues/164/negative-font-size-crashes-thonny
        MIN_SIZE = 4
        MAX_SIZE = 200
        if size < MIN_SIZE:
            return MIN_SIZE
        elif size > MAX_SIZE:
            return MAX_SIZE
        else:
            return size

    def _check_update_window_width(self, delta: int) -> None:
        if not ui_utils.get_zoomed(self):
            self.update_idletasks()
            # TODO: shift to left if right edge goes away from screen
            # TODO: check with screen width
            new_geometry = "{0}x{1}+{2}+{3}".format(
                self.winfo_width() + delta,
                self.winfo_height(),
                self.winfo_x(),
                self.winfo_y(),
            )

            self.geometry(new_geometry)

    def _maximize_view(self, event=None) -> None:
        if self._maximized_view is not None:
            return

        # find the widget that can be relocated
        widget = self.focus_get()
        if isinstance(widget, (EditorNotebook, AutomaticNotebook)):
            current_tab = widget.get_current_child()
            if current_tab is None:
                return

            if not hasattr(current_tab, "maximizable_widget"):
                return

            widget = current_tab.maximizable_widget

        while widget is not None:
            if hasattr(widget, "home_widget"):
                # if widget is view, then widget.master is workbench
                widget.grid(
                    row=1, column=0, sticky=tk.NSEW, in_=widget.master  # type: ignore
                )
                # hide main_frame
                self._main_frame.grid_forget()
                self._maximized_view = widget
                self.get_variable("view.maximize_view").set(True)
                break
            else:
                widget = widget.master  # type: ignore

    def _unmaximize_view(self, event=None) -> None:
        if self._maximized_view is None:
            return

        # restore main_frame
        self._main_frame.grid(row=1, column=0, sticky=tk.NSEW, in_=self)
        # put the maximized view back to its home_widget
        self._maximized_view.grid(
            row=0,
            column=0,
            sticky=tk.NSEW,
            in_=self._maximized_view.home_widget,  # type: ignore
        )
        self._maximized_view = None
        self.get_variable("view.maximize_view").set(False)

    def _cmd_show_options(self) -> None:
        dlg = ConfigurationDialog(self, self._configuration_pages)
        ui_utils.show_dialog(dlg)

    def _cmd_focus_editor(self) -> None:
        self.get_editor_notebook().focus_set()

    def _cmd_focus_shell(self) -> None:
        self.show_view("ShellView", True)

    def _cmd_toggle_full_screen(self) -> None:
        """
        TODO: For mac 
        http://wiki.tcl.tk/44444
        
        Switching a window to fullscreen mode
        (Normal Difference)
        To switch a window to fullscreen mode, the window must first be withdrawn.
              # For Linux/Mac OS X:
        
              set cfs [wm attributes $w -fullscreen]
              if { $::tcl_platform(os) eq "Darwin" } {
                if { $cfs == 0 } {
                  # optional: save the window geometry
                  set savevar [wm geometry $w]
                }
                wm withdraw $w
              }
              wm attributes $w -fullscreen [expr {1-$cfs}]
              if { $::tcl_platform(os) eq "Darwin" } {
                wm deiconify $w
                if { $cfs == 1 } {
                  after idle [list wm geometry $w $savevar]
                }
              }
        
        """
        var = self.get_variable("view.full_screen")
        var.set(not var.get())
        self.attributes("-fullscreen", var.get())

    def _cmd_toggle_maximize_view(self) -> None:
        if self._maximized_view is not None:
            self._unmaximize_view()
        else:
            self._maximize_view()

    def _update_menu(self, menu: tk.Menu, menu_name: str) -> None:
        if menu.index("end") is None:
            return

        for i in range(menu.index("end") + 1):
            item_data = menu.entryconfigure(i)
            if "label" in item_data:
                command_label = menu.entrycget(i, "label")
                if (menu_name, command_label) not in self._menu_item_specs:
                    continue
                tester = self._menu_item_specs[(menu_name, command_label)].tester

                if tester and not tester():
                    menu.entryconfigure(i, state=tk.DISABLED)
                else:
                    menu.entryconfigure(i, state=tk.NORMAL)

    def _find_location_for_menu_item(
        self, menu_name: str, command_label: str
    ) -> Union[str, int]:

        menu = self.get_menu(menu_name)

        if menu.index("end") == None:  # menu is empty
            return "end"

        specs = self._menu_item_specs[(menu_name, command_label)]

        this_group_exists = False
        for i in range(0, menu.index("end") + 1):
            data = menu.entryconfigure(i)
            if "label" in data:
                # it's a command, not separator
                sibling_label = menu.entrycget(i, "label")
                sibling_group = self._menu_item_specs[(menu_name, sibling_label)].group

                if sibling_group == specs.group:
                    this_group_exists = True
                    if (
                        specs.position_in_group == "alphabetic"
                        and sibling_label > command_label
                    ):
                        return i

                if sibling_group > specs.group:
                    assert (
                        not this_group_exists
                    )  # otherwise we would have found the ending separator
                    menu.insert_separator(i)
                    return i
            else:
                # We found a separator
                if this_group_exists:
                    # it must be the ending separator for this group
                    return i

        # no group was bigger, ie. this should go to the end
        if not this_group_exists:
            menu.add_separator()

        return "end"

    def _handle_socket_request(self, client_socket: socket.socket) -> None:
        """runs in separate thread"""
        # read the request
        data = bytes()
        while True:
            new_data = client_socket.recv(1024)
            if len(new_data) > 0:
                data += new_data
            else:
                break

        self._requests_from_socket.put(data)

        # respond OK
        client_socket.sendall(SERVER_SUCCESS.encode(encoding="utf-8"))
        client_socket.shutdown(socket.SHUT_WR)
        logging.debug("AFTER NEW REQUEST %s", client_socket)

    def _poll_socket_requests(self) -> None:
        """runs in gui thread"""
        try:
            while not self._requests_from_socket.empty():
                data = self._requests_from_socket.get()
                args = ast.literal_eval(data.decode("UTF-8"))
                assert isinstance(args, list)
                for filename in args:
                    if os.path.isfile(filename):
                        self.get_editor_notebook().show_file(filename)

                self.become_active_window()
        finally:
            self.after(50, self._poll_socket_requests)

    def _on_close(self) -> None:
        if not self.get_editor_notebook().check_allow_closing():
            return

        try:
            self._save_layout()
            self._editor_notebook.remember_open_files()
            self._configuration_manager.save()
            self.event_generate("WorkbenchClose")
        except Exception:
            self.report_exception()

        self.destroy()
        self._destroyed = True

    def _on_all_key_presses(self, event):
        if running_on_windows():
            ui_utils.handle_mistreated_latin_shortcuts(self._latin_shortcuts, event)

    def _on_focus_in(self, event):
        for editor in self.get_editor_notebook().get_all_editors():
            editor.check_for_external_changes()

    def focus_get(self) -> Optional[tk.Widget]:
        try:
            return tk.Tk.focus_get(self)
        except Exception:
            # This may give error in Ubuntu
            return None

    def destroy(self) -> None:
        try:
            self._destroying = True
            
            # Tk clipboard gets cleared on exit and won't end up in system clipboard
            # https://bugs.python.org/issue1207592
            # https://stackoverflow.com/questions/26321333/tkinter-in-python-3-4-on-windows-dont-post-internal-clipboard-data-to-the-windo
            try:
                clipboard_data = self.clipboard_get()
                if all(map(os.path.exists, clipboard_data.splitlines())):
                    # Looks like the clipboard contains file name(s)
                    # Most likely this means actual file cut/copy operation
                    # was made outside of Thonny.
                    # Don't want to replace this with simple string data of file names.
                    pass
                else:
                    import pyperclip
                    pyperclip.copy(clipboard_data)
            except Exception:
                pass
                
            tk.Tk.destroy(self)
        except tk.TclError:
            logging.exception("Error while destroying workbench")
        finally:
            runner = get_runner()
            if runner != None:
                runner.destroy_backend()

    def _on_configure(self, event) -> None:
        # called when window is moved or resized
        if (
            hasattr(
                self, "_maximized_view"
            )  # configure may happen before the attribute is defined
            and self._maximized_view  # type: ignore
        ):
            # grid again, otherwise it acts weird
            self._maximized_view.grid(
                row=1,
                column=0,
                sticky=tk.NSEW,
                in_=self._maximized_view.master,  # type: ignore
            )

    def _on_tk_exception(self, exc, val, tb) -> None:
        # copied from tkinter.Tk.report_callback_exception with modifications
        # see http://bugs.python.org/issue22384
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        self.report_exception()

    def report_exception(self, title: str = "Internal error") -> None:
        logging.exception(title)
        if tk._default_root and not self._destroying:  # type: ignore
            (typ, value, _) = sys.exc_info()
            assert typ is not None
            if issubclass(typ, UserError):
                msg = str(value)
            else:
                msg = traceback.format_exc()
            
            dlg = ui_utils.LongTextDialog(title, msg, parent=self)
            ui_utils.show_dialog(dlg, self)

    def _open_views(self) -> None:
        for nb_name in self._view_notebooks:
            view_name = self.get_option("layout.notebook_" + nb_name + "_visible_view")
            if view_name != None:
                if view_name == "GlobalsView":
                    # was renamed in 2.2b5
                    view_name = "VariablesView"
                
                if self.get_ui_mode() != "simple" or view_name in SIMPLE_MODE_VIEWS:
                    self.show_view(view_name)

        # make sure VariablesView is at least loaded
        # otherwise it may miss globals events
        # and will show empty table on open
        self.get_view("VariablesView")

        if ((self.get_option("assistance.open_assistant_on_errors") 
            or self.get_option("assistance.open_assistant_on_warnings"))
            and 
            (self.get_ui_mode() != "simple" or "AssistantView" in SIMPLE_MODE_VIEWS)):
            self.get_view("AssistantView")

    def _save_layout(self) -> None:
        self.update_idletasks()
        self.set_option("layout.zoomed", ui_utils.get_zoomed(self))

        for nb_name in self._view_notebooks:
            widget = self._view_notebooks[nb_name].get_visible_child()
            if hasattr(widget, "maximizable_widget"):
                view = widget.maximizable_widget
                view_name = type(view).__name__
                self.set_option(
                    "layout.notebook_" + nb_name + "_visible_view", view_name
                )
            else:
                self.set_option("layout.notebook_" + nb_name + "_visible_view", None)

        if not ui_utils.get_zoomed(self) or running_on_mac_os():
            # can't restore zoom on mac without setting actual dimensions
            self.set_option("layout.top", self.winfo_y())
            self.set_option("layout.left", self.winfo_x())
            self.set_option("layout.width", self.winfo_width())
            self.set_option("layout.height", self.winfo_height())

        self.set_option("layout.west_pw_width", self._west_pw.preferred_size_in_pw)
        self.set_option("layout.east_pw_width", self._east_pw.preferred_size_in_pw)
        for key in ["nw", "sw", "s", "se", "ne"]:
            self.set_option(
                "layout.%s_nb_height" % key,
                self._view_notebooks[key].preferred_size_in_pw,
            )

    def update_title(self, event=None) -> None:
        editor = self.get_editor_notebook().get_current_editor()
        title_text = "Thonny"
        if editor != None:
            title_text += "  -  " + editor.get_long_description()

        self.title(title_text)

    def become_active_window(self, force=True) -> None:
        # Looks like at least on Windows all following is required
        # for ensuring the window gets focus
        # (deiconify, ..., iconify, deiconify)
        self.deiconify()

        if force:
            self.attributes("-topmost", True)
            self.after_idle(self.attributes, "-topmost", False)
            self.lift()

            if not running_on_linux():
                # http://stackoverflow.com/a/13867710/261181
                self.iconify()
                self.deiconify()

        editor = self.get_editor_notebook().get_current_editor()
        if editor is not None:
            # This method is meant to be called when new file is opened, so it's safe to
            # send the focus to the editor
            editor.focus_set()
        else:
            self.focus_set()

    def open_url(self, url):
        m = re.match(r"^thonny-editor://(.*?)(#(\d+)(:(\d+))?)?$", url)
        if m is not None:
            filename = m.group(1).replace("%20", " ")
            lineno = None if m.group(3) is None else int(m.group(3))
            col_offset = None if m.group(5) is None else int(m.group(5))
            if lineno is None:
                self.get_editor_notebook().show_file(filename)
            else:
                self.get_editor_notebook().show_file_at_line(
                    filename, lineno, col_offset
                )

            return

        m = re.match(r"^thonny-help://(.*?)(#(.+))?$", url)
        if m is not None:
            topic = m.group(1)
            fragment = m.group(3)
            self.show_view("HelpView").load_topic(topic, fragment)
            return
        
        if url.endswith(".rst") and not url.startswith("http"):
            parts = url.split("#", maxsplit=1)
            topic = parts[0][:-4]
            if len(parts) == 2:
                fragment = parts[1]
            else:
                fragment = None
                
            self.show_view("HelpView").load_topic(topic, fragment)
            return

        # Fallback
        webbrowser.open(url, False, True)

    def bell(self, displayof=0):
        if not self.get_option("general.disable_notification_sound"):
            super().bell(displayof=displayof)

    def _mac_quit(self, *args):
        self._on_close()


class WorkbenchEvent(Record):
    def __init__(self, sequence: str, **kwargs) -> None:
        Record.__init__(self, **kwargs)
        self.sequence = sequence
