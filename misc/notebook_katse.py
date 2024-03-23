import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)



main_frame = tk.Frame(root, background="red")
main_frame.rowconfigure(0, weight=1)
main_frame.columnconfigure(0, weight=1)

main_frame.grid()

nb = ttk.Notebook(main_frame)

p1 = ttk.Label(master=nb, text="page 1")
p2 = ttk.Label(master=nb, text="page 2")

nb.add(p1, text="Page 1")
nb.add(p2, text="Page 2")

nb.grid(row=0, column=0, sticky="nsew", padx=3)


root.mainloop()
