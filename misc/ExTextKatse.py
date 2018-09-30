import tkinter as tk

from thonny.tktextext import TextFrame, TweakableText

root = tk.Tk()
frame = TextFrame(
    root,
    read_only=False,
    wrap=tk.NONE,
    line_numbers=True,
    line_length_margin=13,
    text_class=TweakableText,
)
frame.grid()
text = frame.text

text.direct_insert("1.0", "Essa\n    'tessa\nkossa\nx=34+(45*89*(a+45)")
text.tag_configure("string", background="yellow")
text.tag_add("string", "2.0", "3.0")


text.tag_configure("paren", underline=True)
text.tag_add("paren", "4.6", "5.0")

root.mainloop()
