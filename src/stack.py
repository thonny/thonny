# -*- coding: utf-8 -*-

import ui_utils


class StackPanel(ui_utils.TreeFrame):
    def __init__(self, master, vm, editor_book):
        ui_utils.TreeFrame.__init__(self, master, ['description'])
        self._frames = {}
        self._vm = vm
        self._editor_book = editor_book
        """
        self._locals_frame = locals_frame
        self._globals_frame = globals_frame
        self._builtins_frame = builtins_frame
        """
        self.tree["show"] = ""
        self.tree.bind("<Double-Button-1>", self._show_frame)
    
    def handle_vm_message(self, msg):
        if not hasattr(msg, "stack"):
            return
        
        self._frames.clear()
        item_ids = self.tree.get_children()
        
        for i in range(len(msg.stack)):
            frame = msg.stack[i]
            
            if len(item_ids) <= i:
                # new frame
                item_id = self.tree.insert("", "end")
            else:
                item_id = item_ids[i]
            
            self.tree.set(item_id, "description", frame.get_description())
            
            self._frames[item_id] = frame
        
        # remove old frames
        self.tree.delete(*item_ids[len(msg.stack):])
        
    
    def _show_frame(self, event):
        # TODO: only when paused and debug state
        item_id = self.tree.identify_row(event.y)
        if item_id != "":
            frame = self._frames[item_id]
            self._editor_book.show_file(frame.filename, frame.focus)
            #self._locals_frame.show_stack_frame(frame)
            #self._builtins_frame.show_stack_frame(frame)
            #print(frame)
            #print(frame.filename)



