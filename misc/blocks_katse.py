import tkinter as tk

pos = [0,0]

def down(e):
    pos[0] = e.x
    pos[1] = e.y

def drag(e):
    dx = e.x - pos[0]
    dy = e.y - pos[1]
    c.move("pop", dx, dy)
    pos[0] = e.x
    pos[1] = e.y

root = tk.Tk()

c = tk.Canvas(root, width=600, height=600)
c.grid()

p = c.create_polygon(35,75,
                     50,50, 60,50, 240,50, 250,50,
                     265,75,
                     250,100, 240,100, 60,100, 50,100, fill="pink", outline="red", smooth=True, splinesteps=12, tags=("pop",))
c.create_oval(20,300, 550, 550)
print(c.postscript())
e = tk.Entry(root, border=0, bg="#ffaaaa")
#e.grid()
c.create_window(150, 75, window=e, tags=("pop",))
c.bind("<1>", down)
c.bind("<B1-Motion>", drag)
root.mainloop()
