import tkinter as tk
from tkinter import ttk
from tkinter import font
from tkinter.font import nametofont

root = tk.Tk()

b1 = ttk.Button(root, text="essa")
b1.grid(pady=10)

b2 = ttk.Button(root, text="tessa")
b2.grid(pady=10)

e1 = ttk.Entry(root)
e1.grid(pady=10, padx=10)

s = ttk.Style()
#print(s.element_options("Combobox.field"))

s.theme_settings("clam", {
    "TButton" : {
        "configure" : {
            "background" : "red"
        }
    }
})

s.theme_settings("clam", {
    "TButton" : {
        "configure" : {
            "foreground" : "blue"
        }
    }
})

e1.bind("<<ThemeChanged>>", lambda e: print("E!"), True)
e1.destroy()

s.theme_use("clam")

root.mainloop()