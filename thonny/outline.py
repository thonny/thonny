







########
########
# PLEASE NOTE - THIS FEATURE IS STILL UNDER DESIGN / CONSTRUCTION
########
########













import pyclbr
import os
from operator import itemgetter
import sys
import tkinter as tk
from tkinter import ttk

#TODO - go over imports, see which are needed

#TODO - see if there's a way to select or somehow mark the line
#that contains the item that's double-clicked on

#TODO - find out if there's a way to display 2nd level nested classes/methods

#TODO - automatic outline updating
#TODO - if file isn't saved or can't be parsed display an error message instead

#TODO - normalize method names, put _ in front of private ones

class OutlineFrame(ttk.Frame):
    def __init__(self, master, editor_notebook):
        ttk.Frame.__init__(self, master)
        self.editor_notebook = editor_notebook #reference to the notebook containing editors
        self.current_path = None #path of the currently opened file

        #init and place scrollbar
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

        #init and place tree
        self.tree = ttk.Treeview(self, yscrollcommand=self.vert_scrollbar.set)
        #self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.tree.yview


        #init error label
        #TODO - make wraplength dynamic, also listen to the resize event and reset the wraplength
        self.error_label = ttk.Label(self, anchor=tk.CENTER, wraplength=200, text="Outline cannot be displayed until the current file is saved.")
        self.error_label.grid(row=0, column=0, sticky=tk.NSEW)

        #set single-cell frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        #init tree events
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")

        #configure the only tree column
        self.tree.column('#0', anchor=tk.W, stretch=True)
        self.tree.heading('#0', text='Item (type / line)', anchor=tk.W)

        #marks whether the outline is currently shown
        self.outline_shown = False #TODO - think about removing this entirely

    #sets the current path and parses the module structure from it
    def load_content_from_path(self, path):
        return False
        self.current_path = path
        modulename = os.path.splitext(os.path.basename(path))[0]
        self.module_data = pyclbr.readmodule_ex(modulename, [path])
        self.module_data = sorted([i[1] for i in self.module_data.items() if i[1].module == modulename], key=lambda x:x.lineno)
        self._display_content() #and now let's display the data

    #displays the parsed content
    def _display_content(self):
        if not self.module_data or self.module_data == None:
            return

        #go over each top-level item
        for item in self.module_data:
            if isinstance(item, pyclbr.Class):
                itemtype = 'class'
            else:
                itemtype = 'def'

            #create the text to be played for this item
            item_text = item.name + ' (' + itemtype + ' @ ' + str(item.lineno) + ')'
            #insert the item, set lineno as a 'hidden' value
            current = self.tree.insert('', 'end', text=item_text, values = item.lineno)
            #in the case of a class item, also go over the 2nd level methods,
            #do similar stuff as for top-level items
            if isinstance(item, pyclbr.Class):
                    for method in sorted(item.methods.items(), key=lambda x:x[1]):
                        item_text = method[0] + ' (def @ ' + str(method[1]) + ')'
                        self.tree.insert(current, 'end', text=item_text, values = method[1])
        

    #TODO - reconsider this        
    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)

    #TODO - reconsider this    
    def on_select(self, event):
        pass

    #TODO - change this if you decide to update outline on switching tabs
    def on_double_click(self, event):
        editor = self.editor_notebook.get_editor(self.current_path)
        self.editor_notebook.select(editor)
        lineno = self.tree.item(self.tree.focus())['values'][0]
        index = editor._code_view.text.index(str(lineno) + '.0')
        editor._code_view.text.see(index)
