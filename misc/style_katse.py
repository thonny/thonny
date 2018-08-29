import tkinter as tk
from tkinter import font, ttk
from tkinter.font import nametofont

root = tk.Tk()
style = ttk.Style()
print(style.layout("TFrame"))
style.layout("TFrame", [])
style.configure("TFrame", background="pink")

nb = ttk.Notebook(root)
nb.grid(sticky="nsew")

nb.add(ttk.Button(nb, text="bt"), text="nunu")

nb.add(tk.Frame(nb, background="pink"), text="fr")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.mainloop()
