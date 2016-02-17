import tkinter as tk
from thonny.tktextext import EnhancedText

root = tk.Tk()
text = EnhancedText(root, read_only=True)
text.grid()

text.direct_insert("1.0", "Essa\n    'tessa\nkossa\nx=34+(45*89*(a+45)")
text.tag_configure('string', background='yellow')
text.tag_add("string", "2.0", "3.0")


text.tag_configure('paren', underline=True)
text.tag_add("paren", "4.6", "5.0")

root.mainloop()