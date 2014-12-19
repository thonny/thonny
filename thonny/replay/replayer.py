import tkinter as tk
import tkinter.ttk as ttk
from thonny import ui_utils
from thonny.ui_utils import TextWrapper
from thonny.user_logging import parse_log_line, TextInsertEvent,\
    TextDeleteEvent, UserEvent
from thonny.codeview import CodeView


class ReplayWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        
        self.main_pw   = ui_utils.create_PanedWindow(self, orient=tk.HORIZONTAL)
        self.left_pw  = ui_utils.create_PanedWindow(self.main_pw, orient=tk.VERTICAL)
        self.right_frame = ttk.Frame(self.main_pw)
        self.editor_book = EditorNotebook(self.left_pw)
        shell_book = ui_utils.PanelBook(self.main_pw)
        self.shell = ShellFrame(shell_book)
        self.log_frame = LogFrame(self.right_frame, self.editor_book)
        self.control_frame = ControlFrame(self.right_frame)
        
        self.main_pw.grid(padx=10, pady=10, sticky=tk.NSEW)
        self.main_pw.add(self.left_pw)
        self.main_pw.add(self.right_frame)
        self.left_pw.add(self.editor_book)
        self.left_pw.add(shell_book)
        shell_book.add(self.shell, text="Shell")
        self.log_frame.grid()
        self.control_frame.grid()
        
        self.log_frame.load_log("C:/users/aivar/.thonny/user_logs/2014-09-02_09-53-22_0.txt")
        
            

class ControlFrame(ttk.Frame):
    pass

class LogFrame(ui_utils.TreeFrame):
    def __init__(self, master, editor_book):
        ui_utils.TreeFrame.__init__(self, master, ("desc", "pause", "time"))
        self.editor_book = editor_book
        self.all_events = []
        self.last_event_index = -1
        self.loading = False 

    def load_log(self, filename):
        self._clear_tree()
        self.all_events = []
        self.last_event_index = -1
        self.loading = True
        
        with open(filename, encoding="UTF-8") as f:
            for line in f:
                event = parse_log_line(line)
                node_id = self.tree.insert("", "end")
                self.tree.set(node_id, "desc", event.compact_description())
                self.tree.set(node_id, "pause", str(-1)) # TODO:
                self.tree.set(node_id, "time", str(event.event_time))
                self.all_events.append(event)
        
        self.loading = False
        
    def replay_event(self, event):
        "this should be called with events in correct order"
        print("log replay", event)
        self.editor_book.replay_event(event)
    
    def undo_event(self, event):
        "this should be called with events in correct order"
        print("log undo", event)
        self.editor_book.undo_event(event)
    
    def on_select(self, event):
        # parameter "event" is here tkinter event
        if self.loading:
            return 
        
        iid = self.tree.focus()
        if iid != '':
            self.select_event(self.tree.index(iid))
        
    def select_event(self, event_index):
        # here event means logged event
        if event_index > self.last_event_index:
            # replay all events between last replayed event up to and including this event
            while self.last_event_index < event_index:
                self.replay_event(self.all_events[self.last_event_index+1])
                self.last_event_index += 1
                
        elif event_index < self.last_event_index:
            # undo all events up to and excluding this event
            while self.last_event_index > event_index:
                self.undo_event(self.all_events[self.last_event_index])
                self.last_event_index -= 1

class ShellFrame(ttk.Frame, TextWrapper):
    pass


class ReplayerCodeView(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        self.vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.vbar.grid(row=0, column=2, sticky=tk.NSEW)
        self.hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hbar.grid(row=1, column=0, sticky=tk.NSEW, columnspan=2)
        self.text = tk.Text(self,
                yscrollcommand=self.vbar.set,
                xscrollcommand=self.hbar.set,
                borderwidth=0,
                font=ui_utils.EDITOR_FONT,
                wrap=tk.NONE,
                insertwidth=2,
                #selectborderwidth=2,
                inactiveselectbackground='gray',
                #highlightthickness=0, # TODO: try different in Mac and Linux
                #highlightcolor="gray",
                padx=5,
                pady=5,
                undo=True,
                autoseparators=False)
        
        self.text.grid(row=0, column=1, sticky=tk.NSEW)
        self.hbar['command'] = self.text.xview
        self.vbar['command'] = self.text.yview
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        

class Editor(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        assert isinstance(master, EditorNotebook)
        self.code_view = ReplayerCodeView(self)
        self.code_view.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
    
    def replay_event(self, event):
        if isinstance(event, TextInsertEvent):
            self.code_view.text.insert(event.position, event.text, event.tags)
        elif isinstance(event, TextDeleteEvent):
            self.code_view.text.delete(event.from_position, event.to_position)
    
    def undo_event(self, event):
        raise Exception

class EditorNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master, padding=0)
        self.editors_by_id = {}
    
    def get_editor_by_id(self, editor_id):
        if editor_id not in self.editors_by_id:
            editor = Editor(self)
            self.add(editor, text="<untitled>")
            self.select(editor)
            self.editors_by_id[editor_id] = editor
            
        
        return self.editors_by_id[editor_id]
    
    def replay_event(self, event):
        if hasattr(event, "editor_id"):
            editor = self.get_editor_by_id(event.editor_id)
            editor.replay_event(event)
    
    def undo_event(self, event):
        if hasattr(event, "editor_id"):
            editor = self.get_editor_by_id(event.editor_id)
            editor.undo_event(event)

if __name__ == "__main__":
    ReplayWindow().mainloop()    