# -*- coding: utf-8 -*-
from tkinter import ttk
from thonny.misc_utils import running_on_linux
from thonny.globals import get_workbench

_images = set() # for keeping references to tkinter images to avoid garbace colleting them



def tweak_notebooks():
    style = ttk.Style()
    theme = style.theme_use()
    
    if theme in ["xpnative", "vista"]:
        get_workbench().get_image('gray_line.gif', "gray_line")
        
        style.element_create("gray_line", "image", "gray_line",
                                   ("!selected", "gray_line"), 
                                   height=1, width=10, border=1)
        
        style.layout('Tab', [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'sticky': 'nswe', 'side': 'top', 'children': [
                    ('Notebook.focus', {'sticky': 'nswe', 'side': 'top', 'children': [
                        ('Notebook.label', {'sticky': '', 'side': 'left'}),
                    ]})
                ]}),
                ('gray_line', {'sticky': 'we', 'side': 'bottom'}),
            ]}),
        ])
    
    style.configure("Tab", padding=(4,1,0,0))
    if theme == "clam":
        style.configure("ButtonNotebook.Tab", padding=(6,4,2,3))
    else:
        style.configure("ButtonNotebook.Tab", padding=(4,1,1,3))
            
    if theme == "aqua":
        style.map("TNotebook.Tab", foreground=[('selected', 'white'), ('!selected', 'black')])


def tweak_treeviews():
    style = ttk.Style()
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

def tweak_menubuttons():
    style = ttk.Style()
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

def tweak_paned_windows():
    style = ttk.Style()
    style.configure("Sash", sashthickness=10)


def load_plugin():
    tweak_notebooks()
    tweak_treeviews()
    tweak_paned_windows()
    
    
