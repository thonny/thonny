from thonny import get_workbench
from thonny.workbench import SyntaxThemeSettings


def tomorrow() -> SyntaxThemeSettings:
    # https://github.com/chriskempson/tomorrow-theme/blob/master/GEdit/Tomorrow.xml
    normal_fg = "#4D4D4C"
    string_fg = "#718C00"

    return {
        "TEXT": {"foreground": normal_fg, "insertbackground": normal_fg, "background": "#FFFFFF"},
        "GUTTER": {"foreground": "#4d4d4c", "background": "#efefef"},
        "current_line": {"background": "#efefef"},
        "sel": {"foreground": "#4D4D4C", "background": "#D6D6D6"},
        "number": {"foreground": "#718c00"},
        "definition": {"foreground": "#4271AE", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string_fg},
        "open_string3": {"foreground": string_fg},
        "keyword": {"foreground": "#8959A8", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#4271ae"},
        "comment": {"foreground": "#8E908C"},
    }


def tomorrow_night() -> SyntaxThemeSettings:
    # https://github.com/chriskempson/tomorrow-theme/blob/master/GEdit/Tomorrow-Night.xml
    normal_fg = "#c5c8c6"
    string_fg = "#b5bd68"
    string3_fg = string_fg

    return {
        "TEXT": {"foreground": normal_fg, "insertbackground": normal_fg, "background": "#1d1f21"},
        "GUTTER": {"foreground": "#c5c8c6", "background": "#282a2e"},
        "sel": {"foreground": "#c5c8c6", "background": "#373b41"},
        "current_line": {"background": "#282a2e"},
        "number": {"foreground": "#de935f"},
        "definition": {"foreground": "#81a2be", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string3_fg},
        "open_string3": {"foreground": string3_fg},
        "keyword": {"foreground": "#b294bb", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#81a2be"},
        "comment": {"foreground": "#969896"},
        # paren matcher
        "surrounding_parens": {
            "background": "#373b41",
            "foreground": "white",
            "font": "BoldEditorFont",
        },
    }


def tomorrow_night_blue() -> SyntaxThemeSettings:
    # https://github.com/chriskempson/tomorrow-theme/blob/master/GEdit/Tomorrow-Night-Blue.xml
    normal_fg = "#ffffff"
    string_fg = "#d1f1a9"
    string3_fg = string_fg

    return {
        "TEXT": {"foreground": normal_fg, "insertbackground": normal_fg, "background": "#002451"},
        "GUTTER": {"foreground": "#ffffff", "background": "#00346e"},
        "sel": {"foreground": "#ffffff", "background": "#003f8e"},
        "current_line": {"background": "#00346e"},
        "number": {"foreground": "#ffc58f"},
        "definition": {"foreground": "#bbdaff", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string3_fg},
        "open_string3": {"foreground": string3_fg},
        "keyword": {"foreground": "#ebbbff", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#bbdaff"},
        "comment": {"foreground": "#7285b7"},
        # paren matcher
        "surrounding_parens": {
            "background": "#00346e",
            "foreground": "white",
            "font": "BoldEditorFont",
        },
    }


def tomorrow_night_bright() -> SyntaxThemeSettings:
    # https://github.com/chriskempson/tomorrow-theme/blob/master/GEdit/Tomorrow-Night-Bright.xml
    normal_fg = "#dedede"
    string_fg = "#b9ca4a"
    string3_fg = string_fg

    return {
        "TEXT": {"foreground": normal_fg, "insertbackground": normal_fg, "background": "#000000"},
        "GUTTER": {"foreground": "#dedede", "background": "#2a2a2a"},
        "current_line": {"background": "#2a2a2a"},
        "sel": {"foreground": "#dedede", "background": "#424242"},
        "number": {"foreground": "#e78c45"},
        "definition": {"foreground": "#7aa6da", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string3_fg},
        "open_string3": {"foreground": string3_fg},
        "keyword": {"foreground": "#c397d8", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#7aa6da"},
        "comment": {"foreground": "#969896"},
        # paren matcher
        "surrounding_parens": {
            "background": "#2a2a2a",
            "foreground": "white",
            "font": "BoldEditorFont",
        },
    }


def tomorrow_night_eighties() -> SyntaxThemeSettings:
    # https://github.com/chriskempson/tomorrow-theme/blob/master/GEdit/Tomorrow-Night-Eighties.xml
    normal_fg = "#cccccc"
    string_fg = "#99cc99"
    string3_fg = string_fg

    return {
        "TEXT": {"foreground": normal_fg, "insertbackground": normal_fg, "background": "#2d2d2d"},
        "GUTTER": {"foreground": "#cccccc", "background": "#393939"},
        "current_line": {"background": "#393939"},
        "sel": {"foreground": "#cccccc", "background": "#515151"},
        "number": {"foreground": "#f99157"},
        "definition": {"foreground": "#6699cc", "font": "BoldEditorFont"},
        "string": {"foreground": string_fg},
        "string3": {"foreground": string_fg},
        "open_string": {"foreground": string3_fg},
        "open_string3": {"foreground": string3_fg},
        "keyword": {"foreground": "#cc99cc", "font": "BoldEditorFont"},
        "builtin": {"foreground": "#6699cc"},
        "comment": {"foreground": "#999999"},
        # paren matcher
        "surrounding_parens": {
            "background": "#393939",
            "foreground": "white",
            "font": "BoldEditorFont",
        },
    }


def load_plugin() -> None:
    get_workbench().add_syntax_theme("Tomorrow", "Default Light", tomorrow)
    get_workbench().add_syntax_theme("Tomorrow Night", "Default Dark", tomorrow_night)
    get_workbench().add_syntax_theme("Tomorrow Night Blue", "Tomorrow Night", tomorrow_night_blue)
    get_workbench().add_syntax_theme(
        "Tomorrow Night Bright", "Tomorrow Night", tomorrow_night_bright
    )
    get_workbench().add_syntax_theme(
        "Tomorrow Night Eighties", "Tomorrow Night", tomorrow_night_eighties()
    )

    get_workbench().set_default("view.syntax_theme", "Default Light")
