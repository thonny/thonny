import os.path
import tkinter as tk
from tkinter import font

root = tk.Tk()
text = tk.Text(root)
text.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

text.insert("1.0", """
while True:
    a = int(input("kalapala: "))
    b = int(input("kalapala: "))
    if a > b:
        print(a+b)
    elif a == b:
        print("Done")
        break
    
print("Done")""")

def get_level_bitmap(width, height, is_first, is_last):
    
    
    filename = "temp_%d_%d_%s_%s.xbm" % (width, height, is_first, is_last)
    
    #if os.path.exists(filename):
    #    return filename
    
    offset = 3
    size = width * height
    
    # need to pad size so that it is multiple of 8
    if size % 8 != 0:
        size += 8 - (size % 8)
    
    byte_hexes = []
    for byte_index in range(size // 8):
        byte = 0
        for bit_index in range(7,-1,-1):
            i = byte_index * 8 + bit_index
            x = i % width
            y = i // width
            
            byte <<= 1
            if (x in [ offset+1] 
                or is_first and (
                    y in [0,1] and x == offset+2
                    or y == 0 and x == offset+3
                )
                or is_last and (
                    y in [height-1,height-2] and x == offset+2
                    or y == height-1 and x == offset+3
                )):
                byte |= 1
                
        byte_hexes.append(format(byte, "#04x"))
                
    data = (
        "#define im_width %d\n" % width
        + "#define im_height %d\n" % height
        + "static char im_bits[] = {\n"
        + "%s\n" % ",".join(byte_hexes)
        + "};"
    )
    
    with open(filename, "w") as fp:
        fp.write(data)
    return filename
    


text_font = font.nametofont(text["font"])
root.update()
print(text_font.measure("    "), text_font.measure("linespace"))
text.tag_configure("top", bgstipple="@"+get_level_bitmap(32,16, True, False), background="gray")
text.tag_configure("middle", bgstipple="@"+get_level_bitmap(32,16, False, False), background="gray")
text.tag_configure("bottom", bgstipple="@"+get_level_bitmap(32,16, False, True), background="gray")
text.tag_configure("both", bgstipple="@"+get_level_bitmap(32,16, True, True), background="gray")

text.tag_configure("shift", lmargin1=6)
text.tag_configure("sel", bgstipple="@white.xbm", background="blue", foreground="white")

text.tag_add("shift", "1.0", "end")
text.tag_add("top", "2.0", "2.1")

for i in range(3, 10):
    text.tag_add("middle", "%d.0" % i, "%d.1" % i)

text.tag_add("middle", "10.0", "10.1")
text.tag_add("top", "11.0", "11.1")
text.tag_raise("sel")


def onconf(e):
    print(text.bbox("2.7"))
    print(text_font.measure("    "), text_font.measure("linespace"))

root.bind("<Configure>", onconf, True)

root.mainloop()