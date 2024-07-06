from typing import Optional

from thonny import get_workbench
from thonny.misc_utils import running_on_windows
from thonny.ui_utils import scale
from thonny.workbench import UiThemeSettings


def tidy(
    frame_background: str,
    text_background: str,
    normal_detail: str,
    high_detail: str,
    low_detail: str,
    scrollbar_background: str,
    trough_background: str,
    active_tab_background: str,
    normal_foreground: str,
    high_foreground: str,
    low_foreground: str,
    link_foreground: str,
    custom_menubar: Optional[
        int
    ] = None,  # NB! Should be 1 or 0, not True or False (Tk would convert False to "False")
) -> UiThemeSettings:
    # https://wiki.tcl.tk/37973 (Changing colors)
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c

    if active_tab_background == "normal_detail":
        active_tab_background = normal_detail
    elif active_tab_background == "frame_background":
        active_tab_background = frame_background

    return {
        ".": {
            "configure": {
                "foreground": normal_foreground,
                "background": frame_background,
                "lightcolor": frame_background,
                "darkcolor": frame_background,
                "bordercolor": low_detail,
                "selectbackground": high_detail,
                "selectforeground": high_foreground,
            },
            "map": {
                "foreground": [("disabled", low_foreground), ("active", high_foreground)],
                "background": [("disabled", frame_background), ("active", high_detail)],
                "selectbackground": [("!focus", low_detail)],
                "selectforeground": [("!focus", normal_foreground)],
            },
        },
        "TNotebook": {
            # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkNotebook.c
            "configure": {
                "bordercolor": low_detail,
                "tabmargins": [scale(1), 0, 0, 0],  # Margins around tab row
            }
        },
        "ButtonNotebook.TNotebook": {"configure": {"bordercolor": low_detail}},
        "ViewNotebook.TNotebook": {"configure": {"bordercolor": low_detail}},
        "TNotebook.Tab": {
            "configure": {"background": frame_background, "bordercolor": low_detail},
            "map": {
                "background": [
                    ("selected", active_tab_background),
                    ("!selected", "!active", frame_background),
                    ("active", "!selected", frame_background),
                ],
                "bordercolor": [("selected", low_detail), ("!selected", low_detail)],
                "lightcolor": [
                    ("selected", active_tab_background),
                    ("!selected", frame_background),
                ],
            },
        },
        "CustomNotebook": {
            "configure": {
                "bordercolor": high_detail,
            }
        },
        "CustomNotebook.Tab": {
            "configure": {
                "background": frame_background,
                "activebackground": active_tab_background,
                "hoverbackground": normal_detail,
                "indicatorbackground": active_tab_background,
                "dynamic_border": 1,
            }
        },
        "TextPanedWindow": {"configure": {"background": text_background}},
        "Treeview": {
            "configure": {"background": text_background, "borderwidth": 0, "relief": "flat"},
            "map": {
                "background": [
                    ("selected", "focus", high_detail),
                    ("selected", "!focus", low_detail),
                ],
                "foreground": [
                    ("selected", "focus", high_foreground),
                    ("selected", "!focus", normal_foreground),
                ],
            },
        },
        "Heading": {
            # https://stackoverflow.com/questions/32051780/how-to-edit-the-style-of-a-heading-in-treeview-python-ttk
            "configure": {
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "borderwidth": 1,
                "topmost_pixels_to_hide": 2,
            },
            "map": {
                "background": [
                    ("!active", active_tab_background),
                    ("active", active_tab_background),
                ]
            },
        },
        "TEntry": {
            "configure": {
                "fieldbackground": text_background,
                "lightcolor": text_background,
                "insertcolor": normal_foreground,
                "borderwidth": 1,
            },
            "map": {
                "background": [("readonly", text_background)],
                "bordercolor": [],
                "lightcolor": [("focus", high_detail)],
                "darkcolor": [],
            },
        },
        "TCombobox": {
            "configure": {
                "background": text_background,
                "fieldbackground": text_background,
                "selectbackground": text_background,
                "lightcolor": text_background,
                "darkcolor": text_background,
                "bordercolor": high_detail,
                "arrowcolor": normal_foreground,
                "foreground": normal_foreground,
                "selectforeground": normal_foreground,
                # "padding" : [12,2,12,2],
            },
            "map": {
                "background": [("active", frame_background), ("readonly", frame_background)],
                "fieldbackground": [],
                "selectbackground": [],
                "selectforeground": [],
                "foreground": [],
                "arrowcolor": [],
            },
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(1.15),
                "relief": "solid",
                "background": scrollbar_background,
                "darkcolor": trough_background,
                "lightcolor": trough_background,
                "bordercolor": trough_background,
                "troughcolor": trough_background,
                # arrowcolor="white"
                "arrowsize": scale(7),  # affects bar size as well, even without arrows
            },
            "map": {
                "background": [
                    ("!disabled", scrollbar_background),
                    ("disabled", trough_background),
                ],
                "darkcolor": [("!disabled", trough_background), ("disabled", trough_background)],
                "lightcolor": [("!disabled", trough_background), ("disabled", trough_background)],
            },
        },
        "Vertical.TScrollbar": {
            # Remove scrollbar buttons/arrows:
            "layout": [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "sticky": "ns",
                        "children": [
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
            # Remove scrollbar buttons/arrows:
            "layout": [
                (
                    "Horizontal.Scrollbar.trough",
                    {
                        "sticky": "we",
                        "children": [
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
                "background": [("disabled", trough_background), ("!disabled", normal_detail)],
                "troughcolor": [("disabled", trough_background)],
                "bordercolor": [("disabled", trough_background)],
                "darkcolor": [("disabled", trough_background)],
                "lightcolor": [("disabled", trough_background)],
            },
        },
        "TButton": {
            "configure": {
                "background": normal_detail,
                "foreground": normal_foreground,
                "lightcolor": normal_detail,
                "darkcolor": normal_detail,
            },
            "map": {
                "foreground": [("disabled", low_foreground), ("alternate", high_foreground)],
                "background": [("pressed", low_detail), ("active", high_detail)],
                "bordercolor": [("alternate", high_detail)],
                "lightcolor": [("active", normal_detail), ("alternate", normal_detail)],
                "darkcolor": [("active", normal_detail), ("alternate", normal_detail)],
            },
        },
        "TCheckbutton": {
            "configure": {
                "indicatorforeground": normal_foreground,
                "indicatorbackground": text_background,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", low_foreground),
                    ("disabled", low_foreground),
                ],
                "indicatorbackground": [
                    ("disabled", "alternate", text_background),
                    ("disabled", text_background),
                ],
            },
        },
        "TRadiobutton": {
            "configure": {
                "indicatorforeground": normal_foreground,
                "indicatorbackground": text_background,
            },
            "map": {
                "indicatorforeground": [
                    ("disabled", "alternate", low_foreground),
                    ("disabled", low_foreground),
                ]
            },
        },
        "Toolbutton": {
            "configure": {"background": frame_background},
            "map": {"background": [("disabled", frame_background), ("active", high_detail)]},
        },
        "CustomToolbutton": {
            "configure": {
                "background": frame_background,
                "activebackground": high_detail,
                "foreground": normal_foreground,
            }
        },
        "TLabel": {"configure": {"foreground": normal_foreground}},
        "Url.TLabel": {"configure": {"foreground": link_foreground}},
        "Tip.TLabel": {"configure": {"foreground": normal_foreground, "background": normal_detail}},
        "Tip.TFrame": {"configure": {"background": low_detail}},
        "TScale": {
            "configure": {
                "background": high_detail,
                "troughcolor": normal_detail,
                "lightcolor": high_detail,
                "darkcolor": high_detail,
                # "bordercolor" : "red",
                # "sliderlength" : 40,
                # "sliderthickness" : 60,
                "gripcount": 0,
            },
            "map": {"background": [], "troughcolor": []},
        },
        "TScale.slider": {
            "configure": {
                "background": "red",
                "troughcolor": "yellow",
                "lightcolor": "green",
                "darkcolor": "white",
                # "sliderlength" : 40,
                # "sliderthickness" : 60,
            }
        },
        "ViewBody.TFrame": {"configure": {"background": text_background}},
        "ViewToolbar.TFrame": {"configure": {"background": active_tab_background}},
        "ViewToolbar.Toolbutton": {"configure": {"background": active_tab_background}},
        "ViewTab.TLabel": {"configure": {"background": active_tab_background, "padding": [5, 0]}},
        "ViewToolbar.TLabel": {
            "configure": {
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "bordercolor": active_tab_background,
                "borderwidth": 1,
                "padding": [scale(4), 0],
            }
        },
        "Active.ViewTab.TLabel": {
            "configure": {
                "foreground": normal_foreground,
                # "font" : "BoldTkDefaultFont",
                "background": active_tab_background,
                "lightcolor": active_tab_background,
                "darkcolor": active_tab_background,
                "relief": "sunken",
                "bordercolor": high_detail,
                "borderwidth": 1,
            },
            "map": {
                "lightcolor": [("hover", active_tab_background)],
                "bordercolor": [("hover", high_detail)],
                "background": [("hover", active_tab_background)],
                "darkcolor": [("hover", active_tab_background)],
                "relief": [("hover", "sunken")],
                "borderwidth": [("hover", 1)],
            },
        },
        "Inactive.ViewTab.TLabel": {
            "configure": {"foreground": normal_foreground},
            "map": {"background": [("hover", high_detail)]},
        },
        "Text": {"configure": {"background": text_background, "foreground": normal_foreground}},
        "Gutter": {"configure": {"background": low_detail, "foreground": low_foreground}},
        "Listbox": {
            "configure": {
                "background": text_background,
                "foreground": normal_foreground,
                "selectbackground": high_detail,
                "selectforeground": high_foreground,
                "disabledforeground": low_foreground,
                "highlightbackground": normal_detail,
                "highlightcolor": high_detail,
                "highlightthickness": 0,
            }
        },
        "Menubar": {
            "configure": {
                # Regular, system-provided Windows menubar doesn't allow changing colors.
                # custom=True replaces it with a custom-built menubar.
                "custom": running_on_windows() if custom_menubar is None else custom_menubar,
                "background": frame_background,
                "foreground": normal_foreground,
                "activebackground": normal_foreground,
                "activeforeground": frame_background,
                "relief": "flat",
            }
        },
        "Menu": {
            "configure": {
                "background": normal_detail,
                "foreground": high_foreground,
                "selectcolor": normal_foreground,
                # "borderwidth": 0, # Interacts badly with right-clicks in Linux
                "activebackground": normal_foreground,
                "activeforeground": frame_background,
                # "activeborderwidth": 0, # Interacts badly with right-clicks in Linux
                "relief": "flat",
            }
        },
        "CustomMenubarLabel.TLabel": {
            "configure": {"padding": [scale(10), scale(2), 0, scale(15)]}
        },
    }


def load_plugin() -> None:
    dark_images = {"tab-close-active": "tab-close-active-dark"}

    for active_tab_background, variant in [("normal_detail", "A"), ("frame_background", "B")]:
        get_workbench().add_ui_theme(
            f"Tidy Dark {variant}",
            "Enhanced Clam",
            tidy(
                frame_background="#252525",
                text_background="#2d2d2d",
                normal_detail="#404040",
                high_detail="#585858",
                low_detail="#404040",
                scrollbar_background="#4d4d4d",
                trough_background="#353535",
                active_tab_background=active_tab_background,
                normal_foreground="#9f9f9f",
                high_foreground="#eeeeee",
                low_foreground="#666666",
                link_foreground="#2293e5",
            ),
            images=dark_images,
        )

        get_workbench().add_ui_theme(
            f"Tidy Dark Green {variant}",
            "Enhanced Clam",
            tidy(
                frame_background="#1D291A",
                text_background="#273627",
                normal_detail="#263E28",
                high_detail="#3c553e",
                low_detail="#33402F",
                scrollbar_background="#415041",
                trough_background="#2b3c2c",
                active_tab_background=active_tab_background,
                normal_foreground="#9E9E9E",
                high_foreground="#eeeeee",
                low_foreground="#5a725b",
                link_foreground="#2293e5",
            ),
            images=dark_images,
        )

        get_workbench().add_ui_theme(
            f"Tidy Dark Blue {variant}",
            "Enhanced Clam",
            tidy(
                frame_background="#1A1C29",
                text_background="#272936",
                normal_detail="#2D3345",
                high_detail="#3C436E",
                low_detail="#2F3640",
                scrollbar_background="#4F5162",
                trough_background="#30313D",
                active_tab_background=active_tab_background,
                normal_foreground="#9E9E9E",
                high_foreground="#eeeeee",
                low_foreground="#5a5c72",
                link_foreground="#567cc4",
            ),
            images=dark_images,
        )

        get_workbench().add_ui_theme(
            f"Tidy Sepia {variant}",
            "Enhanced Clam",
            tidy(
                frame_background="#E8E7DC",
                text_background="#F7F6F0",
                normal_detail="#DEDCC8",
                high_detail="#c6c3bf",
                low_detail="#D4D0B8",
                scrollbar_background="#cdcbb7",
                trough_background="#EEEDE0",
                active_tab_background=active_tab_background,
                normal_foreground="#222222",
                high_foreground="#000000",
                low_foreground="#999999",
                custom_menubar=0,
                link_foreground="#325aa8",
            ),
        )

        get_workbench().add_ui_theme(
            f"Tidy Light {variant}",
            "Enhanced Clam",
            tidy(
                frame_background="#EBEBEB",
                text_background="#ffffff",
                normal_detail="#DFDFDF",
                high_detail="#c6c3bf",
                low_detail="#c6c3bf",
                scrollbar_background="#c6c3bf",
                trough_background="#f5f5f5",
                active_tab_background=active_tab_background,
                normal_foreground="#222222",
                high_foreground="#000000",
                low_foreground="#999999",
                custom_menubar=0,
                link_foreground="#32478d",
            ),
        )
