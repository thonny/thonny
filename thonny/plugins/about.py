# -*- coding: utf-8 -*-

import datetime
import webbrowser
import platform

import tkinter as tk
from tkinter import ttk
import tkinter.font as font

import thonny
from thonny import misc_utils, ui_utils
from thonny.misc_utils import get_python_version_string
from thonny.globals import get_workbench

class AboutDialog(tk.Toplevel):
    def __init__(self, master):
        tk.Toplevel.__init__(self, master)
        

        main_frame = ttk.Frame(self)
        main_frame.grid(sticky=tk.NSEW, ipadx=15, ipady=15)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.title("About Thonny")
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._ok)
        
        
        #bg_frame = ttk.Frame(self) # gives proper color in aqua
        #bg_frame.grid()
        
        heading_font = font.nametofont("TkHeadingFont").copy()
        heading_font.configure(size=19, weight="bold")
        heading_label = ttk.Label(main_frame, 
                                  text="Thonny " + thonny.get_version(),
                                  font=heading_font)
        heading_label.grid()
        
        
        url = "http://thonny.org"
        url_font = font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1)
        url_label = ttk.Label(main_frame, text=url,
                              cursor="hand2",
                              foreground="blue",
                              font=url_font,)
        url_label.grid()
        url_label.bind("<Button-1>", lambda _:webbrowser.open(url))
        
        if platform.system() == "Linux":
            try:
                import distro # distro don't need to be installed
                system_desc = distro.name(True)
            except ImportError:
                system_desc = "Linux"
                
            if "32" not in system_desc and "64" not in system_desc:
                system_desc += " " + self.get_os_word_size_guess()
        else:
            system_desc = (platform.system() 
                        + " " + platform.release()  
                        + " " + self.get_os_word_size_guess())
        
        platform_label = ttk.Label(main_frame, justify=tk.CENTER, 
                                   text= system_desc + "\n"
                                        + "Python " + get_python_version_string() 
                                        + "Tk " + ui_utils.get_tk_version_str())
        platform_label.grid(pady=20)
        
        credits_label = ttk.Label(main_frame, text="Made in\nUniversity of Tartu, Estonia\n"
                                + "with the help from\nopen-source community",
                              cursor="hand2",
                              foreground="blue",
                              font=url_font,
                              justify=tk.CENTER)
        credits_label.grid()
        credits_label.bind("<Button-1>", lambda _:webbrowser.open("https://bitbucket.org/plas/thonny/src/master/CREDITS.rst"))
        
        license_font = font.nametofont("TkDefaultFont").copy()
        license_font.configure(size=7)
        license_label = ttk.Label(main_frame,
                                  text="Copyright (©) "
                                  + str(datetime.datetime.now().year)
                                  + " Aivar Annamaa\n"
                                  + "This program comes with\n"
                                  + "ABSOLUTELY NO WARRANTY!\n"
                                  + "It is free software, and you are welcome to\n"
                                  + "redistribute it under certain conditions, see\n"
                                  + "https://opensource.org/licenses/MIT\n"
                                  + "for details",
                                  justify=tk.CENTER, font=license_font)
        license_label.grid(pady=20)
        
        
        ok_button = ttk.Button(main_frame, text="OK", command=self._ok, default="active")
        ok_button.grid(pady=(0,15))
        ok_button.focus_set()
        
        self.bind('<Return>', self._ok, True) 
        self.bind('<Escape>', self._ok, True)
        
        ui_utils.center_window(self, master)        
        self.wait_window()
        
    def _ok(self, event=None):
        self.destroy()
    
    def get_os_word_size_guess(self):
        if "32" in platform.machine() and "64" not in platform.machine():
            return "(32-bit)"
        elif "64" in platform.machine() and "32" not in platform.machine():
            return "(64-bit)"
        else:
            return ""


def load_plugin():
    def open_about(*args):
        AboutDialog(get_workbench())
        
    get_workbench().add_command("changelog", "help", "Version history",
                                lambda: webbrowser.open("https://bitbucket.org/plas/thonny/src/master/CHANGELOG.rst"), group=60)
    get_workbench().add_command("about", "help", "About Thonny", open_about, group=61)
    
    # For Mac
    get_workbench().createcommand("tkAboutDialog", open_about)


    