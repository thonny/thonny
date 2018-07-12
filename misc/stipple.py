import os.path
import tkinter as tk
from tkinter import font

spacing1 = 6
spacing3 = 6
root = tk.Tk()
text = tk.Text(root, spacing1=spacing1, spacing3=spacing3,
               highlightthickness=0,
               borderwidth=0, relief="flat")
text.grid(row=0, column=0, sticky="nsew")

root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

text.insert("1.0", """print('hello')
while True:
    a = int(input("kalapala: "))
    b = int(input("kalapala: "))
    if a > b:
        print(a+b)
    elif a == b:
        print("Done")
        break
print("Done")
""")

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
    offset = w-7
    stripe_width = 3
    gap = 0
    return (offset <= x < offset+stripe_width 
            and (
                gap <= y < height-gap
                or y < gap and not top
                or y >= height-gap and not bottom
            )
    )

def lines2(x, y, height, top, bottom):
    offset = w-5
    stripe_width = 4
    gap = 0
    return (offset <= x < offset+stripe_width 
            or top and (x >= offset or x <= 2) and y == 0
            or bottom and (x >= offset or x <= 2) and y == height-1
    )

def horline(x, y, height, top, bottom):
    return (y == 0
            or bottom and y == height-1)

def full(x, y, height, top, bottom):
    return True

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

predi = lines2
text.tag_configure("top", bgstipple="@"+get_level_bitmap(w,h, True, False, predi), background=c)
text.tag_configure("middle", bgstipple="@"+get_level_bitmap(w,h, False, False, predi), background=c)
text.tag_configure("bottom", bgstipple="@"+get_level_bitmap(w,h, False, True, predi), background=c)
text.tag_configure("both", bgstipple="@"+get_level_bitmap(w,h, True, True, predi), background=c)
text.tag_configure("horline", bgstipple="@"+get_level_bitmap(w,h, True, False, horline), background=c)
text.tag_configure("horline_both", bgstipple="@"+get_level_bitmap(w,h, True, True, horline), background=c)

text.tag_configure("sel", bgstipple="@"+get_level_bitmap(w,h, True, True, full),
                   background="blue")

text.tag_configure("shift", lmargin1=2)

text.tag_add("shift", "1.0", "end")
##############

#text.tag_add("top", "2.0", "2.1")
#for i in range(3, 9):
#    text.tag_add("middle", "%d.0" % i, "%d.1" % i)

#text.tag_add("bottom", "9.0", "9.1")
#text.tag_add("both", "10.0", "10.1")
#text.tag_add("both", "11.0", "11.1")


#############
text.tag_add("top", "3.3", "3.4")
text.tag_add("top", "4.3", "4.4")
text.tag_add("top", "5.3", "5.4")
text.tag_add("middle", "6.3", "6.4")
text.tag_add("middle", "7.3", "7.4")
text.tag_add("middle", "8.3", "8.4")
text.tag_add("middle", "9.3", "9.4")

text.tag_add("both", "6.7", "6.8")
text.tag_add("top", "8.7", "8.8")
text.tag_add("top", "9.7", "9.8")

########
text.tag_add("horline", "10.0", "11.0")
text.tag_add("horline", "11.0", "12.0")
text.tag_add("horline", "2.0", "3.0")
text.tag_add("horline", "3.4", "4.0")
text.tag_add("horline", "4.4", "5.0")
text.tag_add("horline", "5.4", "6.0")

text.tag_add("horline_both", "6.8", "7.0")
#text.tag_add("horline", "7.8", "8.0")
text.tag_add("horline", "8.8", "9.0")
text.tag_add("horline", "9.8", "10.0")

#text.tag_configure("horline", background="red")

text.tag_raise("sel")


root.mainloop()