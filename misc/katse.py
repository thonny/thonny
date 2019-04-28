import tkinter as tk
from tkinter import ttk

root = tk.Tk()


nb = ttk.Notebook(root,
                  #highlightthickness=0
                  #borderwidth=0
                  )

nb.grid(row=0, column=0)

root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

fr = tk.Frame(nb, background="red")
bt = ttk.Button(fr, text="nubb")
bt.grid(pady=10, padx=10)
nb.add(fr, text="ram", 
       #padding=(0,0,0,-1)
       )

style = ttk.Style()
style.layout("TNotebook", [('Notebook.client', {'sticky': 'nswe', 'border': 0})])
print(style.layout("TNotebook"))
print(style.theme_names())
print(style.theme_use("xpnative"))

style.configure("TNotebook", padding=0)
print(style.map("TNotebook"))

root.mainloop()
