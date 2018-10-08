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
    }


def default_dark() -> SyntaxThemeSettings:
    default_fg = "#B3B3B3"
    string_fg = "#8DC76F"
    open_string_bg = "#224533"

    # s.configure("Local.Code", foreground="#BCCAE8")
    # s.configure("MatchedName.Code", background="#193022")

    return {
        "TEXT": {
            "foreground": default_fg,
            "insertbackground": default_fg,
            "background": "#2d2d2d",
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
        "stderr": {"foreground": "#ff3e40"},
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
