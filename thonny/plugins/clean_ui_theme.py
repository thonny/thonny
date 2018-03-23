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
          foreground="#9E9E9E"):
    
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    BG = window_background
    TEXT_BG = code_background
    ACTIVE_TAB = detail_background
    FG = foreground
    SELBG = "#2D3D2D"
    SCROLL_BG = ACTIVE_TAB
    SCBORDER = TEXT_BG
    
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
                #bordercolor="red",
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
        
        "Tab" : {
            "configure" : {
                #background=BG,
                #lightcolor="gray",
                "darkcolor" : "red",
                #bordercolor="#4F634A",
                "bordercolor" : detail_background,
                "borderwidth" : 10,
            },
            
            "map" : { # TODO: või TNotebook.Tab ??
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
                "background" : "gray" # TODO:
            },
            
            "map" : {
                "background" : [("disabled", "red"), # TODO:
                                ("!disabled", "gray")]            
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
        
        "Text" : {
            "configure" : {
                "background" : code_background,
                "readonlybackground" : "Yellow"
            }
        },
        
        "TextMargin" : {
            "configure" : {
                "backgronud" : detail_background,
                "foreground" : "#466148" # TODO:
            }
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
    
    

    
    

def dark_syntax_theme():    
    
    default_fg = "#B3B3B3" # TODO: where to specify base color?
    
    string_fg = "#8DC76F"
    open_string_bg = "#453B22"
    
    return {
        "definition"    : {"foreground" : default_fg},
        "magic"         : {"foreground" : default_fg},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        "open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#9A79AD", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : "#FFCABF"},
        "comment"       : {"foreground" : "#C8DEE6"}
    }
    #s.configure("Local.Code", foreground="#BCCAE8")
    #s.configure("MatchedName.Code", background="#193022")
    #s.configure("MatchedParens.Code", foreground="#F0995B")
    #s.configure("OpenParens.Code", background="#193022")
    
    #s.configure("StdOut.Shell", foreground="LightGray")
    #s.configure("StdIn.Shell", foreground="LightBlue")
    #s.configure("StdErr.Shell", foreground="Crimson")

def load_early_plugin():
    get_workbench().add_ui_theme("Clean Dark", "Enhanced Clam", clean)
