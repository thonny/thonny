# -*- coding: utf-8 -*-
from tkinter import ttk, messagebox, filedialog
from tkinter.dialog import Dialog

from thonny import tktextext, misc_utils
from thonny import get_workbench
from thonny.misc_utils import running_on_mac_os, running_on_windows, running_on_linux
from typing import Union, List  # @UnusedImport
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import traceback

import textwrap
import re
import collections
import threading
import signal
import subprocess
import os
import logging
import shutil
import platform
from typing import Callable, Optional
from thonny.tktextext import TweakableText
from thonny.common import TextRange

class CustomMenubar(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master, style="CustomMenubar.TFrame")
        self._menus = []
        self._opened_menu = None
        
        
        ttk.Style().map("CustomMenubarLabel.TLabel",
              background=[("!active", lookup_style_option("Menubar", "background", "gray")),
                          ("active",  lookup_style_option("Menubar", "activebackground", "LightYellow"))],
              foreground=[("!active", lookup_style_option("Menubar", "foreground", "black")),
                          ("active",  lookup_style_option("Menubar", "activeforeground", "black"))],
              )
    
    def add_cascade(self, label, menu):
        label_widget = ttk.Label(self, style="CustomMenubarLabel.TLabel",
                                 text=label,
                                 padding=[6,3,6,2], 
                                 font="TkDefaultFont")
        
        if len(self._menus) == 0:
            padx = (6,0)
        else:
            padx = 0
        
        label_widget.grid(row=0, column=len(self._menus), padx=padx)
        
        def enter(event):
            label_widget.state(("active",))
            
            # Don't know how to open this menu when another menu is open
            # another tk_popup just doesn't work unless old menu is closed by click or Esc 
            # https://stackoverflow.com/questions/38081470/is-there-a-way-to-know-if-tkinter-optionmenu-dropdown-is-active
            # unpost doesn't work in Win and Mac: https://www.tcl.tk/man/tcl8.5/TkCmd/menu.htm#M62
            #print("ENTER", menu, self._opened_menu)
            if self._opened_menu is not None:
                self._opened_menu.unpost()
                click(event)
        
        def leave(event):
            label_widget.state(("!active",))
        
        def click(event):
            try:
                #print("Before")
                self._opened_menu = menu
                menu.tk_popup(label_widget.winfo_rootx(), 
                          label_widget.winfo_rooty() + label_widget.winfo_height())
            finally:
                #print("After")
                self._opened_menu = None
            
        
        label_widget.bind("<Enter>", enter, True)
        label_widget.bind("<Leave>", leave, True)
        label_widget.bind("<1>", click, True)
        self._menus.append(menu)

class AutomaticPanedWindow(tk.PanedWindow):
    """
    Enables inserting panes according to their position_key-s.
    Automatically adds/removes itself to/from its master AutomaticPanedWindow.
    Fixes some style glitches.
    """ 

    
    def __init__(self, master, position_key=None,
                first_pane_size=1/3, last_pane_size=1/3, **kwargs):
        
        tk.PanedWindow.__init__(self, master, **kwargs)
        
        self.position_key = position_key
        self.visible_panes = set()
        self.first_pane_size = first_pane_size
        self.last_pane_size = last_pane_size
        self._restoring_pane_sizes = False
        
        self._last_window_size = (0,0)
        self._full_size_not_final = True
        self._configure_binding = self.winfo_toplevel().bind("<Configure>", self._on_window_resize, True)
        self._update_appearance_binding = self.bind("<<ThemeChanged>>", self._update_appearance, True)
        self.bind("<B1-Motion>", self._on_mouse_dragged, True)
        self._update_appearance()
    
    def insert(self, pos, child, **kw):
        if pos == "auto":
            # According to documentation I should use self.panes()
            # but this doesn't return expected widgets
            for sibling in sorted(self.visible_panes, 
                                  key=lambda p:p.position_key 
                                        if hasattr(p, "position_key")
                                        else 0):
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
        self._check_restore_pane_sizes()
    
    def remove(self, child):
        tk.PanedWindow.remove(self, child)
        self.visible_panes.remove(child)
        self._update_visibility()
        self._check_restore_pane_sizes()
    
    def forget(self, child):
        tk.PanedWindow.forget(self, child)
        self.visible_panes.remove(child)
        self._update_visibility()
        self._check_restore_pane_sizes()
    
    def destroy(self):
        self.winfo_toplevel().unbind("<Configure>", self._configure_binding)
        self.unbind("<<ThemeChanged>>", self._update_appearance_binding)
        tk.PanedWindow.destroy(self)
        
    
    
    def is_visible(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return self.winfo_ismapped()
        else:
            return self in self.master.visible_panes
    
    def _on_window_resize(self, event):
        if event.width < 10 or event.height < 10:
            return
        window = self.winfo_toplevel()
        window_size = (window.winfo_width(), window.winfo_height())
        initializing = hasattr(window, "initializing") and window.initializing
        
        if (not initializing
            and not self._restoring_pane_sizes 
            and (window_size != self._last_window_size or self._full_size_not_final)):
            self._check_restore_pane_sizes()
            self._last_window_size = window_size
    
    def _on_mouse_dragged(self, event):
        if event.widget == self and not self._restoring_pane_sizes:
            self._store_pane_sizes()
            
    
    def _store_pane_sizes(self):
        if len(self.panes()) > 1:
            self.last_pane_size = self._get_pane_size("last")
            if len(self.panes()) > 2:
                self.first_pane_size = self._get_pane_size("first")
    
    def _check_restore_pane_sizes(self):
        """last (and maybe first) pane sizes are stored, first (or middle)
        pane changes its size when window is resized"""
        
        window = self.winfo_toplevel()
        if hasattr(window, "initializing") and window.initializing:
            return
        
        try:
            self._restoring_pane_sizes = True
            if len(self.panes()) > 1:
                self._set_pane_size("last", self.last_pane_size)
                if len(self.panes()) > 2:
                    self._set_pane_size("first", self.first_pane_size)
        finally:
            self._restoring_pane_sizes = False
    
    def _get_pane_size(self, which):
        self.update_idletasks()
        
        if which == "first":
            coord = self.sash_coord(0)
        else:
            coord = self.sash_coord(len(self.panes())-2)
            
        if self.cget("orient") == tk.HORIZONTAL:
            full_size = self.winfo_width()
            sash_distance = coord[0]
        else:
            full_size = self.winfo_height()
            sash_distance = coord[1]
        
        if which == "first":
            return sash_distance
        else:
            return full_size - sash_distance 
        
    
    def _set_pane_size(self, which, size):
        
        if self.cget("orient") == tk.HORIZONTAL:
            full_size = self.winfo_width()
        else:
            full_size = self.winfo_height()
        
        self._full_size_not_final = full_size == 1
        
        if self._full_size_not_final:
            return
        
        if isinstance(size, float):
            size = int(full_size * size)
        
        #print("full vs size", full_size, size)
        
        if which == "first":
            sash_index = 0
            sash_distance = size 
        else:
            sash_index = len(self.panes())-2
            sash_distance = full_size - size 
        
        if self.cget("orient") == tk.HORIZONTAL:
            self.sash_place(sash_index, sash_distance, 0)
            #print("PLACE", sash_index, sash_distance, 0)
        else:
            self.sash_place(sash_index, 0, sash_distance)
            #print("PLACE", sash_index, 0, sash_distance)
      
    
    def _update_visibility(self):
        if not isinstance(self.master, AutomaticPanedWindow):
            return
        
        if len(self.visible_panes) == 0 and self.is_visible():
            self.master.forget(self)
            
        if len(self.panes()) > 0 and not self.is_visible():
            self.master.insert("auto", self)
        
    
    def _update_appearance(self, event=None):
        self.configure(sashwidth=lookup_style_option("Sash", "sashthickness", 10))
        self.configure(background=lookup_style_option("TPanedWindow", "background"))
    
class ClosableNotebook(ttk.Notebook):
    def __init__(self, master, style="ButtonNotebook.TNotebook", **kw):
        super().__init__(master, style=style, **kw)
        
        self.tab_menu = self.create_tab_menu()
        self._popup_index = None
        self.pressed_index = None
        
        self.bind("<ButtonPress-1>", self._letf_btn_press, True)
        self.bind("<ButtonRelease-1>", self._left_btn_release, True)
        if running_on_mac_os():
            self.bind("<ButtonPress-2>", self._right_btn_press, True)
            self.bind("<Control-Button-1>", self._right_btn_press, True)
        else:  
            self.bind("<ButtonPress-3>", self._right_btn_press, True)
        
        #self._check_update_style()
    
    def create_tab_menu(self):
        menu = tk.Menu(self.winfo_toplevel(), tearoff=False,
                       **get_style_configuration("Menu"))
        menu.add_command(label="Close", command=self._close_tab_from_menu)
        menu.add_command(label="Close others", command=self._close_other_tabs)
        menu.add_command(label="Close all", command=self.close_tabs)
        return menu
    
    def _letf_btn_press(self, event):
        try:
            elem = self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))
        
            if "closebutton" in elem:
                self.state(['pressed'])
                self.pressed_index = index
        except Exception:
            # may fail, if clicked outside of tab
            return
    
    def _left_btn_release(self, event):
        if not self.instate(['pressed']):
            return
    
        try:
            elem =  self.identify(event.x, event.y)
            index = self.index("@%d,%d" % (event.x, event.y))
        except Exception:
            # may fail, when mouse is dragged
            return
        else:
            if "closebutton" in elem and self.pressed_index == index:
                self.close_tab(index)
        
            self.state(["!pressed"])
        finally:
            self.pressed_index = None
    
    def _right_btn_press(self, event):
        try:
            index = self.index("@%d,%d" % (event.x, event.y))
            self._popup_index = index
            self.tab_menu.tk_popup(*self.winfo_toplevel().winfo_pointerxy())
        except Exception:
            logging.exception("Opening tab menu")
    
    def _close_tab_from_menu(self):
        self.close_tab(self._popup_index)
    
    def _close_other_tabs(self):
        self.close_tabs(self._popup_index)
    
    def close_tabs(self, except_index=None):
        for tab_index in reversed(range(len(self.winfo_children()))):
            if except_index is not None and tab_index == except_index:
                continue
            else:
                self.close_tab(tab_index)
                    
    def close_tab(self, index):
        child = self.get_child_by_index(index)
        print(type(child), vars(child))
        if hasattr(child, "close"):
            child.close()
        else:
            self.forget(index)
            child.destroy()

    def get_child_by_index(self, index):
        tab_id = self.tabs()[index]
        if tab_id:
            return self.nametowidget(tab_id)
        else:
            return None

    def get_current_child(self):
        child_id = self.select()
        if child_id:
            return self.nametowidget(child_id)
        else:
            return None
    
    def focus_set(self):
        editor = self.get_current_child()
        if editor: 
            editor.focus_set()
        else:
            super().focus_set()
            
    def _check_update_style(self):
        style = ttk.Style()
        if "closebutton" in style.element_names():
            # It's done already
            return
        
        # respect if required images have been defined already
        if "img_close" not in self.image_names():
            img_dir = os.path.join(os.path.dirname(__file__), "res")
            ClosableNotebook._close_img = tk.PhotoImage("img_tab_close", 
                file=os.path.join(img_dir, "tab_close.gif"))
            ClosableNotebook._close_active_img = tk.PhotoImage("img_tab_close_active", 
                file=os.path.join(img_dir, "tab_close_active.gif"))
        
        style.element_create("closebutton", "image", "img_tab_close",
            ("active", "pressed", "!disabled", "img_tab_close_active"),
            ("active", "!disabled", "img_tab_close_active"), border=8, sticky='')
    
        style.layout("ButtonNotebook.TNotebook.Tab", [
            ("Notebook.tab", {"sticky": "nswe", "children":
                [("Notebook.padding", {"side": "top", "sticky": "nswe",
                                             "children":
                    [("Notebook.focus", {"side": "top", "sticky": "nswe",
                                               "children":
                        [("Notebook.label", {"side": "left", "sticky": ''}),
                         ("Notebook.closebutton", {"side": "left", "sticky": ''})
                         ]
                    })]
                })]
            })]
        )
    

class AutomaticNotebook(ClosableNotebook):
    """
    Enables inserting views according to their position keys.
    Remember its own position key. Automatically updates its visibility.
    """
    def __init__(self, master, position_key):
        if get_workbench().get_mode() == "simple":
            style="TNotebook"
        else:
            style="ButtonNotebook.TNotebook"
        super().__init__(master, style=style, padding=0)
        self.position_key = position_key
    
    def add(self, child, **kw):
        super().add(child, **kw)
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
            
        super().insert(pos, child, **kw)
        self._update_visibility()
    
    def hide(self, tab_id):
        super().hide(tab_id)
        self._update_visibility()
    
    def forget(self, tab_id):
        if (tab_id in self.tabs()
            or tab_id in self.winfo_children()):
            super().forget(tab_id)
        self._update_visibility()
    
    def is_visible(self):
        return self in self.master.visible_panes
    
    def get_visible_child(self):
        for child in self.winfo_children():
            if str(child) == str(self.select()):
                return child
            
        return None
        
        
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
        # http://wiki.tcl.tk/44444#pagetoc50f90d9a
        self.vert_scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, style=scrollbar_style("Vertical"))
        if show_scrollbar:
            self.vert_scrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        
        self.tree = ttk.Treeview(self, columns=columns, 
                                 displaycolumns=displaycolumns, 
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
    
    def clear(self):
        self._clear_tree()
    
    def on_select(self, event):
        pass
    
    def on_double_click(self, event):
        pass

def scrollbar_style(orientation):
    # In mac ttk.Scrollbar uses native rendering unless style attribute is set
    # see http://wiki.tcl.tk/44444#pagetoc50f90d9a
    # Native rendering doesn't look good in dark themes
    if running_on_mac_os() and get_workbench().uses_dark_ui_theme():
        return orientation + ".TScrollbar"
    else:
        return None

def sequence_to_accelerator(sequence):
    """Translates Tk event sequence to customary shortcut string
    for showing in the menu"""
    
    if not sequence:
        return ""
    
    if not sequence.startswith("<"):
        return sequence
    
    accelerator = (sequence
        .strip("<>")
        .replace("Key-", "")
        .replace("KeyPress-", "")
        .replace("Control", "Ctrl")
    )
    
    # Tweaking individual parts
    parts = accelerator.split("-")
    # tkinter shows shift with capital letter, but in shortcuts it's customary to include it explicitly
    if len(parts[-1]) == 1 and parts[-1].isupper() and not "Shift" in parts:
        parts.insert(-1, "Shift")
    
    # even when shift is not required, it's customary to show shortcut with capital letter
    if len(parts[-1]) == 1:
        parts[-1] = parts[-1].upper()
    
    accelerator = "+".join(parts)
    
    # Post processing
    accelerator = (accelerator
        .replace("Minus", "-").replace("minus", "-")
        .replace("Plus", "+").replace("plus", "+"))
    
    return accelerator
    

        
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

class EnhancedTextWithLogging(tktextext.EnhancedText):
    def direct_insert(self, index, chars, tags=()):
        try:
            # try removing line numbers
            # TODO: shouldn't it take place only on paste?
            # TODO: does it occur when opening a file with line numbers in it?
            #if self._propose_remove_line_numbers and isinstance(chars, str):
            #    chars = try_remove_linenumbers(chars, self)
            concrete_index = self.index(index)
            return tktextext.EnhancedText.direct_insert(self, index, chars, tags=tags)
        finally:
            get_workbench().event_generate("TextInsert", index=concrete_index, 
                                           text=chars, tags=tags, text_widget=self)

    
    def direct_delete(self, index1, index2=None):
        try:
            # index1 may be eg "sel.first" and it doesn't make sense *after* deletion
            concrete_index1 = self.index(index1)
            if index2 is not None:
                concrete_index2 = self.index(index2)
            else:
                concrete_index2 = None
                
            return tktextext.EnhancedText.direct_delete(self, index1, index2=index2)
        finally:
            get_workbench().event_generate("TextDelete", index1=concrete_index1,
                                           index2=concrete_index2, text_widget=self)
            
    
class SafeScrollbar(ttk.Scrollbar):
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
    
    def set(self, first, last):
        try:
            ttk.Scrollbar.set(self, first, last)
        except Exception:
            traceback.print_exc()

class AutoScrollbar(SafeScrollbar):
    # http://effbot.org/zone/tkinter-autoscrollbar.htm
    # a vert_scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    
    def __init__(self, master=None, **kw):
        super().__init__(master=master, **kw)
    
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.grid_remove()
        elif float(lo) > 0.001 or float(hi) < 0.009:
            # with >0 and <1 it occasionally made scrollbar wobble back and forth
            self.grid()
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


class VerticallyScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0,0, 
                                                    window=self.interior, 
                                                    anchor=tk.NW)
        self.bind('<Configure>', self._configure_interior, "+")
        self.bind('<Expose>', self._expose, "+")
    
    def _expose(self, event):
        self.update_idletasks()
        self.update_scrollbars()
    
    def _configure_interior(self, event):
        self.update_scrollbars()

    def update_scrollbars(self):
        # update the scrollbars to match the size of the inner frame
        size = (self.canvas.winfo_width() , self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if (self.interior.winfo_reqwidth() != self.canvas.winfo_width()
            and self.canvas.winfo_width() > 10):
            # update the interior's width to fit canvas
            #print("CAWI", self.canvas.winfo_width())
            self.canvas.itemconfigure(self.interior_id,
                                      width=self.canvas.winfo_width())
        

class ScrollableFrame(ttk.Frame):
    # http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        
        # set up scrolling with canvas
        vscrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        hscrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        vscrollbar.config(command=self.canvas.yview)
        hscrollbar.config(command=self.canvas.xview)
        
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        
        self.canvas.grid(row=0, column=0, sticky=tk.NSEW)
        vscrollbar.grid(row=0, column=1, sticky=tk.NSEW)
        hscrollbar.grid(row=1, column=0, sticky=tk.NSEW)
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.interior = ttk.Frame(self.canvas)
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
        size = (self.canvas.winfo_reqwidth() , self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        
class ThemedListbox(tk.Listbox):
    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(master=master, cnf=cnf, **kw)
    
        self._ui_theme_change_binding = self.bind("<<ThemeChanged>>", 
                                                  self._reload_theme_options, True)
        self._reload_theme_options()
        
    def _reload_theme_options(self, event=None):
        style = ttk.Style()
        
        states = []
        if self["state"] == "disabled":
            states.append("disabled")
        
        # Following crashes when a combobox is focused
        #if self.focus_get() == self:
        #    states.append("focus")
        opts = {}
        for key in ["background", "foreground", 
                     "highlightthickness", "highlightcolor", "highlightbackground"]:
            value = style.lookup(self.get_style_name(), key, states)
            if value:
                opts[key] = value
                
        self.configure(opts)
    
    def get_style_name(self):
        return "Listbox"
    
    def destroy(self):
        self.unbind("<<ThemeChanged>>", self._ui_theme_change_binding)
        super().destroy()

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

        super().__init__(master, title)

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

    def __init__(self, widget, options):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.options = options

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
        if running_on_mac_os():
            # TODO: maybe it's because of Tk 8.5, not because of Mac
            tw.wm_transient(self.widget)
        tw.wm_geometry("+%d+%d" % (x, y))
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass        
        label = tk.Label(tw, text=self.text, **self.options)
        label.pack()

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text, **kw):
    options = get_style_configuration("Tooltip").copy()
    options.setdefault("background", "#ffffe0")
    options.setdefault("relief", "solid")
    options.setdefault("borderwidth", 1)
    options.setdefault("padx", 1)
    options.setdefault("pady", 0)
    options.update(kw)
    
    toolTip = ToolTip(widget, options)
    def enter(event):
        toolTip.showtip(text)
    def leave(event):
        toolTip.hidetip()
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)

class NoteBox(tk.Toplevel):
    def __init__(self, master=None, 
                 max_default_width=300,
                 **kw):
        super().__init__(master=master,
                         highlightthickness=0, 
                         **kw)
        
        self._max_default_width = max_default_width
        
        self.wm_overrideredirect(True)
        if running_on_mac_os():
            # TODO: maybe it's because of Tk 8.5, not because of Mac
            self.wm_transient(self.widget)
        try:
            # For Mac OS
            self.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", self._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        
        self._current_chars = ""
        self._click_bindings = {}
        
        self.padx = 5
        self.pady = 5
        self.text = TweakableText(self,
                            background="#ffffe0",
                            borderwidth=1,
                            relief="solid",
                            undo=False,
                            read_only=True,
                            font="TkDefaultFont",
                            highlightthickness=0,
                            padx=self.padx,
                            pady=self.pady,
                            wrap="word")
        
        self.text.grid(row=0, column=0, sticky="nsew")
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.text.bind("<Escape>", self.close, True)
        
        #tk._default_root.bind_all("<1>", self._close_maybe, True)
        #tk._default_root.bind_all("<Key>", self.close, True)
        
        self.withdraw()
    
    def clear(self):
        for tag in self._click_bindings:
            self.text.tag_unbind(tag, "<1>", self._click_bindings[tag])
            self.text.tag_remove(tag, "1.0", "end")
            
        self.text.direct_delete("1.0", "end")
        self._current_chars = ""
        self._click_bindings.clear()
    
    def set_content(self, *items):
        self.clear()
        
        for item in items:
            if isinstance(item, str):
                self.text.direct_insert("1.0", item)
                self._current_chars = item
            else:
                assert isinstance(item, (list, tuple))
                chars, *props = item
                if len(props) > 0 and callable(props[-1]):
                    tags = tuple(props[:-1])
                    click_handler = props[-1]
                else:
                    tags = tuple(props)
                    click_handler = None
                
                self.append_text(chars, tags, click_handler)
                    
            self.text.see("1.0")
    
    def append_text(self, chars, tags=(), click_handler=None):
        tags = tuple(tags)
        
        if click_handler is not None:
            click_tag = "click_%d" % len(self._click_bindings)
            tags = tags + (click_tag,)
            binding = self.text.tag_bind(click_tag, "<1>", click_handler, True)
            self._click_bindings[click_tag] = binding
        
        self.text.direct_insert("end", chars, tags)
        self._current_chars += chars
        
    def place(self, target, focus=None):
        
        # Compute the area that will be described by this Note
        focus_x = target.winfo_rootx()
        focus_y = target.winfo_rooty()
        focus_height = target.winfo_height()

        if isinstance(focus, TextRange):
            assert isinstance(target, tk.Text)
            topleft = target.bbox("%d.%d" % (focus.lineno, focus.col_offset))
            if focus.end_col_offset == 0:
                botright = target.bbox("%d.%d lineend" % (focus.end_lineno-1, focus.end_lineno-1))
            else:
                botright = target.bbox("%d.%d" % (focus.end_lineno, focus.end_col_offset))
            
            if topleft and botright:
                focus_x += topleft[0]
                focus_y += topleft[1]
                focus_height = botright[1] - topleft[1] + botright[3]
                
        elif isinstance(focus, (list, tuple)):
            focus_x += focus[0] 
            focus_y += focus[1]
            focus_height = focus[3] 
        
        elif focus is None:
            pass
        
        else:
            raise TypeError("Unsupported focus")
        
        # Compute dimensions of the note
        font = self.text["font"]
        if isinstance(font, str):
            font = tk.font.nametofont(font)
            
        lines = self._current_chars.splitlines()
        max_line_width = 0
        for line in lines:
            
            max_line_width = max(max_line_width, 
                                  font.measure(line))
        
        width = min(max_line_width, self._max_default_width) + self.padx*2 + 2
        self.wm_geometry("%dx%d+%d+%d" % (
            width, 100,
            focus_x, focus_y + focus_height
        ))
        
        self.update_idletasks()
        line_count = int(float(self.text.index("end")))
        line_height = font.metrics()["linespace"]
        
        self.wm_geometry("%dx%d+%d+%d" % (
            width, line_count * line_height,
            focus_x, focus_y + focus_height
        ))
        
        # TODO: detect the situation when note doesn't fit under
        # the focus box and should be placed above
            
        
        self.deiconify()
    
    def show_note(self, *content_items: Union[str, List],
                  target=None, focus=None) -> None:
    
        self.set_content(*content_items)
        self.place(target, focus)
        
    def _close_maybe(self, event):
        if event.widget not in [self, self.text]:
            self.close(event)
    
    def close(self, event=None):
        self.withdraw()
        

def get_widget_offset_from_toplevel(widget):
    x = 0
    y = 0
    print("roo", widget.winfo_rootx(), widget.winfo_rooty())
    toplevel = widget.winfo_toplevel()
    while widget != toplevel:
        x += widget.winfo_x()
        y += widget.winfo_y()
        widget = widget.master
    return x, y

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



def create_string_var(value, modification_listener=None):
    """Creates a tk.StringVar with "modified" attribute
    showing whether the variable has been modified after creation"""
    return _create_var(tk.StringVar, value, modification_listener)

def create_int_var(value, modification_listener=None):
    """See create_string_var"""
    return _create_var(tk.IntVar, value, modification_listener)

def create_double_var(value, modification_listener=None):
    """See create_string_var"""
    return _create_var(tk.DoubleVar, value, modification_listener)

def create_boolean_var(value, modification_listener=None):
    """See create_string_var"""
    return _create_var(tk.BooleanVar, value, modification_listener)

def _create_var(class_, value, modification_listener):
    var = class_(value=value)
    var.modified = False
    
    def on_write(*args):
        var.modified = True
        if modification_listener:
            try:
                modification_listener()
            except Exception:
                # Otherwise whole process will be brought down
                # because for some reason Tk tries to call non-existing method
                # on variable
                get_workbench().report_exception()
    
    # TODO: https://bugs.python.org/issue22115 (deprecation warning)
    var.trace("w", on_write)
    return var

def shift_is_pressed(event_state):
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event_state & 0x0001

def control_is_pressed(event_state):
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # http://stackoverflow.com/q/32426250/261181
    return event_state & 0x0004

def sequence_to_event_state_and_keycode(sequence):
    # remember handlers for certain shortcuts which require
    # different treatment on non-latin keyboards
    if sequence[0] != "<":
        return None
    
    parts = sequence.strip("<").strip(">").split("-")
    # support only latin letters for now
    if parts[-1].lower() not in list("abcdefghijklmnopqrstuvwxyz"):
        return
    
    letter = parts.pop(-1)
    if "Key" in parts:
        parts.remove("Key")
    if "key" in parts:
        parts.remove("key")
    
    
    modifiers = {part.lower() for part in parts}
    
    if letter.isupper():
        modifiers.add("shift")
    
    if modifiers not in [{"control"}, {"control", "shift"}]:
        # don't support others for now
        return
    
    event_state = 0
    # http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/event-handlers.html
    # https://stackoverflow.com/questions/32426250/python-documentation-and-or-lack-thereof-e-g-keyboard-event-state
    for modifier in modifiers:
        if modifier == "shift":
            event_state |= 0x0001
        elif modifier == "control":
            event_state |= 0x0004
        else:
            # unsupported modifier
            return None
    
    # for latin letters keycode is same as its ascii code
    return (event_state, ord(letter.upper()))
    

def select_sequence(win_version, mac_version, linux_version=None):
    if running_on_windows():
        return win_version
    elif running_on_mac_os():
        return mac_version
    elif running_on_linux() and linux_version:
        return linux_version
    else:
        return win_version

def try_remove_linenumbers(text, master):
    try:        
        if has_line_numbers(text) and tkMessageBox.askyesno (
                  title="Remove linenumbers",
                  message="Do you want to remove linenumbers from pasted text?",
                  default=tkMessageBox.YES,
                  master=master):
            return remove_line_numbers(text)
        else:
            return text
    except Exception:
        traceback.print_exc()
        return text


def has_line_numbers(text):
    lines = text.splitlines()
    return (len(lines) > 2 
            and all([len(split_after_line_number(line)) == 2 for line in lines]))

def split_after_line_number(s): 
    parts = re.split("(^\s*\d+\.?)", s)
    if len(parts) == 1:
        return parts
    else:
        assert len(parts) == 3 and parts[0] == ''
        return parts[1:]

def remove_line_numbers(s):
    cleaned_lines = []
    for line in s.splitlines():
        parts = split_after_line_number(line)
        if len(parts) != 2:
            return s
        else:
            cleaned_lines.append(parts[1])
    
    return textwrap.dedent(("\n".join(cleaned_lines)) + "\n")
    
def center_window(win, master=None):
    # looks like it doesn't take window border into account
    win.update_idletasks()
    
    if getattr(master, "initializing", False):
        # can't get reliable positions when main window is not in mainloop yet
        left = (win.winfo_screenwidth() - 600) // 2
        top = (win.winfo_screenheight() - 400) // 2
    else:
        if master is None:
            left = win.winfo_screenwidth() - win.winfo_width() // 2
            top = win.winfo_screenheight() - win.winfo_height() // 2
        else:
            left = master.winfo_rootx() + master.winfo_width() // 2 - win.winfo_width() // 2
            top = master.winfo_rooty() + master.winfo_height() // 2 - win.winfo_height() // 2
        
    win.geometry("+%d+%d" % (left, top))

class BusyTk(tk.Tk):
    def __init__(self, async_result, description, title="Please wait!"):
        self._async_result = async_result
        tk.Tk.__init__(self)
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_width = screen_width // 3
        win_height = screen_height // 3
        x = screen_width//2 - win_width//2
        y = screen_height//2 - win_height//2
        self.geometry("%dx%d+%d+%d" % (win_width, win_height, x, y))        
        
        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        self.title(title)
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.protocol("WM_DELETE_WINDOW", self._ok)
        self.desc_label = ttk.Label(main_frame, text=description)
        self.desc_label.grid(padx=20, pady=20, sticky="nsew")
        
        self.update_idletasks()
        self.after(500, self._poll)
    
    def _poll(self):
        if self._async_result.ready():
            self._ok()
        else:
            self.after(500, self._poll)
            self.desc_label["text"] = self.desc_label["text"] + "."
    
    def _ok(self):
        self.destroy() 

def run_with_busy_window(action, args=(), description="Working"):
    # http://stackoverflow.com/a/14299004/261181
    from multiprocessing.pool import ThreadPool
    pool = ThreadPool(processes=1)
    
    async_result = pool.apply_async(action, args) 
    dlg = BusyTk(async_result, description=description)
    dlg.mainloop()
    
    return async_result.get()  

class FileCopyDialog(tk.Toplevel):
    def __init__(self, master, source, destination, description=None,
                 fsync=True):
        self._source = source
        self._destination = destination 
        self._old_bytes_copied = 0
        self._bytes_copied = 0
        self._fsync = fsync
        self._done = False
        self._cancelled = False
        self._closed = False
        
        super().__init__(master)
        
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        
        self.title("Copying")
        
        if description is None:
            description = "Copying\n  %s\nto\n  %s" % (source, destination)
        
        label = ttk.Label(main_frame, text=description)
        label.grid(row=0, column=0, columnspan=2, sticky="nw", padx=15, pady=15)
        
        self._bar = ttk.Progressbar(main_frame, maximum=os.path.getsize(source), length=200)
        self._bar.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=15, pady=0)
        
        self._cancel_button = ttk.Button(main_frame, text="Cancel", command=self._cancel)
        self._cancel_button.grid(row=2, column=1, sticky="ne", padx=15, pady=15)
        self._bar.focus_set()
        
        main_frame.columnconfigure(0, weight=1)
        
        self._update_progress()
            
        self.bind('<Escape>', self._cancel, True) # escape-close only if process has completed 
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        center_window(self, master)
        self._start()
    
    def _start(self):
        def work():
            self._copy_progess = 0
            
            with open(self._source, "rb") as fsrc:
                with open(self._destination, 'wb') as fdst:
                    while True:
                        buf = fsrc.read(16*1024)
                        if not buf:
                            break
                        
                        fdst.write(buf)
                        fdst.flush()
                        if self._fsync:
                            os.fsync(fdst)
                        self._bytes_copied += len(buf)
                        
            
            self._done = True
        
        threading.Thread(target=work, daemon=True).start()
    
    def _update_progress(self):
        if self._done:
            if not self._closed:
                self._close()
            return
        
        self._bar.step(self._bytes_copied - self._old_bytes_copied)
        self._old_bytes_copied = self._bytes_copied
        
        self.after(100, self._update_progress)
    
    def _close(self):
        self.destroy()
        self._closed = True
    
    
    def _cancel(self, event=None):
        self._cancelled = True
        self._close()
         
        
        

class SubprocessDialog(tk.Toplevel):
    """Shows incrementally the output of given subprocess.
    Allows cancelling"""
    
    def __init__(self, master, proc, title, long_description=None, autoclose=True,
                 conclusion="Done."):
        self._closed = False
        self._proc = proc
        self.stdout = ""
        self.stderr = ""
        self._stdout_thread = None
        self._stderr_thread = None
        self.returncode = None
        self.cancelled = False
        self._autoclose = autoclose
        self._event_queue = collections.deque()
        self._conclusion = conclusion
        
        tk.Toplevel.__init__(self, master)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        main_frame = ttk.Frame(self) # To get styled background
        main_frame.grid(sticky="nsew")

        text_font=tk.font.nametofont("TkFixedFont").copy()
        text_font["size"] = int(text_font["size"] * 0.9)
        text_font["family"] = "Courier" if running_on_mac_os() else "Courier New"
        text_frame = tktextext.TextFrame(main_frame, read_only=True, horizontal_scrollbar=False,
                                         background=lookup_style_option("TFrame", "background"),
                                         font=text_font,
                                         wrap="word")
        text_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=15, pady=15)
        self.text = text_frame.text
        self.text["width"] = 60
        self.text["height"] = 7
        if long_description is not None:
            self.text.direct_insert("1.0", long_description + "\n\n")
        
        self.button = ttk.Button(main_frame, text="Cancel", command=self._close)
        self.button.grid(row=1, column=0, pady=(0,15))
        
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        

        self.title(title)
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        #self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.text.focus_set()
        
        
        self.bind('<Escape>', self._close_if_done, True) # escape-close only if process has completed 
        self.protocol("WM_DELETE_WINDOW", self._close)
        center_window(self, master)
        
        self._start_listening()
    
    def _start_listening(self):
       
        def listen_stream(stream_name):
            stream = getattr(self._proc, stream_name)
            while True:
                data = stream.readline()
                self._event_queue.append((stream_name, data))
                setattr(self, stream_name, getattr(self, stream_name) + data)
                if data == '':
                    break
            
            self.returncode = self._proc.wait()
        
        self._stdout_thread = threading.Thread(target=listen_stream, args=["stdout"], daemon=True)
        self._stdout_thread.start()
        if self._proc.stderr is not None:
            self._stderr_thread = threading.Thread(target=listen_stream, args=["stderr"], daemon=True)
            self._stderr_thread.start()
        
        def poll_output_events():
            if self._closed:
                return
            
            while len(self._event_queue) > 0:
                stream_name, data = self._event_queue.popleft()
                self.text.direct_insert("end", data, tags=(stream_name, ))
                self.text.see("end")
            
            self.returncode = self._proc.poll() 
            if self.returncode == None:
                self.after(200, poll_output_events)
            else:
                self.button["text"] = "OK"
                self.button.focus_set()
                if self.returncode != 0:
                    self.text.direct_insert("end", "\n\nReturn code: ", ("stderr", ))
                elif self._autoclose:
                    self._close()
                else:
                    self.text.direct_insert("end", "\n\n" + self._conclusion)
                    self.text.see("end")
        
        poll_output_events()
        
    
    def _close_if_done(self, event):
        if self._proc.poll() is not None:
            self._close(event)        

    def _close(self, event=None):
        if self._proc.poll() is None:
            if messagebox.askyesno("Cancel the process?",
                "The process is still running.\nAre you sure you want to cancel?"):
                # try gently first
                try:
                    if running_on_windows():
                        os.kill(self._proc.pid, signal.CTRL_BREAK_EVENT)  # @UndefinedVariable
                    else:
                        os.kill(self._proc.pid, signal.SIGINT)
                        
                    self._proc.wait(2)
                except subprocess.TimeoutExpired:
                    if self._proc.poll() is None:
                        # now let's be more concrete
                        self._proc.kill()
                
                
                self.cancelled = True
                # Wait for threads to finish
                self._stdout_thread.join(2)
                if self._stderr_thread is not None:
                    self._stderr_thread.join(2)
                
                # fetch output about cancelling
                while len(self._event_queue) > 0:
                    stream_name, data = self._event_queue.popleft()
                    self.text.direct_insert("end", data, tags=(stream_name, ))
                self.text.direct_insert("end", "\n\nPROCESS CANCELLED")
                self.text.see("end")
                    
                    
            else:
                return
        else:
            self._closed = True
            self.destroy()

def get_busy_cursor():
    if running_on_windows():
        return "wait"
    elif running_on_mac_os():
        return "spinning"
    else:
        return "watch"

def get_tk_version_str():
    return tk._default_root.tk.call('info', 'patchlevel')

def get_tk_version_info():
    result = []
    for part in get_tk_version_str().split("."):
        try:
            result.append(int(part))
        except Exception:
            result.append(0)
    return tuple(result) 

def get_style_configuration(style_name, default={}):
    style = ttk.Style()
    # NB! style.configure seems to reuse the returned dict 
    # Don't change it without copying first
    result = style.configure(style_name)
    if result is None:
        return default
    else:
        return result
    
    

def lookup_style_option(style_name, option_name, default=None):
    style = ttk.Style()
    setting = style.lookup(style_name, option_name)
    if setting in [None, ""]:
        return default
    elif setting == "True":
        return True
    elif setting == "False":
        return False
    else:
        return setting

def scale(value):
    return get_workbench().scale(value)

def open_path_in_system_file_manager(path):
    if running_on_mac_os():
        # http://stackoverflow.com/a/3520693/261181
        # -R doesn't allow showing hidden folders
        subprocess.Popen(["open", path])
    elif running_on_linux():
        subprocess.Popen(["xdg-open", path])
    else:
        assert running_on_windows()
        subprocess.Popen(["explorer", path])


def _get_dialog_provider():
    if platform.system() != "Linux":
        return filedialog
    
    if shutil.which("zenity"):
        return _ZenityDialogProvider
    
    # fallback
    import tkinter.filedialog
    return tkinter.filedialog
    
def asksaveasfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getSaveFile.htm
    return _get_dialog_provider().asksaveasfilename(**options)

def askopenfilename(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    return _get_dialog_provider().askopenfilename(**options)

def askopenfilenames(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
    return _get_dialog_provider().askopenfilenames(**options)

def askdirectory(**options):
    # https://tcl.tk/man/tcl8.6/TkCmd/chooseDirectory.htm
    return _get_dialog_provider().askdirectory(**options)


class _ZenityDialogProvider:
    # https://www.writebash.com/bash-gui/zenity-create-file-selection-dialog-224.html
    # http://linux.byexamples.com/archives/259/a-complete-zenity-dialog-examples-1/
    # http://linux.byexamples.com/archives/265/a-complete-zenity-dialog-examples-2/
    
    # another possibility is to use PyGobject: https://github.com/poulp/zenipy
    
    @classmethod
    def askopenfilename(cls, **options):
        args = cls._convert_common_options("Open file", **options)
        return cls._call(args)
        
    @classmethod
    def askopenfilenames(cls, **options):
        args = cls._convert_common_options("Open files", **options)
        return cls._call(args + ["--multiple"]).split("|")
        
    @classmethod
    def asksaveasfilename(cls, **options):
        args = cls._convert_common_options("Save as", **options)
        args.append("--save")
        if options.get("confirmoverwrite", True):
            args.append("--confirm-overwrite")
        
        filename = cls._call(args)
        if not filename:
            return None
            
        if ("defaultextension" in options
            and "." not in os.path.basename(filename)):
            filename += options["defaultextension"]
            
        return filename
        
    @classmethod
    def askdirectory(cls, **options):
        args = cls._convert_common_options("Select directory", **options)
        args.append("--directory")
        return cls._call(args)
    
    @classmethod
    def _convert_common_options(cls, default_title, **options):
        args = ["--file-selection",
                "--title=%s" % options.get("title", default_title),
                ]
        
        filename = _options_to_zenity_filename(options)
        if filename:                
            args.append("--filename=%s" % filename)
        
        parent = options.get("parent", options.get("master", None))
        if parent is not None:
            args.append("--modal")
            args.append("--attach=%s" % parent.winfo_id())
                
        for desc, pattern in options.get("filetypes", ()):
            # zenity requires star before extension
            pattern = pattern.replace(" .", " *.")
            if pattern.startswith("."):
                pattern = "*" + pattern
                
            args.append("--file-filter=%s | %s" % (desc, pattern))
            
        return args
        
    
    @classmethod
    def _call(cls, args):
        args = ["zenity", "--name=Thonny", "--class=Thonny"] + args
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            # could check stderr, but it may contain irrelevant warnings
            return None


def _options_to_zenity_filename(options):
    if "initialdir" in options:
        if "initialfile" in options:
            return os.path.join(options["initialdir"], options["initialfile"])
        else:
            return options["initialdir"] + os.path.sep
            
    return None

def register_latin_shortcut(registry, sequence: str, handler: Callable, tester: Optional[Callable]) -> None:
    res = sequence_to_event_state_and_keycode(sequence)
    if res is not None:
        if res not in registry:
            registry[res] = []
        registry[res].append((handler, tester))


def handle_mistreated_latin_shortcuts(registry, event):
    # tries to handle Ctrl+LatinLetter shortcuts 
    # given from non-Latin keyboards
    # See: https://bitbucket.org/plas/thonny/issues/422/edit-keyboard-shortcuts-ctrl-c-ctrl-v-etc
    
    # only consider events with Control held
    if not event.state & 0x04:
        return
    
    if running_on_mac_os():
        return
    
    
    # consider only part of the state,
    # because at least on Windows, Ctrl-shortcuts' state 
    # has something extra
    simplified_state = 0x04
    if shift_is_pressed(event.state):
        simplified_state |= 0x01
        
    #print(simplified_state, event.keycode)
    if (simplified_state, event.keycode) in registry:
        if event.keycode != ord(event.char):
            # keycode and char doesn't match,
            # this means non-latin keyboard
            for handler, tester in registry[(simplified_state, event.keycode)]:
                if tester is None or tester():
                    handler()


def show_dialog(dlg, master=None):
    if master is None:
        master = tk._default_root
        
    focused_widget = master.focus_get()
    center_window(dlg, master)        
    dlg.transient(master)
    dlg.grab_set()
    master.wait_window(dlg)
    dlg.grab_release()
    master.lift()
    master.focus_force()
    if focused_widget is not None:
        focused_widget.focus_set()

        
if __name__ == "__main__":
    root = tk.Tk()
    closa = ClosableNotebook(root)
    closa.add(ttk.Button(closa, text="B1"), text="B1")
    closa.add(ttk.Button(closa, text="B2"), text="B2")
    closa.grid()
    root.mainloop()
