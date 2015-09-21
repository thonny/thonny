# -*- coding: utf-8 -*-

import sys
import webbrowser
import platform

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

from thonny import misc_utils
from thonny.misc_utils import running_on_mac_os
from thonny.globals import get_workbench

class AboutDialog(tk.Toplevel):
    def __init__(self, master, version):
        tk.Toplevel.__init__(self, master, borderwidth=15)
        
        #self.geometry("200x200")
        # TODO: position in the center of master
        self.geometry("+%d+%d" % (master.winfo_rootx() + master.winfo_width() // 2 - 50,
                                  master.winfo_rooty() + master.winfo_height() // 2 - 150))

        self.title("About Thonny")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._ok)
        
        
        #bg_frame = ttk.Frame(self) # gives proper color in aqua
        #bg_frame.grid()
        
        version_str = str(version)
        if version_str.count(".") == 1:
            version_str += ".0"
        
        heading_font = font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(self, 
                                  text="Thonny " + version_str,
                                  font=heading_font)
        heading_label.grid()
        
        
        url = "http://thonny.cs.ut.ee"
        url_font = font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(self, text=url,
                              cursor="hand2",
                              foreground="blue",
                              font=url_font,)
        url_label.grid()
        url_label.bind("<Button-1>", lambda _:webbrowser.open(url))
        
        python_version = ".".join(map(str, sys.version_info[:3]))
        if sys.version_info[3] != "final":
            python_version += "-" + sys.version_info[3]
        platform_label = ttk.Label(self, justify=tk.CENTER, 
                                   text=platform.system() + " " 
                                        + platform.release()  
                                        + " " + self.get_os_word_size_guess() + "\n"
                                        + "Python " + python_version 
                                        + " (" + ("64" if sys.maxsize > 2**32 else "32")+ " bit)\n"
                                        + "Tk " + self.tk.call('info', 'patchlevel'))
        platform_label.grid(pady=20)
        
        license_font = font.nametofont("TkDefaultFont").copy()
        license_font.configure(size=7)
        license_label = ttk.Label(self,
                                  text="Coppyright (©) 2014 Aivar Annamaa\n"
                                  + "This program comes with\n"
                                  + "ABSOLUTELY NO WARRANTY!\n"
                                  + "It is free software, and you are welcome to\n"
                                  + "redistribute it under certain conditions, see\n"
                                  + "http://www.gnu.org/licenses/gpl-3.0.txt\n"
                                  + "for details\n",
                                  justify=tk.CENTER, font=license_font)
        license_label.grid()
        
        ok_button = ttk.Button(self, text="OK", command=self._ok, default="active")
        ok_button.grid()
        ok_button.focus_set()
        
        self.bind('<Return>', self._ok, True) 
        self.bind('<Escape>', self._ok, True) 
        self.wait_window()
        
    def _ok(self, event=None):
        self.destroy()
    
    def get_os_word_size_guess(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return "(32 bit)"
        elif "64" in platform.machine() and "32" not in platform.machine():
            return "(64 bit)"
        else:
            return ""


def load_plugin():
    get_workbench().add_command("about", 
        "Thonny" if running_on_mac_os() else "help",
        "About Thonny",
        lambda: AboutDialog(get_workbench(), get_workbench().get_version()))

    