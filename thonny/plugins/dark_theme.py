from thonny.globals import get_workbench

"""
Darkula
    Main dark: #282828
    Lighter dark (sidebar): #3C3F41
    Scrollbar: #595B5D
    List header: #677896
"""


def dark_clam(s):
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    BG = "#2a3b26"
    FG = "#9E9E9E"
    TEXTBG = "#2e4437"
    ACTIVE_TAB = "#677896"
    ACTIVE_TAB = "#4C6346"
    ACTIVE_TAB = "#344D36"
    
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
    
    s.configure("TextMargin",
                background=ACTIVE_TAB,
                foreground="#466148")
    
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
                tabmargins=[2, 0, 0, 0],     # Margins around tab row
                #tabplacement="w",             # How to pack tabs within tab row
                #mintabwidth=20,               # Minimum tab width
                #padding=[40, 40, 40, 40],     # External padding
                #relief="flat",                # not sure whether this does anything
                #borderwidth=0,                # ...
                #expand=[17, 17, 17, 17]        #
                 
    )
    
    
    s.configure("Tab", 
                background=BG,
                #lightcolor="gray",
                darkcolor="red",
                #bordercolor="#4F634A",
                bordercolor=ACTIVE_TAB,
                borderwidth=10,
                )
    #print(s.layout("TNotebook"))
    
    #s.configure("ButtonNotebook.Tab", background=BG, 
    #            lightcolor="blue", bordercolor="red", darkcolor="yellow")
    #s.configure("TNotebook.Tab", background=BG,
    #            lightcolor="blue", bordercolor="red", darkcolor="yellow")
    #print(s.map("TNotebook.Tab"))
    s.map("TNotebook.Tab", 
          background=[("selected", ACTIVE_TAB), ("!selected", BG)],
          #lightcolor=[("selected", "#333333"), ("!selected", "#333333")],
          #lightcolor=[("selected", "white"), ("!selected", "white")],
          lightcolor=[("selected", ACTIVE_TAB), ("!selected", BG)],
          #expand=[("selected", [1,2,13,4])] # can be used to make selected tab bigger 
    )
    
    # Treeview
    # https://stackoverflow.com/questions/32051780/how-to-edit-the-style-of-a-heading-in-treeview-python-ttk
    print(s.map("Treeview.Heading"))
    print(s.layout("Treeview.Heading"))
    print(s.element_options("Treeheading.border"))
    s.configure("Treeview", background=TEXTBG)
    s.configure("Treeview.Heading", background=ACTIVE_TAB, lightcolor=ACTIVE_TAB, borderwidth=0)
    
    
    # Scrollbars
    SCROLL_BG = "#334036"
    #SCROLL_BG = "#2D3D2A"
    SCBORDER = "#38443d"
    
    # Remove scrollbar buttons/arrows:
    s.layout("Vertical.TScrollbar", 
        [('Vertical.Scrollbar.trough', {'sticky': 'ns', 'children': [
            # Uncomment if you want the buttons back
            #('Vertical.Scrollbar.uparrow', {'side': 'top', 'sticky': ''}),
            #('Vertical.Scrollbar.downarrow', {'side': 'bottom', 'sticky': ''}),
            ('Vertical.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
        ]})]
    )
    
    s.layout("Horizontal.TScrollbar", 
        [('Horizontal.Scrollbar.trough', {'sticky': 'we', 'children': [
            # Uncomment if you want the buttons back
            #('Horizontal.Scrollbar.leftarrow', {'side': 'left', 'sticky': ''}),
            #('Horizontal.Scrollbar.rightarrow', {'side': 'right', 'sticky': ''}), 
            ('Horizontal.Scrollbar.thumb', {'expand': '1', 'sticky': 'nswe'})
        ]})]
    )
    
    
    s.configure("TScrollbar", gripcount=0, borderwidth=0, relief="flat", arrowsize=19,
                darkcolor=SCROLL_BG, lightcolor=SCROLL_BG, bordercolor=SCBORDER,
                troughcolor=BG,
                #arrowcolor="white"
                )
    
    s.map("TScrollbar",
          background=[("disabled", SCROLL_BG), ("!disabled", SCROLL_BG)],
          #arrowcolor=[("disabled", BG), ("!disabled", SCROLL_BG)],
          #troughcolor=[("disabled", "red"), ("!disabled", "red")],
    )
    print(s.map("TScrollbar"))
    
    
    
    
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
    s.configure("Code", foreground="#B3B3B3")
    s.configure("String.Code", foreground="#8DC76F")
    s.configure("Keyword.Code", foreground="#9A79AD")
    
    s.configure("StdOut.Shell", foreground="LightGray")
    s.configure("StdIn.Shell", foreground="LightBlue")
    s.configure("StdErr.Shell", foreground="Crimson")

def load_early_plugin():
    get_workbench().add_theme("Dark Clam", "Base Clam", dark_clam)
