from thonny.globals import get_workbench
from thonny.misc_utils import running_on_windows

"""
Darkula
    Main dark: #282828
    Lighter dark (sidebar): #3C3F41
    Scrollbar: #595B5D
    List header: #677896
"""

def clean(window_background="#1D291A",
          code_background="#273627",
          detail_background="#2D452F",
          foreground="#9E9E9E",
          disabled_foreground="#485C49"):
    
    # https://wiki.tcl.tk/37973
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    BG = window_background
    TEXT_BG = code_background
    ACTIVE_TAB = detail_background
    FG = foreground
    SELBG = "#2D3D2D"
    SCROLL_BG = ACTIVE_TAB
    SCBORDER = TEXT_BG
    
    focus_border = "lightgreen"
    nonfocus_border = "#3A5234"
    
    lighter_detail_background = "#3C6E40"
    darker_detail_background = "#33402F"
    
    return {
        "." : {
            "configure" : {
                "foreground" : foreground,
                "background" : window_background,
                "lightcolor" : window_background,
                "darkcolor"  : window_background,
                "bordercolor" : window_background,
            }
        },
        
        "TNotebook" : {
            # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkNotebook.c
            "configure" : {
                #"background" : window_background,
                #??"lightcolor"=BG,
                #??"darkcolor"=BG,
                "bordercolor" : detail_background,
                #tabposition="w",              # Where to place tabs
                "tabmargins" : [1, 0, 0, 0],     # Margins around tab row
                #tabplacement="w",             # How to pack tabs within tab row
                #mintabwidth=20,               # Minimum tab width
                #padding=[40, 40, 40, 40],     # External padding
                #relief="flat",                # not sure whether this does anything
                #borderwidth=0,                # ...
                #expand=[17, 17, 17, 17]        #
            }
        },
        
        "ButtonNotebook.TNotebook" : {
            "configure" : {
                "bordercolor" : window_background,
            }
        },
        
        "AutomaticNotebook.TNotebook" : {
            "configure" : {
                "bordercolor" : window_background,
            }
        },
        
        "TNotebook.Tab" : {
            "configure" : {
                "background" : BG,
                "lightcolor" : "gray",
                "darkcolor" : "red",
                #bordercolor="#4F634A",
                "bordercolor" : detail_background,
                "borderwidth" : 10,
            },
            
            "map" : { 
                "background" : [("selected", detail_background), ("!selected", window_background)],
                "bordercolor" : [("selected", window_background), ("!selected", detail_background)],
                #lightcolor=[("selected", "#333333"), ("!selected", "#333333")],
                #lightcolor=[("selected", "white"), ("!selected", "white")],
                "lightcolor" : [("selected", detail_background), ("!selected", window_background)],
                #expand=[("selected", [1,2,13,4])] # can be used to make selected tab bigger 
                     
            }
        },
        
        "Treeview" : {
            "configure" : {
                "background" : code_background, # TODO: should be set in parent
            },
            "map" : {
                "background" : [('selected', SELBG)],
                "foreground" : [('selected', FG)],
            }
        },
        
        "Treeview.Heading" : {
        # https://stackoverflow.com/questions/32051780/how-to-edit-the-style-of-a-heading-in-treeview-python-ttk
            "configure" : {
                "background" : ACTIVE_TAB,
                "lightcolor" : ACTIVE_TAB,
                "borderwidth" : 0
            },
            "map" : {
                "background" : [("!active", ACTIVE_TAB), ("active", ACTIVE_TAB)]
            }
        },
        
        "TEntry" : {
            "configure" : {
                "fieldbackground" : code_background,
                "lightcolor" : nonfocus_border,
                "insertcolor" : foreground,
            },
            "map" : {
                "background" : [("readonly", code_background)],
                "bordercolor" : [],
                "lightcolor" : [("focus", focus_border)],
                "darkcolor" : []
            }
        },
        
        "TCombobox" : {
            "configure" : {
                "background" : code_background,
                "fieldbackground" : code_background,
                "selectbackground" : code_background,
                "lightcolor" : code_background,
                "darkcolor" : code_background,
                "bordercolor" : code_background,
                "arrowcolor" : foreground,
                "foreground" : foreground,
                "seleftforeground" : foreground,
                #"padding" : [12,2,12,2],
            },
            "map" : {
                "background" : [("active", code_background)],
                "fieldbackground" : [],
                "selectbackground" : [],
                "selectforeground" : [],
                "foreground" : [],
                "arrowcolor" : []
            }
        },
        
        "__ComboboxListbox" : {
            "configure" : {
                "relief" : "solid",
                "borderwidth" : 15,
                "background" : code_background,
                "foreground" : foreground,
            }
        },
        
        "TScrollbar" : {
            "configure" : {
                "gripcount" : 0,
                "borderwidth" : 0,
                "relief" : "flat",
                "darkcolor" : SCROLL_BG,
                "lightcolor" : SCROLL_BG,
                "bordercolor" : SCBORDER,
                "troughcolor" : TEXT_BG,
                #arrowcolor="white"
            },
            "map" : {
                "background" : [("!disabled", SCROLL_BG), ("disabled", SCROLL_BG)],
                "darkcolor" : [("!disabled", TEXT_BG), ("disabled", TEXT_BG)],
                "lightcolor" : [("!disabled", TEXT_BG), ("disabled", TEXT_BG)],
            }
        },
        
        "Vertical.TScrollbar" : {
            # Remove scrollbar buttons/arrows:
            "layout" : [
                ('Vertical.Scrollbar.trough', {'sticky': 'ns', 'children': [
                    ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
                ]})
            ]
        },
        
        "Horizontal.TScrollbar" : {
            # Remove scrollbar buttons/arrows:
            "layout" : [
                ('Horizontal.Scrollbar.trough', {'sticky': 'we', 'children': [
                    ('Horizontal.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
                ]})
            ],
            "map" : {
                # Make disabled Hor Scrollbar invisible
                "background" : [("disabled", BG), ("!disabled", SCROLL_BG)],
                "troughcolor" : [("disabled", BG)],
                "bordercolor" : [("disabled", BG)],
                "darkcolor" : [("disabled", BG)],
                "lightcolor" : [("disabled", BG)],
            }
        },
        
        "TButton" : {
            "configure" : {
                "background" : detail_background,
                "foreground" : foreground,
            },
            
            "map" : {
                "foreground" : [("disabled", disabled_foreground),
                                ("alternate", "white")],
                "background" : [("pressed", darker_detail_background),
                                ("active", lighter_detail_background)],
                "bordercolor": [("alternate", "#1B211C")]           
            }
        },
        
        "Toolbutton" : {
            "configure" : {
                "background" : BG
            },
            
            "map" : {
                "background": [("disabled", BG)]
            }
        },
        
        "__TFrame" : {
            "configure"  : {
                "bordercolor" : "red",
                "lightcolor" : "green",
                "darkcolor" : "blue",
                "borderwidth" : 17,
            }
        },
        
        "TLabel" : {
            "configure"  : {
                "foreground" : FG
            }
        },
        
        "Text" : {
            "configure" : {
                "background" : code_background,
                "foreground" : foreground
            },
        },
        
        "TextMargin" : {
            "configure" : {
                "background" : darker_detail_background,
                "foreground" : "#466148" 
            }
        },
        
        "Listbox" : {
            "configure" : {
                "background" : code_background,
                "foreground" : foreground,
                "highlightbackground" : nonfocus_border,
                "highlightcolor" : focus_border,
                "highlightthickness" : 1,
            },
        },
        
        "Menubar" : {
            "configure" : {
                # Regular, system-provided Windows menubar doesn't allow changing colors.
                # custom=True replaces it with a custom-built menubar.
                "custom" : running_on_windows(), 
                "background" : BG,
                "foreground" : FG,
                "activebackground" : FG, 
                "activeforeground" : BG, 
            }
        },
        
        "Menu" : {
            "configure" : {
                "background" : ACTIVE_TAB,
                "foreground" : "white",
                "selectcolor" : "white",
                "borderwidth" : 0,
                "activebackground" : FG,
                "activeforeground" : BG,
                "activeborderwidth" : 0,
                #relief="flat"
            }
        },
        
        "CustomMenubarLabel.TLabel" : {
            "configure" : {
                "space" : 70,
                "padding" : [12,3,0,2]
            }
        }
    }
    
    

def load_early_plugin():
    get_workbench().add_ui_theme("Clean Dark", "Enhanced Clam", clean)
