import tkinter as tk
from tkinter import filedialog

root = tk.Tk()

typevar = tk.StringVar(master=root)
def ask_file():
    res = filedialog.asksaveasfilename(parent=root, typevariable=typevar,
                               filetypes=[("Python", ".py .pyi"),
                                          ("all", ".*")],
                                       initialdir="/Users/user/python_stuff")
    print(repr(res), repr(typevar.get()))

btn = tk.Button(root, text="doitasfasf \nasdfasdf", command=ask_file)
btn.grid()
root.mainloop()
