import sys
import traceback
import tkinter as tk
import tkinter.ttk as ttk
from thonny import ui_utils
from thonny.plugins.filebrowser import FileBrowser
from thonny.globals import get_workbench


class ReplayWindow(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        tk.Tk.report_callback_exception = self.on_tk_exception
        
        self.main_pw   = ui_utils.AutomaticPanedWindow(self, orient=tk.HORIZONTAL)
        self.center_pw  = ui_utils.AutomaticPanedWindow(self.main_pw, orient=tk.VERTICAL)
        self.right_frame = ttk.Frame(self.main_pw)
        self.editor_notebook = ReplayerEditorNotebook(self.center_pw)
        shell_book = ui_utils.AutomaticNotebook(self.main_pw)
        self.shell = ShellFrame(shell_book)
        self.log_frame = LogFrame(self.right_frame, self.editor_notebook, self.shell)
        self.browser = ReplayerFileBrowser(self.main_pw, self.log_frame)
        self.control_frame = ControlFrame(self.right_frame)
        
        self.main_pw.grid(padx=10, pady=10, sticky=tk.NSEW)
        self.main_pw.add(self.browser, minsize=200)
        self.main_pw.add(self.center_pw, minsize=700)
        self.main_pw.add(self.right_frame, minsize=200)
        self.center_pw.add(self.editor_notebook, minsize=500)
        self.center_pw.add(shell_book)
        shell_book.add(self.shell, text="Shell")
        self.log_frame.grid(sticky=tk.NSEW)
        self.control_frame.grid(sticky=tk.NSEW)
        self.right_frame.columnconfigure(0, weight=1)
        self.right_frame.rowconfigure(0, weight=1)
        
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.state("zoomed")
        
        if len(sys.argv) > 1:
            self.log_frame.load_log(sys.argv[1])
        else:
            try: 
                self.log_frame.load_log("C:/users/aivar/.thonny/user_logs/2014-12-16_16-54-56_0.txt")
            except:
                pass
            

    def on_tk_exception(self, exc, val, tb):
        # copied from tkinter.Tk.report_callback_exception
        # Aivar: following statement kills the process when run with pythonw.exe
        # http://bugs.python.org/issue22384
        #sys.stderr.write("Exception in Tkinter callback\n")
        sys.last_type = exc
        sys.last_value = val
        sys.last_traceback = tb
        traceback.print_exception(exc, val, tb)
        
        # TODO: Command+C for Mac
        tk.messagebox.showerror("Internal error. Use Ctrl+C to copy",
                                traceback.format_exc())
    

class ReplayerFileBrowser(FileBrowser):
    
    def __init__(self, master, log_frame):
        FileBrowser.__init__(self, master, show_hidden_files=True)
        self.log_frame = log_frame

    def on_double_click(self, event):
        path = self.get_selected_path()
        if path:
            self.log_frame.load_log(path)
            
class ControlFrame(ttk.Frame):
    def __init__(self, master, **kw):
        ttk.Frame.__init__(self, master=master, **kw)
        
        self.toggle_button = ttk.Button(self, text="Play")
        self.speed_scale = ttk.Scale(self, from_=1, to=100, orient=tk.HORIZONTAL)
        
        self.toggle_button.grid(row=0, column=0, sticky=tk.NSEW, pady=(10,0), padx=(0,5))
        self.speed_scale.grid(row=0, column=1, sticky=tk.NSEW, pady=(10,0), padx=(5,0))
        
        self.columnconfigure(1, weight=1)
        
        

class LogFrame(ui_utils.TreeFrame):
    def __init__(self, master, editor_book, shell):
        ui_utils.TreeFrame.__init__(self, master, ("desc", "pause", "time"))
        self.editor_notebook = editor_book
        self.shell = shell
        self.all_events = []
        self.last_event_index = -1
        self.loading = False 
        self.shell_editor_id = None

    def load_log(self, filename):
        self._clear_tree()
        self.all_events = []
        self.last_event_index = -1
        self.loading = True
        self.editor_notebook.clear()
        self.shell.clear()
        
        with open(filename, encoding="UTF-8") as f:
            last_event = None
            for line in f:
                event = parse_log_line(line)
                if (isinstance(event, ProgramLoseFocusEvent) 
                    and isinstance(last_event, ProgramLoseFocusEvent)
                    or isinstance(event, ProgramGetFocusEvent)
                    or isinstance(event, EditorGetFocusEvent) # TODO:
                    or isinstance(event, EditorLoseFocusEvent)
                    or isinstance(event, KeyPressEvent)
                    ):
                    # They are doubled for some reason
                    continue
                
                node_id = self.tree.insert("", "end")
                self.tree.set(node_id, "desc", event.compact_description())
                if last_event:
                    delta = event.event_time - last_event.event_time
                    pause = delta.seconds
                else:
                    pause = 0   
                self.tree.set(node_id, "pause", str(pause if pause else ""))
                self.tree.set(node_id, "time", str(event.event_time))
                self.all_events.append(event)
                
                if isinstance(event, ShellCreateEvent):
                    self.shell_editor_id = event.editor_id
                
                last_event = event
                
        self.loading = False
        
    def replay_event(self, event):
        "this should be called with events in correct order"
        #print("log replay", event)
        
        if hasattr(event, "editor_id"):
            if event.editor_id == self.shell_editor_id:
                self.shell.replay_event(event)
            else:
                self.editor_notebook.replay_event(event)
    
    def undo_event(self, event):
        "this should be called with events in correct order"
        #print("log undo", event)
        if hasattr(event, "editor_id"):
            if event.editor_id == self.shell_editor_id:
                self.shell.undo_event(event)
            else:
                self.editor_notebook.undo_event(event)
    
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
                font=get_workbench().get_font("EditorFont"),
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
        

class ReplayerEditor(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.code_view = ReplayerCodeView(self)
        self.code_view.grid(sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text_states_before = {} # self.text_states[event_id] contains editor content before event with id event_id
    
    def replay_event(self, event):
        if isinstance(event, TextInsertEvent) or isinstance(event, TextDeleteEvent):
            self.text_states_before[id(event)] = self.code_view.text.get("1.0", "end")
            self.see_event(event)
            
            if isinstance(event, TextInsertEvent):
                self.code_view.text.insert(event.position, event.text, event.tags)
                
            elif isinstance(event, TextDeleteEvent):
                if event.to_position:
                    self.code_view.text.delete(event.from_position, event.to_position)
                else:
                    self.code_view.text.delete(event.from_position)
        
    
    def undo_event(self, event):
        if id(event) in self.text_states_before:
            self.code_view.text.delete("1.0", "end")
            self.code_view.text.insert("1.0", self.text_states_before[id(event)])
            self.see_event(event)
    
    def see_event(self, event):
        if hasattr(event, "to_position") and event.to_position:
            self.code_view.text.see(event.to_position)
            
        if hasattr(event, "from_position") and event.from_position:
            self.code_view.text.see(event.from_position)
            
        if hasattr(event, "position") and event.position:
            self.code_view.text.see(event.position)

class ReplayerEditorNotebook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master, padding=0)
        self.editors_by_id = {}
    
    def clear(self):
        
        for child in self.winfo_children():
            child.destroy()
        
        self.editors_by_id = {}
    
    def get_editor_by_id(self, editor_id):
        if editor_id not in self.editors_by_id:
            editor = ReplayerEditor(self)
            self.add(editor, text="<untitled>")
            self.editors_by_id[editor_id] = editor
            
        return self.editors_by_id[editor_id]
    
    def replay_event(self, event):
        if hasattr(event, "editor_id"):
            editor = self.get_editor_by_id(event.editor_id)
            #print(event.editor_id, id(editor), event)
            self.select(editor)
            editor.replay_event(event)
    
    def undo_event(self, event):
        if hasattr(event, "editor_id"):
            editor = self.get_editor_by_id(event.editor_id)
            editor.undo_event(event)

class ShellFrame(ReplayerEditor):
    
    def clear(self):
        self.code_view.text.delete("1.0", "end")


def run():
    try:
        ReplayWindow().mainloop()
    except:
        get_workbench().report_internal_error()

if __name__ == "__main__":
    run()