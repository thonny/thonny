import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench
from thonny import ui_utils
from thonny.ui_utils import create_tooltip

class GridFrame(ttk.Frame):
    def __init__(self, master, columns, displaycolumns='#all', show_scrollbar=True):
        ttk.Frame.__init__(self, master)
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        if show_scrollbar:
            self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.tree = ttk.Treeview(self, columns=columns, displaycolumns=displaycolumns, 
                                 yscrollcommand=self.vert_scrollbar.set)
        self.tree['show'] = 'headings'
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")
        
    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)
    
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        pass



class ObjectInspector2(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        toolbar = ttk.Frame(self)
        toolbar.grid(row=0, column=0, sticky="nsew")
        
        def create_navigation_link(col, image_filename, action, tooltip, padx=0):
            button = ttk.Button(toolbar, 
                         #command=handler, 
                         image=get_workbench().get_image(image_filename), 
                         style="Toolbutton", # TODO: does this cause problems in some Macs?
                         state=tk.NORMAL
                         )
            ui_utils.create_tooltip(button, tooltip,
                       **get_workbench().get_option("theme.tooltip_options", {'padx':3, 'pady':1})
                       )
            
            button.grid(row=0, column=col, sticky=tk.NE, padx=padx, pady=4)
            button.bind("<Button-1>", action)
            return button
        
        tab1 = tk.Label(toolbar, text=" General ", relief="flat")
        tab1.grid(row=0, column=1, pady=5, padx=5, sticky="nsew")
        
        tab2 = tk.Label(toolbar, text=" Data ", relief="sunken")
        tab2.grid(row=0, column=2, pady=5, padx=5, sticky="nsew")
        
        tab3 = tk.Label(toolbar, text=" Atts ", relief="flat")
        tab3.grid(row=0, column=3, pady=5, padx=5, sticky="nsew")
        
        self.back_button = create_navigation_link(7, "nav_backward.gif", self.navigate_back, "Previous object")
        self.forward_button = create_navigation_link(8, "nav_forward.gif", self.navigate_forward, "Next object", (0,10))
        self.back_links = []
        self.forward_links = []
        
        self.search_box = ttk.Entry(toolbar, 
                                    #borderwidth=1, 
                                    #background=ui_utils.get_main_background()
                                   )
        self.search_box.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        toolbar.columnconfigure(0, weight=1)
        
        self.data_frame = GridFrame(self, ["id", "first_name", "last_name", "age"])
        self.data_frame.grid(row=1, column=0, sticky="nsew")
        self.data_frame.tree.heading('id', text='id', anchor=tk.W) 
        self.data_frame.tree.heading('first_name', text='first_name\nadsf', anchor=tk.W) 
        self.data_frame.tree.heading('last_name', text='last_name', anchor=tk.W) 
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


    
    def navigate_back(self, event):
        if len(self.back_links) == 0:
            return
        
        self.forward_links.append(self.object_id)
        self._show_object_by_id(self.back_links.pop(), True)
    
    def navigate_forward(self, event):
        if len(self.forward_links) == 0:
            return
    
        self.back_links.append(self.object_id)
        self._show_object_by_id(self.forward_links.pop(), True)


def load_plugin():
    get_workbench().add_view(ObjectInspector2, "Object inspector 2", "se")