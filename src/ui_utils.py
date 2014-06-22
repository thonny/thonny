# -*- coding: utf-8 -*-

import os.path
 
import tkinter as tk
from tkinter import ttk
import tkinter.font as tk_font

import config

from user_logging import log_user_event, TextDeleteEvent, TextInsertEvent,\
    UndoEvent, RedoEvent, CutEvent, PasteEvent, CopyEvent, EditorGetFocusEvent,\
    EditorLoseFocusEvent, CommandEvent, KeyPressEvent


SASHTHICKNESS = 10
CLAM_BACKGROUND = "#dcdad5"
CALM_WHITE = '#fdfdfd'
EDITOR_FONT = None 
BOLD_EDITOR_FONT = None
IO_FONT = None
TREE_FONT = None


imgdir = os.path.join(os.path.dirname(__file__), 'res')

_images = {} # save them here to avoid them being gc-d 
_event_data = {}
_next_event_data_serial = 1

_held_keys = set()
_modifier_keys = {"Control_L", "Alt_L", "Shift_L",   
                  "Control_R", "Alt_R", "Shift_R",
                  #"131074", "1048584", "262145", # TODO: check on real Mac
                  #"270336", "131076", "1048592"
                  } 

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

def setup_style():
    style = ttk.Style()
    print(style.theme_names())
    if 'xpnative' in style.theme_names():
        # gives better scrollbars in empty editors
        # and Python 2.7 and 3.1 don't have "vista" theme anyway
        theme = 'xpnative'
    elif 'aqua' in style.theme_names():
        theme = 'aqua'
    elif 'clam' in style.theme_names():
        theme = 'clam'
    else:
        theme = style.theme_use()
        
    style.theme_use(theme)
    #style.theme_use("clam")
    
    
    style.configure("Sash", sashthickness=SASHTHICKNESS)
    
    # get rid of Treeview borders
    style.layout("Treeview", [
        ('Treeview.treearea', {'sticky': 'nswe'})
    ])
    
    # necessary for Python 2.7 TODO: doesn't help for aqua
    style.configure("Treeview", background="white")
    
    
    """
    _images[1] = tk.PhotoImage("img_close",
        file=os.path.join(imgdir, '1x1_white.gif'))
    _images[2] = tk.PhotoImage("img_closeactive",
        file=os.path.join(imgdir, 'close_active.gif'))
    _images[3] = tk.PhotoImage("img_closepressed",
        file=os.path.join(imgdir, 'close_pressed.gif'))
        
    style.element_create("close", "image", "img_close",
        ("active", "pressed", "!disabled", "img_closepressed"),
        ("active", "!disabled", "img_closeactive"), border=8, sticky='')
    """
    _images[4] = tk.PhotoImage("gray_line1", file=os.path.join(imgdir, 'gray_line.gif'))
    _images[5] = tk.PhotoImage("gray_line2", file=os.path.join(imgdir, 'gray_line.gif'))
    
    style.element_create("gray_line", "image", "gray_line1",
                               ("!selected", "gray_line2"), 
                               height=1, width=10, border=1)
    
    
    if theme == "xpnative":
        # add a line below active tab to separate it from content
        style.layout("Tab", [
            ('Notebook.tab', {'sticky': 'nswe', 'children': [
                ('Notebook.padding', {'sticky': 'nswe', 'children': [
                    ('Notebook.focus', {'sticky': 'nswe', 'children': [
                        ('Notebook.label', {'sticky': '', 'side': 'left'}),
                        #("close", {"side": "left", "sticky": ''})
                    ], 'side': 'top'})
                ], 'side': 'top'}),
                ('gray_line', {'sticky': 'we', 'side': 'bottom'}),
            ]}),
        ])
        
        style.configure("Tab", padding=(4,1,0,0))
        
    elif theme == "aqua":
        style.map("TNotebook.Tab", foreground=[('selected', 'white'), ('!selected', 'black')])
        
        
        
    
    """
    ################
    #print(style.layout("TMenubutton"))
    style.layout("TMenubutton", [
        ('Menubutton.dropdown', {'side': 'right', 'sticky': 'ns'}),
        ('Menubutton.button', {'children': [
            #('Menubutton.padding', {'children': [
                ('Menubutton.label', {'sticky': ''})
            #], 'expand': '1', 'sticky': 'we'})
        ], 'expand': '1', 'sticky': 'nswe'})
    ])
    
    style.configure("TMenubutton", padding=14)
    """
    
    
    #print(style.map("Treeview"))
    #print(style.layout("Treeview"))
    setup_fonts()
    style.configure("Treeview.treearea", font=TREE_FONT)
    if running_on_linux():
        style.map("Treeview",
              background=[('selected', 'focus', 'light blue'),
                          ('selected', '!focus', 'light grey'),
                          ],
              foreground=[('selected', 'black'),
                          ],
              )
    else:
        style.map("Treeview",
              background=[('selected', 'focus', 'SystemHighlight'),
                          ('selected', '!focus', 'light grey'),
                          ],
              foreground=[('selected', 'SystemHighlightText')],
              )
    
    


def setup_fonts():
    if running_on_mac_os():
        base_font_size = 15
    else:
        base_font_size = 10;
    # fonts
    global EDITOR_FONT, BOLD_EDITOR_FONT, IO_FONT, TREE_FONT
    EDITOR_FONT = tk_font.Font(family="Courier New", size=base_font_size)
    BOLD_EDITOR_FONT = tk_font.Font(family="Courier New", size=base_font_size, weight="bold")
    IO_FONT = tk_font.Font(family='Courier New', size=base_font_size-2, slant="roman")
    default_font = tk_font.nametofont("TkDefaultFont")
    TREE_FONT = tk_font.Font(family=default_font.cget("family"), size=12)


class _KeyboardZoomable:
    def __init__(self):
        self.held_keys = set()
    
    def normalize_keysym(self, keycode, keysym):
        if keysym.startswith("Control"):
            return "Control"
        elif keysym == '??' and keycode in (1048584, 1048592, '1048584', '1048592'):
            print("Fake control")
            return "Control"
        else:
            return keysym
        
    def cmd_key_press(self, event):
        print("press", event.keycode, event.keysym, event.keysym_num, event.num)
        
        norm_keysym = self.normalize_keysym(event.keycode, event.keysym)
        
        if norm_keysym in self.held_keys: # ignore repeated events
            return
        
        self.held_keys.add(norm_keysym)
        
        if norm_keysym == "Return":
            if 'Control' in self.held_keys:
                self.zoom_in() 
            else:
                self.execute_focus()
        elif norm_keysym == 'Control':
            self.preview_zoom()

    
    def cmd_key_release(self, event):
        print("release", event.keycode, event.keysym, event.keysym_num, event.num)
        norm_keysym = self.normalize_keysym(event.keycode, event.keysym)

        if norm_keysym in self.held_keys:
            self.held_keys.remove(norm_keysym)
        
        # don't clear if zoom-in has already occured
        if norm_keysym == "Control" and self.current_zoom == None:
            self.clear_preview()
    
    def zoom_in(self):
        pass
    
    def execute_focus(self):
        pass
         
    def preview_zoom(self):
        pass
    
    def clear_preview(self):
        pass
    
class PanelBook(ttk.Notebook):
    def __init__(self, master):
        ttk.Notebook.__init__(self, master, padding=0)
        """
        self.menubutton = create_menubutton(self)
        self._position_menubutton()
        self.bind("<Configure>", self._position_menubutton)
        """
    
    def _position_menubutton(self, *args):
        #self.update_idletasks()
        self.menubutton.place(y=0,
            x=self.winfo_width() - self.menubutton.winfo_width(),
            anchor=tk.NW)

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
    def __init__(self):
        self._text_redirector = WidgetRedirector(self.text)
        self._original_user_text_insert = self._text_redirector.register("insert", self._user_text_insert)
        self._original_user_text_delete = self._text_redirector.register("delete", self._user_text_delete)
        
        self.text.bind("<<Undo>>", self.on_text_undo, "+")
        self.text.bind("<<Redo>>", self.on_text_redo, "+")
        self.text.bind("<<Cut>>", self.on_text_cut, "+")
        self.text.bind("<<Copy>>", self.on_text_copy, "+")
        self.text.bind("<<Paste>>", self.on_text_paste, "+")
        # self.text.bind("<<Selection>>", self.on_text_selection_change, "+")
        self.text.bind("<FocusIn>", self.on_text_get_focus, "+")
        self.text.bind("<FocusOut>", self.on_text_lose_focus, "+")
        self.text.bind("<Key>", self.on_text_key_press, "+")
        
        self._last_event_kind = None
 
    def _user_text_insert(self, *args, **kw):
        index = self.text.index(args[0])
        # subclass may intercept this forwarding
#        print("INS", args[0], args[1], self.text.index(args[0]), self.text.index(tk.INSERT))
        
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
        self.text.edit_separator()        
        log_user_event(CutEvent(self));
        
    def on_text_copy(self, e):
        self._last_event_kind = "copy"
        self.text.edit_separator()        
        log_user_event(CopyEvent(self));
        
    def on_text_paste(self, e):
        self._last_event_kind = "paste"
        self.text.edit_separator()        
        log_user_event(PasteEvent(self));
    
    def on_text_get_focus(self, e):
        self._last_event_kind = "get_focus"
        self.text.edit_separator()        
        log_user_event(EditorGetFocusEvent(self));
        
    def on_text_lose_focus(self, e):
        self._last_event_kind = "lose_focus"
        self.text.edit_separator()        
        log_user_event(EditorLoseFocusEvent(self));
    
    def on_text_key_press(self, e):
        if e.keysym in ("BackSpace", "Delete"):
            if self._last_event_kind != "delete":
                self.text.edit_separator()
            self._last_event_kind = "delete"
        
        elif e.char:
            if self._last_event_kind != "insert":
                self.text.edit_separator()
            self._last_event_kind = "insert"


        if e.char in ("\r", "\n", " "):
            self.text.edit_separator()
        log_user_event(KeyPressEvent(self, e, self.text.index(tk.INSERT)))


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

def running_on_windows():
    return tk._default_root.call('tk', 'windowingsystem') == "win32"
    
def running_on_mac_os():
    return tk._default_root.call('tk', 'windowingsystem') == "aqua"
    
def running_on_linux():
    return tk._default_root.call('tk', 'windowingsystem') == "x11"


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
        if variable == None and variable_name != None:
            self.variable = config.prefs_vars[variable_name]
    
    def _find_target(self):
        if hasattr(self._target_or_finder, '__call__'):
            return self._target_or_finder()
        else:
            return self._target_or_finder
    
    def execute(self, event=None):
        if hasattr(event, "keysym"):
            # ignore long-press-repeated keypresses
            if event.keysym in _held_keys:
                return
            
            _register_key_press(event)
        
        
        if self.is_enabled():
            target = self._find_target()
            method_name = "cmd_" + self.cmd_id
            method = getattr(target, method_name)
            if self.source != None:
                source = self.source
            elif event != None:
                source = "shortcut"
            else:
                source = "menu"
                
            log_user_event(CommandEvent(self.cmd_id, source))
                
            return method()
        else:
            # tk._default_root is our beloved main window             
            tk._default_root.bell()
            print("Cmd execute: cmd_" + self.cmd_id + " not enabled")
    
    def is_enabled(self):
        target = self._find_target()
        
        if target == None:
            return False
        else:
            method_name = "cmd_" + self.cmd_id + "_enabled"
            if hasattr(target, method_name):
                availability_method = getattr(target, method_name)
                return availability_method()
            else:
                # Let's be optimistic
                return hasattr(target, "cmd_" + self.cmd_id)
        
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
                
def generate_event(widget, descriptor, data=None):
    global _next_event_data_serial
    
    if data != None:
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