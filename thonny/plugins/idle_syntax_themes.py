from thonny.globals import get_workbench

def idle_classic():
    string_fg = "#00aa00"
    return {
        "TEXT"          : {"foreground" : "black", "insertbackground" : "black", "background" : "white"},
        "sel"           : {"foreground" : "black", "background" : "gray"},
        
        "number"        : {"foreground" : "black"},
        "definition"    : {"foreground" : "#0000ff", "font" : "EditorFont"},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg},
        "open_string3"  : {"foreground" : string_fg},
        "keyword"       : {"foreground" : "#ff7700", "font" : "EditorFont"},
        "builtin"       : {"foreground" : "#900090"},
        "comment"       : {"foreground" : "#dd0000"},
        
        "prompt"        : {"foreground" : "#770000"},
        "stdin"         : {"foreground" : "black"},
        "stdout"        : {"foreground" : "Blue"},
        "value"         : {"foreground" : "Blue"},
        "stderr"        : {"foreground" : "Red"},
        
        "found"                 : {"foreground" : "", "underline" : True},
        "current_found"         : {"foreground" : "white", "background" : "black"},
    }
        

def idle_dark():
    normal_fg = "white"
    string_fg = "#02ff02"
    
    return {
        "TEXT"          : {"foreground" : normal_fg, "insertbackground" : normal_fg, "background" : "#002240"},
        "sel"           : {"foreground" : "#FFFFFF", "background" : "#7e7e7e"},
        
        "number"        : {"foreground" : normal_fg},
        "definition"    : {"foreground" : "#5e5eff", "font" : "EditorFont"},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg},
        "open_string3"  : {"foreground" : string_fg},
        "keyword"       : {"foreground" : "#ff8000", "font" : "EditorFont"},
        "builtin"       : {"foreground" : "#ff00ff"},
        "comment"       : {"foreground" : "#dd0000"},
        
        "prompt"        : {"foreground" : "#ff4d4d"},
        "stdin"         : {"foreground" : normal_fg},
        "stdout"        : {"foreground" : "#c2d1fa"},
        "value"         : {"foreground" : "#c2d1fa"},
        "stderr"        : {"foreground" : "#ffb3b3"},
        
        "found"                 : {"foreground" : "", "underline" : True},
        "current_found"         : {"foreground" : "#002240", "background" : "#fbfbfb"},
    }
        

def load_early_plugin():
    get_workbench().add_syntax_theme("IDLE Classic", "Default Light", idle_classic)
    get_workbench().add_syntax_theme("IDLE Dark", "Default Dark", idle_dark)
