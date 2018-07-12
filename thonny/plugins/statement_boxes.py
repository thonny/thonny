import os.path
from thonny import get_workbench, jedi_utils
from tkinter import font
import thonny
import logging

def create_bitmap_file(width, height, predicate, name):
    
    cache_dir = os.path.join(thonny.THONNY_USER_DIR, "image_cache")
    name = "%s_%d_%d.xbm" % (name, width, height)
    filename = os.path.join(cache_dir, name)
    
    #if os.path.exists(filename):
    #    return filename
    
    byte_hexes = []
    
    if width % 8 == 0:
        row_size = width
    else:
        # need to pad row size so that it is multiple of 8
        row_size = width + 8 - (width % 8)
    
    for y in range(height):
        for byte_index in range(row_size // 8):
            byte = 0
            for bit_index in range(7,-1,-1):
                x = byte_index * 8 + bit_index
                
                byte <<= 1
                if predicate(x, y):
                    byte |= 1
                    
            byte_hexes.append(format(byte, "#04x"))
                
    data = (
        "#define im_width %d\n" % width
        + "#define im_height %d\n" % height
        + "static char im_bits[] = {\n"
        + "%s\n" % ",".join(byte_hexes)
        + "};"
    )
    
    os.makedirs(cache_dir, exist_ok=True)
    with open(filename, "w") as fp:
        fp.write(data)
    return filename
    


def configure_tags(text):
    #text.update()
    text_font = text["font"]
    if isinstance(text_font, str):
        text_font = font.nametofont(text_font)
    
    indent_width = text_font.measure("    ")
    _, _, _, line_height = text.bbox("1.0")
    
    if line_height < 5:
        # text not ready yet
        return False
    
    print(indent_width, line_height)
    
    def ver(x: int, y: int, top: bool, bottom: bool) -> bool:
        # tells where to show pixels in vertical border of the statement
        offset = indent_width-5
        stripe_width = 4
        return (offset <= x < offset+stripe_width 
                or top and (x >= offset or x <= 2) and y == 0
                or bottom and (x >= offset or x <= 2) and y == line_height-1
        )
        
    def hor(x: int, y: int, top: bool, bottom: bool) -> bool:
        # tells where to show pixels in statement line
        return (
            top and y == 0
            or bottom and y == line_height-1
        )
    
    color = "red"
    for orient, base_predicate in [("ver", ver), ("hor", hor)]:
        for top in [True, False]:
            for bottom in [True, False]:
                def predicate(x, y, 
                              # need to make base_predicate, top and bottom local
                              base_predicate=base_predicate,
                              top=top,
                              bottom=bottom):
                    return base_predicate(x, y, top, bottom)
                    
                tag_name = "%s_%s_%s" % (orient, top, bottom)
                bitmap_path = create_bitmap_file(indent_width, line_height, 
                                                 predicate, tag_name)
                text.tag_configure(tag_name, background=color,
                                   bgstipple="@" + bitmap_path.replace("\\", "/"))
    
    
    return True
    
def add_tags(text):
    source = text.get("1.0", "end")
    tree = jedi_utils.parse_source(source)
    print("adding tags", tree)

def handle_events(event):
    if hasattr(event, "text_widget"):
        text = event.text_widget
    else:
        text = event.widget
    
    configure_and_add_tags(text)

def configure_and_add_tags(text):
    if not getattr(text, "structure_tags_configured", False):
        try:
            if configure_tags(text):
                text.structure_tags_configured = True
            else:
                text.after(500, lambda: configure_and_add_tags(text))
                return
        except:
            logging.exception("Problem with defining structure tags")
            return
    
    add_tags(text)
        

def load_plugin() -> None:
    wb = get_workbench() 

    wb.set_default("view.program_structure", False)
    wb.bind_class("CodeViewText", "<<TextChange>>", handle_events, True)
