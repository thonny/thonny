import tkinter as tk

root = tk.Tk()
menubar = tk.Menu(root, tearoff=False)

root["menu"] = menubar

def do_stuff():
    print("stuff")

w_menu = tk.Menu(menubar, tearoff=False, name="window")
w_menu.add_command(command=do_stuff, label="do stuff")

menubar.add_cascade(label="Window", menu=w_menu)

root.mainloop()
