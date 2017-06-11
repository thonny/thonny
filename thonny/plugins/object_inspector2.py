import tkinter as tk
from tkinter import ttk
from thonny.globals import get_workbench

class ObjectInspector2(ttk.Frame):
    def __init__(self, master):
        ttk.Frame.__init__(self, master)
        self.search_box = ttk.Entry(self)
        self.search_box.grid(row=0, column=0, sticky="nsew")


def load_plugin():
    get_workbench().add_view(ObjectInspector2, "Object inspector 2", "se")