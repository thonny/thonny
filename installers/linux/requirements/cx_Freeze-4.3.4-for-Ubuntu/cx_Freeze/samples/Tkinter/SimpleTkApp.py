#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from tkinter import Tk, Label, Button, BOTTOM
except ImportError:
    from Tkinter import Tk, Label, Button, BOTTOM

root = Tk()
root.title('Button')
Label(text='I am a button').pack(pady=15)
Button(text='Button').pack(side=BOTTOM)
root.mainloop()
