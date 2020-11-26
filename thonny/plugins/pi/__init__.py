import logging
import os
import re

from thonny import get_workbench
from thonny.ui_utils import scale

DESKTOP_SESSION = os.environ.get("DESKTOP_SESSION", "_")
CONFIGURATION_PATH = os.path.join(
    os.path.expanduser("~"), ".config/lxsession", DESKTOP_SESSION, "desktop.conf"
)
GLOBAL_CONFIGURATION_PATH = os.path.join("/etc/xdg/lxsession", DESKTOP_SESSION, "desktop.conf")

logger = logging.getLogger(__name__)


def pix():
    MAIN_BACKGROUND = "#ededed"
    detail_bg = "#d0d0d0"
    detail_bg2 = "#cfcdc8"
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    scrollbar_button_settings = {}
    for direction, element_name in [
        ("up", "Vertical.Scrollbar.uparrow"),
        ("down", "Vertical.Scrollbar.downarrow"),
        ("left", "Horizontal.Scrollbar.leftarrow"),
        ("right", "Horizontal.Scrollbar.rightarrow"),
    ]:
        # load the image
        img_name = "scrollbar-button-" + direction
        for suffix in ["", "-insens"]:
            get_workbench().get_image(
                os.path.join(res_dir, img_name + suffix + ".png"), img_name + suffix
            )

        scrollbar_button_settings[element_name] = {
            "element create": (
                "image",
                img_name,
                ("!disabled", img_name),
                ("disabled", img_name + "-insens"),
            )
        }

    settings = {
        ".": {"configure": {"background": MAIN_BACKGROUND}},
        "Toolbutton": {
            "configure": {"borderwidth": 1},
            "map": {
                "relief": [("disabled", "flat"), ("hover", "groove"), ("!hover", "flat")],
                "background": [
                    ("disabled", MAIN_BACKGROUND),
                    ("!hover", MAIN_BACKGROUND),
                    ("hover", "#ffffff"),
                ],
            },
        },
        "Treeview.Heading": {
            "configure": {
                "background": "#f0f0f0",
                "foreground": "#808080",
                "relief": "flat",
                "borderwidth": 1,
            },
            "map": {"foreground": [("active", "black")]},
        },
        "TNotebook.Tab": {
            "map": {"background": [("!selected", detail_bg), ("selected", MAIN_BACKGROUND)]}
        },
        "ButtonNotebook.TNotebook.Tab": {
            "map": {
                "background": [("!selected", detail_bg), ("selected", MAIN_BACKGROUND)],
                "padding": [
                    ("selected", [scale(4), scale(2), scale(4), scale(3)]),
                    ("!selected", [scale(4), scale(2), scale(4), scale(3)]),
                ],
            }
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(1),
                "relief": "solid",
                "background": "#9e9e9e",
                "darkcolor": "#d6d6d6",
                "lightcolor": "#d6d6d6",
                "bordercolor": "#d6d6d6",
                "troughcolor": "#d6d6d6",
                "arrowsize": scale(1),
                "arrowcolor": "gray",
            },
            "map": {"background": [], "darkcolor": [], "lightcolor": []},
        },
        # Padding allows twaking thumb width
        "Vertical.TScrollbar": {
            "layout": [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "sticky": "ns",
                        "children": [
                            ("Vertical.Scrollbar.uparrow", {"side": "top", "sticky": ""}),
                            ("Vertical.Scrollbar.downarrow", {"side": "bottom", "sticky": ""}),
                            (
                                "Vertical.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Vertical.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ]
        },
        "Horizontal.TScrollbar": {
            "layout": [
                (
                    "Horizontal.Scrollbar.trough",
                    {
                        "sticky": "we",
                        "children": [
                            ("Horizontal.Scrollbar.leftarrow", {"side": "left", "sticky": ""}),
                            ("Horizontal.Scrollbar.rightarrow", {"side": "right", "sticky": ""}),
                            (
                                "Horizontal.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Horizontal.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
            "map": {
                # Make disabled Hor Scrollbar invisible
                "background": [("disabled", "#d6d6d6")],
                "troughcolor": [("disabled", "#d6d6d6")],
                "bordercolor": [("disabled", "#d6d6d6")],
                "darkcolor": [("disabled", "#d6d6d6")],
                "lightcolor": [("disabled", "#d6d6d6")],
            },
        },
        "TCombobox": {"configure": {"arrowsize": scale(10)}},
        "Menubar": {
            "configure": {
                "background": MAIN_BACKGROUND,
                "relief": "flat",
                "activebackground": "#ffffff",
                "activeborderwidth": 0,
            }
        },
        "Menu": {
            "configure": {
                "background": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "activeborderwidth": 0,
                # "activebackground" : bg, # updated below
                # "activeforeground" : fg,
            }
        },
        "Tooltip": {
            "configure": {
                "background": "#808080",
                "foreground": "#ffffff",
                "borderwidth": 0,
                "padx": 10,
                "pady": 10,
            }
        },
        "Tip.TLabel": {"configure": {"background": detail_bg2, "foreground": "black"}},
        "Tip.TFrame": {"configure": {"background": detail_bg2}},
        "OPTIONS": {"configure": {"icons_in_menus": False, "shortcuts_in_tooltips": False}},
    }

    settings.update(scrollbar_button_settings)

    # try to refine settings according to system configuration
    """Note that fonts are set globally, 
    ie. all themes will later inherit these"""
    update_fonts()

    for path in [GLOBAL_CONFIGURATION_PATH, CONFIGURATION_PATH]:
        if os.path.exists(path):
            with open(path) as fp:
                try:
                    for line in fp:
                        if "sGtk/ColorScheme" in line:
                            if "selected_bg_color" in line:
                                bgr = re.search(
                                    r"selected_bg_color:#([0-9a-fA-F]*)", line, re.M
                                ).group(
                                    1
                                )  # @UndefinedVariable
                                color = "#" + bgr[0:2] + bgr[4:6] + bgr[8:10]
                                if is_good_color(color):
                                    settings["Menu"]["configure"]["activebackground"] = color
                            if "selected_fg_color" in line:
                                fgr = re.search(
                                    r"selected_fg_color:#([0-9a-fA-F]*)", line, re.M
                                ).group(
                                    1
                                )  # @UndefinedVariable
                                color = "#" + fgr[0:2] + fgr[4:6] + fgr[8:10]
                                if is_good_color(color):
                                    settings["Menu"]["configure"]["activeforeground"] = color
                except Exception as e:
                    logger.error("Could not update colors", exc_info=e)

    return settings


def is_good_color(s):
    return bool(re.match("^#[0-9a-fA-F]{6}$", s))


def pix_dark():
    update_fonts()
    return {}


def update_fonts():
    from tkinter import font

    options = {}
    for path in [GLOBAL_CONFIGURATION_PATH, CONFIGURATION_PATH]:
        if os.path.exists(path):
            try:
                with open(path) as fp:
                    for line in fp:
                        if "sGtk/FontName" in line:
                            result = re.search(
                                r"=([^0-9]*) ([0-9]*)", line, re.M
                            )  # @UndefinedVariable
                            family = result.group(1)
                            options["size"] = int(result.group(2))

                            if re.search(r"\bBold\b", family):
                                options["weight"] = "bold"
                            else:
                                options["weight"] = "normal"

                            if re.search(r"\bItalic\b", family):
                                options["slant"] = "italic"
                            else:
                                options["slant"] = "roman"

                            options["family"] = family.replace(" Bold", "").replace(" Italic", "")
            except Exception as e:
                logger.error("Could not update fonts", exc_info=e)

    if options:
        for name in ["TkDefaultFont", "TkMenuFont", "TkTextFont", "TkHeadingFont"]:
            font.nametofont(name).configure(**options)


def load_plugin():

    # set custom images
    if get_workbench().get_ui_mode() == "simple" and get_workbench().winfo_screenwidth() >= 1280:
        images = {
            "run-current-script": "media-playback-start48.png",
            "stop": "process-stop48.png",
            "new-file": "document-new48.png",
            "open-file": "document-open48.png",
            "save-file": "document-save48.png",
            "debug-current-script": "debug-run48.png",
            "step-over": "debug-step-over48.png",
            "step-into": "debug-step-into48.png",
            "step-out": "debug-step-out48.png",
            "run-to-cursor": "debug-run-cursor48.png",
            "tab-close": "window-close.png",
            "tab-close-active": "window-close-act.png",
            "resume": "resume48.png",
            "zoom": "zoom48.png",
            "quit": "quit48.png",
        }
    else:
        images = {
            "run-current-script": "media-playback-start.png",
            "stop": "process-stop.png",
            "new-file": "document-new.png",
            "open-file": "document-open.png",
            "save-file": "document-save.png",
            "debug-current-script": "debug-run.png",
            "step-over": "debug-step-over.png",
            "step-into": "debug-step-into.png",
            "step-out": "debug-step-out.png",
            "run-to-cursor": "debug-run-cursor.png",
            "tab-close": "window-close.png",
            "tab-close-active": "window-close-act.png",
            "resume": "resume.png",
            "zoom": "zoom.png",
            "quit": "quit.png",
        }

    res_dir = os.path.join(os.path.dirname(__file__), "res")
    theme_image_map = {}
    for image in images:
        theme_image_map[image] = os.path.join(res_dir, images[image])

    get_workbench().add_ui_theme("Raspberry Pi", "Enhanced Clam", pix, theme_image_map)
    get_workbench().add_ui_theme("Raspberry Pi Dark", "Clean Dark", pix_dark, theme_image_map)
