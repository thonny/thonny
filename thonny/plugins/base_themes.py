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

def base_windows(style, **opts):
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

def base_clam(style, **opts):
    style.theme_use("clam")
    style.configure("Tab", padding=(4,1,0,0))
    style.configure("ButtonNotebook.Tab", padding=(6,4,2,3))
        
    # other widgets
    tweak_menus(style)
    tweak_treeviews(style)
    tweak_menubuttons(style)
    tweak_paned_windows(style)

def base_aqua(style, **opts):
    style.theme_use("aqua")
    style.configure("Tab", padding=(4,1,0,0))
    style.configure("ButtonNotebook.Tab", padding=(4,1,1,3))
    
    # other widgets
    tweak_menus(style)
    tweak_treeviews(style)
    tweak_menubuttons(style)
    tweak_paned_windows(style)

def load_early_plugin():
    from tkinter import ttk
    available_themes = ttk.Style().theme_names()
    
    get_workbench().add_theme("Clam", base_clam)
    
    if "xpnative" in available_themes:
        get_workbench().add_theme("Windows", base_windows)
    if "aqua" in available_themes:
        get_workbench().add_theme("Aqua", base_aqua)
        
    
    