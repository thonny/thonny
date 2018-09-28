import tkinter as tk

root = tk.Tk()
text = tk.Text(root)
text.grid()

text.insert(
    "1.0",
    """first
second
third
""",
)

text.tag_configure("bgstip", bgstipple="gray50", background="pink")
text.tag_configure("fgstip", fgstipple="gray50", foreground="blue")
text.tag_add("bgstip", "2.0", "3.2")
text.tag_add("fgstip", "3.0", "3.5")

root.mainloop()
