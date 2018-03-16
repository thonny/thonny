import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.font import nametofont

root = tk.Tk()

b1 = ttk.Button(root, text="essa")
b1.grid(pady=10)

b2 = ttk.Button(root, text="tessa")
b2.grid(pady=10)

e1 = ttk.Entry(root)
e1.grid(pady=10, padx=10)

s = ttk.Style()
s.theme_use("clam")

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

settings = {
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
            "width" : "11", 
            "padding" : 5, 
            "relief" : "raised"
        },
        "mape" : {
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
            # TODO:
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

s.theme_create("clam2", "clam", settings)
s.theme_create("clam3", "clam2")
s.theme_use("clam3")


root.mainloop()