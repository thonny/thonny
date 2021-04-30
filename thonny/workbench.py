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
import shutil
import socket
import sys
import tkinter as tk
import tkinter.font as tk_font
import traceback
from threading import Thread
from tkinter import messagebox, ttk
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, Union, cast
from warnings import warn

import thonny
from thonny import (
    THONNY_USER_DIR,
    assistance,
    get_runner,
    get_shell,
    is_portable,
    languages,
    running,
    ui_utils,
)
from thonny.common import Record, UserError, normpath_with_actual_case
from thonny.config import try_load_configuration
from thonny.config_ui import ConfigurationDialog
from thonny.editors import EditorNotebook
from thonny.languages import tr
from thonny.misc_utils import (
    copy_to_clipboard,
    running_on_linux,
    running_on_mac_os,
    running_on_rpi,
    running_on_windows,
)
from thonny.plugins.microbit import MicrobitFlashingDialog
from thonny.plugins.micropython.uf2dialog import Uf2FlashingDialog
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
    caps_lock_is_on,
    shift_is_pressed,
    ems_to_pixels,
)

logger = logging.getLogger(__name__)

SERVER_SUCCESS = "OK"
SIMPLE_MODE_VIEWS = ["ShellView"]

MenuItem = collections.namedtuple("MenuItem", ["group", "position_in_group", "tester"])
BackendSpec = collections.namedtuple(
    "BackendSpec", ["name", "proxy_class", "description", "config_page_constructor", "sort_key"]
)

BasicUiThemeSettings = Dict[str, Dict[str, Union[Dict, Sequence]]]
CompoundUiThemeSettings = List[BasicUiThemeSettings]
UiThemeSettings = Union[BasicUiThemeSettings, CompoundUiThemeSettings]
FlexibleUiThemeSettings = Union[UiThemeSettings, Callable[[], UiThemeSettings]]

SyntaxThemeSettings = Dict[str, Dict[str, Union[str, int, bool]]]
FlexibleSyntaxThemeSettings = Union[SyntaxThemeSettings, Callable[[], SyntaxThemeSettings]]

OBSOLETE_PLUGINS = [
    "thonnycontrib.pi",
    "thonnycontrib.micropython",
    "thonnycontrib.circuitpython",
    "thonnycontrib.microbit",
    "thonnycontrib.esp",
    "thonnycontrib.rpi_pico",
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

    def __init__(self) -> None:
        thonny._workbench = self
        self.ready = False
        self._closing = False
        self._destroyed = False
        self._lost_focus = False
        self._is_portable = is_portable()
        self.initializing = True

        self._init_configuration()
        self._tweak_environment()
        self._check_init_server_loop()

        tk.Tk.__init__(self, className="Thonny")
        tk.Tk.report_callback_exception = self._on_tk_exception  # type: ignore
        ui_utils.add_messagebox_parent_checker()
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
        self._toolbar_buttons = {}
        self._view_records = {}  # type: Dict[str, Dict[str, Any]]
        self.content_inspector_classes = []  # type: List[Type]
        self._latin_shortcuts = {}  # type: Dict[Tuple[int,int], List[Tuple[Callable, Callable]]]

        self._init_language()

        self._active_ui_mode = os.environ.get("THONNY_MODE", self.get_option("general.ui_mode"))

        self._init_scaling()

        self._init_theming()
        self._init_window()
        self.option_add("*Dialog.msg.wrapLength", "8i")

        self.add_view(
            ShellView, tr("Shell"), "s", visible_by_default=True, default_position_key="A"
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
        # self._init_backend_switcher()
        self._init_regular_mode_link()  # TODO:

        self._show_views()
        # Make sure ShellView is loaded
        get_shell()

        self._init_commands()
        self._init_icon()
        try:
            self._editor_notebook.load_startup_files()
        except Exception:
            self.report_exception()

        self._editor_notebook.focus_set()
        self._try_action(self._open_views)

        self.bind_class("CodeViewText", "<<CursorMove>>", self.update_title, True)
        self.bind_class("CodeViewText", "<<Modified>>", self.update_title, True)
        self.bind_class("CodeViewText", "<<TextChange>>", self.update_title, True)
        self.get_editor_notebook().bind("<<NotebookTabChanged>>", self.update_title, True)
        self.get_editor_notebook().bind("<<NotebookTabChanged>>", self._update_toolbar, True)
        self.bind_all("<KeyPress>", self._on_all_key_presses, True)
        self.bind("<FocusOut>", self._on_focus_out, True)
        self.bind("<FocusIn>", self._on_focus_in, True)
        self.bind("BackendRestart", self._on_backend_restart, True)

        self._publish_commands()
        self.initializing = False
        self.event_generate("<<WorkbenchInitialized>>")
        self._make_sanity_checks()
        if self._is_server():
            self._poll_ipc_requests()

        """
        for name in sorted(sys.modules):
            if (
                not name.startswith("_")
                and not name.startswith("thonny")
                and not name.startswith("tkinter")
            ):
                print(name)
        """

        self.after(1, self._start_runner)  # Show UI already before waiting for the backend to start
        self.after_idle(self.advertise_ready)

    def advertise_ready(self):
        self.event_generate("WorkbenchReady")
        self.ready = True

    def _make_sanity_checks(self):
        home_dir = os.path.expanduser("~")
        bad_home_msg = None
        if home_dir == "~":
            bad_home_msg = "Can not find your home directory."
        elif not os.path.exists(home_dir):
            bad_home_msg = "Reported home directory (%s) does not exist." % home_dir
        if bad_home_msg:
            messagebox.showwarning(
                "Problems with home directory",
                bad_home_msg + "\nThis may cause problems for Thonny.",
                master=self,
            )

    def _try_action(self, action: Callable) -> None:
        try:
            action()
        except Exception:
            self.report_exception()

    def _init_configuration(self) -> None:
        self._configuration_manager = try_load_configuration(thonny.CONFIGURATION_FILE)
        self._configuration_pages = []  # type: List[Tuple[str, str, Type[tk.Widget]]]

        self.set_default("general.single_instance", thonny.SINGLE_INSTANCE_DEFAULT)
        self.set_default("general.ui_mode", "simple" if running_on_rpi() else "regular")
        self.set_default("general.debug_mode", False)
        self.set_default("general.disable_notification_sound", False)
        self.set_default("general.scaling", "default")
        self.set_default("general.language", languages.BASE_LANGUAGE_CODE)
        self.set_default("general.font_scaling_mode", "default")
        self.set_default("general.environment", [])
        self.set_default("file.avoid_zenity", False)
        self.set_default("run.working_directory", os.path.expanduser("~"))
        self.update_debug_mode()

    def _tweak_environment(self):
        for entry in self.get_option("general.environment"):
            if "=" in entry:
                key, val = entry.split("=", maxsplit=1)
                os.environ[key] = os.path.expandvars(val)
            else:
                logger.warning("No '=' in environment entry '%s'", entry)

    def update_debug_mode(self):
        os.environ["THONNY_DEBUG"] = str(self.get_option("general.debug_mode", False))
        thonny.set_logging_level()

    def _init_language(self) -> None:
        """Initialize language."""
        languages.set_language(self.get_option("general.language"))

    def _init_window(self) -> None:
        self.title("Thonny")

        self.set_default("layout.zoomed", False)
        self.set_default("layout.top", 15)
        self.set_default("layout.left", 150)
        if self.in_simple_mode():
            self.set_default("layout.width", 1050)
            self.set_default("layout.height", 700)
        else:
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
                min(max(self.get_option("layout.width"), 320), self.winfo_screenwidth()),
                min(max(self.get_option("layout.height"), 240), self.winfo_screenheight()),
                min(max(self.get_option("layout.left"), 0), self.winfo_screenwidth() - 200),
                min(max(self.get_option("layout.top"), 0), self.winfo_screenheight() - 200),
            )
        )

        if self.get_option("layout.zoomed"):
            ui_utils.set_zoomed(self, True)

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.bind("<Configure>", self._on_configure, True)

    def _init_statusbar(self):
        self._statusbar = ttk.Frame(self)

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
        self.get_menu("file", tr("File"))
        self.get_menu("edit", tr("Edit"))
        self.get_menu("view", tr("View"))
        self.get_menu("run", tr("Run"))
        self.get_menu("tools", tr("Tools"))
        self.get_menu("help", tr("Help"))

    def _load_plugins(self) -> None:
        # built-in plugins
        import thonny.plugins  # pylint: disable=redefined-outer-name

        self._load_plugins_from_path(thonny.plugins.__path__, "thonny.plugins.")  # type: ignore

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

        modules = []
        for _, module_name, _ in sorted(pkgutil.iter_modules(path, prefix), key=lambda x: x[2]):
            if module_name in OBSOLETE_PLUGINS:
                logging.debug("Skipping plug-in %s", module_name)
            else:
                try:
                    m = importlib.import_module(module_name)
                    if hasattr(m, load_function_name):
                        modules.append(m)
                except Exception:
                    logging.exception("Failed loading plugin '" + module_name + "'")

        def module_sort_key(m):
            return getattr(m, "load_order_key", m.__name__)

        for m in sorted(modules, key=module_sort_key):
            getattr(m, load_function_name)()

    def _init_fonts(self) -> None:
        # set up editor and shell fonts
        self.set_default("view.io_font_family", "Courier" if running_on_mac_os() else "Courier New")

        default_editor_family = "Courier New"
        families = tk_font.families()

        for family in ["Consolas", "Ubuntu Mono", "Menlo", "DejaVu Sans Mono"]:
            if family in families:
                default_editor_family = family
                break

        self.set_default("view.editor_font_family", default_editor_family)

        if running_on_mac_os():
            self.set_default("view.editor_font_size", 14)
            self.set_default("view.io_font_size", 12)
        elif self.in_simple_mode():
            self.set_default("view.editor_font_size", 12)
            self.set_default("view.io_font_size", 12)
        else:
            self.set_default("view.editor_font_size", 13)
            self.set_default("view.io_font_size", 11)

        default_font = tk_font.nametofont("TkDefaultFont")

        if running_on_linux():
            heading_font = tk_font.nametofont("TkHeadingFont")
            heading_font.configure(weight="normal")
            caption_font = tk_font.nametofont("TkCaptionFont")
            caption_font.configure(weight="normal", size=default_font.cget("size"))

        small_link_ratio = 0.8 if running_on_windows() else 0.7
        self._fonts = [
            tk_font.Font(
                name="SmallLinkFont",
                family=default_font.cget("family"),
                size=int(default_font.cget("size") * small_link_ratio),
                underline=True,
            ),
            tk_font.Font(name="IOFont", family=self.get_option("view.io_font_family")),
            tk_font.Font(
                name="BoldIOFont", family=self.get_option("view.io_font_family"), weight="bold"
            ),
            tk_font.Font(
                name="UnderlineIOFont",
                family=self.get_option("view.io_font_family"),
                underline=True,
            ),
            tk_font.Font(
                name="ItalicIOFont", family=self.get_option("view.io_font_family"), slant="italic"
            ),
            tk_font.Font(
                name="BoldItalicIOFont",
                family=self.get_option("view.io_font_family"),
                weight="bold",
                slant="italic",
            ),
            tk_font.Font(name="EditorFont", family=self.get_option("view.editor_font_family")),
            tk_font.Font(name="SmallEditorFont", family=self.get_option("view.editor_font_family")),
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

    def _start_runner(self) -> None:
        try:
            self.update_idletasks()  # allow UI to complete
            thonny._runner = self._runner
            self._runner.start()
            self._update_toolbar()
        except Exception:
            self.report_exception("Error when initializing backend")

    def _check_init_server_loop(self) -> None:
        """Socket will listen requests from newer Thonny instances,
        which try to delegate opening files to older instance"""

        if not self.get_option("general.single_instance") or os.path.exists(
            thonny.get_ipc_file_path()
        ):
            self._ipc_requests = None
            return

        self._ipc_requests = queue.Queue()  # type: queue.Queue[bytes]
        server_socket, actual_secret = self._create_server_socket()
        server_socket.listen(10)

        def server_loop():
            while True:
                logging.debug("Waiting for next client")
                (client_socket, _) = server_socket.accept()
                try:
                    data = bytes()
                    while True:
                        new_data = client_socket.recv(1024)
                        if len(new_data) > 0:
                            data += new_data
                        else:
                            break
                    proposed_secret, args = ast.literal_eval(data.decode("UTF-8"))
                    if proposed_secret == actual_secret:
                        self._ipc_requests.put(args)
                        # respond OK
                        client_socket.sendall(SERVER_SUCCESS.encode(encoding="utf-8"))
                        client_socket.shutdown(socket.SHUT_WR)
                        logging.debug("AFTER NEW REQUEST %s", client_socket)
                    else:
                        client_socket.shutdown(socket.SHUT_WR)
                        raise PermissionError("Wrong secret")

                except Exception as e:
                    logger.exception("Error in ipc server loop", exc_info=e)

        Thread(target=server_loop, daemon=True).start()

    def _create_server_socket(self):
        if running_on_windows():
            server_socket = socket.socket(socket.AF_INET)  # @UndefinedVariable
            server_socket.bind(("127.0.0.1", 0))

            # advertise the port and secret
            port = server_socket.getsockname()[1]
            import uuid

            secret = str(uuid.uuid4())

            with open(thonny.get_ipc_file_path(), "w") as fp:
                fp.write(str(port) + "\n")
                fp.write(secret + "\n")

        else:
            server_socket = socket.socket(socket.AF_UNIX)  # @UndefinedVariable
            server_socket.bind(thonny.get_ipc_file_path())
            secret = ""

        os.chmod(thonny.get_ipc_file_path(), 0o600)
        return server_socket, secret

    def _init_commands(self) -> None:

        self.add_command(
            "exit",
            "file",
            tr("Exit"),
            self._on_close,
            default_sequence=select_sequence("<Alt-F4>", "<Command-q>", "<Control-q>"),
            extra_sequences=["<Alt-F4>"]
            if running_on_linux()
            else ["<Control-q>"]
            if running_on_windows()
            else [],
        )

        self.add_command("show_options", "tools", tr("Options..."), self.show_options, group=180)
        self.createcommand("::tk::mac::ShowPreferences", self.show_options)
        self.createcommand("::tk::mac::Quit", self._mac_quit)

        self.add_command(
            "increase_font_size",
            "view",
            tr("Increase font size"),
            lambda: self._change_font_size(1),
            default_sequence=select_sequence("<Control-plus>", "<Command-Shift-plus>"),
            extra_sequences=["<Control-KP_Add>"],
            group=60,
        )

        self.add_command(
            "decrease_font_size",
            "view",
            tr("Decrease font size"),
            lambda: self._change_font_size(-1),
            default_sequence=select_sequence("<Control-minus>", "<Command-minus>"),
            extra_sequences=["<Control-KP_Subtract>"],
            group=60,
        )

        self.bind("<Control-MouseWheel>", self._cmd_zoom_with_mouse, True)

        self.add_command(
            "focus_editor",
            "view",
            tr("Focus editor"),
            self._cmd_focus_editor,
            default_sequence=select_sequence("<Alt-e>", "<Command-Alt-e>"),
            group=70,
        )

        self.add_command(
            "focus_shell",
            "view",
            tr("Focus shell"),
            self._cmd_focus_shell,
            default_sequence=select_sequence("<Alt-s>", "<Command-Alt-s>"),
            group=70,
        )

        if self.get_ui_mode() == "expert":

            self.add_command(
                "toggle_maximize_view",
                "view",
                tr("Maximize view"),
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
                tr("Full screen"),
                self._cmd_toggle_full_screen,
                flag_name="view.full_screen",
                default_sequence=select_sequence("<F11>", "<Command-Shift-F>"),
                group=80,
            )

        if self.in_simple_mode():
            self.add_command(
                "font",
                "tools",
                tr("Change font size"),
                caption=tr("Zoom"),
                handler=self._toggle_font_size,
                image="zoom",
                include_in_toolbar=True,
            )

            self.add_command(
                "quit",
                "help",
                tr("Exit Thonny"),
                self._on_close,
                image="quit",
                caption=tr("Quit"),
                include_in_toolbar=True,
                group=101,
            )

        if thonny.in_debug_mode():
            self.bind_all("<Control-Shift-Alt-D>", self._print_state_for_debugging, True)

    def _print_state_for_debugging(self, event) -> None:
        print(get_runner()._postponed_commands)

    def _init_containers(self) -> None:

        margin = 10
        # Main frame functions as
        # - a background behind padding of main_pw, without this OS X leaves white border
        # - a container to be hidden, when a view is maximized and restored when view is back home
        main_frame = ttk.Frame(self)  #
        self._main_frame = main_frame
        main_frame.grid(row=1, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._maximized_view = None  # type: Optional[tk.Widget]

        self._toolbar = ttk.Frame(main_frame, padding=0)
        self._toolbar.grid(column=0, row=0, sticky=tk.NSEW, padx=margin, pady=(5, 0))

        self.set_default("layout.west_pw_width", self.scale(150))
        self.set_default("layout.east_pw_width", self.scale(150))

        self.set_default("layout.s_nb_height", self.scale(150))
        self.set_default("layout.nw_nb_height", self.scale(150))
        self.set_default("layout.sw_nb_height", self.scale(150))
        self.set_default("layout.ne_nb_height", self.scale(150))
        self.set_default("layout.se_nb_height", self.scale(150))

        self._main_pw = AutomaticPanedWindow(main_frame, orient=tk.HORIZONTAL)

        self._main_pw.grid(column=0, row=1, sticky=tk.NSEW, padx=margin, pady=(margin, 0))
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
                self._west_pw, 1, preferred_size_in_pw=self.get_option("layout.nw_nb_height")
            ),
            "w": AutomaticNotebook(self._west_pw, 2),
            "sw": AutomaticNotebook(
                self._west_pw, 3, preferred_size_in_pw=self.get_option("layout.sw_nb_height")
            ),
            "s": AutomaticNotebook(
                self._center_pw, 3, preferred_size_in_pw=self.get_option("layout.s_nb_height")
            ),
            "ne": AutomaticNotebook(
                self._east_pw, 1, preferred_size_in_pw=self.get_option("layout.ne_nb_height")
            ),
            "e": AutomaticNotebook(self._east_pw, 2),
            "se": AutomaticNotebook(
                self._east_pw, 3, preferred_size_in_pw=self.get_option("layout.se_nb_height")
            ),
        }

        for nb_name in self._view_notebooks:
            self.set_default("layout.notebook_" + nb_name + "_visible_view", None)

        self._editor_notebook = EditorNotebook(self._center_pw)
        self._editor_notebook.position_key = 1
        self._center_pw.insert("auto", self._editor_notebook)

        self._statusbar = ttk.Frame(main_frame)
        self._statusbar.grid(column=0, row=2, sticky="nsew", padx=margin, pady=(0))
        self._statusbar.columnconfigure(2, weight=2)
        self._status_label = ttk.Label(self._statusbar, text="")
        self._status_label.grid(row=1, column=1, sticky="w")

        self._init_backend_switcher()

    def _init_backend_switcher(self):

        # Set up the menu
        self._backend_conf_variable = tk.StringVar(value="{}")

        if running_on_mac_os():
            menu_conf = {}
        else:
            menu_conf = get_style_configuration("Menu")
        self._backend_menu = tk.Menu(self._statusbar, tearoff=False, **menu_conf)

        # Set up the button
        self._backend_button = ttk.Button(self._statusbar, text="", style="Toolbutton")

        self._backend_button.grid(row=1, column=3, sticky="e")
        self._backend_button.configure(command=self._post_backend_menu)

    def _post_backend_menu(self):
        menu_font = tk_font.nametofont("TkMenuFont")

        def choose_backend():
            backend_conf = ast.literal_eval(self._backend_conf_variable.get())
            assert isinstance(backend_conf, dict), "backend conf is %r" % backend_conf
            for name, value in backend_conf.items():
                self.set_option(name, value)
            get_runner().restart_backend(False)

        self._backend_menu.delete(0, "end")
        max_description_width = 0
        button_text_width = menu_font.measure(self._backend_button.cget("text"))

        num_entries = 0
        for backend in sorted(self.get_backends().values(), key=lambda x: x.sort_key):
            entries = backend.proxy_class.get_switcher_entries()

            if not entries:
                continue

            if len(entries) == 1:
                self._backend_menu.add_radiobutton(
                    label=backend.description,
                    command=choose_backend,
                    variable=self._backend_conf_variable,
                    value=repr(entries[0][0]),
                )
            else:
                submenu = tk.Menu(self._backend_menu, tearoff=False)
                for conf, label in entries:
                    submenu.add_radiobutton(
                        label=label,
                        command=choose_backend,
                        variable=self._backend_conf_variable,
                        value=repr(conf),
                    )
                self._backend_menu.add_cascade(label=backend.description, menu=submenu)

            max_description_width = max(
                menu_font.measure(backend.description), max_description_width
            )
        num_entries += 1

        # self._backend_conf_variable.set(value=self.get_option("run.backend_name"))

        self._backend_menu.add_separator()
        self._backend_menu.add_command(
            label=tr("Configure interpreter..."),
            command=lambda: self.show_options("interpreter"),
        )

        post_x = self._backend_button.winfo_rootx()
        post_y = (
            self._backend_button.winfo_rooty()
            - self._backend_menu.yposition("end")
            - self._backend_menu.yposition(1)
        )

        if self.winfo_screenwidth() / self.winfo_screenheight() > 2:
            # Most likely several monitors.
            # Tk will adjust x properly with single monitor, but when Thonny is maximized
            # on a monitor, which has another monitor to its right, the menu can be partially
            # displayed on another monitor (at least in Ubuntu).
            width_diff = max_description_width - button_text_width
            post_x -= width_diff + menu_font.measure("mmm")

        try:
            self._backend_menu.tk_popup(post_x, post_y)
        except tk.TclError as e:
            if not 'unknown option "-state"' in str(e):
                logger.warning("Problem with switcher popup", exc_info=e)

    def _on_backend_restart(self, event):
        proxy = get_runner().get_backend_proxy()
        if proxy:
            desc = proxy.get_clean_description()
            self._backend_conf_variable.set(value=repr(proxy.get_current_switcher_configuration()))
        else:
            backend_conf = self._backends.get(self.get_option("run.backend_name"), None)
            if backend_conf:
                desc = backend_conf.description
            else:
                desc = "<no backend>"
        self._backend_button.configure(text=desc)

    def _init_theming(self) -> None:
        self._style = ttk.Style()
        self._ui_themes = (
            {}
        )  # type: Dict[str, Tuple[Optional[str], FlexibleUiThemeSettings, Dict[str, str]]] # value is (parent, settings, images)
        self._syntax_themes = (
            {}
        )  # type: Dict[str, Tuple[Optional[str], FlexibleSyntaxThemeSettings]] # value is (parent, settings)
        self.set_default("view.ui_theme", ui_utils.get_default_theme())

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
        alternative_caption: Optional[str] = None,
        include_in_menu: bool = True,
        include_in_toolbar: bool = False,
        submenu: Optional[tk.Menu] = None,
        bell_when_denied: bool = True,
        show_extra_sequences=False,
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

        # Temporary solution for plug-ins made for versions before 3.2
        if menu_name == "device":
            menu_name = "tools"
            group = 150

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
                alternative_caption=alternative_caption,
                include_in_menu=include_in_menu,
                include_in_toolbar=include_in_toolbar,
                submenu=submenu,
                bell_when_denied=bell_when_denied,
                show_extra_sequences=show_extra_sequences,
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
        alternative_caption: Optional[str] = None,
        include_in_menu: bool = True,
        include_in_toolbar: bool = False,
        submenu: Optional[tk.Menu] = None,
        bell_when_denied: bool = True,
        show_extra_sequences: bool = False,
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

            self.event_generate("UICommandDispatched", command_id=command_id, denied=denied)

        def dispatch_if_caps_lock_is_on(event):
            if caps_lock_is_on(event.state) and not shift_is_pressed(event.state):
                dispatch(event)

        sequence_option_name = "shortcuts." + command_id
        self.set_default(sequence_option_name, default_sequence)
        sequence = self.get_option(sequence_option_name)

        if sequence:
            if not skip_sequence_binding:
                self.bind_all(sequence, dispatch, True)
                # work around caps-lock problem
                # https://github.com/thonny/thonny/issues/1347
                # Unfortunately the solution doesn't work with sequences involving Shift
                # (in Linux with the expected solution Shift sequences did not come through
                # with Caps Lock, and in Windows, the shift handlers started to react
                # on non-shift keypresses)
                # Python 3.7 on Mac seems to require lower letters for shift sequences.
                parts = sequence.strip("<>").split("-")
                if len(parts[-1]) == 1 and parts[-1].islower() and "Shift" not in parts:
                    lock_sequence = "<%s-Lock-%s>" % ("-".join(parts[:-1]), parts[-1].upper())
                    self.bind_all(lock_sequence, dispatch_if_caps_lock_is_on, True)

            # register shortcut even without binding
            register_latin_shortcut(self._latin_shortcuts, sequence, handler, tester)

        for extra_sequence in extra_sequences:
            self.bind_all(extra_sequence, dispatch, True)
            if "greek_" not in extra_sequence.lower() or running_on_linux():
                # Use greek alternatives only on Linux
                # (they are not required on Mac
                # and cause double events on Windows)
                register_latin_shortcut(self._latin_shortcuts, sequence, handler, tester)

        menu = self.get_menu(menu_name)

        if image:
            _image = self.get_image(image)  # type: Optional[tk.PhotoImage]
            _disabled_image = self.get_image(image, disabled=True)
        else:
            _image = None
            _disabled_image = None

        if not accelerator and sequence:
            accelerator = sequence_to_accelerator(sequence)
            """
            # Does not work on Mac
            if show_extra_sequences:
                for extra_seq in extra_sequences:
                    accelerator += " or " + sequence_to_accelerator(extra_seq)
            """

        if include_in_menu:

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

            if _image and lookup_style_option("OPTIONS", "icons_in_menus", True):
                menu_image = _image  # type: Optional[tk.PhotoImage]
            elif flag_name:
                # no image or black next to a checkbox
                menu_image = None
            else:
                menu_image = self.get_image("16x16-blank")

            # remember the details that can't be stored in Tkinter objects
            self._menu_item_specs[(menu_name, command_label)] = MenuItem(
                group, position_in_group, tester
            )

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
                command_id,
                _image,
                _disabled_image,
                command_label,
                caption,
                caption if alternative_caption is None else alternative_caption,
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

        if self.in_simple_mode():
            visibility_flag = tk.BooleanVar(value=view_id in SIMPLE_MODE_VIEWS)
        else:
            visibility_flag = cast(tk.BooleanVar, self.get_variable("view." + view_id + ".visible"))

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

    def add_configuration_page(
        self, key: str, title: str, page_class: Type[tk.Widget], order: int
    ) -> None:
        self._configuration_pages.append((key, title, page_class, order))

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
        proxy_class.backend_name = name  # type: ignore
        proxy_class.backend_description = description  # type: ignore
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
            warn(tr("Overwriting theme '%s'") % name)

        self._ui_themes[name] = (parent, settings, images)

    def add_syntax_theme(
        self, name: str, parent: Optional[str], settings: FlexibleSyntaxThemeSettings
    ) -> None:
        if name in self._syntax_themes:
            warn(tr("Overwriting theme '%s'") % name)

        self._syntax_themes[name] = (parent, settings)

    def get_usable_ui_theme_names(self) -> Sequence[str]:
        return sorted([name for name in self._ui_themes if self._ui_themes[name][0] is not None])

    def get_syntax_theme_names(self) -> Sequence[str]:
        return sorted(self._syntax_themes.keys())

    def get_ui_mode(self) -> str:
        return self._active_ui_mode

    def in_simple_mode(self) -> bool:
        return self.get_ui_mode() == "simple"

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
        for setting in ["background", "foreground", "selectBackground", "selectForeground"]:
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

        label = ttk.Label(frame, text=tr("Program arguments:"))
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
            tr("Program arguments"),
            toggle,
            flag_name="view.show_program_arguments",
            group=11,
        )

        update_visibility()

    def _init_regular_mode_link(self):
        if self.get_ui_mode() != "simple":
            return

        label = ttk.Label(
            self._toolbar,
            text=tr("Switch to\nregular\nmode"),
            justify="right",
            font="SmallLinkFont",
            style="Url.TLabel",
            cursor="hand2",
        )
        label.grid(row=0, column=1001, sticky="ne")

        def on_click(event):
            self.set_option("general.ui_mode", "regular")
            tk.messagebox.showinfo(
                tr("Regular mode"),
                tr(
                    "Configuration has been updated. "
                    + "Restart Thonny to start working in regular mode.\n\n"
                    + "(See 'Tools → Options → General' if you change your mind later.)"
                ),
                master=self,
            )

        label.bind("<1>", on_click, True)

    def _switch_backend_group(self, group):
        pass

    def _switch_darkness(self, mode):
        pass

    def _switch_to_regular_mode(self):
        pass

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
        """Was used by thonny-pi. Not recommended anymore"""
        self._default_image_mapping.update(mapping)

    def get_backends(self) -> Dict[str, BackendSpec]:
        return self._backends

    def get_option(self, name: str, default=None) -> Any:
        # Need to return Any, otherwise each typed call site needs to cast
        return self._configuration_manager.get_option(name, default)

    def set_option(self, name: str, value: Any) -> None:
        self._configuration_manager.set_option(name, value)

    def get_local_cwd(self) -> str:
        cwd = self.get_option("run.working_directory")
        if os.path.exists(cwd):
            return normpath_with_actual_case(cwd)
        else:
            return normpath_with_actual_case(os.path.expanduser("~"))

    def set_local_cwd(self, value: str) -> None:
        if self.get_option("run.working_directory") != value:
            self.set_option("run.working_directory", value)
            if value:
                self.event_generate("LocalWorkingDirectoryChanged", cwd=value)

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

        # For compatibility with plug-ins
        if name in ["device", "tempdevice"] and label is None:
            label = tr("Device")

        if name not in self._menus:
            if running_on_mac_os():
                conf = {}
            else:
                conf = get_style_configuration("Menu")

            menu = tk.Menu(self._menubar, **conf)
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
            view = class_(self)  # View's master is workbench to allow making it maximized
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

    def get_image(
        self, filename: str, tk_name: Optional[str] = None, disabled=False
    ) -> tk.PhotoImage:

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

        if disabled:
            filename = os.path.join(
                os.path.dirname(filename), "_disabled_" + os.path.basename(filename)
            )
            if not os.path.exists(filename):
                return None

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
            without package name (eg. 'ShellView')"""

        if view_id == "MainFileBrowser":
            # Was renamed in 3.1.1
            view_id = "FilesView"

        # NB! Don't forget that view.home_widget is added to notebook, not view directly
        # get or create
        view = self.get_view(view_id)
        notebook = view.home_widget.master  # type: ignore

        if hasattr(view, "before_show") and view.before_show() == False:  # type: ignore
            return False

        if view.hidden:  # type: ignore
            notebook.insert(
                "auto", view.home_widget, text=self._view_records[view_id]["label"]  # type: ignore
            )
            view.hidden = False  # type: ignore
            if hasattr(view, "on_show"):  # type: ignore
                view.on_show()

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
                return True

            if hasattr(view, "before_hide") and view.before_hide() == False:
                return False

            view.home_widget.master.forget(view.home_widget)
            self.set_option("view." + view_id + ".visible", False)

            self.event_generate("HideView", view=view, view_id=view_id)
            view.hidden = True

        return True

    def event_generate(self, sequence: str, event: Optional[Record] = None, **kwargs) -> None:
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
                        self.report_exception("Problem when handling '" + sequence + "'")

        if not self._closing:
            self._update_toolbar()

    def bind(self, sequence: str, func: Callable, add: bool = None) -> None:  # type: ignore
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

    def unbind(self, sequence: str, func=None) -> None:
        # pylint: disable=arguments-differ
        if sequence.startswith("<"):
            tk.Tk.unbind(self, sequence, funcid=func)
        else:
            try:
                self._event_handlers[sequence].remove(func)
            except Exception:
                logger.exception("Can't remove binding for '%s' and '%s'", sequence, func)

    def in_heap_mode(self) -> bool:
        # TODO: add a separate command for enabling the heap mode
        # untie the mode from HeapView

        return self._configuration_manager.has_option("view.HeapView.visible") and self.get_option(
            "view.HeapView.visible"
        )

    def in_debug_mode(self) -> bool:
        return (
            os.environ.get("THONNY_DEBUG", False)
            in [
                "1",
                1,
                "True",
                True,
                "true",
            ]
            or self.get_option("general.debug_mode", False)
        )

    def _init_scaling(self) -> None:
        self._default_scaling_factor = self.tk.call("tk", "scaling")
        if self._default_scaling_factor > 10:
            # it may be infinity in eg. Fedora
            self._default_scaling_factor = 1.33

        scaling = self.get_option("general.scaling")
        if scaling in ["default", "auto"]:  # auto was used in 2.2b3
            self._scaling_factor = self._default_scaling_factor
        else:
            self._scaling_factor = float(scaling)

        MAC_SCALING_MODIFIER = 1.7
        if running_on_mac_os():
            self._scaling_factor *= MAC_SCALING_MODIFIER

        self.tk.call("tk", "scaling", self._scaling_factor)

        font_scaling_mode = self.get_option("general.font_scaling_mode")

        if (
            running_on_linux()
            and font_scaling_mode in ["default", "extra"]
            and scaling not in ["default", "auto"]
        ):
            # update system fonts which are given in pixel sizes
            for name in tk_font.names():
                f = tk_font.nametofont(name)
                orig_size = f.cget("size")
                # According to do documentation, absolute values of negative font sizes
                # should be interpreted as pixel sizes (not affected by "tk scaling")
                # and positive values are point sizes, which are supposed to scale automatically
                # http://www.tcl.tk/man/tcl8.6/TkCmd/font.htm#M26

                # Unfortunately it seems that this cannot be relied on
                # https://groups.google.com/forum/#!msg/comp.lang.tcl/ZpL6tq77M4M/GXImiV2INRQJ

                # My experiments show that manually changing negative font sizes
                # doesn't have any effect -- fonts keep their default size
                # (Tested in Raspbian Stretch, Ubuntu 18.04 and Fedora 29)
                # On the other hand positive sizes scale well (and they don't scale automatically)

                # convert pixel sizes to point_size
                if orig_size < 0:
                    orig_size = -orig_size / self._default_scaling_factor

                # scale
                scaled_size = round(
                    orig_size * (self._scaling_factor / self._default_scaling_factor)
                )
                f.configure(size=scaled_size)

        elif running_on_mac_os() and scaling not in ["default", "auto"]:
            # see http://wiki.tcl.tk/44444
            # update system fonts
            for name in tk_font.names():
                f = tk_font.nametofont(name)
                orig_size = f.cget("size")
                assert orig_size > 0
                f.configure(size=int(orig_size * self._scaling_factor / MAC_SCALING_MODIFIER))

    def update_fonts(self) -> None:
        editor_font_size = self._guard_font_size(self.get_option("view.editor_font_size"))
        editor_font_family = self.get_option("view.editor_font_family")

        io_font_size = self._guard_font_size(self.get_option("view.io_font_size"))
        io_font_family = self.get_option("view.io_font_family")
        for io_name in [
            "IOFont",
            "BoldIOFont",
            "UnderlineIOFont",
            "ItalicIOFont",
            "BoldItalicIOFont",
        ]:
            tk_font.nametofont(io_name).configure(family=io_font_family, size=io_font_size)

        try:
            shell = self.get_view("ShellView", create=False)
        except Exception:
            # shell may be not created yet
            pass
        else:
            shell.update_tabs()

        tk_font.nametofont("EditorFont").configure(family=editor_font_family, size=editor_font_size)
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

        if self.get_ui_mode() == "simple":
            default_size_factor = max(0.7, 1 - (editor_font_size - 10) / 25)
            small_size_factor = max(0.6, 0.8 - (editor_font_size - 10) / 25)

            tk_font.nametofont("TkDefaultFont").configure(
                size=round(editor_font_size * default_size_factor)
            )
            tk_font.nametofont("TkHeadingFont").configure(
                size=round(editor_font_size * default_size_factor)
            )
            tk_font.nametofont("SmallLinkFont").configure(
                size=round(editor_font_size * small_size_factor)
            )

        # Update Treeview font and row height
        if running_on_mac_os():
            treeview_font_size = int(editor_font_size * 0.7 + 4)
        else:
            treeview_font_size = int(editor_font_size * 0.7 + 2)

        treeview_font = tk_font.nametofont("TreeviewFont")
        treeview_font.configure(size=treeview_font_size)
        rowheight = round(treeview_font.metrics("linespace") * 1.2)

        style = ttk.Style()
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
        command_id: str,
        image: Optional[tk.PhotoImage],
        disabled_image: Optional[tk.PhotoImage],
        command_label: str,
        caption: str,
        alternative_caption: str,
        accelerator: Optional[str],
        handler: Callable[[], None],
        tester: Optional[Callable[[], bool]],
        toolbar_group: int,
    ) -> None:

        assert caption is not None and len(caption) > 0, (
            "Missing caption for '%s'. Toolbar commands must have caption." % command_label
        )
        slaves = self._toolbar.grid_slaves(0, toolbar_group)
        if len(slaves) == 0:
            group_frame = ttk.Frame(self._toolbar)
            if self.in_simple_mode():
                padx = 0  # type: Union[int, Tuple[int, int]]
            else:
                padx = (0, 10)
            group_frame.grid(row=0, column=toolbar_group, padx=padx)
        else:
            group_frame = slaves[0]

        if self.in_simple_mode():
            screen_width = self.winfo_screenwidth()
            if screen_width >= 1280:
                button_width = max(7, len(caption), len(alternative_caption))
            elif screen_width >= 1024:
                button_width = max(6, len(caption), len(alternative_caption))
            else:
                button_width = max(5, len(caption), len(alternative_caption))
        else:
            button_width = None

        if disabled_image is not None:
            image_spec = [image, "disabled", disabled_image]
        else:
            image_spec = image

        button = ttk.Button(
            group_frame,
            image=image_spec,
            style="Toolbutton",
            state=tk.NORMAL,
            text=caption,
            compound="top" if self.in_simple_mode() else None,
            pad=(10, 0) if self.in_simple_mode() else None,
            width=button_width,
        )

        def toolbar_handler(*args):
            handler(*args)
            self._update_toolbar()
            if self.focus_get() == button:
                # previously selected widget would be better candidate, but this is
                # better than button
                self._editor_notebook.focus_set()

        button.configure(command=toolbar_handler)

        button.pack(side=tk.LEFT)
        button.tester = tester  # type: ignore
        tooltip_text = command_label
        if self.get_ui_mode() != "simple":
            if accelerator and lookup_style_option(
                "OPTIONS", "shortcuts_in_tooltips", default=True
            ):
                tooltip_text += " (" + accelerator + ")"
            create_tooltip(button, tooltip_text)

        self._toolbar_buttons[command_id] = button

    def get_toolbar_button(self, command_id):
        return self._toolbar_buttons[command_id]

    def _update_toolbar(self, event=None) -> None:
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

    def _toggle_font_size(self) -> None:
        current_size = self.get_option("view.editor_font_size")

        if self.winfo_screenwidth() < 1024:
            # assuming 32x32 icons
            small_size = 10
            medium_size = 12
            large_size = 14
        elif self.winfo_screenwidth() < 1280:
            # assuming 32x32 icons
            small_size = 12
            medium_size = 14
            large_size = 18
        else:
            small_size = 12
            medium_size = 16
            large_size = 20

        widths = {10: 800, 12: 1050, 14: 1200, 16: 1300, 18: 1400, 20: 1650}

        if current_size < small_size or current_size >= large_size:
            new_size = small_size
        elif current_size < medium_size:
            new_size = medium_size
        else:
            new_size = large_size

        self._change_font_size(new_size - current_size)

        new_width = min(widths[new_size], self.winfo_screenwidth())
        geo = re.findall(r"\d+", self.wm_geometry())
        self.geometry("{0}x{1}+{2}+{3}".format(new_width, geo[1], geo[2], geo[3]))

    def _change_font_size(self, delta: int) -> None:

        if delta != 0:
            editor_font_size = self.get_option("view.editor_font_size")
            editor_font_size += delta
            self.set_option("view.editor_font_size", self._guard_font_size(editor_font_size))
            io_font_size = self.get_option("view.io_font_size")
            io_font_size += delta
            self.set_option("view.io_font_size", self._guard_font_size(io_font_size))
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
                self.winfo_width() + delta, self.winfo_height(), self.winfo_x(), self.winfo_y()
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
                widget.grid(row=1, column=0, sticky=tk.NSEW, in_=widget.master)  # type: ignore
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
            row=0, column=0, sticky=tk.NSEW, in_=self._maximized_view.home_widget  # type: ignore
        )
        self._maximized_view = None
        self.get_variable("view.maximize_view").set(False)

    def show_options(self, page_key=None):
        dlg = ConfigurationDialog(self, self._configuration_pages)
        if page_key:
            dlg.select_page(page_key)

        ui_utils.show_dialog(dlg)

        if dlg.backend_restart_required:
            get_runner().restart_backend(False)

    def _cmd_focus_editor(self) -> None:
        self.get_editor_notebook().focus_set()

    def _cmd_focus_shell(self) -> None:
        self.show_view("ShellView", True)
        shell = get_shell()
        # go to the end of any current input
        shell.text.mark_set("insert", "end")
        shell.text.see("insert")

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

                enabled = not tester
                if tester:
                    try:
                        enabled = tester()
                    except Exception as e:
                        logging.exception(
                            "Could not check command tester for '%s'", item_data, exc_info=e
                        )
                        traceback.print_exc()
                        enabled = False

                if enabled:
                    menu.entryconfigure(i, state=tk.NORMAL)
                else:
                    menu.entryconfigure(i, state=tk.DISABLED)

    def _find_location_for_menu_item(self, menu_name: str, command_label: str) -> Union[str, int]:

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
                    if specs.position_in_group == "alphabetic" and sibling_label > command_label:
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

    def _poll_ipc_requests(self) -> None:
        try:
            if self._ipc_requests.empty():
                return

            while not self._ipc_requests.empty():
                args = self._ipc_requests.get()
                try:
                    for filename in args:
                        if os.path.isfile(filename):
                            self.get_editor_notebook().show_file(filename)

                except Exception as e:
                    logger.exception("Problem processing ipc request", exc_info=e)

            self.become_active_window()
        finally:
            self.after(50, self._poll_ipc_requests)

    def _on_close(self) -> None:
        if self._editor_notebook and not self._editor_notebook.check_allow_closing():
            return

        self._closing = True
        try:
            self._save_layout()
            self._editor_notebook.remember_open_files()
            self.event_generate("WorkbenchClose")
            self._configuration_manager.save()
            temp_dir = self.get_temp_dir(create_if_doesnt_exist=False)
            if os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    logger.error("Could not remove temp dir", exc_info=e)
        except Exception:
            self.report_exception()

        self.destroy()
        self._destroyed = True

    def _on_all_key_presses(self, event):
        if running_on_windows():
            ui_utils.handle_mistreated_latin_shortcuts(self._latin_shortcuts, event)

    def _on_focus_in(self, event):
        if self._lost_focus:
            self._lost_focus = False
            self.event_generate("WindowFocusIn")

    def _on_focus_out(self, event):
        if self.focus_get() is None:
            if not self._lost_focus:
                self._lost_focus = True
                self.event_generate("WindowFocusOut")

    def focus_get(self) -> Optional[tk.Widget]:
        try:
            return tk.Tk.focus_get(self)
        except Exception:
            # This may give error in Ubuntu
            return None

    def destroy(self) -> None:
        try:
            if self._is_server() and os.path.exists(thonny.get_ipc_file_path()):
                os.remove(thonny.get_ipc_file_path())

            self._closing = True

            # Tk clipboard gets cleared on exit and won't end up in system clipboard
            # https://bugs.python.org/issue1207592
            # https://stackoverflow.com/questions/26321333/tkinter-in-python-3-4-on-windows-dont-post-internal-clipboard-data-to-the-windo
            try:
                clipboard_data = self.clipboard_get()
                if len(clipboard_data) < 1000 and all(
                    map(os.path.exists, clipboard_data.splitlines())
                ):
                    # Looks like the clipboard contains file name(s)
                    # Most likely this means actual file cut/copy operation
                    # was made outside of Thonny.
                    # Don't want to replace this with simple string data of file names.
                    pass
                else:
                    copy_to_clipboard(clipboard_data)
            except Exception:
                pass

        except Exception:
            logging.exception("Error while destroying workbench")

        finally:
            try:
                super().destroy()
            finally:
                runner = get_runner()
                if runner != None:
                    runner.destroy_backend()

    def _on_configure(self, event) -> None:
        # called when window is moved or resized
        if (
            hasattr(self, "_maximized_view")  # configure may happen before the attribute is defined
            and self._maximized_view  # type: ignore
        ):
            # grid again, otherwise it acts weird
            self._maximized_view.grid(
                row=1, column=0, sticky=tk.NSEW, in_=self._maximized_view.master  # type: ignore
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
        if tk._default_root and not self._closing:  # type: ignore
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

                if (
                    self.get_ui_mode() != "simple" or view_name in SIMPLE_MODE_VIEWS
                ) and view_name in self._view_records:
                    self.show_view(view_name)

        # make sure VariablesView is at least loaded
        # otherwise it may miss globals events
        # and will show empty table on open
        self.get_view("VariablesView")

        if (
            self.get_option("assistance.open_assistant_on_errors")
            or self.get_option("assistance.open_assistant_on_warnings")
        ) and (self.get_ui_mode() != "simple" or "AssistantView" in SIMPLE_MODE_VIEWS):
            self.get_view("AssistantView")

    def _save_layout(self) -> None:
        self.update_idletasks()
        self.set_option("layout.zoomed", ui_utils.get_zoomed(self))

        for nb_name in self._view_notebooks:
            widget = self._view_notebooks[nb_name].get_visible_child()
            if hasattr(widget, "maximizable_widget"):
                view = widget.maximizable_widget
                view_name = type(view).__name__
                self.set_option("layout.notebook_" + nb_name + "_visible_view", view_name)
            else:
                self.set_option("layout.notebook_" + nb_name + "_visible_view", None)

        if not ui_utils.get_zoomed(self) or running_on_mac_os():
            # can't restore zoom on mac without setting actual dimensions
            gparts = re.findall(r"\d+", self.wm_geometry())
            self.set_option("layout.width", int(gparts[0]))
            self.set_option("layout.height", int(gparts[1]))
            self.set_option("layout.left", int(gparts[2]))
            self.set_option("layout.top", int(gparts[3]))

        self.set_option("layout.west_pw_width", self._west_pw.preferred_size_in_pw)
        self.set_option("layout.east_pw_width", self._east_pw.preferred_size_in_pw)
        for key in ["nw", "sw", "s", "se", "ne"]:
            self.set_option(
                "layout.%s_nb_height" % key, self._view_notebooks[key].preferred_size_in_pw
            )

    def update_title(self, event=None) -> None:
        editor = self.get_editor_notebook().get_current_editor()
        if self._is_portable:
            title_text = "Portable Thonny"
        else:
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
                self.get_editor_notebook().show_file_at_line(filename, lineno, col_offset)

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
        import webbrowser

        webbrowser.open(url, False, True)

    def open_help_topic(self, topic, fragment=None):
        self.show_view("HelpView").load_topic(topic, fragment)

    def bell(self, displayof=0):
        if not self.get_option("general.disable_notification_sound"):
            super().bell(displayof=displayof)

    def _mac_quit(self, *args):
        self._on_close()

    def _is_server(self):
        return self._ipc_requests is not None

    def get_toolbar(self):
        return self._toolbar

    def get_temp_dir(self, create_if_doesnt_exist=True):
        path = os.path.join(THONNY_USER_DIR, "temp")
        if create_if_doesnt_exist:
            os.makedirs(path, exist_ok=True)
        return path


class WorkbenchEvent(Record):
    def __init__(self, sequence: str, **kwargs) -> None:
        Record.__init__(self, **kwargs)
        self.sequence = sequence
