import os.path
import platform
import subprocess

from thonny import get_workbench
from thonny.languages import tr
from thonny.ui_utils import select_sequence


def print_current_script():
    editor = _get_current_editor()
    assert editor is not None

    template_fn = os.path.join(os.path.dirname(__file__), "template.html")
    with open(template_fn, encoding="utf-8") as f:
        template_html = f.read()

    script_html = _export_text_as_html(editor.get_text_widget())
    title_html = escape_html(editor.get_title())
    full_html = template_html.replace("%title%", title_html).replace("%script%", script_html)

    import tempfile

    temp_handle, temp_fn = tempfile.mkstemp(
        suffix=".html", prefix="thonny_", dir=get_workbench().get_temp_dir()
    )
    with os.fdopen(temp_handle, "w", encoding="utf-8") as f:
        f.write(full_html)

    if platform.system() == "Darwin":
        subprocess.Popen(["open", temp_fn])
    else:
        import webbrowser

        webbrowser.open(temp_fn)


def can_print_current_script():
    return _get_current_editor() is not None


def _export_text_as_html(text):
    last_line = int(float(text.index("end-1c")))
    result = ""
    for i in range(1, last_line + 1):
        result += "<code>" + _export_line_as_html(text, i) + "</code>\n"
    return result


def _export_line_as_html(text, lineno):
    s = text.get("%d.0" % lineno, "%d.0 lineend" % lineno).strip("\r\n")

    parts = []
    for i in range(len(s)):
        tag_names = text.tag_names("%d.%d" % (lineno, i))
        if not parts or parts[-1][1] != tag_names:
            parts.append([s[i], tag_names])
        else:
            parts[-1][0] += s[i]

    # print(lineno, parts)
    result = ""
    for s, tags in parts:
        if tags:
            result += "<span class='%s'>%s</span>" % (" ".join(tags), escape_html(s))
        else:
            result += escape_html(s)

    return result


def escape_html(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _get_current_editor():
    return get_workbench().get_editor_notebook().get_current_editor()


def load_plugin():
    get_workbench().add_command(
        "printcurrent",
        "file",
        tr("Print..."),
        print_current_script,
        can_print_current_script,
        default_sequence=select_sequence("<Control-p>", "<Command-p>"),
        extra_sequences=["<Control-Greek_pi>"],
        group=11,
    )
