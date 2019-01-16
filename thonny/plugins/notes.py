import os.path
from thonny.tktextext import TextFrame
from thonny import get_workbench, ui_utils, THONNY_USER_DIR

class NotesView(TextFrame):
    def __init__(self, master):
        super().__init__(master,
                         horizontal_scrollbar_class=ui_utils.AutoScrollbar,
                         wrap="word")
        
        self.filename = os.path.join(THONNY_USER_DIR, "user_notes.txt") 
        self.load_content()
        
        get_workbench().bind("ToplevelResponse", self.save_content, True)
        
        
        
    def load_content(self):
        if not os.path.isfile(self.filename):
            self.text.insert("1.0",
                             "This box is meant for your working notes -- assignment instructions, "
                             + "code snippets, whatever.\n\n"
                             + "Everything will be saved automatically "
                             + "and loaded when you open Thonny next time.\n\n"
                             + "Feel free to delete this text to make room for your own notes.")
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
    get_workbench().add_view(NotesView, "Notes", "ne", default_position_key="zz")
    