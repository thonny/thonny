import os.path
from thonny import get_workbench, jedi_utils
from tkinter import font
import thonny
import logging
from thonny.codeview import get_syntax_options_for_tag

python_tree = jedi_utils.import_python_tree()

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
    


def configure_text(text):
    spacing1 = 2
    spacing3 = 3
    text_font = text["font"]
    text.configure(spacing1=spacing1, spacing3=spacing3)
    text.master._gutter.configure(spacing1=spacing1, spacing3=spacing3)
    if isinstance(text_font, str):
        text_font = font.nametofont(text_font)
    
    indent_width = text_font.measure("    ")
    bbox = text.bbox("1.0")
    if bbox is None or bbox[3] < 5:
        # text not ready yet
        # TODO: Text in Tk 8.6 has sync method
        return False
    
    line_height = bbox[3] + spacing1 + spacing3
    
    print(indent_width, line_height)
    
    def ver(x: int, y: int, top: bool, bottom: bool) -> bool:
        # tells where to show pixels in vertical border of the statement
        # It would be convenient if tiling started from the start of 
        # 1st char, but it is offset a bit
        # In order to make computation easier, I'm offsetting x as well
        x = (x-5) % indent_width
        
        stripe_width = 4
        gap = 3
        left = indent_width-stripe_width - gap
        
        return (left <= x < left+stripe_width 
                or top and y == 0 and x >= left
                or bottom and y == line_height-1 and x >= left
        )
        
    def hor(x: int, y: int, top: bool, bottom: bool) -> bool:
        # tells where to show pixels in statement line
        return (
            top and y == 0
            or bottom and y == line_height-1
        )
    
    color = get_syntax_options_for_tag("GUTTER").get("background", "gray")
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
                                   bgstipple="@" + bitmap_path)
    
    
    return True

def print_tree(node, level=0):
    indent = "  " * level
    #if (isinstance(node, python_tree.PythonNode) and node.type == "sim"
    if (node.type in ("simple_stmt",)
        or isinstance(node, python_tree.Flow)
        ):
        print(indent, node.type, node.start_pos, node.end_pos)
        
    if hasattr(node, "children"):
        for child in node.children:
            print_tree(child, level+1)

def add_tags(text):
    source = text.get("1.0", "end")
    tree = jedi_utils.parse_source(source)
    
    print_tree(tree)
    
    def tag_tree(node):
        if (node.type == "simple_stmt"
            or isinstance(node, (python_tree.Flow,
                                 python_tree.Scope))):
            #print(indent, node.type, node.start_pos, node.end_pos)
            first_line_start = "%d.%d" % node.start_pos
            first_line_end = "%d.%d" % (node.start_pos[0]+1, 0)
            print(node)
            
            # create horizontal lines
            if node.start_pos[0] > 1: # skip for first line
                tag_name = "hor_%s_False" % True # Todo  
                text.tag_add(tag_name, first_line_start, first_line_end)
                print(tag_name, first_line_start, first_line_end)
            
            if node.start_pos[1] > 0:
                # tag line beginnings
                # TODO: handle unprocessed empty and comment lines
                # between last tag and this one
                
                assert node.end_pos[1] == 0 
                for lineno in range(node.start_pos[0], node.end_pos[0]):
                    top = lineno == node.start_pos[0]
                    bottom = False
                    text.tag_add("ver_%s_%s" % (top, bottom),
                                 "%d.%d" % (lineno, node.start_pos[1]-2),
                                 "%d.%d" % (lineno, node.start_pos[1]),
                                 )
                    print("ver_%s_%s" % (top, bottom),
                                 "%d.%d" % (lineno, node.start_pos[1]-2),
                                 "%d.%d" % (lineno, node.start_pos[1]),
                                 )
            
        if node.type != "simple_stmt" and hasattr(node, "children"):
            for child in node.children:
                tag_tree(child)
    
    tag_tree(tree)

def handle_editor_event(event):
    configure_and_add_tags(event.editor.get_text_widget())

def handle_events(event):
    if hasattr(event, "text_widget"):
        text = event.text_widget
    else:
        text = event.widget
    
    configure_and_add_tags(text)

def configure_and_add_tags(text):
    if not getattr(text, "structure_tags_configured", False):
        try:
            if configure_text(text):
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
    wb.bind("Save", handle_editor_event, True)
    wb.bind("Open", handle_editor_event, True)
