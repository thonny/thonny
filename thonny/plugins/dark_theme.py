from thonny.globals import get_workbench
from thonny.misc_utils import running_on_windows

"""
Darkula
    Main dark: #282828
    Lighter dark (sidebar): #3C3F41
    Scrollbar: #595B5D
    List header: #677896
"""
from thonny.plugins import base_themes


def clean(s,
          window_background="#1D291A",
          code_background="#273627",
          detail_background="#2D452F",
          foreground="#9E9E9E"):
    
    base_themes.base_clam(s)
    # https://github.com/tcltk/tk/blob/master/library/ttk/clamTheme.tcl
    # https://github.com/tcltk/tk/blob/master/generic/ttk/ttkClamTheme.c
    BG = window_background
    TEXT_BG = code_background
    ACTIVE_TAB = detail_background
    
    FG = foreground
    
    s.configure(".", 
                background=BG,
                foreground=FG,
                lightcolor=BG,
                darkcolor=BG,
                bordercolor=BG,
                )

    s.configure("Text",
                background=TEXT_BG,
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
                tabmargins=[1, 0, 0, 0],     # Margins around tab row
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
          bordercolor=[("selected", BG), ("!selected", ACTIVE_TAB)],
          #lightcolor=[("selected", "#333333"), ("!selected", "#333333")],
          #lightcolor=[("selected", "white"), ("!selected", "white")],
          lightcolor=[("selected", ACTIVE_TAB), ("!selected", BG)],
          #expand=[("selected", [1,2,13,4])] # can be used to make selected tab bigger 
    )
    
    # Treeview
    # https://stackoverflow.com/questions/32051780/how-to-edit-the-style-of-a-heading-in-treeview-python-ttk
    #print(s.map("Treeview.Heading"))
    #print(s.layout("Treeview.Heading"))
    #print(s.element_options("Treeheading.cell"))
    s.configure("Treeview", background=TEXT_BG)
    s.configure("Treeview.Heading", background=ACTIVE_TAB, lightcolor=ACTIVE_TAB, borderwidth=0)
    s.map("Treeview.Heading",
          background=[("!active", ACTIVE_TAB), ("active", ACTIVE_TAB)],
          )
    
    #TEXT_BG = "#273627"
    SELBG = "#2D3D2D"
    """
    s.map("Treeview",
          background=[('selected', 'focus', FG),
                      ('selected', '!focus', TEXT_BG),
                      ],
          foreground=[
                      ('!selected', FG),
                      ('selected', 'focus', BG),
                      ('selected', '!focus', FG),
                      ],
    )
    """
    s.map("Treeview",
          background=[('selected', SELBG),
                      ],
          foreground=[
                      ('selected', FG),
                      ],
    )
    
    # Scrollbars
    SCROLL_BG = ACTIVE_TAB
    SCBORDER = TEXT_BG
    
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
    
    
    s.configure("TScrollbar", gripcount=0, borderwidth=0, relief="flat",
                darkcolor=SCROLL_BG, lightcolor=SCROLL_BG, bordercolor=SCBORDER,
                troughcolor=TEXT_BG,
                #arrowcolor="white"
                )
    
    s.map("TScrollbar",
          background=[("!disabled", SCROLL_BG), ("disabled", SCROLL_BG)],
          darkcolor=[("!disabled", TEXT_BG), ("disabled", TEXT_BG)],
          lightcolor=[("!disabled", TEXT_BG), ("disabled", TEXT_BG)],
    )
    
    # Make disabled Hor Scrollbar invisible
    s.map("Horizontal.TScrollbar",
          background=[("disabled", BG), ("!disabled", SCROLL_BG)],
          troughcolor=[("disabled", BG)],
          bordercolor=[("disabled", BG)],
          darkcolor=[("disabled", BG)],
          lightcolor=[("disabled", BG)],
    )
    #print(s.map("TScrollbar"))
    
    
    
    
    # Menus
    s.configure("Menubar",
                # Regular, system-provided Windows menubar doesn't allow changing colors.
                # custom=True replaces it with a custom-built menubar.
                custom=running_on_windows(), 
                background=BG,
                foreground=FG,
                activebackground=FG, 
                activeforeground=BG, 
                )
    
    s.configure("Menu",
                background=ACTIVE_TAB,
                foreground="white",
                selectcolor="white",
                borderwidth=0,
                activebackground=FG,
                activeforeground=BG,
                activeborderwidth=0,
                #relief="flat"
    )
    
    s.configure("CustomMenubarLabel.TLabel",
                space=70,
                padding=[12,3,0,2])
    
    
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
    TEXT_FG = "#B3B3B3"
    s.configure("Code", foreground=TEXT_FG)
    s.configure("String.Code", foreground="#8DC76F")
    s.configure("Keyword.Code", foreground="#9A79AD")
    s.configure("Local.Code", foreground="#BCCAE8")
    s.configure("MatchedName.Code", background="#193022")
    s.configure("MatchedParens.Code", foreground="#F0995B")
    s.configure("OpenParens.Code", background="#193022")
    s.configure("OpenString.Code", background="#453B22")
    s.configure("Number.Code", foreground="#FFCABF")
    s.configure("Comment.Code", foreground="#C8DEE6")
    
    s.configure("StdOut.Shell", foreground="LightGray")
    s.configure("StdIn.Shell", foreground="LightBlue")
    s.configure("StdErr.Shell", foreground="Crimson")

def _load_early_plugin():
    get_workbench().add_theme("Clean Dark", clean)
