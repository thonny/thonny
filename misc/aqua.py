import tkinter as tk
from tkinter import ttk

root = tk.Tk()

style = ttk.Style(root)

tb = ttk.Button(root, style="Toolbutton", text="ajoi")
tb.grid(padx=20, pady=20)

print(style.layout("Toolbutton"))

root.mainloop()
