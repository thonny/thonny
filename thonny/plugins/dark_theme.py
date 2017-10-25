from thonny.globals import get_workbench

def dark_clam(s):
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    BG = "#2a3b26"
    FG = "LightGray"
    TEXTBG = "#2e4437"
    s.configure(".", 
                background=BG,
                foreground=FG,
                lightcolor=BG,
                darkcolor=BG,
                bordercolor=BG,
                )

    s.configure("Text",
                background=TEXTBG,
                readonlybackground="Yellow")
    
    # TNotebook
    # ('background', 'bordercolor', 'lightcolor', 'darkcolor')
    
    # TNotebook.Tab
    # map: background, lightcolor, padding, expand
    
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkNotebook.c
    s.configure("TNotebook",
                background=BG,
                lightcolor=BG,
                darkcolor=BG,
                #bordercolor="red",
                #tabposition="w",              # Where to place tabs
                #tabmargins=[2, 50, 2, 0],     # Margins around tab row
                #tabplacement="w",             # How to pack tabs within tab row
                #mintabwidth=20,               # Minimum tab width
                #padding=[40, 40, 40, 40],     # External padding
                #relief="flat",                # not sure whether this does anything
                #borderwidth=0,                # ...
                expand=[17, 17, 17, 17]        # 
    )
    s.configure("Tab", 
                background=BG,
                lightcolor=BG,
                darkcolor=BG,
                )
    #print(s.layout("TNotebook"))
    
    #s.configure("ButtonNotebook.Tab", background=BG, 
    #            lightcolor="blue", bordercolor="red", darkcolor="yellow")
    #s.configure("TNotebook.Tab", background=BG,
    #            lightcolor="blue", bordercolor="red", darkcolor="yellow")
    #print(s.map("TNotebook.Tab"))
    s.map("TNotebook.Tab", 
          background=[("selected", "gray"), ("!selected", BG)],
          lightcolor=[("selected", "#333333"), ("!selected", "#333333")],
          #expand=[("selected", [1,2,13,4])] # can be used to make selected tab bigger 
    )
    
    # Treeview
    print(s.map("Treeview"))
    print(s.layout("Treeview"))
    s.configure("Treeview", background=TEXTBG)
    
    
    # Scrollbars
    SCBACK = "#3b4941"
    SCBORDER = "#38443d"
    s.configure("TScrollbar", gripcount=0, borderwidth=0, relief="flat", arrowsize=19,
                darkcolor=SCBACK, lightcolor=SCBACK, bordercolor=SCBORDER,
                troughcolor=BG,
                arrowcolor="white")
    s.map("TScrollbar",
          background=[("disabled", SCBACK), ("!disabled", SCBACK)],
          arrowcolor=[("disabled", SCBACK), ("!disabled", SCBACK)],
          #troughcolor=[("disabled", "red"), ("!disabled", "red")],
          
    )
    
    
    # Menus
    s.configure("Menubar",
                background=BG,
                activebackground=BG, 
                foreground="white")
    
    s.configure("Menu",
                background=BG,
                foreground="white",
                activebackground="white",
                activeforeground="black",
    )
    
    
    # Buttons
    s.configure("TButton",
                background="gray")
    s.map("TButton",
          background=[("disabled", "red"),
                      ("!disabled", "gray")])

    s.configure("Toolbutton",
                background=BG)
    s.map("Toolbutton",
          background=[("disabled", BG)])
    
    # Code
    s.configure("Code", foreground="LightGray")
    s.configure("String.Code", foreground="LightGreen")
    s.configure("StdOut.Shell", foreground="LightGray")
    s.configure("StdIn.Shell", foreground="LightBlue")
    s.configure("StdErr.Shell", foreground="Crimson")

def load_early_plugin():
    get_workbench().add_theme("Dark Clam", "Base Clam", dark_clam)
