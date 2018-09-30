import tkinter as tk

root = tk.Tk()

text = tk.Text(root)
text.grid()


def check(event):
    print(
        "keycode:",
        event.keycode,
        "state:",
        event.state,
        "char:",
        repr(event.char),
        "keysym",
        event.keysym,
        "keysym_num",
        event.keysym_num,
    )
    # return "break"


text.bind("<KeyPress>", check, True)

root.mainloop()
