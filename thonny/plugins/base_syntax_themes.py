from thonny.globals import get_workbench

def default_light():
    light_fg = "DarkGray"
    string_fg = "DarkGreen"
    open_string_bg = "#c3f9d3"
    
    return {
        "TEXT"          : {"foreground" : "black", "insertbackground" : "black"},
        "definition"    : {"foreground" : light_fg},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        "open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#7f0055", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : "red"},
        "comment"       : {"foreground" : light_fg},
        
        "prompt"        : {"foreground" : "purple", "font" : "BoldEditorFont"},
        "magic"         : {"foreground" : light_fg},
        "stdin"         : {"foreground" : "Blue"},
        "stdout"        : {"foreground" : "Black"},
        "stderr"        : {"foreground" : "Red"},
        "value"         : {"foreground" : "DarkBlue"},
        "hyperlink"     : {"foreground" : "#3A66DD", "underline" : True}
    }

def default_dark():
    default_fg = "#B3B3B3" 
    string_fg = "#8DC76F"
    open_string_bg = "#453B22"
    
    #s.configure("Local.Code", foreground="#BCCAE8")
    #s.configure("MatchedName.Code", background="#193022")
    #s.configure("MatchedParens.Code", foreground="#F0995B")
    #s.configure("OpenParens.Code", background="#193022")
    
    #s.configure("StdOut.Shell", foreground="LightGray")
    #s.configure("StdIn.Shell", foreground="LightBlue")
    #s.configure("StdErr.Shell", foreground="Crimson")
    
    return {
        "TEXT"          : {"foreground" : default_fg, "insertbackground" : default_fg},
        "definition"    : {"foreground" : default_fg},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        "open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#9A79AD", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : "#FFCABF"},
        "comment"       : {"foreground" : "#C8DEE6"},
        
        "prompt"        : {"foreground" : "#5BEBBB", "font" : "BoldEditorFont"},
        "magic"         : {"foreground" : "pink"},
        "stdin"         : {"foreground" : "LightBlue"},
        "stdout"        : {"foreground" : "LightGray"},
        "stderr"        : {"foreground" : "#EB5B83"},
        "value"         : {"foreground" : "#EBEB5B"},
        "hyperlink"     : {"foreground" : "#DC5BEB", "underline" : True}
    }

def load_early_plugin():
    get_workbench().add_syntax_theme("Default light", None, default_light)
    get_workbench().add_syntax_theme("Default dark", None, default_dark)
    get_workbench().set_default("view.syntax_theme", "Default light")
    