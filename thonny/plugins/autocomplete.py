#TODO - remove unnecessary imports, organize them to use the same import syntax

from tkinter import Text, Toplevel
from idlelib.WidgetRedirector import WidgetRedirector
import jedi
from thonny.globals import get_workbench



#TODO list:
#1) make autocomplete window colors (both bg and fg) configurable
#2) adjust the window position in cases where it's too close to bottom or right edge - but make sure the current line is shown
#3) perhaps make the number of maximum autocomplete options to show configurable?

#the primary method that's intended to be called from codeview
#uses jedi functionality to get a list of completion suggestions based on the code source
#if 0 suggestions are found, does nothing
#if 1 suggestion is found, inserts it into the text
#if 2+ suggestions are found, creates a vertical list of suggestions where the user can choose
def autocomplete(codeview, row, column):
    try: #everything in a try block - if something goes wrong, we don't want the program to crash
        get_workbench().event_generate("AutocompleteQuery",
            editor=codeview.master,
            row=row,
            column=column)
                
        script = jedi.Script(codeview.get_content(), row, column, codeview.master._filename)
        completions = script.completions() #get the list of suggestions

        if len(completions) == 0:
            return

        elif len(completions) == 1:
            _complete(codeview, completions[0]) #insert the only completion

        else:
            AutocompleteWindow(codeview, completions) #create the window
    except:
        return

def _get_partial_string(completion): #calculates the partial string such as it was for user when autocomplete was called, used for user_logging info
    return completion.name[:-len(completion.complete)]

#inserts the chosen completion into the current position in the codeview
def _complete(codeview, completion):
    get_workbench().event_generate("AutocompleteFinished",
        partial_string=_get_partial_string(completion),
        chosen_completion=completion.name)
    codeview._user_text_insert(codeview.text.index('insert'), completion.complete)

#top-level container of the vertical list of suggestions
# TODO: do we need the toplevel?
class AutocompleteWindow(Toplevel): 
    def __init__(self, master, completions):
        Toplevel.__init__(self, background='red') #TODO - background configurable

        #create and place the text windget
        self.text = AutocompleteWindowText(self, master, completions)
        self.text.grid(row=0, column=0)

        #calculate and apply the position of the window
        insert_index = master.text.index("insert");
        wordlen = len(completions[0].name) - len(completions[0].complete)
        insert_pos = master.text.bbox(str(insert_index) + '-%dc' % wordlen);
        self.geometry('+%d+%d' % (master.text.winfo_rootx() + insert_pos[0] - 2, master.text.winfo_rooty() + insert_pos[1] + insert_pos[3]))

        #create bindings
        self.bind("<Escape>", self.destroy)
        self.bind("<B1-Motion>", lambda e: "break")
        self.bind("<Double-Button-1>", self.text._set_marked_line)
        self.bind("<Button-1>", self.text._handle_click)
        self.bind_all("<Button-1>", self.text._handle_click) #if the click is outside window, destroy it
        self.overrideredirect(1) #remove the title bar

#inner container showing the list of suggestions
class AutocompleteWindowText(Text):
    def __init__(self, master, codeview, content, *args, **kwargs):
        
        #init the text widget - note the height calculation, #TODO - make the height configurable?
        Text.__init__(self, master, height=min(len(content), 10), width=30, takefocus=1, insertontime=0, background='#ececea', borderwidth=1, wrap='none', *args, **kwargs)

        self.parent = master
        self.codeview = codeview
        self.redirector = WidgetRedirector(self) #a (fancy?) way of disabling it
        self.content = content #list of completions
        self.marked_line = None #currently selected line
        #tag for the currently selected line, #TODO - make colours configurable
        self.tag_configure("selected", background="#eefb1a", underline=True)
        self._draw_content() #populate the list
        self.mark_set("insert", '1.0')
        #redirect insert/delete actions
        self.insert = self.redirector.register("insert", lambda *args, **kw: "break")
        self.delete = self.redirector.register("delete", lambda *args, **kw: "break")
        #register event bindings
        self.bind("<B1-Motion>", lambda e: "break")
        self.bind("<Double-Button-1>", self._choose_completion)
        self.bind("<Button-1>", self._handle_click)
        self.bind("<Up>", self._up_marked_line)
        self.bind("<Down>", self._down_marked_line)
        self.bind("<Return>", self._choose_completion)
        self.bind("<Escape>", self._ok)
        #set the first completion in the list as selected
        self._mark_line(1)
        #force focus in the window
        self.focus_force()

    #listens to all left clicks - if outside the autocomplete window, close it
    def _handle_click(self, event):
        inside_widget = True

        
        if self.parent.winfo_containing(event.x_root, event.y_root) != self:
            inside_widget = False

        if inside_widget:
            self._set_marked_line(event) #set the market line based on where click was made

        else:
            self._ok() #destroy the window

    #populate the window with suggestions 
    def _draw_content(self):
        for line_index in range(len(self.content)):
            self.insert(self.index("end"), self.content[line_index].name)
            if line_index != len(self.content)-1:
                self.insert(self.index("end"), '\n')

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
    def _choose_completion(self):
        completion = self.content[self.marked_line-1]
        _complete(self.codeview, completion)
        self._ok(cancel=False)
        
    #unregister global bindings, destroy both inner and top-level widgets
    def _ok(self, event=None, cancel=True):
        if cancel:
            get_workbench().event_generate("AutocompleteCanceled", editor=self.codeview.master)
        self.parent.unbind_all("<Button-1>")
        self.parent.destroy()
        self.destroy()

def _load_plugin():
    def cmd_autocomplete():
        # TODO: enable autocomplete also in shell
        editor = get_workbench().get_editor_notebook().get_current_editor()
        if editor:
            text = editor._code_view.text
            index = text.index('insert')
            delim = index.index('.')
            row = int(index[0:delim])
            column = int(index[delim+1:])
            autocomplete(editor._code_view, row, column)
    
    get_workbench().add_command("autocomplete", "edit", "Auto-complete",
        cmd_autocomplete,
        default_sequence="<Control-space>"
        # TODO: tester
        )