from thonny.globals import get_workbench
from thonny.misc_utils import running_on_linux
from thonny.ui_utils import CALM_WHITE

def _treeview_settings():
    light_blue = "#ADD8E6" 
    light_grey = "#D3D3D3"
    
    if running_on_linux():
        bg_sel_focus = light_blue
        fg = "black"
    else:
        bg_sel_focus = 'SystemHighlight'
        fg = 'SystemHighlightText'
    
    return {
        "Treeview" : {
            "configure" : {
                "background" : "white", # TODO: use sys colors , Not required in Python 3 ???
                "font" : "TreeviewFont"
            },
            "map" : {
                "background" : [('selected', 'focus', bg_sel_focus),
                                ('selected', '!focus', light_grey)],
                "foreground" : [('selected', fg)]
            },
            "layout" : [
                # get rid of borders
                ('Treeview.treearea', {'sticky': 'nswe'})
            ]
        }
    }

def _menubutton_settings():
    return {
        "TMenubutton" : {
            "configure" : {
                "padding" : 14
            },
            "layout" : [
                ('Menubutton.dropdown', {'side': 'right', 'sticky': 'ns'}),
                ('Menubutton.button', {'children': [
                    #('Menubutton.padding', {'children': [
                        ('Menubutton.label', {'sticky': ''})
                    #], 'expand': '1', 'sticky': 'we'})
                ], 'expand': '1', 'sticky': 'nswe'})
            ]
        }
    }

def _paned_window_settings():
    return {
        "Sash" : {
            "configure" : {
                "sashthickness" : 10
            }
        }
    }


def _menu_settings():
    return {
        "Menubar" : {
            "configure" : {
                "activeborderwidth" : 0
            }
        }
    }


def _text_settings():
    return {
        "Text" : {
            "configure" : {
                "background" : "SystemWindow",
                "foreground" : "SystemWindowText"
            },
        },
        "Syntax.Text" : {
            "map" : {
                "background" : [("readonly", "Yellow")]
            }
        },
        "Gutter" : {
            "configure" : {
                "background" : '#e0e0e0',
                "foreground" : '#999999' 
            }
        },
    }


def clam():
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    defaultfg =      "#000000"
    disabledfg =     "#999999"
    frame =          "#dcdad5"
    window =         "#ffffff"
    dark =           "#cfcdc8"
    darker =         "#bab5ab"
    darkest =        "#9e9a91"
    lighter =        "#eeebe7"
    selectbg =       "#4a6984"
    selectfg =       "#ffffff"
    altindicator =   "#5895bc"
    disabledaltindicator =    "#a0a0a0"
    
    return {
        "." : {
            "configure" : {
                "background"        : frame,
                "foreground"        : defaultfg,
                "bordercolor"       : darkest,
                "darkcolor"         : dark,
                "lightcolor"        : lighter,
                "troughcolor"       : darker,
                "selectbackground"  : selectbg,
                "selectforeground"  : selectfg,
                "selectborderwidth" : 0,
                "font" : "TkDefaultFont",
            },
            
            "map" : {
                "background" : [("disabled", frame), 
                                ("active", lighter)],
                "foreground" : [("disabled", disabledfg)],
                "selectbackground" : [("!focus", darkest)],
                "selectforeground" : [("!focus", "white")]
            },
        },
            
        "TButton" : {
            "configure" : {
                "anchor" : "center", 
                "width" : 11, 
                "padding" : 5, 
                "relief" : "raised"
            },
            "map" : {
                "background" : [("disabled", frame),
                                ("pressed", darker),
                                ("active", lighter)],
                "lightcolor" : [("pressed", darker)],
                "darkcolor"  : [("pressed", darker)],
                "bordercolor": [("alternate", "#000000")],
            }
        },
        
        "Toolbutton" : {
            "configure" : {
                "anchor" : "center",
                "padding" : 2,
                "relief" : "flat"
            },
            "map" : {
                "relief" : [("disabled",  "flat"),
                            ("selected", "sunken"),
                            ("pressed", "sunken"),
                            ("active", "raised")],
                "background" : [("disabled", frame),
                                ("pressed", darker),
                                ("active", lighter)],
                "lightcolor" : [("pressed", darker)],
                "darkcolor" : [("pressed", darker)]
            }
        },
        
        "TCheckbutton" : {
            "configure" : {
                "indicatorbackground" : "#ffffff",
                "indicatormargin" : [1, 1, 4, 1],
                "padding" :  2,
            },
            "map" : {
                "indicatorbackground" : [("pressed", frame),
                                         ("!disabled", "alternate", altindicator),
                                         ("disabled", "alternate", disabledaltindicator),
                                         ("disabled", frame)]
            }
        },
        
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton" : {
            "configure" : {
                "indicatorbackground" : "#ffffff",
                "indicatormargin" : [1, 1, 4, 1],
                "padding" :  2,
            },
            "map" : {
                "indicatorbackground" : [("pressed", frame),
                                         ("!disabled", "alternate", altindicator),
                                         ("disabled", "alternate", disabledaltindicator),
                                         ("disabled", frame)]
            }
        },
        
        "TMenubutton" : {
            "configure" : {
                "width" : 11,
                "padding" : 5,
                "relief" : "raised"
            }
        },
        
        "TEntry" : {
            "configure" : {
                "padding" : 1,
                "insertwidth" : 1
            },
            "map" : {
                "background" : [("readonly", frame)],
                "bordercolor" : [("focus", selectbg)],
                "lightcolor" : [("focus", "#6f9dc6")],
                "darkcolor" : [("focus", "#6f9dc6")]
            }
        },
        
        "TCombobox" : {
            "configure" : {
                "padding" : [4,2,2,2],
                "insertwidth" : 1,
            },
            "map" : {
                "background" : [("active", lighter),
                                ("pressed", lighter)],
                "fieldbackground" : [("readonly", "focus", selectbg),
                                     ("readonly", frame)],
                "foreground" : [("readonly", "focus", selectfg)],
                "arrowcolor" : [("disabled", disabledfg)]
            }
        },
        
        "ComboboxPopdownFrame" : {
            "configure" : {
                "relief" : "solid",
                "borderwidth" : 1
            }
        },
        
        "TSpinbox" : {
            "configure" : {
                "arrowsize" : 10,
                "padding" : [2, 0, 10, 0],
            },
            "map" : {
                "background" : [("readonly", frame)],
                "arrowcolor" : [("disabled", disabledfg)]
            }
        },
        
        "TNotebook.Tab" : {
            "configure" : {
                "padding" : [6, 2, 6, 2]
            },
            "map" : {
                "padding" : [("selected", [6, 4, 6, 2])],
                "background" : [("selected", frame), 
                                ("",        darker)],
                "lightcolor" : [("selected", lighter), 
                                ("",        dark)], 
            }
        },
        
        "Treeview" : {
            "configure" : {
                "background" : window,
            },
            "map" : {
                "background" : [("disabled", frame),
                                ("!disabled", "!selected", window),
                                ("selected", selectbg)],
                "foreground" : [("disabled", disabledfg),
                                ("!disabled", "!selected", defaultfg),
                                ("selected", selectfg)]        
            }
        },
        
        # Treeview heading
        "Heading" : {
            "configure" : {
                "font" : "TkHeadingFont",
                "relief" : "raised",
                "padding" : [3, 3, 3, 3]
            }
        },
        
        "TLabelframe" : {
            "configure" : {
                "labeloutside" : True,
                "labelmargins" : [0, 0, 0, 4]
            }
        },
        
        "TProgressbar" : {
            "configure" : {
                "background" : frame
            }
        },
        
        "Sash" : {
            "configure" : {
                "sashthickness" : 6,
                "gripcount" : 10
            }
        }
    }
    

def xpnative():
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/xpTheme.tcl
    return {
        "." : {
            "configure" : {
                "background"        : "SystemButtonFace",
                "foreground"        : "SystemWindowText",
                "selectbackground"  : "SystemHighlightText",
                "selectforeground"  : "SystemHighlight",
                "font" : "TkDefaultFont",
            },
            
            "map" : {
                "foreground" : [("disabled", "SystemGrayText")],
            },
        },
            
        "TButton" : {
            "configure" : {
                "anchor" : "center", 
                "width" : 11, 
                "padding" : [1, 1], 
            },
        },
        
        "Toolbutton" : {
            "configure" : {
                "padding" :[4, 4],
            },
        },
        
        "TCheckbutton" : {
            "configure" : {
                "padding" :  2,
            },
        },
        
        # TRadiobutton has same style as TCheckbutton
        "TRadiobutton" : {
            "configure" : {
                "padding" :  2,
            },
        },
        
        "TMenubutton" : {
            "configure" : {
                "padding" : [8, 4],
            }
        },
        
        "TEntry" : {
            "configure" : {
                "padding" : [2, 2, 2, 4],
            },
            "map" : {
                "selectbackground" : [("!focus", "SystemWindow")],
                "selectforeground" : [("!focus", "SystemWindowText")]
            }
        },
        
        "TCombobox" : {
            "configure" : {
                "padding" : 2,
            },
            "map" : {
                "selectbackground" : [("!focus", "SystemWindow")],
                "selectforeground" : [("!focus", "SystemWindowText")],
                "foreground" : [("disabled", "SystemGrayText"),
                                ("readonly", "focus", "SystemHighlightText")],
                "focusfill" : [("readonly", "focus", "SystemHighlight")]
            }
        },
        
        "ComboboxPopdownFrame" : {
            "configure" : {
                "relief" : "solid",
                "borderwidth" : 1
            }
        },
        
        "TSpinbox" : {
            "configure" : {
                "padding" : [2, 0, 14, 0],
            },
            "map" : {
                "selectbackground" : [("!focus", "SystemWindow")],
                "selectforeground" : [("!focus", "SystemWindowText")],
            }
        },
        
        "TNotebook" : {
            "configure" : {
                "tabmargins" : [2, 2, 2, 0]
            }
        },
        
        "TNotebook.Tab" : {
            "map" : {
                "expand" : [("selected", [2, 2, 2, 2])],
            }
        },
        
        "Treeview" : {
            "configure" : {
                "background" : "SystemWindow",
            },
            "map" : {
                "background" : [("disabled", "SystemButtonFace"),
                                ("!disabled", "!selected", "SystemWindow"),
                                ("selected", "SystemHighlight")],
                "foreground" : [("disabled", "SystemGrayText"),
                                ("!disabled", "!selected", "SystemWindowText"),
                                ("selected", "SystemHighlightText")]        
            }
        },
        
        
        "Heading" : { # Treeview heading
            "configure" : {
                "font" : "TkHeadingFont",
                "relief" : "raised"
            }
        },
        
        "TLabelframe.Label" : {
            "configure" : {
                "foreground" : "#0046d5",
            }
        },
    }

def windows():
    return [
        xpnative(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        {
            "TNotebook" : {
                "configure" : {
                    # With tabmargins I can get a gray line below tab, which separates
                    # tab content from label
                    "tabmargins" : [2, 2, 2, 2]
                }
            },
            "Tab" : {
                "configure" : {
                    "padding" : [3,1,3,0]
                }
            },
            "ButtonNotebook.TNotebook.Tab" : {
                "configure" : {
                    "padding" : (4,1,1,0)
                }
            },
        }
    ]

def enhanced_clam():
    return [
        clam(),
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        _text_settings(),
        {
            "Tab" : {
                "configure" : {
                    "padding" : (40,1,0,0)
                }
            },
            "ButtonNotebook.Tab" : {
                "configure" : {
                    "padding" : (6,4,2,3)
                }
            },
            "TScrollbar" : {
                "configure" : {
                    "gripcount" : 0
                }
            },
        }
    ]

def enhanced_aqua():
    return [
        _treeview_settings(),
        _menubutton_settings(),
        _paned_window_settings(),
        _menu_settings(),
        {
            "Tab" : {
                "configure" : {
                    "padding" : (4,1,0,0)
                }
            },
            "ButtonNotebook.Tab" : {
                "configure" : {
                    "padding" : (4,1,1,3)
                }
            }
        }
    ]



def load_early_plugin():
    from tkinter import ttk
    original_themes = ttk.Style().theme_names() 
    
    # load all base themes
    for name in original_themes:
        if name == "clam":
            settings = clam()
        elif name == "xpnative":
            settings = xpnative()
        else:
            settings = {}
             
        get_workbench().add_ui_theme(name, None, settings)
    
    get_workbench().add_ui_theme("Enhanced Clam", "clam", enhanced_clam())
    
    if "xpnative" in original_themes:
        get_workbench().add_ui_theme("Windows", "xpnative", windows())
    
    if "aqua" in original_themes:
        get_workbench().add_ui_theme("Enhanced Aqua", "aqua", enhanced_aqua())
    

    if "Windows" in get_workbench().get_usable_ui_theme_names():
        get_workbench().set_default("view.ui_theme", "Windows")
        
    elif "Enhanced Clam" in get_workbench().get_usable_ui_theme_names():
        get_workbench().set_default("view.ui_theme", "Enhanced Clam")
        
    
    