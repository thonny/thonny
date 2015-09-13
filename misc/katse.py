import tkinter as tk
from tkinter import ttk

root = tk.Tk()


def do_stuff(e=None):
    pass


root.option_add('*tearOff', tk.FALSE)
menubar = tk.Menu(root)
root["menu"] = menubar

file_menu = tk.Menu(menubar)
menubar.add_cascade(label="File", menu=file_menu)

print(file_menu.index("end"))
file_menu.add_separator()
print(file_menu.index("end"))
file_menu.add_separator()
print(file_menu.index("end"))
file_menu.add_command(label="Tessa", command=do_stuff)
print(file_menu.index("end"))


b1 = ttk.Button(root, command=do_stuff)
b1.grid()

root.mainloop()