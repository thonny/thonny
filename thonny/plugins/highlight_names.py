from jedi import Script
from thonny.tktextext import EnhancedText


NAME_CONF = {'background': 'Black', 'foreground': 'White'}


def highlight(text: EnhancedText):
    text.tag_delete("NAME")
    text.tag_config("NAME", NAME_CONF)
    index = text.index("insert").split(".")
    l, c = int(index[0]), int(index[1])
    script = Script(text.get('1.0', 'end-1c'), l, c)

    for u in script.usages():
        line, column = (u.line, u.column)
        if None not in (line, column):
            begin = "%d.%d" % (line, column)
            end = begin + ("+%dc" % len(u.name))
            text.tag_add("NAME", "%d.%d" % (line, column), end)