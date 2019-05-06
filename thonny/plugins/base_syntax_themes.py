from thonny import get_workbench
from thonny.workbench import SyntaxThemeSettings


def default_light() -> SyntaxThemeSettings:
    default_fg = "black"
    default_bg = "#fdfdfd"
    light_fg = "DarkGray"
    string_fg = "DarkGreen"
    open_string_bg = "#c3f9d3"

    return {
        "TEXT": {
            "foreground": default_fg,
            "insertbackground": default_fg,
            "background": default_bg,
        },
        "GUTTER": {"foreground": "#999999", "background": "#e0e0e0"},
        "breakpoint": {"foreground": "crimson"},
        "current_line": {"background": "#f5f5f5"},
        "definition": {"foreground": "DarkBlue", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg, "background": open_string_bg},
        "open_string3": {"foreground": string_fg, "background": open_string_bg},
        "keyword": {"foreground": "#7f0055", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#7f0055"},
        "number": {"foreground": "#B04600"},
        "comment": {"foreground": light_fg},
        "prompt": {"foreground": "purple", "font": "BoldEditorFont"},
        "magic": {"foreground": light_fg},
        "stdin": {"foreground": "Blue"},
        "stdout": {"foreground": "Black"},
        "stderr": {"foreground": "Red"},
        "value": {"foreground": "DarkBlue"},
        "hyperlink": {"foreground": "#3A66DD", "underline": True},
        # paren matcher
        "surrounding_parens": {"foreground": "Blue", "font": "BoldEditorFont"},
        "unclosed_expression": {"background": "LightGray"},
        # find/replace
        "found": {"foreground": "blue", "underline": True},
        "current_found": {"foreground": "white", "background": "red"},
        "matched_name": {"background": "#e6ecfe"},
        "local_name": {"font": "ItalicEditorFont"},
        # debugger
        "active_focus": {"background": "#F8FC9A", "borderwidth": 1, "relief": "solid"},
        "suspended_focus": {"background": "", "borderwidth": 1, "relief": "solid"},
        "completed_focus": {
            "background": "#BBEDB2",
            "borderwidth": 1,
            "relief": "flat",
        },
        "exception_focus": {
            "background": "#FFBFD6",
            "borderwidth": 1,
            "relief": "solid",
        },
        "expression_box": {"background": "#DCEDF2", "foreground": default_fg},
        
        "black_fg" : {"foreground" : "#0c0c0c"},
        "black_bg" : {"background" : "#0c0c0c"},
        "bright_black_fg" : {"foreground" : "#767676"},
        "bright_black_bg" : {"background" : "#767676"},
        "dim_black_fg" : {"foreground" : "#000000"},
        "dim_black_bg" : {"background" : "#000000"},
        
        "red_fg" : {"foreground" : "#c50f1f"},
        "red_bg" : {"background" : "#c50f1f"},
        "bright_red_fg" : {"foreground" : "#e74856"},
        "bright_red_bg" : {"background" : "#e74856"},
        "dim_red_fg" : {"foreground" : "#9d0c18"},
        "dim_red_bg" : {"background" : "#9d0c18"},
        
        "green_fg" : {"foreground" : "#13a10e"},
        "green_bg" : {"background" : "#13a10e"},
        "bright_green_fg" : {"foreground" : "#16c60c"},
        "bright_green_bg" : {"background" : "#16c60c"},
        "dim_green_fg" : {"foreground" : "#0f800b"},
        "dim_green_bg" : {"background" : "#0f800b"},
        
        "yellow_fg" : {"foreground" : "#c19c00"},
        "yellow_bg" : {"background" : "#c19c00"},
        "bright_yellow_fg" : {"foreground" : "#f9f1a5"},
        "bright_yellow_bg" : {"background" : "#f9f1a5"},
        "dim_yellow_fg" : {"foreground" : "#9a7c00"},
        "dim_yellow_bg" : {"background" : "#9a7c00"},
        
        "blue_fg" : {"foreground" : "#0037da"},
        "blue_bg" : {"background" : "#0037da"},
        "bright_blue_fg" : {"foreground" : "#3b78ff"},
        "bright_blue_bg" : {"background" : "#3b78ff"},
        "dim_blue_fg" : {"foreground" : "#002cae"},
        "dim_blue_bg" : {"background" : "#002cae"},
        
        "magenta_fg" : {"foreground" : "#881798"},
        "magenta_bg" : {"background" : "#881798"},
        "bright_magenta_fg" : {"foreground" : "#b4009e"},
        "bright_magenta_bg" : {"background" : "#b4009e"},
        "dim_magenta_fg" : {"foreground" : "#6c1279"},
        "dim_magenta_bg" : {"background" : "#6c1279"},
        
        "cyan_fg" : {"foreground" : "#3a96dd"},
        "cyan_bg" : {"background" : "#3a96dd"},
        "bright_cyan_fg" : {"foreground" : "#61d6d6"},
        "bright_cyan_bg" : {"background" : "#61d6d6"},
        "dim_cyan_fg" : {"foreground" : "#2e78b0"},
        "dim_cyan_bg" : {"background" : "#2e78b0"},
        
        "white_fg" : {"foreground" : "#cccccc"},
        "white_bg" : {"background" : "#cccccc"},
        "bright_white_fg" : {"foreground" : "#f2f2f2"},
        "bright_white_bg" : {"background" : "#f2f2f2"},
        "dim_white_fg" : {"foreground" : "#a3a3a3"},
        "dim_white_bg" : {"background" : "#a3a3a3"},
        
        "fore_fg" : {"foreground" : default_fg},
        "fore_bg" : {"background" : default_fg},
        "bright_fore_fg" : {"foreground" : "#ffffff"},
        "bright_fore_bg" : {"background" : "#ffffff"},
        "dim_fore_fg" : {"foreground" : "#e0e0e0"},
        "dim_fore_bg" : {"background" : "#e0e0e0"},
        
        "back_fg" : {"foreground" : default_bg},
        "back_bg" : {"background" : default_bg},
        "bright_back_fg" : {"foreground" : "#000000"},
        "bright_back_bg" : {"background" : "#000000"},
        "dim_back_fg" : {"foreground" : "#222222"},
        "dim_back_bg" : {"background" : "#222222"},
        
        "intense" : {"font": "BoldEditorFont"}
    }


def default_dark() -> SyntaxThemeSettings:
    default_fg = "#B3B3B3"
    default_bg = "#2d2d2d"
    string_fg = "#8DC76F"
    open_string_bg = "#224533"

    # s.configure("Local.Code", foreground="#BCCAE8")
    # s.configure("MatchedName.Code", background="#193022")

    return {
        "TEXT": {
            "foreground": default_fg,
            "insertbackground": default_fg,
            "background": default_bg,
        },
        "GUTTER": {"foreground": "#606060", "background": "#323232"},
        "breakpoint": {"foreground": "pink"},
        "current_line": {"background": "#363636"},
        "sel": {"foreground": "#eeeeee", "background": "#6E6E6E"},
        "definition": {"foreground": default_fg},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg, "background": open_string_bg},
        "open_string3": {"foreground": string_fg, "background": open_string_bg},
        "builtin": {"foreground": "#A9B1C9"},
        "keyword": {"foreground": "#A9B1C9", "font": "BoldEditorFont"},
        "number": {"foreground": "#FFCABF"},
        "comment": {"foreground": "#D4D44E"},
        # shell
        "prompt": {"foreground": "#5BEBBB", "font": "BoldEditorFont"},
        "magic": {"foreground": "pink"},
        "stdin": {"foreground": "LightBlue"},
        "stdout": {"foreground": "LightGray"},
        "stderr": {"foreground": "#EB5B83"},
        "value": {"foreground": "#EBEB5B"},
        "hyperlink": {"foreground": "#619DC7", "underline": True},
        # paren matcher
        "surrounding_parens": {"foreground": "#F0995B", "font": "BoldEditorFont"},
        "unclosed_expression": {"background": "#000000"},
        # find/replace
        "found": {"underline": True},
        "current_found": {"foreground": "white", "background": "red"},
        "matched_name": {"background": "#474747"},
        "local_name": {"font": "ItalicEditorFont"},
        # debugger
        "active_focus": {"background": "#807238", "borderwidth": 1, "relief": "solid"},
        "suspended_focus": {"background": "", "borderwidth": 1, "relief": "solid"},
        "completed_focus": {
            "background": "#807238",
            "borderwidth": 1,
            "relief": "flat",
        },
        "exception_focus": {
            "background": "#FFBFD6",
            "borderwidth": 1,
            "relief": "solid",
        },
        "expression_box": {"background": "#506E67", "foreground": default_fg},
        
        "black_fg" : {"foreground" : "#0c0c0c"},
        "black_bg" : {"background" : "#0c0c0c"},
        "bright_black_fg" : {"foreground" : "#767676"},
        "bright_black_bg" : {"background" : "#767676"},
        "dim_black_fg" : {"foreground" : "#000000"},
        "dim_black_bg" : {"background" : "#000000"},
        
        "red_fg" : {"foreground" : "#c50f1f"},
        "red_bg" : {"background" : "#c50f1f"},
        "bright_red_fg" : {"foreground" : "#e74856"},
        "bright_red_bg" : {"background" : "#e74856"},
        "dim_red_fg" : {"foreground" : "#9d0c18"},
        "dim_red_bg" : {"background" : "#9d0c18"},
        
        "green_fg" : {"foreground" : "#13a10e"},
        "green_bg" : {"background" : "#13a10e"},
        "bright_green_fg" : {"foreground" : "#16c60c"},
        "bright_green_bg" : {"background" : "#16c60c"},
        "dim_green_fg" : {"foreground" : "#0f800b"},
        "dim_green_bg" : {"background" : "#0f800b"},
        
        "yellow_fg" : {"foreground" : "#c19c00"},
        "yellow_bg" : {"background" : "#c19c00"},
        "bright_yellow_fg" : {"foreground" : "#f9f1a5"},
        "bright_yellow_bg" : {"background" : "#f9f1a5"},
        "dim_yellow_fg" : {"foreground" : "#9a7c00"},
        "dim_yellow_bg" : {"background" : "#9a7c00"},
        
        "blue_fg" : {"foreground" : "#0037da"},
        "blue_bg" : {"background" : "#0037da"},
        "bright_blue_fg" : {"foreground" : "#3b78ff"},
        "bright_blue_bg" : {"background" : "#3b78ff"},
        "dim_blue_fg" : {"foreground" : "#002cae"},
        "dim_blue_bg" : {"background" : "#002cae"},
        
        "magenta_fg" : {"foreground" : "#881798"},
        "magenta_bg" : {"background" : "#881798"},
        "bright_magenta_fg" : {"foreground" : "#b4009e"},
        "bright_magenta_bg" : {"background" : "#b4009e"},
        "dim_magenta_fg" : {"foreground" : "#6c1279"},
        "dim_magenta_bg" : {"background" : "#6c1279"},
        
        "cyan_fg" : {"foreground" : "#3a96dd"},
        "cyan_bg" : {"background" : "#3a96dd"},
        "bright_cyan_fg" : {"foreground" : "#61d6d6"},
        "bright_cyan_bg" : {"background" : "#61d6d6"},
        "dim_cyan_fg" : {"foreground" : "#2e78b0"},
        "dim_cyan_bg" : {"background" : "#2e78b0"},
        
        "white_fg" : {"foreground" : "#cccccc"},
        "white_bg" : {"background" : "#cccccc"},
        "bright_white_fg" : {"foreground" : "#f2f2f2"},
        "bright_white_bg" : {"background" : "#f2f2f2"},
        "dim_white_fg" : {"foreground" : "#a3a3a3"},
        "dim_white_bg" : {"background" : "#a3a3a3"},
        
        "default_fg" : {"foreground" : default_fg},
        "default_bg" : {"background" : default_bg},
        "bright_default_fg" : {"foreground" : "#000000"},
        "bright_default_bg" : {"background" : "#ffffff"},
        "dim_default_fg" : {"foreground" : "#222222"},
        "dim_default_bg" : {"background" : "#e0e0e0"},
        
        "intense" : {"font": "BoldEditorFont"}
    }


def default_dark_green() -> SyntaxThemeSettings:
    open_string_bg = "#453B22"

    return {
        "TEXT": {"background": "#273627"},
        "GUTTER": {"background": "#33402F"},
        "current_line": {"background": "#2E402E"},
        "sel": {"background": "#6E6E6E"},
        "unclosed_expression": {"background": "#0F1F15"},
        "open_string": {"background": open_string_bg},
        "open_string3": {"background": open_string_bg},
        "keyword": {"foreground": "#88CFB6", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#88CFB6"},
        # debugger
        "active_focus": {"background": "#807238"},
        "completed_focus": {"background": "#807238"},
        "exception_focus": {"background": "#FFBFD6"},
        "expression_box": {"background": "#506E67"},
    }


def default_dark_blue() -> SyntaxThemeSettings:
    open_string_bg = "#224533"
    return {
        "TEXT": {"background": "#272936"},
        "GUTTER": {"background": "#2F3640"},
        "current_line": {"background": "#2D3040"},
        "sel": {"background": "#6E6E6E"},
        "unclosed_expression": {"background": "#100B21"},
        "open_string": {"background": open_string_bg},
        "open_string3": {"background": open_string_bg},
        "keyword": {"foreground": "#8899CF", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#8899CF"},
        # debugger
        "active_focus": {"background": "#807238"},
        "completed_focus": {"background": "#807238"},
        "exception_focus": {"background": "#FFBFD6"},
        "expression_box": {"background": "#506E67"},
    }


def idle_classic() -> SyntaxThemeSettings:
    string_fg = "#00aa00"
    return {
        "TEXT": {
            "foreground": "black",
            "insertbackground": "black",
            "background": "white",
        },
        "GUTTER": {"foreground": "gray", "background": "#efefef"},
        "sel": {"foreground": "black", "background": "gray"},
        "number": {"foreground": "black"},
        "definition": {"foreground": "#0000ff", "font": "EditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg},
        "open_string3": {"foreground": string_fg},
        "keyword": {"foreground": "#ff7700", "font": "EditorFont"},
        "builtin": {"foreground": "#900090"},
        "comment": {"foreground": "#dd0000"},
        "prompt": {"foreground": "#770000"},
        "stdin": {"foreground": "black"},
        "stdout": {"foreground": "Blue"},
        "value": {"foreground": "Blue"},
        "stderr": {"foreground": "Red"},
        "found": {"foreground": "", "underline": True},
        "current_found": {"foreground": "white", "background": "black"},
    }


def idle_dark() -> SyntaxThemeSettings:
    normal_fg = "white"
    string_fg = "#02ff02"

    return {
        "TEXT": {
            "foreground": normal_fg,
            "insertbackground": normal_fg,
            "background": "#002240",
        },
        "sel": {"foreground": "#FFFFFF", "background": "#7e7e7e"},
        "number": {"foreground": normal_fg},
        "definition": {"foreground": "#5e5eff", "font": "EditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg},
        "open_string3": {"foreground": string_fg},
        "keyword": {"foreground": "#ff8000", "font": "EditorFont"},
        "builtin": {"foreground": "#ff00ff"},
        "comment": {"foreground": "#dd0000"},
        "prompt": {"foreground": "#ff4d4d"},
        "stdin": {"foreground": normal_fg},
        "stdout": {"foreground": "#c2d1fa"},
        "value": {"foreground": "#c2d1fa"},
        "stderr": {"foreground": "#ffb3b3"},
        "found": {"foreground": "", "underline": True},
        "current_found": {"foreground": "#002240", "background": "#fbfbfb"},
    }


def desert_sunset() -> SyntaxThemeSettings:
    normal_fg = "#f0e68c"
    string_fg = "#ffa0a0"

    return {
        "TEXT": {
            "foreground": normal_fg,
            "insertbackground": normal_fg,
            "background": "#333333",
        },
        "GUTTER": {"foreground": "gray", "background": "#404040"},
        "sel": {"foreground": "#000000", "background": "gray"},
        "number": {"foreground": normal_fg},
        "definition": {"foreground": "#98fb98"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg},
        "open_string3": {"foreground": string_fg},
        "keyword": {"foreground": "#cc6600"},
        "builtin": {"foreground": "#519e51"},
        "comment": {"foreground": "#87ceeb"},
        "prompt": {"foreground": "#87ceeb"},
        "stdin": {"foreground": normal_fg},
        "stdout": {"foreground": "#eeeeee"},
        "value": {"foreground": "#eeeeee"},
        "stderr": {"foreground": "#ff595b"},
        "found": {"foreground": "", "underline": True},
        "current_found": {"foreground": "#ffffff", "background": "#333333"},
    }


def zenburn() -> SyntaxThemeSettings:
    # https://github.com/mig/gedit-themes/blob/master/zenburn.xml
    # https://github.com/trusktr/gedit-color-schemes/blob/master/gtksourceview-3.0/styles/zenburn.xml
    normal_fg = "#dcdccc"
    string_fg = "#cc9393"

    return {
        "TEXT": {
            "foreground": normal_fg,
            "insertbackground": normal_fg,
            "background": "#3f3f3f",
        },
        "GUTTER": {"foreground": "#7f8f8f", "background": "#464646"},
        "current_line": {"background": "#4A4A4A"},
        "sel": {"foreground": "white", "background": "#506070"},
        "number": {"foreground": "#8cd0d3"},
        "definition": {"foreground": "#f4a020", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg},
        "open_string3": {"foreground": string_fg},
        "keyword": {"foreground": "#f0dfaf", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#efef8f"},
        "comment": {"foreground": "#7f9f7f"},
        "prompt": {"foreground": "#87ceeb"},
        "stdin": {"foreground": normal_fg},
        "stdout": {"foreground": "#eeeeee"},
        "value": {"foreground": "#eeeeee"},
        "stderr": {"foreground": "#ff3e40"},
        # paren matcher
        "surrounding_parens": {"foreground": "white", "font": "BoldEditorFont"},
    }


def load_plugin() -> None:
    get_workbench().add_syntax_theme("Default Light", None, default_light)
    get_workbench().add_syntax_theme("Default Dark", None, default_dark)
    get_workbench().add_syntax_theme(
        "Default Dark Green", "Default Dark", default_dark_green
    )
    get_workbench().add_syntax_theme(
        "Default Dark Blue", "Default Dark", default_dark_blue
    )
    get_workbench().add_syntax_theme("Desert Sunset", "Default Dark", desert_sunset)
    get_workbench().add_syntax_theme("Zenburn", "Default Dark", zenburn)
    get_workbench().add_syntax_theme("IDLE Classic", "Default Light", idle_classic)

    # Comments in IDLE Dark really hurt the eyes
    # get_workbench().add_syntax_theme("IDLE Dark", "Default Dark", idle_dark)

    get_workbench().set_default("view.syntax_theme", "Default Light")
