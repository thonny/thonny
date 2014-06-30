import turtle

turtle.getcanvas().winfo_toplevel().wm_attributes("-topmost", True)

for i in range(4):
    turtle.forward(100)
    turtle.left(90)