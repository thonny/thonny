import tkinter as tk
from tkinter import ttk

root = tk.Tk()

style = ttk.Style(root)

style.theme_use("clam")

style.configure("Mamma.TLabel", background="red")
style.map("Mamma.TLabel",
          background=[('active','green'), ('!active','blue')],)

fr = tk.Frame(root, background="green")
fr.grid(padx=20, pady=20)

lb = tk.Label(fr, text="ajoi", background="green")
lb.grid(padx=15, pady=0)

def enter(event):
    fr.configure(background="red")
    lb.configure(background="red")

def leave(event):
    fr.configure(background="green")
    lb.configure(background="green")

fr.bind("<Enter>", enter, True)
fr.bind("<Leave>", leave, True)

#print(style.layout("Toolbutton"))

root.mainloop()
