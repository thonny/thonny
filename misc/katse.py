import tkinter as tk
from tkinter import ttk

root = tk.Tk()


root.geometry("+105+105")
root.update_idletasks()
print(root.winfo_x(), root.winfo_y())
print(root.winfo_rootx(), root.winfo_rooty())
print(root.wm_geometry())

root.mainloop()
