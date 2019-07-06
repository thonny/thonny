import tkinter as tk
from tkinter import ttk

root = tk.Tk()

entry = ttk.Entry(root)
entry.grid()

combo = ttk.Combobox(root)
combo.grid()

from tkinter.font import nametofont

nametofont("TkTextFont").configure(size=33)

root.mainloop()
