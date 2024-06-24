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
                    ("selected", normal_detail),
                    ("!selected", "!active", frame_background),
                    ("active", "!selected", frame_background),
                ],
                "bordercolor": [("selected", frame_background), ("!selected", low_detail)],
                "lightcolor": [("selected", normal_detail), ("!selected", frame_background)],
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
                "activebackground": normal_detail,
                "indicatorbackground": normal_detail,
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
                "background": normal_detail,
                "lightcolor": normal_detail,
                "darkcolor": normal_detail,
                "borderwidth": 1,
                "topmost_pixels_to_hide": 2,
            },
            "map": {"background": [("!active", normal_detail), ("active", normal_detail)]},
        },
        "TEntry": {
            "configure": {
                "fieldbackground": text_background,
                "lightcolor": normal_detail,
                "insertcolor": normal_foreground,
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
                "bordercolor": text_background,
                "arrowcolor": normal_foreground,
                "foreground": normal_foreground,
                "seleftforeground": normal_foreground,
                # "padding" : [12,2,12,2],
            },
            "map": {
                "background": [("active", text_background)],
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
                "padding": scale(1.1),
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
                # Make disabled Hor Scrollbar invisible
                "background": [("disabled", frame_background), ("!disabled", normal_detail)],
                "troughcolor": [("disabled", normal_detail)],
                "bordercolor": [("disabled", frame_background)],
                "darkcolor": [("disabled", frame_background)],
                "lightcolor": [("disabled", frame_background)],
            },
        },
        "TButton": {
            "configure": {"background": normal_detail, "foreground": normal_foreground},
            "map": {
                "foreground": [("disabled", low_foreground), ("alternate", high_foreground)],
                "background": [("pressed", low_detail), ("active", high_detail)],
                "bordercolor": [("alternate", high_detail)],
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
        "Tip.TLabel": {
            "configure": {"foreground": normal_foreground, "background": normal_foreground}
        },
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
        "ViewToolbar.TFrame": {"configure": {"background": normal_detail}},
        "ViewToolbar.Toolbutton": {"configure": {"background": normal_detail}},
        "ViewTab.TLabel": {"configure": {"background": normal_detail, "padding": [5, 0]}},
        "ViewToolbar.TLabel": {
            "configure": {"background": normal_detail, "padding": [scale(4), 0]}
        },
        "Active.ViewTab.TLabel": {
            "configure": {
                "foreground": high_foreground,
                # "font" : "BoldTkDefaultFont",
                "background": text_background,
            }
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

    get_workbench().add_ui_theme(
        "Tidy Dark",
        "Enhanced Clam",
        tidy(
            frame_background="#252525",
            text_background="#2d2d2d",
            normal_detail="#404040",
            high_detail="#585858",
            low_detail="#404040",
            scrollbar_background="#2d2d2d",
            trough_background="#3D3D3D",
            normal_foreground="#9f9f9f",
            high_foreground="#eeeeee",
            low_foreground="#666666",
            link_foreground="#2293e5",
        ),
        images=dark_images,
    )

    dark_tip_background = ("#b8c28d",)

    get_workbench().add_ui_theme(
        "Tidy Dark Green",
        "Enhanced Clam",
        tidy(
            frame_background="#1D291A",
            text_background="#273627",
            normal_detail="#263E28",
            high_detail="#264d26",
            low_detail="#33402F",
            scrollbar_background="#273627",
            trough_background="#2D452F",
            normal_foreground="#9E9E9E",
            high_foreground="#eeeeee",
            low_foreground="#5a725b",
            link_foreground="#2293e5",
        ),
        images=dark_images,
    )

    get_workbench().add_ui_theme(
        "Tidy Dark Blue",
        "Enhanced Clam",
        tidy(
            frame_background="#1A1C29",
            text_background="#272936",
            normal_detail="#2D3345",
            high_detail="#3C436E",
            low_detail="#2F3640",
            scrollbar_background="#4F5162",
            trough_background="#30313D",
            normal_foreground="#9E9E9E",
            high_foreground="#eeeeee",
            low_foreground="#5a5c72",
            link_foreground="#567cc4",
        ),
        images=dark_images,
    )

    get_workbench().add_ui_theme(
        "Tidy Sepia",
        "Enhanced Clam",
        tidy(
            frame_background="#E8E7DC",
            text_background="#F7F6F0",
            normal_detail="#DEDCC8",
            high_detail="#c6c3bf",
            low_detail="#D4D0B8",
            scrollbar_background="#cdcbb7",
            trough_background="#DEDCC8",
            normal_foreground="#222222",
            high_foreground="#000000",
            low_foreground="#999999",
            custom_menubar=0,
            link_foreground="#325aa8",
        ),
    )
