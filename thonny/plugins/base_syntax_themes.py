from thonny.globals import get_workbench

def default_light():
    default_fg = "DarkGray"
    string_fg = "DarkGreen"
    open_string_bg = "#c3f9d3"
    
    return {
        "definition"    : {"foreground" : default_fg},
        "magic"         : {"foreground" : default_fg},
        "string"        : {"foreground" : string_fg},
        #"string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        #"open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#7f0055", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : default_fg},
        "comment"       : {"foreground" : default_fg}
    }

def default_dark():
    default_fg = "DarkGray"
    string_fg = "DarkGreen"
    open_string_bg = "#c3f9d3"
    
    return {
        "definition"    : {"foreground" : default_fg},
        "magic"         : {"foreground" : default_fg},
        "string"        : {"foreground" : string_fg},
        #"string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        #"open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#7f0055", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : default_fg},
        "comment"       : {"foreground" : default_fg}
    }

def load_early_plugin():
    get_workbench().add_syntax_theme("Default light", None, default_light)
    get_workbench().add_syntax_theme("Default dark", None, default_light)
    