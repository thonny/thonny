#TODO - remove unnecessary imports, organize them to use the same import syntax

import tkinter as tk
import jedi
from thonny.globals import get_workbench
from thonny.codeview import CodeViewText



#TODO list:
#1) make autocomplete window colors (both bg and fg) configurable
#2) adjust the window position in cases where it's too close to bottom or right edge - but make sure the current line is shown
#3) perhaps make the number of maximum autocomplete options to show configurable?

class Completer(tk.Listbox):
    def __init__(self, text):
        tk.Listbox.__init__(self, master=text,
                            font=get_workbench().get_font("EditorFont"),
                            activestyle="dotbox",
                            exportselection=False)
        
        self.completions = []
        self.text = text
        
        # Auto indenter will eat up returns, therefore I need to raise the priority
        # of this binding
        self.text_priority_bindtag = "completable" + str(self.text.winfo_id())
        self.text.bindtags((self.text_priority_bindtag,) + self.text.bindtags())
        self.text.bind_class(self.text_priority_bindtag, "<Key>", self._on_text_keypress, True)
        
        self.text.bind("<<TextChange>>", self._on_text_change, True) # Assuming TweakableText
    
    def handle_autocomplete_request(self):
        if self._is_visible():
            return
        
        row, column = self._get_position()
        self._update_completions()
        
        if len(self.completions) == 0:
            pass
        elif len(self.completions) == 1:
            self._insert_completion(self.completions[0]) #insert the only completion
        else:
            self._show(self.completions)        
        
        
        get_workbench().event_generate("AutocompleteQuery",
            text_widget=self.text,
            row=row,
            column=column,
            proposed_names=[c.name for c in self.completions])
        
        
    def _show(self, completions):
        typed_name_length = len(completions[0].name) - len(completions[0].complete)
        box_x, box_y, _, box_height = self.text.bbox('insert-%dc' % typed_name_length);
        self.place(x=box_x, y=box_y + box_height,
                   width=400, height=200)

    def _is_visible(self):
        return self.winfo_ismapped()
    
    def _insert_completion(self, completion=None):
        if completion is None:
            completion = self.completions[self.curselection()[0]]
        
        get_workbench().event_generate("AutocompleteInsertion",
            text_widget=self.text,
            typed_name=completion.name[:-len(completion.complete)],
            completed_name=completion.name)
        
        if self._is_visible():
            self._close()
            
        self.text.insert(self.text.index('insert'), completion.complete)
        
        try:
            print(completion.docstring())
        except:
            # jedi crashes in some cases
            pass
        
    
    def _get_filename(self):
        # TODO: allow completing in shell
        if not isinstance(self.text, CodeViewText):
            return None
        
        codeview = self.text.master
        
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor.get_code_view() is codeview:
            return editor.get_filename()
        else:
            return None
    
    def _move_selection(self, delta):
        selected = self.curselection()
        if len(selected) == 0:
            index = 0
        else:
            index = selected[0]
        
        index += delta
        index = max(0, min(self.size()-1, index))
        
        self.selection_clear(0, self.size()-1)
        self.selection_set(index)
        self.activate(index)
    
    def _update_completions(self):
        row, column = self._get_position()
        source = self.text.get("1.0", "end-1c")
        script = jedi.Script(source, row, column, self._get_filename())
        self.completions = script.completions() 

        names = [c.name for c in self.completions]
        self.delete(0, self.size())
        self.insert(0, *names)
        self.activate(0)
        self.selection_set(0)
        
        

    def _get_position(self):
        return map(int, self.text.index("insert").split("."))
    
    def _on_text_keypress(self, event=None):
        if not self._is_visible():
            return
        
        if event.keysym == "Escape":
            self._close()
            return "break"
        elif event.keysym in ["Up", "KP_Up"]:
            self._move_selection(-1)
            return "break"
        elif event.keysym in ["Down", "KP_Down"]:
            self._move_selection(1)
            return "break"
        elif event.keysym in ["Return", "KP_Enter"]:
            self._insert_completion()
            return "break"
    
    def _on_text_change(self, event=None):
        if self._is_visible():
            self._update_completions()

    
    def _close(self, event=False):
        self.place_forget()
    
def handle_autocomplete_request(event=None):
    if event is None:
        text = get_workbench().focus_get()
    else:
        text = event.widget
    
    if not hasattr(text, "completer"):
        text.completer = Completer(text)
    
    text.completer.handle_autocomplete_request()

def load_plugin():
    
    get_workbench().add_command("autocomplete", "edit", "Auto-complete",
        handle_autocomplete_request,
        default_sequence="<Control-space>"
        # TODO: tester
        )