# -*- coding: utf-8 -*-
 
"""
Classes used both by front-end and back-end
"""
import shlex

class Record:
    def __init__(self, **kw):
        self.__dict__.update(kw)
    
    def update(self, **kw):
        self.__dict__.update(kw)
    
    def setdefault(self, **kw):
        "updates those fields that are not yet present (similar to dict.setdefault)"
        for key in kw:
            if not hasattr(self, key):
                setattr(self, key, kw[key])
    
    def __repr__(self):
        keys = self.__dict__.keys()
        items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
    
    def __str__(self):
        keys = sorted(self.__dict__.keys())
        items = ("{}={!r}".format(k, str(self.__dict__[k])) for k in keys)
        return "{}({})".format(self.__class__.__name__, ", ".join(items))
    
    def __eq__(self, other):
        if type(self) != type(other):
            return False
        
        if len(self.__dict__) != len(other.__dict__):
            return False 
        
        for key in self.__dict__:
            if not hasattr(other, key):
                return False
            self_value = getattr(self, key)
            other_value = getattr(other, key)
            
            if type(self_value) != type(other_value) or self_value != other_value:
                return False
        
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
        
    def __hash__(self):
        return hash(repr(self))


class TextRange(Record):
    def __init__(self, lineno, col_offset, end_lineno, end_col_offset):
        self.lineno = lineno
        self.col_offset = col_offset
        self.end_lineno = end_lineno
        self.end_col_offset = end_col_offset
    
    def contains_smaller(self, other):
        return ((other.lineno > self.lineno
                 or other.lineno == self.lineno 
                    and other.col_offset > self.col_offset)
                and (other.end_lineno < self.end_lineno
                 or other.end_lineno == self.end_lineno 
                    and other.end_col_offset < self.end_col_offset))
    
    def contains_smaller_eq(self, other):
        return ((other.lineno > self.lineno
                 or other.lineno == self.lineno 
                    and other.col_offset >= self.col_offset)
                and (other.end_lineno < self.end_lineno
                 or other.end_lineno == self.end_lineno 
                    and other.end_col_offset <= self.end_col_offset))
    
    def not_smaller_in(self, other):
        return not other.contains_smaller(self)

    def is_smaller_in(self, other):
        return other.contains_smaller(self)
    
    def not_smaller_eq_in(self, other):
        return not other.contains_smaller_eq(self)

    def is_smaller_eq_in(self, other):
        return other.contains_smaller_eq(self)
    
    def get_start_index(self):
        return str(self.lineno) + "." + str(self.col_offset)
    
    def get_end_index(self):
        return str(self.end_lineno) + "." + str(self.end_col_offset)
    
    def __str__(self):
        return "TR(" + str(self.lineno) + "." + str(self.col_offset) + ", " \
                     + str(self.end_lineno) + "." + str(self.end_col_offset) + ")"
    
    
                 
class ValueInfo(Record):
    pass

class FrameInfo(Record):
    def get_description(self):
        return (
            "[" + str(self.id) + "] "
            + self.code_name + " in " + self.filename
            + ", focus=" + str(self.focus)
        )


class ActionCommand(Record):
    pass

class ToplevelCommand(ActionCommand):
    pass

class DebuggerCommand(ActionCommand):
    pass

class InputSubmission(Record):
    pass

class InlineCommand(Record):
    """
    Can be used both during debugging and between debugging.
    Initially meant for sending variable and heap info requests
    """
    pass


class CommandSyntaxError(Exception):
    pass

def parse_shell_command(cmd_line):
    assert cmd_line.startswith("%")
    
    parts = cmd_line.split(maxsplit=1)
    return parts[0][1:], parts[1] if len(parts) == 2 else ""



def serialize_message(msg):
    return repr(msg)

def parse_message(msg_string):
    return eval(msg_string)



def quote_path_for_shell(path):
    # http://stackoverflow.com/a/25208652/261181
    try:
        from shlex import quote
    except ImportError:
        from pipes import quote
    
    return quote(path)

def unquote_path(path):
    # TODO: may be incomplete
    return path.strip("'").strip('"').replace("\\\\", "\\")


def print_structure(o):
    print(o.__class__.__name__)
    for attr in dir(o):
        print(attr, "=", getattr(o, attr))

if __name__ == "__main__":
    tr1 = TextRange(1,2,3,4)
    tr2 = TextRange(1,2,3,4)
    print(tr1 == tr2)