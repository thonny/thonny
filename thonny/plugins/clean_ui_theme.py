from thonny.globals import get_workbench
from thonny.misc_utils import running_on_windows


def clean(frame_background,
          text_background,
          normal_detail,
          high_detail,
          low_detail,
          normal_foreground,
          high_foreground,
          low_foreground,
          custom_menubar=None,
          ):
    
    # https://wiki.tcl.tk/37973 (Changing colors)
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    
    
    
    settings = {
        "." : {
            "configure" : {
                "foreground" : normal_foreground,
                "background" : frame_background,
                "lightcolor" : frame_background,
                "darkcolor"  : frame_background,
                "bordercolor" : frame_background,
                "selectbackground"  : high_detail,
                "selectforeground"  : high_foreground,
            },
            
            "map" : {
                "foreground" : [("disabled", low_foreground)],
                "selectbackground" : [("!focus", low_detail)],
                "selectforeground" : [("!focus", normal_foreground)]
            },
        },
        
        "TNotebook" : {
            # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkNotebook.c
            "configure" : {
                "bordercolor" : normal_detail,
                "tabmargins" : [1, 0, 0, 0],     # Margins around tab row
            }
        },
        
        "ButtonNotebook.TNotebook" : {
            "configure" : {
                "bordercolor" : frame_background,
            }
        },
        
        "AutomaticNotebook.TNotebook" : {
            "configure" : {
                "bordercolor" : frame_background,
            }
        },
        
        "TNotebook.Tab" : {
            "configure" : {
                "background" : frame_background,
                "bordercolor" : normal_detail,
                "borderwidth" : 10,
            },
            
            "map" : { 
                "background" : [("selected", normal_detail),
                                ("!selected", "!active", frame_background),
                                ("active", "!selected", high_detail)],
                "bordercolor" : [("selected", frame_background),
                                 ("!selected", normal_detail)],
                "lightcolor" : [("selected", normal_detail),
                                ("!selected", frame_background)],
                     
            }
        },
        
        "Treeview" : {
            "configure" : {
                "background" : text_background, 
            },
            "map" : {
                "background" : [('selected', 'focus', high_detail),
                                ('selected', '!focus', low_detail)],
                "foreground" : [('selected', 'focus', high_foreground),
                                ('selected', '!focus', normal_foreground)],
            }
        },
        
        "Treeview.Heading" : {
        # https://stackoverflow.com/questions/32051780/how-to-edit-the-style-of-a-heading-in-treeview-python-ttk
            "configure" : {
                "background" : normal_detail,
                "lightcolor" : normal_detail,
                "borderwidth" : 0
            },
            "map" : {
                "background" : [("!active", normal_detail),
                                ("active", normal_detail)]
            }
        },
        
        "TEntry" : {
            "configure" : {
                "fieldbackground" : text_background,
                "lightcolor" : normal_detail,
                "insertcolor" : normal_foreground,
            },
            "map" : {
                "background" : [("readonly", text_background)],
                "bordercolor" : [],
                "lightcolor" : [("focus", high_detail)],
                "darkcolor" : []
            }
        },
        
        "TCombobox" : {
            "configure" : {
                "background" : text_background,
                "fieldbackground" : text_background,
                "selectbackground" : text_background,
                "lightcolor" : text_background,
                "darkcolor" : text_background,
                "bordercolor" : text_background,
                "arrowcolor" : normal_foreground,
                "foreground" : normal_foreground,
                "seleftforeground" : normal_foreground,
                #"padding" : [12,2,12,2],
            },
            "map" : {
                "background" : [("active", text_background)],
                "fieldbackground" : [],
                "selectbackground" : [],
                "selectforeground" : [],
                "foreground" : [],
                "arrowcolor" : []
            }
        },
        
        "TScrollbar" : {
            "configure" : {
                "gripcount" : 0,
                "borderwidth" : 0,
                "relief" : "flat",
                "darkcolor" : normal_detail,
                "lightcolor" : normal_detail,
                "bordercolor" : text_background,
                "troughcolor" : text_background,
                #arrowcolor="white"
            },
            "map" : {
                "background" : [("!disabled", normal_detail), ("disabled", normal_detail)],
                "darkcolor" : [("!disabled", text_background), ("disabled", text_background)],
                "lightcolor" : [("!disabled", text_background), ("disabled", text_background)],
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
                "background" : [("disabled", frame_background), ("!disabled", normal_detail)],
                "troughcolor" : [("disabled", frame_background)],
                "bordercolor" : [("disabled", frame_background)],
                "darkcolor" : [("disabled", frame_background)],
                "lightcolor" : [("disabled", frame_background)],
            }
        },
        
        "TButton" : {
            "configure" : {
                "background" : normal_detail,
                "foreground" : normal_foreground,
            },
            
            "map" : {
                "foreground" : [("disabled", low_foreground),
                                ("alternate", high_foreground)],
                "background" : [("pressed", low_detail),
                                ("active", high_detail)],
                "bordercolor": [("alternate", high_detail)]           
            }
        },
        
        "Toolbutton" : {
            "configure" : {
                "background" : frame_background
            },
            
            "map" : {
                "background": [("disabled", frame_background)]
            }
        },
        
        "TLabel" : {
            "configure"  : {
                "foreground" : normal_foreground
            }
        },
        
        "Text" : {
            "configure" : {
                "background" : text_background,
                "foreground" : normal_foreground
            },
        },
        
        "Gutter" : {
            "configure" : {
                "background" : low_detail,
                "foreground" : low_foreground 
            }
        },
        
        "Listbox" : {
            "configure" : {
                "background" : text_background,
                "foreground" : normal_foreground,
                "selectbackground" : high_detail,
                "selectforeground" : high_foreground,
                "disabledforeground" : low_foreground,
                "highlightbackground" : normal_detail,
                "highlightcolor" : high_detail,
                "highlightthickness" : 1,
            },
        },
        "Menubar" : {
            "configure" : {
                # Regular, system-provided Windows menubar doesn't allow changing colors.
                # custom=True replaces it with a custom-built menubar.
                "custom" : running_on_windows() if custom_menubar is None else custom_menubar, 
                "background" : frame_background,
                "foreground" : normal_foreground,
                "activebackground" : normal_foreground, 
                "activeforeground" : frame_background, 
            }
        },
        
        "Menu" : {
            "configure" : {
                "background" : normal_detail,
                "foreground" : high_foreground,
                "selectcolor" : normal_foreground,
                "borderwidth" : 0,
                "activebackground" : normal_foreground,
                "activeforeground" : frame_background,
                "activeborderwidth" : 0,
                "relief" : "flat"
            }
        },
        
        "CustomMenubarLabel.TLabel" : {
            "configure" : {
                "space" : 70,
                "padding" : [12,3,0,2]
            }
        }
    }
    
    
    return settings
    
    
def load_early_plugin():
    get_workbench().add_ui_theme("Clean Dark Green", "Enhanced Clam", 
        clean(frame_background="#1D291A",
              text_background="#273627",
              normal_detail="#2D452F",
              high_detail="#3C6E40",
              low_detail="#33402F",
              normal_foreground="#9E9E9E",
              high_foreground="#eeeeee",
              low_foreground="#485C49",
        )
    )

    get_workbench().add_ui_theme("Clean Dark Blue", "Enhanced Clam", 
        clean(frame_background="#1A1C29",
              text_background="#272936",
              normal_detail="#2D3345",
              high_detail="#3C436E",
              low_detail="#2F3640",
              normal_foreground="#9E9E9E",
              high_foreground="#eeeeee",
              low_foreground="#484A5C",
        )
    )

    get_workbench().add_ui_theme("Clean Sepia", "Enhanced Clam", 
        clean(frame_background="#E8E7DC",
              text_background="#F7F6F0",
              normal_detail="#DEDCC8",
              high_detail="#eeebe7",
              low_detail="#D4D0B8",
              normal_foreground="#222222",
              high_foreground="#000000",
              low_foreground="#999999",
              custom_menubar=0,
        )
    )

