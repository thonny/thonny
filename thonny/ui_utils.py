# -*- coding: utf-8 -*-

import time
import os.path
import tkinter as tk
import tkinter.font as tk_font
from tkinter import ttk

from thonny import config, misc_utils
from thonny.misc_utils import running_on_linux, running_on_mac_os, running_on_windows,\
    try_remove_linenumbers
from thonny.user_logging import log_user_event, TextDeleteEvent, TextInsertEvent,\
    UndoEvent, RedoEvent, CutEvent, PasteEvent, CopyEvent, EditorGetFocusEvent,\
    EditorLoseFocusEvent, CommandEvent, KeyPressEvent
import traceback


SASHTHICKNESS = 10
CLAM_BACKGROUND = "#dcdad5"
CALM_WHITE = '#fdfdfd'
EDITOR_FONT = None 
BOLD_EDITOR_FONT = None
IO_FONT = None
TREE_FONT = None


imgdir = os.path.join(os.path.dirname(__file__), 'res')

_event_data = {}
_next_event_data_serial = 1

_held_keys = set()
_modifier_keys = {"Control_L", "Alt_L", "Shift_L",   
                  "Control_R", "Alt_R", "Shift_R",
                  #"131074", "1048584", "262145", # TODO: check on real Mac
                  #"270336", "131076", "1048592"
                  } 


class PanedWindowForViewNotebooks(tk.PanedWindow):
    """
    Enables positioning panes according to their position_key-s.
    Automatically adds/removes itself to/from its master PanedWindow.
    Fixes some style glitches.
    """ 
    def __init__(self, master, location):
        tk.PanedWindow.__init__(self, master)
        
        self._location = location
        style = ttk.Style()
        if style.theme_use() == "clam":
            self.configure(background=CLAM_BACKGROUND)
        elif style.theme_use() == "aqua":
            self.configure(background="systemSheetBackground")
        elif running_on_windows():
            self.configure(background="SystemButtonFace")
    
    def add_notebook(self, child):
        kwargs = {}
        for sibling in self.panes():
            if (not hasattr(sibling, "position_key") 
                or sibling.position_key > child.position_key):
                kwargs["before"] = sibling
                break
        
        self.add(child, **kwargs)
    
    def _update_visibility(self):
        if len(self.panes()) == 0 and self.winfo_ismapped():
            self.master.remove(self)
            
        if len(self.tabs()) > 0 and not self.winfo_ismapped():
            self.master.add_view_notebook(self)
            if self._location == "w":
                pass
            else:
                pass


class ViewNotebook(ttk.Notebook):
    """
    Allows adding views according to their position keys.
    Remember its own position key. Automatically updates its visibility.
    """
    def __init__(self, master, location):
        ttk.Notebook.__init__(self, master)
        self.location = location
    
    def add_view(self, view, text, position_key):
        view.position_key = position_key
        
        for sibling in map(self.nametowidget, self.tabs()):
            if sibling.position_key > view.position_key:
                where = sibling
                break
        else:
            where = "end"
        
        self.insert(where, view, text=text)
    
    def add(self, child, **kw):
        ttk.Notebook.add(self, child, **kw)
        self._update_visibility()
    
    def insert(self, pos, child, **kw):
        ttk.Notebook.insert(self, pos, child, **kw)
        self._update_visibility()
    
    def hide(self, tab_id):
        ttk.Notebook.hide(self, tab_id)
        self._update_visibility()
    
    def forget(self, tab_id):
        ttk.Notebook.forget(self, tab_id)
        self._update_visibility()
    
    def _update_visibility(self):
        if len(self.tabs()) == 0 and self.winfo_ismapped():
            self.master.remove(self)
            
        if len(self.tabs()) > 0 and not self.winfo_ismapped():
            self.master.add_view_notebook(self)
        

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
        log_user_event(TextInsertEvent(self, index, args[1], tags))
    
        
    def _user_text_delete(self, *args, **kw):
        index1 = self.text.index(args[0])
        index2 = self.text.index(args[1])
#        print("DEL", args[0], args[1], self.text.index(args[0]), self.text.index(args[1]), self.text.index(tk.INSERT))
        # subclass may intercept this forwarding
        self._original_user_text_delete(*args, **kw)
#        print("DEL'", args[0], args[1], self.text.index(args[0]), self.text.index(args[1]), self.text.index(tk.INSERT))
        log_user_event(TextDeleteEvent(self, index1, index2))

    def on_text_undo(self, e):
        self._last_event_kind = "undo"
        log_user_event(UndoEvent(self));
        
    def on_text_redo(self, e):
        self._last_event_kind = "redo"
        log_user_event(RedoEvent(self));
        
    def on_text_cut(self, e):
        self._last_event_kind = "cut"
        self.add_undo_separator()        
        log_user_event(CutEvent(self));
        
    def on_text_copy(self, e):
        self._last_event_kind = "copy"
        self.add_undo_separator()        
        log_user_event(CopyEvent(self));
        
    def on_text_paste(self, e):
        self._last_event_kind = "paste"
        self.add_undo_separator()        
        log_user_event(PasteEvent(self));
    
    def on_text_get_focus(self, e):
        self._last_event_kind = "get_focus"
        self.add_undo_separator()        
        log_user_event(EditorGetFocusEvent(self));
        
    def on_text_lose_focus(self, e):
        self._last_event_kind = "lose_focus"
        self.add_undo_separator()        
        log_user_event(EditorLoseFocusEvent(self));
    
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
        log_user_event(KeyPressEvent(self, e.char, e.keysym, self.text.index(tk.INSERT)))

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


def delete_images():
    # otherwise Tk will print a weird error
    global _images
    del _images


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
        # I removed silecing TclError (Aivar)
        try:
            if m:
                return m(*args)
            else:
                return self.tk.call((self.orig, operation) + args)
        except tk.TclError:
            #traceback.print_exc()
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


def start_keeping_track_of_held_keys(tk_root):
        
    tk_root.bind_all("<KeyPress>", _register_key_press, "+")
    tk_root.bind_all("<KeyRelease>", _register_key_release, "+")

def _register_key_press(event):
    keysym = _get_keysym(event)
    _held_keys.add(keysym)

def _register_key_release(event):
    keysym = _get_keysym(event)
    if keysym in _held_keys:
        _held_keys.remove(keysym)

def _get_keysym(event):
    if event.keysym == "??": # shift, alt, Ctrl in OSx86 (Hackintosh)
        return str(event.keycode)
    else:
        return event.keysym

def non_modifier_key_is_held():
    for keysym in _held_keys:
        if (keysym not in _modifier_keys 
            and not (keysym.isnumeric() and len(keysym) > 0)):
            return True
    
    return False


def _tk_version_warning():
    root = tk._default_root
    try:
        import idlelib.macosxSupport
        return idlelib.macosxSupport.tkVersionWarning(root)
    except ImportError:
        # copied from macosxSupport
        if (root._is_on_mac_os() and
                ('AppKit' in root.tk.call('winfo', 'server', '.')) ):
            patchlevel = root.tk.call('info', 'patchlevel')
            if patchlevel not in ('8.5.7', '8.5.9'):
                return False
            return (r"WARNING: The version of Tcl/Tk ({0}) in use may"
                    r" be unstable.\n"
                    r"Visit http://www.python.org/download/mac/tcltk/"
                    r" for current information.".format(patchlevel))
        else:
            return False

class Command:
    def __init__(self, cmd_id, label, accelerator, target_or_finder,
                 kind="command", variable=None, value=None, onvalue=None,
                 variable_name=None, offvalue=None, system_bound=False,
                 source=None):
        self.cmd_id = cmd_id
        self.label = label
        self.accelerator = accelerator
        self.kind = kind
        self.variable=variable
        self.value = value
        self.onvalue = onvalue
        self.offvalue = offvalue
        self._target_or_finder = target_or_finder
        self.system_bound = system_bound
        self.source = source
        if variable is None and variable_name is not None:
            self.variable = config.prefs_vars[variable_name]
    
    def _find_target(self):
        if hasattr(self._target_or_finder, '__call__'):
            return self._target_or_finder()
        else:
            return self._target_or_finder
    
    def execute(self, event=None):
        if self.system_bound:
            return
        
        if hasattr(event, "keysym"):
            # ignore long-press-repeated keypresses
            # TODO: check this
            if event.keysym in _held_keys:
                return
            
            _register_key_press(event)
        
        
        if self.is_enabled():
            target = self._find_target()
            method_name = "cmd_" + self.cmd_id
            method = getattr(target, method_name)
            if self.source is not None:
                source = self.source
            elif event is not None:
                source = "shortcut"
            else:
                source = "menu"
                
            log_user_event(CommandEvent(self.cmd_id, source))
                
            return method()
        else:
            # tk._default_root is our beloved main window             
            tk._default_root.bell()
            #print("Cmd execute: cmd_" + self.cmd_id + " not enabled")
    
    def is_enabled(self):
        target = self._find_target()
        
        if target is None:
            return False
        else:
            method_name = "cmd_" + self.cmd_id + "_enabled"
            if hasattr(target, method_name):
                availability_method = getattr(target, method_name)
                return availability_method()
            else:
                # Let's be optimistic
                return self.system_bound or hasattr(target, "cmd_" + self.cmd_id)
        
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

def notebook_contains(nb, child):
    return str(child) in nb.tabs()



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

    

def create_PanedWindow(master, orient):
    pw = tk.PanedWindow(master,
                          orient=orient,
                          showhandle="False",
                          sashwidth=SASHTHICKNESS)
    style = ttk.Style()
    if style.theme_use() == "clam":
        pw.configure(background=CLAM_BACKGROUND)
    elif style.theme_use() == "aqua":
        pw.configure(background="systemSheetBackground")
    elif running_on_windows():
        pw.configure(background="SystemButtonFace")

    return pw


                
def generate_event(widget, descriptor, data=None):
    global _next_event_data_serial
    
    if data is not None:
        data_serial = _next_event_data_serial
        _next_event_data_serial += 1 
        _event_data[data_serial] = data
        widget.event_generate(descriptor, serial=data_serial)
    else:
        widget.event_generate(descriptor)
        
        

def get_event_data(event):
    if event.serial in _event_data:
        return _event_data[event.serial]
    else:
        return None

def create_menubutton(master):
    font = tk_font.nametofont("TkTextFont").copy()
    #font.configure(size=7)
    
    if "arrow_down" not in _images:
        _images["arrow_down"] = tk.PhotoImage("img_arrow_down", file=os.path.join(imgdir, 'arrow_down2.gif'))
    
    # trying menubutton
    kw_args = {
        "text" : '@1208323432',
        "image" : _images["arrow_down"],
        "compound" : tk.RIGHT,
        "relief" : tk.FLAT,
        #"foreground": "#777777",
        "font" : font
    }
    
    style = ttk.Style()
    if style.theme_use() == "clam":
        kw_args["background"] = CLAM_BACKGROUND
        
    mb = tk.Menubutton(master, **kw_args)
    #mb = ttk.Menubutton(master, text="__main__")
        
    mb.menu = tk.Menu(mb, tearoff=0)
    mb['menu'] = mb.menu

    # TODO: demo
    mayoVar  = tk.IntVar()
    ketchVar = tk.IntVar()
    mb.menu.add_checkbutton(label='mayo', variable=mayoVar)
    mb.menu.add_checkbutton(label='ketchup', variable=ketchVar)
    
    return mb


def add_pane(paned_window, child, position_key, **kwargs):
    """
    Adds pane to paned_window so that panes are sorted according to position_keys
    """
    for sibling in paned_window.panes():
        if (not hasattr(sibling, "position_key") 
            or sibling.position_key > child.position_key):
            kwargs["before"] = sibling
            break
    
    paned_window.add(child, kwargs)
    
def update_paned_window_visibility(paned_window):
    assert (isinstance(paned_window.master, tk.PanedWindow)
         or isinstance(paned_window.master, ttk.PanedWindow))
    
    if paned_window.winfo_ismapped() and len(paned_window.panes()) == 0:
        paned_window.master.remove(paned_window)
        
    if not paned_window.winfo_ismapped() and len(paned_window.panes()) > 0:
        add_pane(paned_window.master, paned_window, )
        paned_window.master.add(paned_window)
    
    
    update_paned_window_visibility(paned_window.master)
        
        
            
    
    
    