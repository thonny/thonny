from tkinter import Tk, Label

root = Tk()
Label(root, text="External Padding", bg="light grey").grid(row=0, column=0, padx=20)
Label(root, text="Internal Padding", bg="red").grid(row=8, column=0, ipadx=20)
print(root.grid_size())
root.mainloop()
