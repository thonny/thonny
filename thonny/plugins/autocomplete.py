import tkinter as tk
from thonny.globals import get_workbench, get_runner
from thonny.codeview import CodeViewText
from thonny.shell import ShellText
from thonny.common import InlineCommand
from textwrap import dedent



# TODO: adjust the window position in cases where it's too close to bottom or right edge - but make sure the current line is shown
"""Completions get computed on the backend, therefore getting the completions is
asynchronous.
"""
class Completer(tk.Listbox):
    def __init__(self, text):
        self.font = get_workbench().get_font("EditorFont").copy()
        tk.Listbox.__init__(self, master=text,
                            font=self.font,
                            activestyle="dotbox",
                            exportselection=False)
        
        self.text = text
        self.completions = []
        
        # Auto indenter will eat up returns, therefore I need to raise the priority
        # of this binding
        self.text_priority_bindtag = "completable" + str(self.text.winfo_id())
        self.text.bindtags((self.text_priority_bindtag,) + self.text.bindtags())
        self.text.bind_class(self.text_priority_bindtag, "<Key>", self._on_text_keypress, True)
        
        self.text.bind("<<TextChange>>", self._on_text_change, True) # Assuming TweakableText
        
        # TODO: remove binding when editor gets closed
        get_workbench().bind("InlineResult", self._handle_inline_result, True)
    
    def handle_autocomplete_request(self):
        row, column = self._get_position()
        source = self.text.get("1.0", "end-1c")
        
        backend_code = dedent("""\
        try:
            import jedi
            script = jedi.Script(source, row, column, filename)
            completions = [{"name":c.name, "complete":c.complete}
                            for c in script.completions()]
        except ImportError:
            completions = [{"name":"", "complete":"<could not import jedi>"}]
        
        __result__ = {
            "source"   : source,
            "row"      : row,
            "column"   : column,
            "filename" : filename,
            "completions" : completions
        }
        """)
        
        get_runner().send_command(InlineCommand(command="execute_source",
                                                source=backend_code,
                                                request_id=self._get_request_id(),
                                                global_vars={"source" : source,
                                                             "row" : row,
                                                             "column" : column,
                                                             "filename" : self._get_filename()}))
    
    def _handle_inline_result(self, msg):
        if msg.request_id != self._get_request_id():
            return
        
        row, column = self._get_position()
        result = msg.__result__
        print("RESULT", result)
        # check if the response is relevant for current state
        if (result["source"] == self.text.get("1.0", "end-1c")
            and result["row"] == row and result["column"] == column):
            self._present_completions(result["completions"])
        else:
            self._close()
            
    def _present_completions(self, completions):
        self.completions = completions
        
        # broadcast logging info
        row, column = self._get_position()
        get_workbench().event_generate("AutocompleteProposal",
            text_widget=self.text,
            row=row,
            column=column,
            proposal_count=len(completions))
        
        # present
        if len(completions) == 0:
            self._close()
        elif len(completions) == 1:
            self._insert_completion(completions[0]) #insert the only completion
            self._close()
        else:
            self._show_box(completions)
        
            
    def _show_box(self, completions):
        self.delete(0, self.size())
        self.insert(0, *[c["name"] for c in completions])
        self.activate(0)
        self.selection_set(0)
        
        # place box
        if not self._is_visible():
            
            self.font.configure(size=get_workbench().get_font("EditorFont")["size"]-2)
            
            
            #_, _, _, list_box_height = self.bbox(0)
            height = 100 #min(150, list_box_height * len(completions) * 1.15)
            typed_name_length = len(completions[0]["name"]) - len(completions[0]["complete"])
            text_box_x, text_box_y, _, text_box_height = self.text.bbox('insert-%dc' % typed_name_length);
            
            # should the box appear below or above cursor?
            space_below = self.master.winfo_height() - text_box_y - text_box_height
            space_above = text_box_y
            
            if space_below >= height or space_below > space_above:
                height = min(height, space_below)
                y = text_box_y + text_box_height
            else:
                height = min(height, space_above)
                y = text_box_y - height
                
            self.place(x=text_box_x, y=y, width=400, height=height)
                

    def _is_visible(self):
        return self.winfo_ismapped()
    
    def _insert_completion(self, completion):
        get_workbench().event_generate("AutocompleteInsertion",
            text_widget=self.text,
            typed_name=completion["name"][:-len(completion["complete"])],
            completed_name=completion["name"])
        
        if self._is_visible():
            self._close()
            
        self.text.insert(self.text.index('insert'), completion["complete"])
        
    
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
    
    def _get_request_id(self):
        return "autocomplete_" + str(self.text.winfo_id())
    
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
            assert self.size() > 0
            self._insert_completion(self.completions[(self.curselection()[0])])
            return "break"
    
    def _on_text_change(self, event=None):
        if self._is_visible():
            self.handle_autocomplete_request()

    
    def _close(self, event=False):
        self.place_forget()

class ShellCompleter(Completer):
    def handle_autocomplete_request(self):
        backend_code = dedent("""\
        import __main__
        try:
            import jedi
            interpreter = jedi.Interpreter(source, [__main__.__dict__])
            completions = [{"name":c.name, "complete":c.complete}
                            for c in interpreter.completions()]
        except ImportError:
            completions = [{"name":"", "complete":"<could not import jedi>"}]
        
        __result__ = {
            "source"   : source,
            "completions" : completions
        }
        """)
        
        get_runner().send_command(InlineCommand(command="execute_source",
                                                source=backend_code,
                                                request_id=self._get_request_id(),
                                                extra_vars={"source" : self._get_prefix()}))
    
    def _handle_inline_result(self, msg):
        if msg.request_id != self._get_request_id():
            return
        
        # check if the response is relevant for current state
        if msg.__result__["source"] == self._get_prefix():
            self._present_completions(msg.__result__["completions"])
        else:
            self._close()


    def _get_prefix(self):
        return self.text.get("insert linestart", "insert") # TODO: allow multiple line input

        
def handle_autocomplete_request(event=None):
    if event is None:
        text = get_workbench().focus_get()
    else:
        text = event.widget
    
    if not hasattr(text, "autocompleter"):
        if isinstance(text, CodeViewText):
            text.autocompleter = Completer(text)
        elif isinstance(text, ShellText):
            text.autocompleter = ShellCompleter(text)
        else:
            return

    text.autocompleter.handle_autocomplete_request()

def load_plugin():
    
    get_workbench().add_command("autocomplete", "edit", "Auto-complete",
        handle_autocomplete_request,
        default_sequence="<Control-space>"
        # TODO: tester
        )