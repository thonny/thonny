# -*- coding: utf-8 -*-
import os.path
import tkinter as tk
from tkinter import ttk
from thonny.misc_utils import running_on_linux

def load_plugin(workbench):
    style = ttk.Style()

    if 'xpnative' in style.theme_names():
        # gives better scrollbars in empty editors
        theme = 'xpnative'
    elif 'aqua' in style.theme_names():
        theme = 'clam'
    elif 'clam' in style.theme_names():
        theme = 'clam'
    else:
        theme = style.theme_use()
        
    style.theme_use(theme)
    
    style.configure("Sash", sashthickness=10)
    
    # get rid of Treeview borders
    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe'})
    ])
    
    # necessary for Python 2.7 TODO: doesn't help for aqua
    style.configure("Treeview", background="white")
    
    
    """
    _images[1] = tk.PhotoImage("img_close",
        file=os.path.join(imgdir, '1x1_white.gif'))
    _images[2] = tk.PhotoImage("img_closeactive",
        file=os.path.join(imgdir, 'close_active.gif'))
    _images[3] = tk.PhotoImage("img_closepressed",
        file=os.path.join(imgdir, 'close_pressed.gif'))
        
    style.element_create("close", "image", "img_close",
        ("active", "pressed", "!disabled", "img_closepressed"),
        ("active", "!disabled", "img_closeactive"), border=8, sticky='')
    """
    
    global _IMG_GRAY_LINE # Saving the reference, otherwise Tk will garbage collect the images 
    _IMG_GRAY_LINE = tk.PhotoImage("gray_line", file=os.path.join(workbench.get_resource_dir(), 'gray_line.gif'))
    style.element_create("gray_line", "image", "gray_line",
                               ("!selected", "gray_line"), 
                               height=1, width=10, border=1)
    
    
    if theme == "xpnative":
        # add a line below active tab to separate it from content
        style.layout("Tab", [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'sticky': 'nswe', 'children': [
                    ('Notebook.focus', {'sticky': 'nswe', 'children': [
                        ('Notebook.label', {'sticky': '', 'side': 'left'}),
                        #("close", {"side": "left", "sticky": ''})
                    ], 'side': 'top'})
                ], 'side': 'top'}),
                ('gray_line', {'sticky': 'we', 'side': 'bottom'}),
            ]}),
        ])
        
        style.configure("Tab", padding=(4,1,0,0))
        
    elif theme == "aqua":
        style.map("TNotebook.Tab", foreground=[('selected', 'white'), ('!selected', 'black')])
        
        
        
    
    """
    ################
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
    """
    
    
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
