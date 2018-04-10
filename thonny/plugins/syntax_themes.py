from thonny.globals import get_workbench

def default_light():
    default_fg = "black"
    light_fg = "DarkGray"
    string_fg = "DarkGreen"
    open_string_bg = "#c3f9d3"
    
    return {
        "TEXT"          : {"foreground" : default_fg, "insertbackground" : default_fg},
        "definition"    : {"foreground" : default_fg, "font" : "BoldEditorFont"},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        "open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "keyword"       : {"foreground" : "#7f0055", "font" : "BoldEditorFont"},
        "builtin"       : {"foreground" : "black"},
        "number"        : {"foreground" : "#B04600"},
        "comment"       : {"foreground" : light_fg},
        
        "prompt"        : {"foreground" : "purple", "font" : "BoldEditorFont"},
        "magic"         : {"foreground" : light_fg},
        "stdin"         : {"foreground" : "Blue"},
        "stdout"        : {"foreground" : "Black"},
        "stderr"        : {"foreground" : "Red"},
        "value"         : {"foreground" : "DarkBlue"},
        "hyperlink"     : {"foreground" : "#3A66DD", "underline" : True},
        
        # paren matcher
        "surrounding_parens"  : {"foreground" : "Blue", "font" : "BoldEditorFont"},
        "unclosed_expression"  : {"background" : "LightGray"},
        
        # find/replace
        "found" : {"foreground" : "blue", "underline" : True},
        "current_found" : {"foreground" : "white", "background" : "red"},
        
        # debugger
        "active_focus"    : {"background" : "#F8FC9A", "borderwidth" : 1, "relief" : "solid"},
        "suspended_focus" : {"background" : ""       , "borderwidth" : 1, "relief" : "solid"},
        "completed_focus" : {"background" : "#BBEDB2", "borderwidth" : 1, "relief" : "flat"},
        "exception_focus" : {"background" : "#FFBFD6", "borderwidth" : 1, "relief" : "solid"},
        "expression_box"  : {"background" : "#DCEDF2", "foreground" : default_fg},
    }

def default_dark():
    default_fg = "#B3B3B3" 
    string_fg = "#8DC76F"
    open_string_bg = "#453B22"
    
    #s.configure("Local.Code", foreground="#BCCAE8")
    #s.configure("MatchedName.Code", background="#193022")
    
    return {
        "TEXT"          : {"foreground" : default_fg, "insertbackground" : default_fg},
        #"sel"           : {"foreground" : ""},
        "definition"    : {"foreground" : default_fg},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg, "background" : open_string_bg},
        "open_string3"  : {"foreground" : string_fg, "background" : open_string_bg},
        "builtin"       : {"foreground" : default_fg},
        "keyword"       : {"foreground" : "#B088CF", "font" : "BoldEditorFont"},
        "number"        : {"foreground" : "#FFCABF"},
        "comment"       : {"foreground" : "#C8DEE6"},
        
        # shell
        "prompt"        : {"foreground" : "#5BEBBB", "font" : "BoldEditorFont"},
        "magic"         : {"foreground" : "pink"},
        "stdin"         : {"foreground" : "LightBlue"},
        "stdout"        : {"foreground" : "LightGray"},
        "stderr"        : {"foreground" : "#EB5B83"},
        "value"         : {"foreground" : "#EBEB5B"},
        "hyperlink"     : {"foreground" : "#DC5BEB", "underline" : True},
        
        # paren matcher
        "surrounding_parens"  : {"foreground" : "#F0995B", "font" : "BoldEditorFont"},
        "unclosed_expression"  : {"background" : "#193022"},
        
        # find/replace
        "found" : {"underline" : True},
        "current_found" : {"foreground" : "white", "background" : "red"},
        
        # debugger
        "active_focus"    : {"background" : "#807238", "borderwidth" : 1, "relief" : "solid"},
        "suspended_focus" : {"background" : ""       , "borderwidth" : 1, "relief" : "solid"},
        "completed_focus" : {"background" : "#807238", "borderwidth" : 1, "relief" : "flat"},
        "exception_focus" : {"background" : "#FFBFD6", "borderwidth" : 1, "relief" : "solid"},
        "expression_box"  : {"background" : "#506E67", "foreground" : default_fg},
    }


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

def desert():
    normal_fg = "#f0e68c"
    string_fg = "#ffa0a0"
    
    return {
        "TEXT"          : {"foreground" : normal_fg, "insertbackground" : normal_fg, "background" : "#333333"},
        "sel"           : {"foreground" : "#000000", "background" : "gray"},
        
        "number"        : {"foreground" : normal_fg},
        "definition"    : {"foreground" : "#98fb98"},
        "string"        : {"foreground" : string_fg},
        "string3"       : {"foreground" : string_fg},
        "open_string"   : {"foreground" : string_fg},
        "open_string3"  : {"foreground" : string_fg},
        "keyword"       : {"foreground" : "#cc6600"},
        "builtin"       : {"foreground" : "#519e51"},
        "comment"       : {"foreground" : "#87ceeb"},
        
        "prompt"        : {"foreground" : "#87ceeb"},
        "stdin"         : {"foreground" : normal_fg},
        "stdout"        : {"foreground" : "#eeeeee"},
        "value"         : {"foreground" : "#eeeeee"},
        "stderr"        : {"foreground" : "#ff3e40"},
        
        "found"                 : {"foreground" : "", "underline" : True},
        "current_found"         : {"foreground" : "#ffffff", "background" : "#333333"},
    }
    


def load_early_plugin():
    get_workbench().add_syntax_theme("Default Light", None, default_light)
    get_workbench().add_syntax_theme("Default Dark", None, default_dark)
    get_workbench().add_syntax_theme("IDLE Classic", "Default Light", idle_classic)
    get_workbench().add_syntax_theme("IDLE Dark", "Default Dark", idle_dark)
    get_workbench().add_syntax_theme("Desert", "Default Dark", desert)
    
    get_workbench().set_default("view.syntax_theme", "Default Light")
    