import tkinter as tk
from tkinter import ttk

root = tk.Tk()

b1 = ttk.Button(root, text="essa")
b1.grid(pady=10)

b2 = ttk.Button(root, text="tessa")
b2.grid(pady=10)

e1 = ttk.Entry(root)
e1.grid(pady=10, padx=10)

s = ttk.Style()

#s.theme_use("clam")
s.theme_create("uus", "clam")
s.theme_use("uus")


root.mainloop()