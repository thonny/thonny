import os.path
import tkinter as tk
from tkinter import font

root = tk.Tk()
text = tk.Text(root, spacing3=0)
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

def get_level_bitmap(width, height, top_bump, bottom_bump):
    
    
    filename = "temp_%d_%d_%s_%s.xbm" % (width, height, top_bump, bottom_bump)
    
    #if os.path.exists(filename):
    #    return filename
    
    offset = 5
    stripe_width = 1
    bump_height = 1
    bump_width = 2
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
            if (offset <= x < offset+stripe_width 
                or top_bump 
                    and y < bump_height
                    and offset <= x < offset+stripe_width+bump_width
                or bottom_bump 
                    and y >= height-bump_height
                    and offset <= x < offset+stripe_width+bump_width
                ):
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
    

root.update()
c = "gray"
_, _, _, h = text.bbox("2.7")
text_font = font.nametofont(text["font"])
w = text_font.measure("    ")
print(w, h)

text.tag_configure("top", bgstipple="@"+get_level_bitmap(w,h, True, False), background=c)
text.tag_configure("middle", bgstipple="@"+get_level_bitmap(w,h, False, False), background=c)
text.tag_configure("bottom", bgstipple="@"+get_level_bitmap(w,h, False, True), background=c)
text.tag_configure("both", bgstipple="@"+get_level_bitmap(w,h, True, True), background=c)

text.tag_configure("shift", lmargin1=8)

text.tag_add("shift", "1.0", "end")
text.tag_add("top", "2.0", "2.1")
##############

for i in range(3, 10):
    text.tag_add("middle", "%d.0" % i, "%d.1" % i)

text.tag_add("middle", "10.0", "10.1")
text.tag_add("both", "11.0", "11.1")


#############
text.tag_add("top", "3.3", "3.5")
text.tag_add("top", "4.3", "4.5")
text.tag_add("top", "5.3", "5.5")
text.tag_add("middle", "6.3", "6.5")
text.tag_add("middle", "7.3", "7.5")
text.tag_add("middle", "8.3", "8.5")
#text.tag_add("middle", "9.3", "4.4")
text.tag_add("bottom", "9.3", "9.5")


text.tag_raise("sel")


root.mainloop()