import tkinter as tk

root = tk.Tk()

def on_key(event):
    print(bin(event.state), hex(event.state), event)

text = tk.Text(root)
text.grid()

print(repr(text.get("1.0", "end")))
print(text.index("end"), text.index("insert"))
text.insert("1.0", "Essa\n")

print(repr(text.get("1.0", "end")))
print(repr(text.get("end")))

text.tag_add("see", "1.0")
text.tag_add("too", "1.0", "end")

text.tag_lower("too")
text.tag_configure("too", foreground="blue")

text.tag_configure("see", background="red")
text.tag_configure("see", foreground="green", background="")
text.tag_configure("see", foreground="", background="")

text.bind("<Key>", on_key, True)


root.mainloop()
