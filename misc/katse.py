import tkinter as tk

root = tk.Tk()

menubar = tk.Menu(root)
root["menu"] = menubar
root.option_add('*tearOff', tk.FALSE)

file_menu = tk.Menu(menubar)

menubar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="kala")
file_menu.add_separator()


print(menubar.entryconfigure(1, "menu"), file_menu)
print(file_menu.entrycget(0, "label"))
print(file_menu.index("kala"))
file_menu.insert(, "command", label="uus")

root.mainloop()