# -*- coding: utf-8 -*-
from __future__ import print_function, division 
from common import TextRange
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk 

import ast
import ast_utils
import ui_utils

class AstFrame(ui_utils.TreeFrame):
    def __init__(self, master):
        ui_utils.TreeFrame.__init__(self, master,
            columns=('range', 'lineno', 'col_offset', 'end_lineno', 'end_col_offset'),
            displaycolumns=(0,)
        )
        
        self.current_code_view = None
        self.tree.bind("<<TreeviewSelect>>", self.locate_code)

        self.tree.column('#0', width=550, anchor=tk.W)
        self.tree.column('range', width=100, anchor=tk.W)
        self.tree.column('lineno', width=30, anchor=tk.W)
        self.tree.column('col_offset', width=30, anchor=tk.W)
        self.tree.column('end_lineno', width=30, anchor=tk.W)
        self.tree.column('end_col_offset', width=30, anchor=tk.W)
        
        self.tree.heading('#0', text="Node", anchor=tk.W)
        self.tree.heading('range', text='Code range', anchor=tk.W)
        
        self.tree['show'] = ('headings', 'tree')
    
    def locate_code(self, event):
        if self.current_code_view == None:
            return
        
        iid = self.tree.focus()
        
        if iid != '':
            values = self.tree.item(iid)['values']
            if isinstance(values, list) and len(values) >= 5:
                start_line, start_col, end_line, end_col = values[1:5] 
                self.current_code_view.select_range(TextRange(start_line, start_col, 
                                                    end_line, end_col))
        
    
    def clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)
    
    def show_ast(self, code_view):
        self.current_code_view = code_view
        source = code_view.get_content()
        

        #import time
        #start = time.clock()
        root = ast_utils.parse_source(source)
        #ast_utils.insert_expression_markers(root)
        #ast_utils.insert_statement_markers(root)
        #elapsed = (time.clock() - start)
        #print("ELAPSED: ", elapsed)
        
        self.clear_tree()
        
        def _format(key, node, parent_id):
            if isinstance(node, ast.AST):
                children = [(key, child) for key, child in ast.iter_fields(node)]
                value_label = node.__class__.__name__ 
            elif isinstance(node, list):
                children = list(enumerate(node))
                value_label = "list"
            else:
                children = []
                value_label = repr(node)
            
            item_text = str(key) + "=" + value_label
            node_id = self.tree.insert(parent_id, "end", text=item_text, open=True)
            
            if hasattr(node, "lineno") and hasattr(node, "col_offset"):
                self.tree.set(node_id, "lineno", node.lineno)
                self.tree.set(node_id, "col_offset", node.col_offset)
                
                range_str = str(node.lineno) + '.' + str(node.col_offset)
                if hasattr(node, "end_lineno") and hasattr(node, "end_col_offset"):
                    self.tree.set(node_id, "end_lineno", node.end_lineno)
                    self.tree.set(node_id, "end_col_offset", node.end_col_offset)
                    range_str += "  -  " + str(node.end_lineno) + '.' + str(node.end_col_offset)
                else:
                    # fallback
                    self.tree.set(node_id, "end_lineno", node.lineno)
                    self.tree.set(node_id, "end_col_offset", node.col_offset + 1)
                    
                self.tree.set(node_id, "range", range_str)
                
            
            for child_key, child in children:
                _format(child_key, child, node_id)
                
        _format("root", root, "")
#         def is_simple_node(node):
#             if not isinstance(node, ast.AST) and not isinstance(node, list):
#                 return True
#             if node == []:
#                 return True
#             if isinstance(node, ast.AST) and node._fields == []:
#                 return True
#             
#             return False
            
        
        
        
    
        