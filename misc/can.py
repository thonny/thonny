import tkinter as tk

root = tk.Tk()

canvas = tk.Canvas(root, width=200, height=300, background="white")
canvas.grid()

rec1 = canvas.create_rectangle(10, 10, 70, 70, fill="red")
rec2 = canvas.create_rectangle(30, 30, 90, 90, fill="green")
rec3 = canvas.create_rectangle(15, 15, 50, 120, fill="blue")

active_id = None


def on_move(event):
    if active_id is not None:
        canvas.move(active_id, event.x, event.y)
        print("Move", event.x, event.y)


def on_click(event):
    stack = canvas.find_overlapping(event.x, event.y, event.x, event.y)
    print(stack)
    canvas.tag_raise(stack[-1])
    global active_id
    active_id = stack[-1]


canvas.bind("<1>", on_click, True)
canvas.bind("<B1-Motion>", on_move, True)


root.mainloop()
