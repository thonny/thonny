from typing import Callable, Dict, Union  # @UnusedImport

from thonny import get_workbench
from thonny.misc_utils import running_on_linux, running_on_windows
from thonny.workbench import BasicUiThemeSettings, CompoundUiThemeSettings


def scale(value) -> float:
    # dimensions in this module were designed with a 1.67 scale
    return get_workbench().scale(value / 1.67)


def _treeview_settings() -> BasicUiThemeSettings:
    light_blue = "#ADD8E6"
    light_grey = "#D3D3D3"

    if running_on_linux():
        bg_sel_focus = light_blue
        fg = "black"
    else:
        bg_sel_focus = "SystemHighlight"
        fg = "SystemHighlightText"

    return {
        "Treeview": {
            "configure": {"font": "TreeviewFont"},
            "map": {
                "background": [
                    ("selected", "focus", bg_sel_focus),
                    ("selected", "!focus", light_grey),
                ],
                "foreground": [("selected", fg)],
            },
            "layout": [
                # get rid of borders
                ("Treeview.treearea", {"sticky": "nswe"})
            ],
        },
        "treearea": {"configure": {"borderwidth": 0}},
    }


def _menubutton_settings() -> BasicUiThemeSettings:
    return {
        "TMenubutton": {
            "configure": {"padding": scale(14)},
            "layout": [
                ("Menubutton.dropdown", {"side": "right", "sticky": "ns"}),
                (
                    "Menubutton.button",
                    {
                        "children": [
                            # ('Menubutton.padding', {'children': [
                            ("Menubutton.label", {"sticky": ""})
                            # ], 'expand': '1', 'sticky': 'we'})
                        ],
                        "expand": "1",
                        "sticky": "nswe",
                    },
                ),
            ],
        }
    }


def _paned_window_settings() -> BasicUiThemeSettings:
    return {"Sash": {"configure": {"sashthickness": scale(10)}}}


def _menu_settings() -> BasicUiThemeSettings:
    return {"Menubar": {"configure": {"activeborderwidth": 0, "relief": "flat"}}}


def _text_settings() -> BasicUiThemeSettings:
    return {
        "Text": {
            "configure": {
                "background": "SystemWindow" if running_on_windows() else "white",
                "foreground": "SystemWindowText" if running_on_windows() else "black",
            }
        },
        "Syntax.Text": {"map": {"background": [("readonly", "Yellow")]}},
        "Gutter": {"configure": {"background": "#e0e0e0", "foreground": "#999999"}},
    }


def _label_settings() -> BasicUiThemeSettings:
    return {"Url.TLabel": {"configure": {"foreground": "#3A66DD"}}}


def _button_notebook_settings() -> BasicUiThemeSettings:
    # Adapted from https://github.com/python/cpython/blob/2.7/Demo/tkinter/ttk/notebook_closebtn.py
    return {
        "closebutton": {
            "element create": (
                "image",
                "img_close",
                ("active", "pressed", "!disabled", "img_close_active"),
                ("active", "!disabled", "img_close_active"),
                {"padding": scale(2), "sticky": ""},
            )
        },
        "ButtonNotebook.TNotebook.Tab": {
            "layout": [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Notebook.focus",
                                            {
                                                "side": "left",
                                                "sticky": "nswe",
                                                "children": [
                                                    (
                                                        "Notebook.label",
                                                        {"side": "left", "sticky": ""},
                                                    )
                                                ],
                                            },
                                        ),
                                        (
                                            "Notebook.closebutton",
                                            {"side": "right", "sticky": ""},
                                        ),
                                    ],
                                },
                            )
                        ],
                    },
                )
            ]
        },
    }


def clam() -> BasicUiThemeSettings:
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    defaultfg = "#000000"
    disabledfg = "#999999"
    frame = "#dcdad5"
    window = "#ffffff"
    dark = "#cfcdc8"
    darker = "#bab5ab"
    darkest = "#9e9a91"
    lighter = "#eeebe7"
    selectbg = "#4a6984"
    selectfg = "#ffffff"
    altindicator = "#5895bc"
    disabledaltindicator = "#a0a0a0"

    return {
        ".": {
            "configure": {
                "background": frame,
                "foreground": defaultfg,
                "bordercolor": darkest,
                "darkcolor": dark,
                "lightcolor": lighter,
                "troughcolor": darker,
                "selectbackground": selectbg,
                "selectforeground": selectfg,
                "selectborderwidth": 0,
                "font": "TkDefaultFont",
            },
            "map": {
                "background": [("disabled", frame), ("active", lighter)],
                "foreground": [("disabled", disabledfg)],
                "selectbackground": [("!focus", darkest)],
                "selectforeground": [("!focus", "white")],
            },
        },
        "TButton": {
            "configure": {
                "anchor": "center",
                "width": scale(11),
                "padding": scale(5),
                "relief": "raised",
            },
            "map": {
                "background": [
                    ("disabled", frame),
                    ("pressed", darker),
                    ("active", lighter),
                ],
                "lightcolor": [("pressed", darker)],
                "darkcolor": [("pressed", darker)],
                "bordercolor": [("alternate", "#000000")],
            },
        },
        "Toolbutton": {
            "configure": {"anchor": "center", "padding": scale(2), "relief": "flat"},
            "map": {
                "relief": [
                    ("disabled", "flat"),
                    ("selected", "sunken"),
                    ("pressed", "sunken"),
                    ("active", "raised"),
                ],
                "background": [
                    ("disabled", frame),
                    ("pressed", darker),
                    ("active", lighter),
                ],
                "lightcolor": [("pressed", darker)],
                "darkcolor": [("pressed", darker)],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorbackground": "#ffffff",
                "indicatormargin": [scale(1), scale(1), scale(6), scale(1)],
                "padding": scale(2),
            },
            "map": {
                "indicatorbackground": [
                    ("pressed", frame),
                    ("!disabled", "alternate", altindicator),
                    ("disabled", "alternate", disabledaltindicator),
                    ("disabled", frame),
                ]
            },
        },
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton": {
            "configure": {
                "indicatorbackground": "#ffffff",
                "indicatormargin": [scale(1), scale(1), scale(6), scale(1)],
                "padding": scale(2),
            },
            "map": {
                "indicatorbackground": [
                    ("pressed", frame),
                    ("!disabled", "alternate", altindicator),
                    ("disabled", "alternate", disabledaltindicator),
                    ("disabled", frame),
                ]
            },
        },
        "TMenubutton": {
            "configure": {"width": scale(11), "padding": scale(5), "relief": "raised"}
        },
        "TEntry": {
            "configure": {"padding": scale(1), "insertwidth": scale(1)},
            "map": {
                "background": [("readonly", frame)],
                "bordercolor": [("focus", selectbg)],
                "lightcolor": [("focus", "#6f9dc6")],
                "darkcolor": [("focus", "#6f9dc6")],
            },
        },
        "TCombobox": {
            "configure": {
                "padding": [scale(4), scale(2), scale(2), scale(2)],
                "insertwidth": scale(1),
            },
            "map": {
                "background": [("active", lighter), ("pressed", lighter)],
                "fieldbackground": [
                    ("readonly", "focus", selectbg),
                    ("readonly", frame),
                ],
                "foreground": [("readonly", "focus", selectfg)],
                "arrowcolor": [("disabled", disabledfg)],
            },
        },
        "ComboboxPopdownFrame": {
            "configure": {"relief": "solid", "borderwidth": scale(1)}
        },
        "TSpinbox": {
            "configure": {
                "arrowsize": scale(10),
                "padding": [scale(2), 0, scale(10), 0],
            },
            "map": {
                "background": [("readonly", frame)],
                "arrowcolor": [("disabled", disabledfg)],
            },
        },
        "TNotebook.Tab": {
            "configure": {"padding": [scale(6), scale(2), scale(6), scale(2)]},
            "map": {
                "padding": [("selected", [scale(6), scale(4), scale(6), scale(4)])],
                "background": [("selected", frame), ("", darker)],
                "lightcolor": [("selected", lighter), ("", dark)],
            },
        },
        "Treeview": {
            "configure": {"background": window},
            "map": {
                "background": [
                    ("disabled", frame),
                    ("!disabled", "!selected", window),
                    ("selected", selectbg),
                ],
                "foreground": [
                    ("disabled", disabledfg),
                    ("!disabled", "!selected", defaultfg),
                    ("selected", selectfg),
                ],
            },
        },
        # Treeview heading
        "Heading": {
            "configure": {
                "font": "TkHeadingFont",
                "relief": "raised",
                "padding": [scale(3), scale(3), scale(3), scale(3)],
            }
        },
        "TLabelframe": {
            "configure": {"labeloutside": True, "labelmargins": [0, 0, 0, scale(4)]}
        },
        "TProgressbar": {"configure": {"background": frame}},
        "Sash": {"configure": {"sashthickness": scale(6), "gripcount": 10}},
    }


def xpnative() -> BasicUiThemeSettings:
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/xpTheme.tcl
    return {
        ".": {
            "configure": {
                "background": "SystemButtonFace",
                "foreground": "SystemWindowText",
                "selectbackground": "SystemHighlight",
                "selectforeground": "SystemHighlightText",
                "font": "TkDefaultFont",
            },
            "map": {"foreground": [("disabled", "SystemGrayText")]},
        },
        "TButton": {
            "configure": {
                "anchor": "center",
                "width": scale(11),
                "padding": [scale(1), scale(1)],
            }
        },
        "Toolbutton": {"configure": {"padding": [scale(4), scale(4)]}},
        "TCheckbutton": {"configure": {"padding": scale(2)}},
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton": {"configure": {"padding": scale(2)}},
        "TMenubutton": {"configure": {"padding": [scale(8), scale(4)]}},
        "TEntry": {
            "configure": {"padding": [scale(2), scale(2), scale(2), scale(4)]},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
            },
        },
        "TCombobox": {
            "configure": {"padding": scale(2)},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
                "foreground": [
                    ("disabled", "SystemGrayText"),
                    ("readonly", "focus", "SystemHighlightText"),
                ],
                "focusfill": [("readonly", "focus", "SystemHighlight")],
            },
        },
        "ComboboxPopdownFrame": {
            "configure": {"relief": "solid", "borderwidth": scale(1)}
        },
        "TSpinbox": {
            "configure": {"padding": [scale(2), 0, scale(14), 0]},
            "map": {
                "selectbackground": [("!focus", "SystemWindow")],
                "selectforeground": [("!focus", "SystemWindowText")],
            },
        },
        "TNotebook": {"configure": {"tabmargins": [scale(2), scale(2), scale(2), 0]}},
        "TNotebook.Tab": {
            "map": {"expand": [("selected", [scale(2), scale(2), scale(2), scale(2)])]}
        },
        "Treeview": {
            "configure": {"background": "SystemWindow"},
            "map": {
                "background": [
                    ("disabled", "SystemButtonFace"),
                    ("!disabled", "!selected", "SystemWindow"),
                    ("selected", "SystemHighlight"),
                ],
                "foreground": [
                    ("disabled", "SystemGrayText"),
                    ("!disabled", "!selected", "SystemWindowText"),
                    ("selected", "SystemHighlightText"),
                ],
            },
        },
        "Heading": {  # Treeview heading
            "configure": {"font": "TkHeadingFont", "relief": "raised"}
        },
        "TLabelframe.Label": {"configure": {"foreground": "#0046d5"}},
    }


def aqua() -> BasicUiThemeSettings:
    # https://github.com/tcltk/tk/blob/master/library/ttk/aquaTheme.tcl
    return {
        ".": {
            "configure": {
                "font": "TkDefaultFont",
                "background": "systemWindowBody",
                "foreground": "systemModelessDialogActiveText",
                "selectbackground": "systemHighlight",
                "selectforeground": "systemModelessDialogActiveText",
                "selectborderwidth": 0,
                "insertwidth": 1,
                "stipple": "",
            },
            "map": {
                "foreground": [
                    ("disabled", "systemModelessDialogInactiveText"),
                    ("background", "systemModelessDialogInactiveText"),
                ],
                "selectbackground": [
                    ("background", "systemHighlightSecondary"),
                    ("!focus", "systemHighlightSecondary"),
                ],
                "selectforeground": [
                    ("background", "systemModelessDialogInactiveText"),
                    ("!focus", "systemDialogActiveText"),
                ],
            },
        },
        "TButton": {"configure": {"anchor": "center", "width": "6"}},
        "Toolbutton": {"configure": {"padding": 4}},
        "TNotebook": {
            "configure": {
                "tabmargins": [10, 0],
                "tabposition": "n",
                "padding": [18, 8, 18, 17],
            }
        },
        "TNotebook.Tab": {"configure": {"padding": [12, 3, 12, 2]}},
        "TCombobox": {"configure": {"postoffset": [5, -2, -10, 0]}},
        "Heading": {"configure": {"font": "TkHeadingFont"}},
        "Treeview": {
            "configure": {"rowheight": 18, "background": "white"},
            "map": {
                "background": [
                    ("disabled", "systemDialogBackgroundInactive"),
                    ("!disabled", "!selected", "systemWindowBody"),
                    ("selected", "background", "systemHighlightSecondary"),
                    ("selected", "systemHighlight"),
                ],
                "foreground": [
                    ("disabled", "systemModelessDialogInactiveText"),
                    ("!disabled", "!selected", "black"),
                    ("selected", "systemModelessDialogActiveText"),
                ],
            },
        },
        "TProgressbar": {"configure": {"period": 100, "maxphase": 255}},
        "Labelframe": {
            "configure": {"labeloutside": True, "labelmargins": [14, 0, 14, 4]}
        },
    }


def windows() -> CompoundUiThemeSettings:
    return [
        xpnative(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        _label_settings(),
        _button_notebook_settings(),
        {
            "TNotebook": {
                "configure": {
                    # With tabmargins I can get a gray line below tab, which separates
                    # tab content from label
                    "tabmargins": [scale(2), scale(2), scale(2), scale(2)]
                }
            },
            "Tab": {"configure": {"padding": [scale(3), scale(1), scale(3), 0]}},
            "ButtonNotebook.TNotebook.Tab": {
                "configure": {"padding": (scale(4), scale(1), scale(1), 0)}
            },
            "TCombobox": {
                "map": {
                    "selectbackground": [
                        ("readonly", "!focus", "SystemWindow"),
                        ("readonly", "focus", "SystemHighlight"),
                    ],
                    "selectforeground": [
                        ("readonly", "!focus", "SystemWindowText"),
                        ("readonly", "focus", "SystemHighlightText"),
                    ],
                }
            },
            "Listbox": {
                "configure": {
                    "background": "SystemWindow",
                    "foreground": "SystemWindowText",
                    "disabledforeground": "SystemGrayText",
                    "highlightbackground": "SystemActiveBorder",
                    "highlightcolor": "SystemActiveBorder",
                    "highlightthickness": scale(1),
                }
            },
            "ViewBody.TFrame": {
                "configure": {
                    "background": "SystemButtonFace"  # to create the fine line below toolbar
                }
            },
            "ViewToolbar.TFrame": {"configure": {"background": "SystemWindow"}},
            "ViewToolbar.Toolbutton": {"configure": {"background": "SystemWindow"}},
            "ViewTab.TLabel": {
                "configure": {"background": "SystemWindow", "padding": [scale(5), 0]}
            },
            "ViewToolbar.TLabel": {
                "configure": {"background": "SystemWindow", "padding": [scale(5), 0]}
            },
            "Active.ViewTab.TLabel": {
                "configure": {
                    # "font" : "BoldTkDefaultFont",
                    "relief": "sunken",
                    "borderwidth": scale(1),
                }
            },
            "Inactive.ViewTab.TLabel": {
                "configure": {"font": "UnderlineTkDefaultFont"}
            },
        },
    ]


def enhanced_clam() -> CompoundUiThemeSettings:
    return [
        clam(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        _label_settings(),
        _button_notebook_settings(),
        {
            "ButtonNotebook.Tab": {
                "configure": {"padding": (scale(6), scale(4), scale(2), scale(3))}
            },
            "TScrollbar": {
                "configure": {
                    "gripcount": 0,
                    "arrowsize": scale(14),
                    # "arrowcolor" : "DarkGray"
                    # "width" : 99 # no effect
                }
            },
            "TCombobox": {
                "configure": {"arrowsize": scale(14)},
                "map": {
                    "selectbackground": [("readonly", "!focus", "#dcdad5")],
                    "selectforeground": [("readonly", "!focus", "#000000")],
                },
            },
            "TCheckbutton": {"configure": {"indicatorsize": scale(12)}},
            "TRadiobutton": {"configure": {"indicatorsize": scale(12)}},
            "Listbox": {
                "configure": {
                    "background": "white",
                    "foreground": "black",
                    "disabledforeground": "#999999",
                    "highlightbackground": "#4a6984",
                    "highlightcolor": "#4a6984",
                    "highlightthickness": scale(1),
                }
            },
        },
    ]


def enhanced_aqua() -> CompoundUiThemeSettings:
    return [
        _treeview_settings(),
        _menubutton_settings(),
        # _paned_window_settings(),
        _menu_settings(),
        {
            "TPanedWindow": {
                "configure": {"background": "systemDialogBackgroundActive"}
            },
            "TFrame": {"configure": {"background": "systemDialogBackgroundActive"}},
            "Tab": {"map": {"foreground": [("selected", "white")]}},
        },
    ]


def load_plugin() -> None:
    from tkinter import ttk

    original_themes = ttk.Style().theme_names()

    # load all base themes
    for name in original_themes:
        settings = {}  # type: Union[Dict, Callable[[], Dict]]
        if name == "clam":
            settings = clam
        elif name == "xpnative":
            settings = xpnative
        elif name == "aqua":
            settings = aqua

        get_workbench().add_ui_theme(name, None, settings)

    get_workbench().add_ui_theme(
        "Enhanced Clam",
        "clam",
        enhanced_clam,
        {"tab-close": "tab-close-clam", "tab-close-active": "tab-close-active-clam"},
    )

    if "xpnative" in original_themes:
        get_workbench().add_ui_theme("Windows", "xpnative", windows)

    if "aqua" in original_themes:
        get_workbench().add_ui_theme("Kind of Aqua", "aqua", enhanced_aqua)

    if "Windows" in get_workbench().get_usable_ui_theme_names():
        get_workbench().set_default("view.ui_theme", "Windows")

    elif "Enhanced Clam" in get_workbench().get_usable_ui_theme_names():
        get_workbench().set_default("view.ui_theme", "Enhanced Clam")
