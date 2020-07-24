"""
NB! Stippling doesn't work on mac: 
http://wiki.tcl.tk/44444
http://rkeene.org/projects/tcl/tk.fossil/tkthistory/2954673
"""
import logging
import os.path
from tkinter import font

import thonny
from thonny import get_workbench, jedi_utils
from thonny.codeview import get_syntax_options_for_tag


def create_bitmap_file(width, height, predicate, name):

    cache_dir = os.path.join(thonny.THONNY_USER_DIR, "image_cache")
    name = "%s_%d_%d.xbm" % (name, width, height)
    filename = os.path.join(cache_dir, name)

    # if os.path.exists(filename):
    #    return filename

    hex_lines = []

    if width % 8 == 0:
        row_size = width
    else:
        # need to pad row size so that it is multiple of 8
        row_size = width + 8 - (width % 8)

    for y in range(height):
        byte_hexes = []
        for byte_index in range(row_size // 8):
            byte = 0
            for bit_index in range(7, -1, -1):
                x = byte_index * 8 + bit_index

                byte <<= 1
                if predicate(x, y):
                    byte |= 1

            byte_hexes.append(format(byte, "#04x"))
        hex_lines.append(",".join(byte_hexes))

    data = (
        "#define im_width %d\n" % width
        + "#define im_height %d\n" % height
        + "static char im_bits[] = {\n"
        + "%s\n" % ",\n".join(hex_lines)
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
        x = (x - 5) % indent_width

        stripe_width = 8
        gap = 3
        left = indent_width - stripe_width - gap

        return (
            left <= x < left + stripe_width
            or top
            and y == 0
            and x >= left
            or bottom
            and y == line_height - 1
            and x >= left
        )

    def hor(x: int, y: int, top: bool, bottom: bool) -> bool:
        # tells where to show pixels in statement line
        return top and y == 0 or bottom and y == line_height - 1

    color = get_syntax_options_for_tag("GUTTER").get("background", "gray")
    for orient, base_predicate in [("hor", hor), ("ver", ver)]:
        for top in [False, True]:
            for bottom in [False, True]:

                def predicate(
                    x,
                    y,
                    # need to make base_predicate, top and bottom local
                    base_predicate=base_predicate,
                    top=top,
                    bottom=bottom,
                ):
                    return base_predicate(x, y, top, bottom)

                tag_name = "%s_%s_%s" % (orient, top, bottom)
                bitmap_path = create_bitmap_file(indent_width, line_height, predicate, tag_name)
                text.tag_configure(tag_name, background=color, bgstipple="@" + bitmap_path)

    return True


def print_tree(node, level=0):
    from parso.python import tree as python_tree

    indent = "  " * level
    # if (isinstance(node, python_tree.PythonNode) and node.type == "sim"
    if node.type in ("simple_stmt",) or isinstance(node, python_tree.Flow):
        print(indent, node.type, node.start_pos, node.end_pos)

    if hasattr(node, "children"):
        for child in node.children:
            print_tree(child, level + 1)


def clear_tags(text):
    for pos in ["ver", "hor"]:
        for top in [True, False]:
            for bottom in [True, False]:
                text.tag_remove("%s_%s_%s" % (pos, top, bottom), "1.0", "end")


def add_tags(text):
    source = text.get("1.0", "end")
    clear_tags(text)
    tree = jedi_utils.parse_source(source)

    print_tree(tree)
    last_line = 0
    last_col = 0

    def tag_tree(node):
        nonlocal last_line, last_col
        from parso.python import tree as python_tree

        if node.type == "simple_stmt" or isinstance(node, (python_tree.Flow, python_tree.Scope)):

            start_line, start_col = node.start_pos
            end_line, end_col = node.end_pos

            # Before dealing with this node,
            # handle the case, where last vertical tag was meant for
            # same column, but there were empty or comment lines between
            if start_col == last_col:
                for i in range(last_line + 1, start_line):
                    # NB! tag not visible when logically empty line
                    # doesn't have indent prefix
                    text.tag_add(
                        "ver_False_False", "%d.%d" % (i, last_col - 1), "%d.%d" % (i, last_col)
                    )
                    print("ver_False_False", "%d.%d" % (i, last_col - 1), "%d.%d" % (i, last_col))

            print(node)

            # usually end_col is 0
            # exceptions: several statements on the same line (semicoloned statements)
            # also unclosed parens in if-header
            for lineno in range(start_line, end_line if end_col == 0 else end_line + 1):

                top = lineno == start_line and lineno > 1
                bottom = False  # start_line == end_line-1

                # horizontal line (only for first or last line)
                if top or bottom:
                    text.tag_add(
                        "hor_%s_%s" % (top, bottom),
                        "%d.%d" % (lineno, start_col),
                        "%d.%d" % (lineno + 1 if end_col == 0 else lineno, 0),
                    )

                    print(
                        "hor_%s_%s" % (top, bottom),
                        "%d.%d" % (lineno, start_col),
                        "%d.%d" % (lineno + 1, 0),
                    )

                # vertical line (only for indented statements)
                # Note that I'm using start col for all lines
                # (statement's indent shouldn't decrease in continuation lines)
                if start_col > 0:
                    text.tag_add(
                        "ver_%s_%s" % (top, bottom),
                        "%d.%d" % (lineno, start_col - 1),
                        "%d.%d" % (lineno, start_col),
                    )
                    print(
                        "ver_%s_%s" % (top, bottom),
                        "%d.%d" % (lineno, start_col - 1),
                        "%d.%d" % (lineno, start_col),
                    )

                    last_line = lineno
                    last_col = start_col

        # Recurse
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
        except Exception:
            logging.exception("Problem with defining structure tags")
            return

    add_tags(text)


def _load_plugin() -> None:
    wb = get_workbench()

    wb.set_default("view.program_structure", False)
    wb.bind("Save", handle_editor_event, True)
    wb.bind("Open", handle_editor_event, True)
    wb.bind_class("CodeViewText", "<<TextChange>>", handle_events, True)
