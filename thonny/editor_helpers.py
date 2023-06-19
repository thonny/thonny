import tkinter as tk
import traceback
from logging import getLogger
from typing import List, Optional, Tuple

from thonny import get_workbench
from thonny.codeview import CodeViewText, SyntaxText, get_syntax_options_for_tag
from thonny.common import SignatureInfo, SignatureParameter
from thonny.editors import Editor
from thonny.misc_utils import running_on_mac_os
from thonny.shell import ShellText
from thonny.tktextext import TextFrame
from thonny.ui_utils import get_tk_version_info

all_boxes = []

a_box_is_appearing = False

logger = getLogger(__name__)


class EditorInfoBox(tk.Toplevel):
    def __init__(self):
        super().__init__(master=get_workbench())
        self._has_shown_on_screen: bool = False
        all_boxes.append(self)
        self._target_text_widget: Optional[SyntaxText] = None

        get_workbench().bind("<FocusOut>", self._workbench_focus_out, True)

        # If the box has received focus, then it may lose it by a messagebox
        # or mouse click on the main window
        self.bind("<FocusOut>", self._workbench_focus_out, True)

        get_workbench().bind("<Escape>", self.hide, True)
        self.bind("<Escape>", self.hide, True)
        get_workbench().bind_class("EditorCodeViewText", "<1>", self.hide, True)
        get_workbench().bind_class("ShellText", "<1>", self.hide, True)

        get_workbench().bind("SyntaxThemeChanged", self._update_theme, True)

    def _set_window_attributes(self):
        if running_on_mac_os():
            try:
                # Must be the first thing to do after creating window
                # https://wiki.tcl-lang.org/page/MacWindowStyle
                self.tk.call(
                    "::tk::unsupported::MacWindowStyle", "style", self._w, "help", "noActivates"
                )
                if get_tk_version_info() >= (8, 6, 10) and running_on_mac_os():
                    self.wm_overrideredirect(1)
            except tk.TclError:
                pass
        else:
            self.wm_overrideredirect(1)
        self.wm_transient(get_workbench())

        # From IDLE
        # TODO: self.update_idletasks()  # Need for tk8.6.8 on macOS: #40128.
        self.lift()

    def _update_theme(self, event=None):
        pass

    def _check_bind_for_keypress(self, text: tk.Text):
        tag_prefix = "pb_" + type(self).__name__.replace(".", "_")
        if getattr(text, tag_prefix, False):
            return False

        # Need to know about certain keypresses while the completer is active
        # Other plugins (eg. auto indenter) may eat up returns, therefore I need to
        # raise the priority of this binding
        tag = tag_prefix + "_" + str(text.winfo_id())
        text.bindtags((tag,) + text.bindtags())
        text.bind_class(tag, "<Key>", self._on_text_keypress, True)

        setattr(text, tag_prefix, True)

    def _on_text_keypress(self, event=None):
        pass

    def _workbench_focus_out(self, event=None) -> None:
        if not self.is_visible():
            return

        # if a_box_is_appearing:
        # making a box appear may mess up FocusOut events
        #    return

        # Need to close when another app or a Thonny's dialog appears
        # (othewise the box will float above this, at least in Linux).
        # Don't do anything if another EditorInfoBox appears
        for box in all_boxes:
            try:
                # need to try because asking for focus via wrong window may give exception
                if box.focus_get():
                    # it's alright
                    return
            except:
                pass

        self.hide()

    def _get_related_box(self) -> Optional["EditorInfoBox"]:
        return None

    def _show_on_target_text(
        self,
        index: str,
        expected_box_height: int,
        preferred_position: str,
        y_offset: int = 0,
    ) -> None:
        text = self._target_text_widget

        bbox = text.bbox(index)
        if not bbox:
            logger.warning("Could not compute bbox")
            return

        text_box_x, text_box_y, _, text_box_height = bbox

        cursor_root_x = text.winfo_rootx() + text_box_x
        cursor_root_y = text.winfo_rooty() + text_box_y

        if (
            preferred_position == "below"
            and cursor_root_y + text_box_height + expected_box_height > text.winfo_screenheight()
        ):
            position = "above"
        else:
            position = preferred_position

        if position == "above":
            # negative value signifies pixels between window bottom and screen bottom
            y = cursor_root_y - text.winfo_screenheight()
        else:
            y = cursor_root_y + text_box_height

        # TODO reduce x if the box wouldn't fit by width
        x = cursor_root_x
        self._show_on_screen(x, y + y_offset)

    def _show_on_screen(self, x: int, y: int) -> None:
        global a_box_is_appearing
        if a_box_is_appearing:
            logger.debug("Box already appearing, skipping _show_on_screen")
            return

        try:
            a_box_is_appearing = True

            if y < 0:
                self.geometry("+%d-%d" % (x, -y))
            else:
                self.geometry("+%d+%d" % (x, y))

            if not self.winfo_ismapped():
                self._set_window_attributes()
                self._check_update_size()
                self.deiconify()
                if not self._has_shown_on_screen:
                    self.tweak_first_appearance()
            else:
                self._check_update_size()
        finally:
            a_box_is_appearing = False

        self._has_shown_on_screen = True

    def _check_update_size(self) -> None:
        if hasattr(self, "_update_size"):
            # It looks it's not worth trying to move the window away from the viewport
            # for calculations. At least in Ubuntu it doesn't give any advantages and
            # may produce glitches
            # self.geometry("+10000+5000")  # move away from visible screen
            # self.withdraw()

            self.update()  # gives proper data for size calculations
            self._update_size()
            self.update()  # applies updated size

    def hide(self, event: Optional[tk.Event] = None) -> None:
        if self.winfo_ismapped():
            self.withdraw()

        related_box = self._get_related_box()
        if related_box and related_box.is_visible():
            related_box.hide(event)

        # Following looks like a good idea, but in at least in Ubuntu, it would fix
        # entry cursor to the given text and it can't be moved to another text anymore
        # if self._target_text_widget:
        #    self._target_text_widget.focus_set()  # in case the user has clicked on the box

    def is_visible(self) -> bool:
        return self.winfo_ismapped()

    def tweak_first_appearance(self):
        pass


class DocuBoxBase(EditorInfoBox):
    def __init__(self, show_vertical_scrollbar: bool):
        super().__init__()
        self.text_frame = TextFrame(
            master=self,
            horizontal_scrollbar=False,
            vertical_scrollbar=show_vertical_scrollbar,
            read_only=True,
            height=7,
            width=40,
            font="TkDefaultFont",
            wrap="word",
        )
        self.text_frame.grid()
        self.text = self.text_frame.text

        self._update_theme()

    def _update_theme(self, event=None):
        super()._update_theme(event)
        comment_opts = get_syntax_options_for_tag("comment")
        gutter_opts = get_syntax_options_for_tag("GUTTER")
        text_opts = get_syntax_options_for_tag("TEXT")
        self.text["background"] = gutter_opts["background"]
        self.text["foreground"] = text_opts["foreground"]
        self.text.tag_configure("prose", font="TkDefaultFont")
        self.text.tag_configure("active", font="BoldTkDefaultFont")
        self.text.tag_configure("annotation", **comment_opts)
        self.text.tag_configure("default", **comment_opts)
        self.text.tag_configure("marker", **comment_opts)

    def _append_chars(self, chars, tags=()):
        self.text.direct_insert("end", chars, tags=tuple(tags))

    def render_signatures(self, signatures: List[SignatureInfo], only_params=False) -> None:
        for i, sig in enumerate(signatures):
            if i > 0:
                self._append_chars("\n")
            self.render_signature(sig, only_params)

    def render_signature(self, sig: SignatureInfo, only_params) -> None:
        if not only_params:
            self._append_chars(sig.name)

        self._append_chars("(")

        is_positional = False
        is_kw_only = False

        for i, param in enumerate(sig.params):
            if i > 0:
                self._append_chars(", ")
            if len(sig.params) > 20:
                self._append_chars("\n    ")

            is_positional |= param.kind == "POSITIONAL_ONLY"
            if is_positional and param.kind != "POSITIONAL_ONLY":
                self._append_chars("/, ", ["marker"])
                is_positional = False

            if param.kind == "VAR_POSITIONAL":
                is_kw_only = True
            elif param.kind == "KEYWORD_ONLY" and not is_kw_only:
                self._append_chars("*, ", ["marker"])
                is_kw_only = True

            is_active_parameter = sig.current_param_index == i
            self.render_parameter(param, is_active_parameter)

        if is_positional:
            self._append_chars(", /", ["marker"])

        self._append_chars(")")

        if sig.return_type and not only_params:
            self._append_chars(" -> ", ["marker"])
            self._append_chars(sig.return_type, ["annotation"])

    def render_parameter(self, param: SignatureParameter, active: bool) -> None:
        if active:
            base_tags = ["active"]
        else:
            base_tags = []

        if param.kind == "VAR_POSITIONAL":
            self._append_chars("*", base_tags)
        elif param.kind == "VAR_KEYWORD":
            self._append_chars("**", base_tags)

        self._append_chars(param.name, base_tags)

        if param.annotation:
            self._append_chars(":\u00A0" + param.annotation, base_tags + ["annotation"])

        if param.default:
            self._append_chars("=" + param.default, base_tags + ["default"])

    def format_signature(self, s: str) -> str:
        s = s.replace(": ", ":\u00A0")
        if len(s) > self.text["width"] * 1.8 and s.count("(") and s.count(")"):
            args_index = s.index("(") + 1
            suffix_index = s.rindex(")")
            prefix = s[:args_index]
            args = s[args_index:suffix_index].split(", ")
            suffix = s[suffix_index:]
            s = prefix + "\n  " + ",\n  ".join(args) + "\n" + suffix
            # don't keep / and * alone on a line
            s = (
                s.replace("\n  /,", " /,")
                .replace("\n  *,", " *,")
                .replace("\n  /\n)", " /\n)")
                .replace("\n  *\n)", " *\n)")
            )
            return s
        else:
            return s


class DocuBox(DocuBoxBase):
    def __init__(self):
        super().__init__(show_vertical_scrollbar=True)

    def set_content(self, name, item_type, signatures, docstring):
        self.text.direct_delete("1.0", "end")

        # self._append_chars(item_type + "\n")

        if signatures:
            self.render_signatures(signatures)

        if signatures and docstring:
            self._append_chars("\n\n")

        if docstring:
            self._append_chars(docstring, ["prose"])


def get_active_text_widget() -> Optional[SyntaxText]:
    widget = get_workbench().focus_get()
    if isinstance(widget, (CodeViewText, ShellText)):
        return widget

    return None


def get_cursor_position(text: SyntaxText) -> Tuple[int, int]:
    parts = text.index("insert").split(".")
    return int(parts[0]), int(parts[1])


def get_text_filename(text: SyntaxText) -> Optional[str]:
    if isinstance(text, ShellText):
        return "<Shell>"
    elif isinstance(text, CodeViewText):
        editor = getattr(text.master, "home_widget")
        if isinstance(editor, Editor):
            return editor.get_filename()

    return None


def get_relevant_source_and_cursor_position(text: SyntaxText) -> Tuple[str, int, int]:
    if isinstance(text, ShellText):
        source = text.get("input_start", "insert")
        lines = source.splitlines()
        if not lines:
            return source, 1, 0
        else:
            return source, len(lines), len(lines[-1])
    else:
        row, col = get_cursor_position(text)
        return text.get("1.0", "end-1c"), row, col
