# -*- coding: utf-8 -*-

import time
import os.path
import tkinter as tk
from tkinter import ttk, messagebox

from thonny.misc_utils import try_remove_linenumbers, get_res_path,\
    running_on_mac_os
from tkinter.dialog import Dialog
from thonny.globals import get_workbench
from logging import exception


CLAM_BACKGROUND = "#dcdad5"
CALM_WHITE = '#fdfdfd'

_images = set() # for keeping references to tkinter images to avoid garbace colleting them

class AutomaticPanedWindow(tk.PanedWindow):
    """
    Enables inserting panes according to their position_key-s.
    Automatically adds/removes itself to/from its master AutomaticPanedWindow.
    Fixes some style glitches.
    """ 
    def __init__(self, master, position_key=None, **kwargs):
        if not "sashwidth" in kwargs:
            kwargs["sashwidth"]=10
        
        theme = ttk.Style().theme_use()
        
        if not "background" in kwargs:
            kwargs["background"] = "#DCDAD5" if theme == "clam" else "SystemButtonFace"
        
        tk.PanedWindow.__init__(self, master, **kwargs)
        
        """ TODO: test in Linux and Mac 
        style = ttk.Style()
        if style.theme_use() == "clam":
            self.configure(background=CLAM_BACKGROUND)
        elif style.theme_use() == "aqua":
            self.configure(background="systemSheetBackground")
        elif running_on_windows():
            self.configure(background="SystemButtonFace")
        """
        self.position_key = position_key
        self.visible_panes = set()
    
    def insert(self, pos, child, **kw):
        if pos == "auto":
            # According to documentation I should use self.panes()
            # but this doesn't return expected widgets
            for sibling in self.visible_panes:
                if (not hasattr(sibling, "position_key") 
                    or sibling.position_key == None
                    or sibling.position_key > child.position_key):
                    pos = sibling
                    break
            else:
                pos = "end"
            
        if isinstance(pos, tk.Widget):
            kw["before"] = pos
        self.add(child, **kw)

    def add(self, child, **kw):
        if not "minsize" in kw:
            kw["minsize"]=60
            
        tk.PanedWindow.add(self, child, **kw)
        self.visible_panes.add(child)
        self._update_visibility()
    
    def remove(self, child):
        tk.PanedWindow.remove(self, child)
        self.visible_panes.remove(child)
        self._update_visibility()
    
    def forget(self, child):
        tk.PanedWindow.forget(self, child)
        self.visible_panes.remove(child)
        self._update_visibility()
    
    def is_visible(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return self.winfo_ismapped()
        else:
            return self in self.master.visible_panes
    
    def _update_visibility(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return
        
        if len(self.visible_panes) == 0 and self.is_visible():
            self.master.forget(self)
            
        if len(self.panes()) > 0 and not self.is_visible():
            self.master.insert("auto", self)


class AutomaticNotebook(ttk.Notebook):
    """
    Enables inserting views according to their position keys.
    Remember its own position key. Automatically updates its visibility.
    """
    def __init__(self, master, position_key):
        ttk.Notebook.__init__(self, master)
        self.position_key = position_key
    
    def add(self, child, **kw):
        ttk.Notebook.add(self, child, **kw)
        self._update_visibility()
    
    def insert(self, pos, child, **kw):
        if pos == "auto":
            for sibling in map(self.nametowidget, self.tabs()):
                if (not hasattr(sibling, "position_key") 
                    or sibling.position_key == None
                    or sibling.position_key > child.position_key):
                    pos = sibling
                    break
            else:
                pos = "end"
            
        ttk.Notebook.insert(self, pos, child, **kw)
        self._update_visibility()
    
    def hide(self, tab_id):
        ttk.Notebook.hide(self, tab_id)
        self._update_visibility()
    
    def forget(self, tab_id):
        ttk.Notebook.forget(self, tab_id)
        self._update_visibility()
    
    def is_visible(self):
        return self in self.master.visible_panes
        
    def _update_visibility(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return
        if len(self.tabs()) == 0 and self.is_visible():
            self.master.remove(self)
            
        if len(self.tabs()) > 0 and not self.is_visible():
            self.master.insert("auto", self)
        

class TreeFrame(ttk.Frame):
    def __init__(self, master, columns, displaycolumns='#all', show_scrollbar=True):
        ttk.Frame.__init__(self, master)
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        if show_scrollbar:
            self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.tree = ttk.Treeview(self, columns=columns, displaycolumns=displaycolumns, 
                                 yscrollcommand=self.vert_scrollbar.set)
        self.tree['show'] = 'headings'
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.tree.yview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self.on_select, "+")
        self.tree.bind("<Double-Button-1>", self.on_double_click, "+")
        
    def _clear_tree(self):
        for child_id in self.tree.get_children():
            self.tree.delete(child_id)
    
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        pass

class TextWrapper:
    # Used for getting read-only effect
    # http://tkinter.unpythonic.net/wiki/ReadOnlyText

    
    def __init__(self, propose_remove_line_numbers=False):
        self._text_redirector = WidgetRedirector(self.text)
        self._original_user_text_insert = self._text_redirector.register("insert", self._user_text_insert)
        self._original_user_text_delete = self._text_redirector.register("delete", self._user_text_delete)
        """
        self.text.bind("<<Undo>>", self.on_text_undo, "+")
        self.text.bind("<<Redo>>", self.on_text_redo, "+")
        self.text.bind("<<Cut>>", self.on_text_cut, "+")
        self.text.bind("<<Copy>>", self.on_text_copy, "+")
        self.text.bind("<<Paste>>", self.on_text_paste, "+")
        #self.text.bind("<<Selection>>", self.on_text_selection_change, "+")
        self.text.bind("<FocusIn>", self.on_text_get_focus, "+")
        self.text.bind("<FocusOut>", self.on_text_lose_focus, "+")
        self.text.bind("<Key>", self.on_text_key_press, "+")
        self.text.bind("<KeyRelease>", self.on_text_key_release, "+")
        self.text.bind("<1>", self.on_text_mouse_click, "+")
        self.text.bind("<2>", self.on_text_mouse_click, "+")
        self.text.bind("<3>", self.on_text_mouse_click, "+")
        """
        self._last_event_kind = None
        self._last_key_time = 0
        self._propose_remove_line_numbers = propose_remove_line_numbers

        # These are needed because code copied from idlelib relies on such methods
        self.started_undo_blocks = 0
        self.text.undo_block_start = self.undo_block_start
        self.text.undo_block_stop = self.undo_block_stop
        # TODO: see idlelib.EditorWindow.reset_undo
 
    def _user_text_insert(self, *args, **kw):
        index = self.text.index(args[0])
        text = args[1]
        
        if text >= "\uf704" and text <= "\uf70d": # Function keys F1..F10 in Mac cause these
            return
        
        # subclass may intercept this forwarding
#        print("INS", args[0], args[1], self.text.index(args[0]), self.text.index(tk.INSERT))
        
        # try removing line numbers
        # TODO: shouldn't it take place only on paste?
        # TODO: does it occur when opening a file with line numbers in it?
        if self._propose_remove_line_numbers and isinstance(args[1], str):
            args = tuple((args[0],) + (try_remove_linenumbers(args[1], self.text),) + args[2:])
        
        self._original_user_text_insert(*args, **kw)
#        print("INS'", args[0], args[1], self.text.index(args[0]), self.text.index(tk.INSERT))
        if len(args) >= 3:
            tags = args[2]
        else:
            tags = None 
        #log_user_event(TextInsertEvent(self, index, args[1], tags)) TODO:
    
        
    def _user_text_delete(self, *args, **kw):
        index1 = self.text.index(args[0])
        index2 = self.text.index(args[1])
#        print("DEL", args[0], args[1], self.text.index(args[0]), self.text.index(args[1]), self.text.index(tk.INSERT))
        # subclass may intercept this forwarding
        self._original_user_text_delete(*args, **kw)
#        print("DEL'", args[0], args[1], self.text.index(args[0]), self.text.index(args[1]), self.text.index(tk.INSERT))
        #log_user_event(TextDeleteEvent(self, index1, index2)) TODO:

    def on_text_undo(self, e):
        self._last_event_kind = "undo"
        
    def on_text_redo(self, e):
        self._last_event_kind = "redo"
        
    def on_text_cut(self, e):
        self._last_event_kind = "cut"
        self.add_undo_separator()        
        
    def on_text_copy(self, e):
        self._last_event_kind = "copy"
        self.add_undo_separator()        
        
    def on_text_paste(self, e):
        self._last_event_kind = "paste"
        self.add_undo_separator()        
    
    def on_text_get_focus(self, e):
        self._last_event_kind = "get_focus"
        self.add_undo_separator()        
        
    def on_text_lose_focus(self, e):
        self._last_event_kind = "lose_focus"
        self.add_undo_separator()        
    
    def on_text_key_release(self, e):
        pass
            
    def on_text_key_press(self, e):
        #if e.keysym in ('F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'):
        #    return "break" # otherwise it inserts a character in
            
        event_kind = self.get_event_kind(e)
        
        if (event_kind != self._last_event_kind
            or e.char in ("\r", "\n", " ")
            or time.time() - self.last_key_time > 2):
            self.add_undo_separator()
            self._last_event_kind = event_kind

        self.last_key_time = time.time()

    def on_text_mouse_click(self, event):
        self.add_undo_separator()
    
    def add_undo_separator(self):
        if self.started_undo_blocks == 0:
            self.text.edit_separator()
    
    def get_event_kind(self, event):
        if event.keysym in ("BackSpace", "Delete"):
            return "delete"
        elif event.char:
            return "insert"
        else:
            # eg. e.keysym in ("Left", "Up", "Right", "Down", "Home", "End", "Prior", "Next"):
            return "other_key"

    def undo_block_start(self):
        self.started_undo_blocks += 1
    
    def undo_block_stop(self):
        self.started_undo_blocks -= 1
        if self.started_undo_blocks == 0:
            self.add_undo_separator()

class TextFrame(ttk.Frame, TextWrapper):
    def __init__(self, master, readonly=False):
        ttk.Frame.__init__(self, master)
        
        self.readonly = readonly
        self.vert_scrollbar = AutoScrollbar(self, orient=tk.VERTICAL)
        self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.hor_scrollbar = AutoScrollbar(self, orient=tk.HORIZONTAL)
        self.hor_scrollbar.grid(row=1, column=0, sticky=tk.NSEW)
        self.text = tk.Text(self,
                            borderwidth=0,
                            yscrollcommand=self.vert_scrollbar.set,
                            xscrollcommand=self.hor_scrollbar.set,
                            padx=4,
                            insertwidth=2,
                            wrap='none')
        self.text.grid(row=0, column=0, sticky=tk.NSEW)
        self.vert_scrollbar['command'] = self.text.yview
        self.hor_scrollbar['command'] = self.text.xview
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        TextWrapper.__init__(self)
        
        
    def _user_text_insert(self, *args, **kw):
        if not self.readonly:
            TextWrapper._user_text_insert(self, *args, **kw)
    
    def _user_text_delete(self, *args, **kw):
        if not self.readonly:
            TextWrapper._user_text_delete(self, *args, **kw)
    
    def set_content(self, content):
        TextWrapper._user_text_delete(self, "1.0", tk.END)
        TextWrapper._user_text_insert(self, "1.0", content)



class WidgetRedirector:
    # Copied for Python 3.3.2 idlelib.WidgetRedirector so that IDLE is not a requirement
    def __init__(self, widget):
        self._operations = {}
        self.widget = widget            # widget instance
        self.tk = tk = widget.tk        # widget's root
        w = widget._w                   # widget's (full) Tk pathname
        self.orig = w + "_orig"
        # Rename the Tcl command within Tcl:
        tk.call("rename", w, self.orig)
        # Create a new Tcl command whose name is the widget's pathname, and
        # whose action is to dispatch on the operation passed to the widget:
        tk.createcommand(w, self.dispatch)

    def __repr__(self):
        return "WidgetRedirector(%s<%s>)" % (self.widget.__class__.__name__,
                                             self.widget._w)

    def close(self):
        for operation in list(self._operations):
            self.unregister(operation)
        widget = self.widget; del self.widget
        orig = self.orig; del self.orig
        tk = widget.tk
        w = widget._w
        tk.deletecommand(w)
        # restore the original widget Tcl command:
        tk.call("rename", orig, w)

    def register(self, operation, function):
        self._operations[operation] = function
        setattr(self.widget, operation, function)
        return WidgetRedirector.OriginalCommand(self, operation)

    def unregister(self, operation):
        if operation in self._operations:
            function = self._operations[operation]
            del self._operations[operation]
            if hasattr(self.widget, operation):
                delattr(self.widget, operation)
            return function
        else:
            return None

    def dispatch(self, operation, *args):
        '''Callback from Tcl which runs when the widget is referenced.

        If an operation has been registered in self._operations, apply the
        associated function to the args passed into Tcl. Otherwise, pass the
        operation through to Tk via the original Tcl function.

        Note that if a registered function is called, the operation is not
        passed through to Tk.  Apply the function returned by self.register()
        to *args to accomplish that.  For an example, see ColorDelegator.py.

        '''
        m = self._operations.get(operation)
        try:
            if m:
                return m(*args)
            else:
                return self.tk.call((self.orig, operation) + args)
        except tk.TclError:
            exception("Exception caught by WidgetRedirector, operation=" + operation)
            #raise # put it back if you need to debug
            return ""


    class OriginalCommand:
    
        def __init__(self, redir, operation):
            self.redir = redir
            self.operation = operation
            self.tk = redir.tk
            self.orig = redir.orig
            self.tk_call = self.tk.call
            self.orig_and_operation = (self.orig, self.operation)
    
        def __repr__(self):
            return "OriginalCommand(%r, %r)" % (self.redir, self.operation)
    
        def __call__(self, *args):
            return self.tk_call(self.orig_and_operation + args)


def sequence_to_accelerator(sequence):
    """Translates Tk event sequence to customary shortcut string
    for showing in the menu"""
    
    if not sequence:
        return ""
    
    accelerator = (sequence
        .strip("<>")
        .replace("Key-", "")
        .replace("KeyPress", "")
        .replace("Control", "Ctrl")
        .replace("-Minus", "--").replace("-minus", "--")
        .replace("-Plus", "-+").replace("-plus", "-+")
    )
        
    # it's customary to show keys with capital letters
    # but tk would treat this as pressing with shift
    parts = accelerator.split("-")
    if len(parts[-1]) == 1 and "Shift" not in accelerator:
        parts[-1] = parts[-1].upper()
    
    return "+".join(parts)
    

        
def get_zoomed(toplevel):
    if "-zoomed" in toplevel.wm_attributes(): # Linux
        return bool(toplevel.wm_attributes("-zoomed"))
    else: # Win/Mac
        return toplevel.wm_state() == "zoomed"
          

def set_zoomed(toplevel, value):
    if "-zoomed" in toplevel.wm_attributes(): # Linux
        toplevel.wm_attributes("-zoomed", str(int(value)))
    else: # Win/Mac
        if value:
            toplevel.wm_state("zoomed")
        else:
            toplevel.wm_state("normal")


class AutoScrollbar(ttk.Scrollbar):
    # http://effbot.org/zone/tkinter-autoscrollbar.htm
    # a vert_scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        # TODO: this can make GUI hang or max out CPU when scrollbar wobbles back and forth
        """
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        else:
            self.grid()
        """
        ttk.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")
    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")

def update_entry_text(entry, text):
    original_state = entry.cget("state")
    entry.config(state="normal")
    entry.delete(0, "end")
    entry.insert(0, text)
    entry.config(state=original_state)


class ScrollableFrame(tk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    
    def __init__(self, master):
        tk.Frame.__init__(self, master, bg=CALM_WHITE)
        
        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bg=CALM_WHITE, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.interior = tk.Frame(self.canvas, bg=CALM_WHITE)
        self.interior.columnconfigure(0, weight=1)
        self.interior.rowconfigure(0, weight=1)
        self.interior_id = self.canvas.create_window(0,0, 
                                                    window=self.interior, 
                                                    anchor=tk.NW)
        self.bind('<Configure>', self._configure_interior, "+")
        self.bind('<Expose>', self._expose, "+")
        
    def _expose(self, event):
        self.update_idletasks()
        self._configure_interior(event)
    
    def _configure_interior(self, event):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width() , self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10):
            # update the interior's width to fit canvas
            #print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id,
                                      width=self.canvas.winfo_width())

class TtkDialog(Dialog):
    def buttonbox(self):
        '''add standard button box.

        override if you do not want the standard buttons
        '''

        box = ttk.Frame(self)

        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok, True)
        self.bind("<Escape>", self.cancel, True)

        box.pack()

    

class _QueryDialog(TtkDialog):

    def __init__(self, title, prompt,
                 initialvalue=None,
                 minvalue = None, maxvalue = None,
                 master = None,
                 selection_range=None):

        if not master:
            master = tk._default_root

        self.prompt   = prompt
        self.minvalue = minvalue
        self.maxvalue = maxvalue

        self.initialvalue = initialvalue
        self.selection_range = selection_range

        Dialog.__init__(self, master, title)

    def destroy(self):
        self.entry = None
        Dialog.destroy(self)

    def body(self, master):

        w = ttk.Label(master, text=self.prompt, justify=tk.LEFT)
        w.grid(row=0, padx=5, sticky=tk.W)

        self.entry = ttk.Entry(master, name="entry")
        self.entry.grid(row=1, padx=5, sticky="we")

        if self.initialvalue is not None:
            self.entry.insert(0, self.initialvalue)
            
            if self.selection_range:
                self.entry.icursor(self.selection_range[0])
                self.entry.select_range(self.selection_range[0], self.selection_range[1])
            else:
                self.entry.select_range(0, tk.END)

        return self.entry

    def validate(self):
        try:
            result = self.getresult()
        except ValueError:
            messagebox.showwarning(
                "Illegal value",
                self.errormessage + "\nPlease try again",
                parent = self
            )
            return 0

        if self.minvalue is not None and result < self.minvalue:
            messagebox.showwarning(
                "Too small",
                "The allowed minimum value is %s. "
                "Please try again." % self.minvalue,
                parent = self
            )
            return 0

        if self.maxvalue is not None and result > self.maxvalue:
            messagebox.showwarning(
                "Too large",
                "The allowed maximum value is %s. "
                "Please try again." % self.maxvalue,
                parent = self
            )
            return 0

        self.result = result

        return 1

class _QueryString(_QueryDialog):
    def __init__(self, *args, **kw):
        if "show" in kw:
            self.__show = kw["show"]
            del kw["show"]
        else:
            self.__show = None
        _QueryDialog.__init__(self, *args, **kw)

    def body(self, master):
        entry = _QueryDialog.body(self, master)
        if self.__show is not None:
            entry.configure(show=self.__show)
        return entry

    def getresult(self):
        return self.entry.get()


class ToolTip(object):
    """Taken from http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml"""

    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        x, y, _, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + 27
        y = y + cy + self.widget.winfo_rooty() +27
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                      background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                      font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text):
    toolTip = ToolTip(widget)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

def askstring(title, prompt, **kw):
    '''get a string from the user

    Arguments:

        title -- the dialog title
        prompt -- the label text
        **kw -- see SimpleDialog class

    Return value is a string
    '''
    d = _QueryString(title, prompt, **kw)
    return d.result


def get_current_notebook_tab_widget(notebook):    
    for child in notebook.winfo_children():
        if str(child) == str(notebook.select()):
            return child
        
    return None


