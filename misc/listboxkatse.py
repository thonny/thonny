import tkinter as tk

root = tk.Tk()

lb1 = tk.Listbox(
    root, activestyle="dotbox", exportselection=True, selectbackground="red"
)
lb2 = tk.Listbox(root, exportselection=True)

lb1.grid()
lb2.grid()

lb1.insert(0, "üks", "kaks", "kolm")
lb2.insert(0, "üks", "kaks", "kolm")

root.mainloop()
