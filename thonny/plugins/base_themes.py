from thonny.globals import get_workbench
from thonny.misc_utils import running_on_linux

def tweak_treeviews(style):
    # get rid of Treeview borders
    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe'})
    ])
    
    # necessary for Python 2.7 TODO: doesn't help for aqua
    style.configure("Treeview", background="white")
    
    #style.configure("Treeview", font='helvetica 14 bold')
    style.configure("Treeview", font=get_workbench().get_font("TreeviewFont"))

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

def tweak_menubuttons(style):
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

def tweak_paned_windows(style):
    style.configure("Sash", sashthickness=10)


def tweak_menus(style):
    style.configure("Menubar", 
                    activeborderwidth=0)

def set_palette(keywords, numbers, strings, open_strings):
    pass

def base_windows(style):
    style.theme_use("xpnative")
    # Notebooks
    # With tabmargins I can get a gray line below tab, which separates
    # tab content from label
    style.configure("TNotebook", tabmargins=[2, 2, 2, 2])
    style.configure("Tab", padding=[3,1,3,0])
    style.configure("ButtonNotebook.TNotebook.Tab", padding=(4,1,1,0))
    
    # other widgets
    tweak_menus(style)
    tweak_treeviews(style)
    tweak_menubuttons(style)
    tweak_paned_windows(style)

def base_clam(style):
    style.theme_use("clam")
    style.configure("Tab", padding=(4,1,0,0))
    style.configure("ButtonNotebook.Tab", padding=(6,4,2,3))
        
    # other widgets
    tweak_menus(style)
    tweak_treeviews(style)
    tweak_menubuttons(style)
    tweak_paned_windows(style)

def base_aqua(style):
    style.theme_use("aqua")
    style.configure("Tab", padding=(4,1,0,0))
    style.configure("ButtonNotebook.Tab", padding=(4,1,1,3))
    
    # other widgets
    tweak_menus(style)
    tweak_treeviews(style)
    tweak_menubuttons(style)
    tweak_paned_windows(style)


def clam_settings():
    # Transcribed from https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    colors = {
        "disabledfg" :     "#999999",
        "frame" :          "#dcdad5",
        "window" :         "#ffffff",
        "dark" :           "#cfcdc8",
        "darker" :         "#bab5ab",
        "darkest" :        "#9e9a91",
        "lighter" :        "#eeebe7",
        "lightest" :       "#ffffff",
        "selectbg" :       "#4a6984",
        "selectfg" :       "#ffffff",
        "altindicator" :   "#5895bc",
        "disabledaltindicator" :    "#a0a0a0",
    }
    
    return {
        "." : {
            "configure" : {
                "background"        : colors["frame"],
                "foreground"        : "black",
                "bordercolor"       : colors["darkest"],
                "darkcolor"         : colors["dark"],
                "lightcolor"        : colors["lighter"],
                "troughcolor"       : colors["darker"],
                "selectbackground"  : colors["selectbg"],
                "selectforeground"  : colors["selectfg"],
                "selectborderwidth" : 0,
                "font" : "TkDefaultFont",
            },
            
            "map" : {
                "background" : [("disabled", colors["frame"]), 
                                ("active", colors["lighter"])],
                "foreground" : [("disabled", colors["disabledfg"])],
                "selectbackground" : [("!focus", colors["darkest"])],
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
                "background" : [("disabled", colors["frame"]),
                                ("pressed", colors["darker"]),
                                ("active", colors["lighter"])],
                "lightcolor" : [("pressed", colors["darker"])],
                "darkcolor"  : [("pressed", colors["darker"])],
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
                "background" : [("disabled", colors["frame"]),
                                ("pressed", colors["darker"]),
                                ("active", colors["lighter"])],
                "lightcolor" : [("pressed", colors["darker"])],
                "darkcolor" : [("pressed", colors["darker"])]
            }
        },
        
        "TCheckbutton" : {
            "configure" : {
                "indicatorbackground" : "#ffffff",
                "indicatormargin" : [1, 1, 4, 1],
                "padding" :  2,
            },
            "map" : {
                "indicatorbackground" : [("pressed", colors["frame"]),
                                         ("!disabled", "alternate", colors["altindicator"]),
                                         ("disabled", "alternate", colors["disabledaltindicator"]),
                                         ("disabled", colors["frame"])]
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
                "indicatorbackground" : [("pressed", colors["frame"]),
                                         ("!disabled", "alternate", colors["altindicator"]),
                                         ("disabled", "alternate", colors["disabledaltindicator"]),
                                         ("disabled", colors["frame"])]
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
                "background" : [("readonly", colors["frame"])],
                "bordercolor" : [("focus", colors["selectbg"])],
                "lightcolor" : [("focus", "#6f9dc6")],
                "darkcolor" : [("focus", "#6f9dc6")]
            }
        },
        
        "TCombobox" : {
            "configure" : {
                "padding" : 1,
                "insertwidth" : 1,
            },
            "map" : {
                "background" : [("active", colors["lighter"]),
                                ("pressed", colors["lighter"])],
                "fieldbackground" : [("readonly", "focus", colors["selectbg"]),
                                     ("readonly", colors["frame"])],
                "foreground" : [("readonly", "focus", colors["selectfg"])],
                "arrowcolor" : [("disabled", colors["disabledfg"])]
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
                "background" : [("readonly", colors["frame"])],
                "arrowcolor" : [("disabled", colors["disabledfg"])]
            }
        },
        
        "TNotebook.Tab" : {
            "configure" : {
                "padding" : [6, 2, 6, 2]
            },
            "map" : {
                "padding" : [("selected", [6, 4, 6, 2])],
                "background" : [("selected", colors["frame"]), 
                                ("",        colors["darker"])],
                "lightcolor" : [("selected", colors["lighter"]), 
                                ("",        colors["dark"])], 
            }
        },
        
        "Treeview" : {
            "configure" : {
                "background" : colors["window"],
            },
            "map" : {
                "background" : [("disabled", colors["frame"]),
                                ("!disabled", "!selected", colors["window"]),
                                ("selected", colors["selectbg"])],
                "foreground" : [("disabled", colors["disabledfg"]),
                                ("!disabled", "!selected", "black"),
                                ("selected", colors["selectfg"])]        
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
                "background" : colors["frame"]
            }
        },
        
        "Sash" : {
            "configure" : {
                "sashthickness" : 6,
                "gripcount" : 10
            }
        }
    }

def windows_settings():
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

def load_early_plugin():
    from tkinter import ttk
    
    # load all base themes
    for name in ttk.Style().theme_names():
        if name == "clam":
            settings = clam_settings()
        elif name == "xpnative":
            settings = windows_settings()
        else:
            settings = {}
             
        get_workbench().add_theme(name, None, settings)
        
    
    