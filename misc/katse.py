import tkinter as tk
from tkinter import ttk

root = tk.Tk()

t1 = tk.Text(root, undo=True)
t1 = ttk.Entry(root)
t1.grid()

def do_stuff(e=None):
    print(t1.selection_get())
    #print(">" + t1.selection_present() + "<")

b1 = ttk.Button(root, command=do_stuff)
b1.grid()

root.mainloop()