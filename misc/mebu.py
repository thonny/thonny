import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

top = tk.Tk()

mb= ttk.Menubutton ( top, text="condiments")
mb.grid()
mb.menu =  tk.Menu ( mb, tearoff = 0 )
mb["menu"] =  mb.menu

mayoVar = tk.IntVar()
ketchVar = tk.IntVar()

mb.menu.add_checkbutton ( label="mayo",
                          variable=mayoVar )
mb.menu.add_checkbutton ( label="ketchup",
                          variable=ketchVar )

mb.pack()
top.mainloop()
