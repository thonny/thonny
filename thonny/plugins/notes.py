import os.path

from thonny import THONNY_USER_DIR, get_workbench, ui_utils
from thonny.languages import tr
from thonny.tktextext import EnhancedText, TextFrame
from thonny.ui_utils import TextMenu


class NotesText(EnhancedText):
    def __init__(self, master, **kw):
        EnhancedText.__init__(self, master=master, wrap="word", undo=True, **kw)
        self.context_menu = TextMenu(self)

    def on_secondary_click(self, event=None):
        super().on_secondary_click(event=event)
        self.context_menu.tk_popup(event.x_root, event.y_root)


class NotesView(TextFrame):
    def __init__(self, master):
        self.filename = os.path.join(THONNY_USER_DIR, "user_notes.txt")
        super().__init__(
            master, text_class=NotesText, horizontal_scrollbar_class=ui_utils.AutoScrollbar
        )

        self.load_content()
        self.text.edit_reset()

        get_workbench().bind("ToplevelResponse", self.save_content, True)

    def load_content(self):
        if not os.path.isfile(self.filename):
            self.text.insert(
                "1.0",
                tr(
                    "This box is meant for your working notes -- assignment instructions, "
                    + "code snippets, whatever.\n\n"
                    + "Everything will be saved automatically "
                    + "and loaded when you open Thonny next time.\n\n"
                    + "Feel free to delete this text to make room for your own notes."
                ),
            )
            return

        with open(self.filename, encoding="utf-8") as fp:
            content = fp.read()

        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.mark_set("insert", "1.0")
        self.text.see("1.0")

    def save_content(self, event=None):
        with open(self.filename, "w", encoding="utf-8") as fp:
            fp.write(self.text.get("1.0", "end-1c"))

    def destroy(self):
        self.save_content()
        super().destroy()


def load_plugin():
    get_workbench().add_view(NotesView, tr("Notes"), "ne", default_position_key="zz")
