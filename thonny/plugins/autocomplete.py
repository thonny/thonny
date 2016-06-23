#TODO - remove unnecessary imports, organize them to use the same import syntax

import tkinter as tk
import jedi
from thonny.globals import get_workbench
from thonny.tktextext import TweakableText
import traceback
from thonny.codeview import CodeViewText, CodeView



#TODO list:
#1) make autocomplete window colors (both bg and fg) configurable
#2) adjust the window position in cases where it's too close to bottom or right edge - but make sure the current line is shown
#3) perhaps make the number of maximum autocomplete options to show configurable?

#the primary method that's intended to be called from codeview
#uses jedi functionality to get a list of completion suggestions based on the code source
#if 0 suggestions are found, does nothing
#if 1 suggestion is found, inserts it into the text
#if 2+ suggestions are found, creates a vertical list of suggestions where the user can choose
def autocomplete(codeview, row, column, filename):
    try: 
        editor = codeview.master
        get_workbench().event_generate("AutocompleteQuery",
            editor=editor,
            row=row,
            column=column)
        
        script = jedi.Script(codeview.get_content(), row, column, filename)
        completions = script.completions() 

        if len(completions) == 0:
            return

        elif len(completions) == 1:
            _complete(codeview, completions[0]) #insert the only completion

        else:
            AutocompleteWindow(codeview, completions) #create the window
    except:
        # Don't want the crash, rather fail "silently"
        traceback.print_exc()

def _get_partial_string(completion): #calculates the partial string such as it was for user when autocomplete was called, used for user_logging info
    return completion.name[:-len(completion.complete)]

#inserts the chosen completion into the current position in the codeview
def _complete(codeview, completion):
    get_workbench().event_generate("AutocompleteFinished",
        partial_string=_get_partial_string(completion),
        chosen_completion=completion.name)
    codeview.text.insert(codeview.text.index('insert'), completion.complete)

#top-level container of the vertical list of suggestions
# TODO: do we need the toplevel?
class AutocompleteWindow(tk.Toplevel): 
    def __init__(self, codeview, completions):
        tk.Toplevel.__init__(self, background='red') #TODO - background configurable

        #create and place the text windget
        self.text = AutocompleteWindowText(self, codeview, completions)
        self.text.grid(row=0, column=0)

        #calculate and apply the position of the window
        insert_index = codeview.text.index("insert");
        wordlen = len(completions[0].name) - len(completions[0].complete)
        insert_pos = codeview.text.bbox(str(insert_index) + '-%dc' % wordlen);
        self.geometry('+%d+%d' % (codeview.text.winfo_rootx() + insert_pos[0] - 2, codeview.text.winfo_rooty() + insert_pos[1] + insert_pos[3]))

        #create bindings
        self.bind("<Escape>", self.destroy)
        #TODO: ??? self.bind("<B1-Motion>", lambda e: "break")
        self.bind("<Double-Button-1>", self.text._set_marked_line)
        self.bind("<Button-1>", self.text._handle_click)
        self.bind_all("<Button-1>", self.text._handle_click) #if the click is outside window, destroy it
        self.overrideredirect(1) #remove the title bar

#inner container showing the list of suggestions
class AutocompleteWindowText(TweakableText):
    def __init__(self, master, codeview, completions, *args, **kwargs):
        #init the text widget - note the height calculation, #TODO - make the height configurable?
        TweakableText.__init__(self, master, height=min(len(completions), 10), 
                               width=30, takefocus=1, insertontime=0, background='#ececea', 
                               borderwidth=1, wrap='none', read_only=False, 
                               *args, **kwargs)

        self.codeview = codeview
        self.completions = completions
        self.marked_line = None #currently selected line
        #tag for the currently selected line, #TODO - make colours configurable
        self.tag_configure("selected", background="#eefb1a", underline=True)
        self._draw_content() #populate the list
        self.mark_set("insert", '1.0')
        #register event bindings
        self.bind("<B1-Motion>", lambda e: "break", True)
        self.bind("<Double-Button-1>", self._choose_completion, True)
        self.bind("<Button-1>", self._handle_click, True)
        self.bind("<Up>", self._up_marked_line, True)
        self.bind("<Down>", self._down_marked_line, True)
        self.bind("<Return>", self._choose_completion, True)
        self.bind("<Escape>", self._ok, True)
        #set the first completion in the list as selected
        self._mark_line(1)
        #force focus in the window
        self.focus_force()

    #listens to all left clicks - if outside the autocomplete window, close it
    def _handle_click(self, event):
        inside_widget = True

        
        if self.master.winfo_containing(event.x_root, event.y_root) != self:
            inside_widget = False

        if inside_widget:
            self._set_marked_line(event) #set the market line based on where click was made

        else:
            self._ok() #destroy the window

    #populate the window with suggestions 
    def _draw_content(self):
        names = [completion.name for completion in self.completions]
        self.insert("1.0", '\n'.join(names))

    #move the marked line up when up key was pressed
    def _up_marked_line(self, event):
        self.mark_set("insert", self.index('insert') + '-1l')
        index = self.index('insert')
        line = int(index[0:index.index('.')])
        self._mark_line(line)
        self.see(index)
        return 'break'

    #move the marked line down when down key was pressed
    def _down_marked_line(self, event):
        self.mark_set("insert", self.index('insert') + '+1l')
        index = self.index('insert')
        line = int(index[0:index.index('.')])
        self._mark_line(line)
        self.see(index)
        return 'break'

    #calculate the marked line based on mouse click location
    def _set_marked_line(self, event):
        index = self.index('@' + str(event.x) + ',' + str(event.y))
        line = int(index[0:index.index('.')])
        self._mark_line(line)
            
    #do the actual line marking - remove previous tag and add the new one
    def _mark_line(self, newline):
        if self.marked_line is not None and self.marked_line == newline:
            return

        self._clear_marked_line()
        self.marked_line = newline

        start_index = self.index(str(self.marked_line) + '.0')
        end_index = self.index(str(self.marked_line) + '.end')

        self.tag_add("selected", start_index, end_index);

    #clear the previously marked line
    def _clear_marked_line(self):
        if self.marked_line == None:
            return

        start_index = self.index(str(self.marked_line) + '.0')
        end_index = self.index(str(self.marked_line) + '.end')

        self.tag_remove("selected", start_index, end_index);

    #finalize choosing the suggestions - insert it into codeview and close window
    def _choose_completion(self, event=None):
        completion = self.completions[self.marked_line-1]
        _complete(self.codeview, completion)
        self._ok(cancel=False)
        
    #unregister global bindings, destroy both inner and top-level widgets
    def _ok(self, event=None, cancel=True):
        if cancel:
            get_workbench().event_generate("AutocompleteCanceled", editor=self.codeview.master)
        self.master.unbind_all("<Button-1>")
        self.master.destroy()
        self.destroy()

def on_autocomplete_request(event=None):
    if event is None:
        text = get_workbench().focus_get()
    else:
        text = event.widget
    
    if not isinstance(text, CodeViewText):
        return
    
    codeview = text.master
    assert isinstance(codeview, CodeView)
    
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if editor.get_code_view() is codeview:
        filename = editor.get_filename()
    else:
        filename = None
    
    
    row, column = map(int, text.index("insert").split("."))
    autocomplete(codeview, row, column, filename)

def load_plugin():
    
    get_workbench().add_command("autocomplete", "edit", "Auto-complete",
        on_autocomplete_request,
        default_sequence="<Control-space>"
        # TODO: tester
        )