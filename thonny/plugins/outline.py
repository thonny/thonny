import re
import tkinter as tk
from tkinter import ttk

#TODO - see if there's a way to remember the previously focused tree item
#when the tree is rebuilt to avoid reparsing everything on every step
#idea: remember the focus item's name and line number, in the case of
#any change see if there's an item with the same name on the same line,
#or an item on any adjacent lines with nearly the same name (?)

#TODO - see if there's a way to select or somehow mark the line
#that contains the item that's double-clicked on

class OutlineView(ttk.Frame):
    def __init__(self, master, workbench):
        ttk.Frame.__init__(self, master)
        self._workbench = workbench
        self._workbench.get_editor_notebook().bind("<<NotebookTabChanged>>",self._update_frame_contents ,True)

        #init and place scrollbar
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)

        #init and place tree
        self.tree = ttk.Treeview(self, yscrollcommand=self.vert_scrollbar.set)
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.tree.yview

        #set single-cell frame
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        #init tree events
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")

        #configure the only tree column
        self.tree.column('#0', anchor=tk.W, stretch=True)
        self.tree.heading('#0', text='Item (type @ line)', anchor=tk.W)

    def _update_frame_contents(self, event=None):
        self._clear_tree()
        if self._workbench.get_editor_notebook().get_current_editor():
            self.parse_and_display_module(self._workbench.get_editor_notebook().get_current_editor()._code_view)
        
        module_contents = self.active_codeview.get_content()
        nodes = []  #all nodes in format (parent, node_indent, node_children, name, type, linernumber)
        root_node = (None, 0, []) #name, type and linenumber not needed for root
        nodes.append(root_node)
        active_node = root_node

        lineno = 0
        for line in module_contents.split('\n'):
            lineno += 1
            m = re.match('[ ]*[\w]{1}', line)
            if m:
                indent = len(m.group(0))
                while indent <= active_node[1]:
                    active_node = active_node[0]

                t = re.match('[ ]*(?P<type>(def|class){1})[ ]+(?P<name>[\w]+)', line)
                if t:
                    current = (active_node, indent, [], t.group('name'), t.group('type'), lineno)
                    active_node[2].append(current)
                    active_node = current

        self.module_data = nodes
        self._display_content() #and now let's display the data

    #displays the parsed content
    def _display_content(self):
        if not self.module_data or self.module_data == None:
            return

        #go over each item in the root node, which will recursively do the same for child nodes
        for item in self.module_data[0][2]:
            self._add_item_to_tree('', item)

    #adds a single item to the tree, recursively calls itself to add any child nodes
    def _add_item_to_tree(self, parent, item):
        #create the text to be played for this item
        item_text = item[3] + ' (' + item[4] + ' @ ' + str(item[5]) + ')'
        
        #insert the item, set lineno as a 'hidden' value
        current = self.tree.insert(parent, 'end', text=item_text, values = item[5])

        for child in item[2]:
            self._add_item_to_tree(current, child)
        
    #clears the tree by deleting all items      
    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)

    #called when a double-click is performed on any items
    def on_double_click(self, event):
        lineno = self.tree.item(self.tree.focus())['values'][0]
        index = self.active_codeview.text.index(str(lineno) + '.0')
        self.active_codeview.text.see(index) #make sure that the double-clicked item is visible
        self._workbench.event_generate("OutlineDoubleClick",
            item_text=self.tree.item(self.tree.focus(), option='text'))

    #called by editornotebook publisher to notify of changed tab
    def notify_tab_changed(self):
        if self.active_codeview is not None and self.active_codeview.modify_listeners is not None and self in self.active_codeview.modify_listeners:
            self.active_codeview.modify_listeners.remove(self)
        else: 
            self._clear_tree()

def load_plugin(workbench): 
    workbench.add_view(OutlineView, "Outline", "ne")
