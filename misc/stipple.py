import os.path
import tkinter as tk
from tkinter import font

spacing1 = 5
spacing3 = 5
root = tk.Tk()
text = tk.Text(root, spacing1=spacing1, spacing3=spacing3)
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

def brackets(x, y, height, top_bump, bottom_bump):
    offset = 5
    stripe_width = 1
    bump_height = 1
    bump_width = 2
    return (offset <= x < offset+stripe_width 
            or top_bump 
                and y < bump_height
                and offset <= x < offset+stripe_width+bump_width
            or bottom_bump 
                and y >= height-bump_height
                and offset <= x < offset+stripe_width+bump_width
            )


def lines(x, y, height, top, bottom):
    offset = 8
    stripe_width = 1
    gap = 0
    return (offset <= x < offset+stripe_width 
            and (
                gap <= y < height-gap
                or y < gap and not top
                or y >= height-gap and not bottom
            )
    )

def topline(x, y, height, top, bottom):
    return y == 0

def get_level_bitmap(width, height, top_bump, bottom_bump,
                     predicate):
    
    
    filename = "temp_%d_%d_%s_%s_%s.xbm" % (width, height, top_bump,
                                            bottom_bump,
                                            predicate.__name__)
    
    #if os.path.exists(filename):
    #    return filename
    
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
            if predicate(x, y, height, top_bump, bottom_bump):
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
    return os.path.abspath(filename)
    

root.update()
c = "#cccccc"
_, _, _, h = text.bbox("2.7")
h = h + spacing1 + spacing3
text_font = font.nametofont(text["font"])
w = text_font.measure("    ")
print(w, h)

predi = lines
text.tag_configure("top", bgstipple="@"+get_level_bitmap(w,h, True, False, predi), background=c)
text.tag_configure("middle", bgstipple="@"+get_level_bitmap(w,h, False, False, predi), background=c)
text.tag_configure("bottom", bgstipple="@"+get_level_bitmap(w,h, False, True, predi), background=c)
text.tag_configure("both", bgstipple="@"+get_level_bitmap(w,h, True, True, predi), background=c)
text.tag_configure("topline", bgstipple="@"+get_level_bitmap(w,h, True, True, topline), background=c)

text.tag_configure("sel", bgstipple="", background="blue")

text.tag_configure("shift", lmargin1=15)

text.tag_add("shift", "1.0", "end")
##############

#text.tag_add("top", "2.0", "2.1")
#for i in range(3, 9):
#    text.tag_add("middle", "%d.0" % i, "%d.1" % i)

#text.tag_add("bottom", "9.0", "9.1")
#text.tag_add("both", "10.0", "10.1")
#text.tag_add("both", "11.0", "11.1")


#############
text.tag_add("both", "3.2", "3.3")
text.tag_add("both", "4.2", "4.3")
text.tag_add("top", "5.2", "5.3")
text.tag_add("middle", "6.2", "6.3")
text.tag_add("middle", "7.2", "7.3")
text.tag_add("middle", "8.2", "8.3")
#text.tag_add("middle", "9.3", "9.4")
text.tag_add("bottom", "9.2", "9.3")

########
text.tag_add("topline", "10.0", "11.0")
text.tag_add("topline", "11.0", "12.0")
text.tag_add("topline", "2.0", "3.0")
text.tag_add("topline", "3.4", "4.0")
text.tag_add("topline", "4.4", "5.0")
text.tag_add("topline", "5.4", "6.0")


text.tag_raise("sel")


root.mainloop()