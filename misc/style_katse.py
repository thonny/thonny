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

settings = {
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

s.theme_create("win2", "xpnative", settings)
s.theme_use("win2")


root.mainloop()