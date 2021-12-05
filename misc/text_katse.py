import tkinter as tk

root = tk.Tk()

def on_key(event):
    print(bin(event.state), hex(event.state), event)

text = tk.Text(root)
text.grid()

text.insert("1.0", "Essa\ntessa\nkossa")

text.tag_add("see", "1.0")
text.tag_add("too", "1.0", "end")

text.tag_lower("too")
text.tag_configure("too", foreground="blue")

text.tag_configure("see", background="red")
text.tag_configure("see", foreground="green", background="")
text.tag_configure("see", foreground="", background="")

text.bind("<Key>", on_key, True)


root.mainloop()
