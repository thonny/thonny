import tkinter as tk
from tkinter import ttk
import builtins
from typing import List, Optional, Union, Iterable, Tuple
from thonny import ui_utils, tktextext, get_workbench
from collections import namedtuple
import re
from thonny.codeview import get_syntax_options_for_tag

Suggestion = namedtuple("Suggestion", ["title", "general", "specific", "relevance"])

class AssistantView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(self, master, 
                                     horizontal_scrollbar=False,
                                     vertical_scrollbar=True,
                                     read_only=True,
                                     wrap="word",
                                     font="TkDefaultFont",
                                     cursor="arrow",
                                     insertwidth=0)
        self._error_helper_classes = {
            "NameError" : {NameErrorHelper}
        }
        
        self.text.tag_configure("error_title",
                                spacing3=5,
                                foreground=get_syntax_options_for_tag("stderr")["foreground"])
        self.text.tag_configure("intro", font="ItalicTkDefaultFont", spacing3=10)
        self.text.tag_configure("relevant_suggestion_title", font="BoldTkDefaultFont")
        self.text.tag_configure("suggestion_title", lmargin2=16, spacing1=5, spacing3=5)
        self.text.tag_configure("suggestion_body", lmargin1=16, lmargin2=16)
        self.text.tag_configure("specific", font="ItalicTkDefaultFont")
    
    def explain_exception(self, error_type_name, error_message,
                          frame_globals, frame_locals):
        "►▸˃✶ ▼▸▾"
        self._clear()
        self._append_text("%s: %s\n" % (error_type_name, error_message),
                          ("error_title",))
        
        if error_type_name not in self._error_helper_classes:
            self._append_text("No helpers for this error type")
        else:
            helpers = [helper_class(error_type_name, error_message,
                                    frame_globals, frame_locals)
                                    for helper_class in self._error_helper_classes[error_type_name]]
            # TODO: how to select the intro text?
            self._append_text(helpers[0].get_intro() + "\n", ("intro",))
            
            suggestions = [suggestion 
                           for helper in helpers
                           for suggestion in helper.get_suggestions()]
            
            for suggestion in sorted(suggestions, key=lambda s: s.relevance, reverse=True):
                self._append_suggestion(suggestion)
        
        
    def add_error_helper(self, error_type_name, helper_class):
        if error_type_name not in self._error_helper_classes:
            self._error_helper_classes[error_type_name] = []
        self._error_helper_classes[error_type_name].append(helper_class)
    
    def _append_text(self, chars, tags=()):
        self.text.direct_insert("end", chars, tags=tags)
    
    
    def _append_suggestion(self, suggestion):
        label = tk.Label(self.text,
                         image=get_workbench().get_image("boxplus"),
                         borderwidth=0,
                         background="white")
        
        def toggle_body(event=None):
            elide = self.text.tag_cget(body_id_tag, "elide")
            if elide == '1':
                elide = True
            elif elide == '0':
                elide = False
            else:
                elide = bool(elide)
            
            elide = not elide
            
            self.text.tag_configure(body_id_tag, elide=elide)
            if self.text.has_selection():
                self.text.tag_remove("sel", "1.0", "end")
            
            if elide:
                label.configure(image=get_workbench().get_image("boxplus"))
            else:
                label.configure(image=get_workbench().get_image("boxminus"))
                
        title_id_tag = "stitle_%d" % id(suggestion)
        body_id_tag = "sbody_%d" % id(suggestion)
        self.text.tag_configure(body_id_tag, elide=True)
        
        self.text.tag_bind(title_id_tag, "<1>", toggle_body, True)
        
        label.bind("<1>", toggle_body, True)
        
        title_tags = ("suggestion_title", title_id_tag)
        if suggestion.relevance > 5:
            title_tags += ("relevant_suggestion_title",)
        self._append_window(label, title_tags)
        #self._append_image("boxplus", ("suggestion_title", title_tag))
        self._append_text("" + suggestion.title + "\n", title_tags)
        
        if suggestion.general is not None:
            self._append_text(suggestion.general + "\n",
                              ("suggestion_body", body_id_tag))
        if suggestion.specific is not None:
            self._append_text(suggestion.specific + "\n",
                              ("specific", "suggestion_body", body_id_tag))
        # Spacer
        self._append_text("\n", ("suggestion_body", body_id_tag))
            
    
    def _append_window(self, window, tags=()):
        index = self.text.index("end-1c")
        self.text.window_create(index, window=window)
        for tag in tags:
            self.text.tag_add(tag, index)
            
    def _append_image(self, name, tags=()):
        index = self.text.index("end-1c")
        self.text.image_create(index, image=get_workbench().get_image(name))
        for tag in tags:
            self.text.tag_add(tag, index)
            
    
    def _clear(self):
        self.text.direct_delete("1.0", "end")

class Helper:
    def get_intro(self):
        raise NotImplementedError()
    
    def get_suggestions(self) -> Iterable[Suggestion]:
        raise NotImplementedError()

class DebugHelper(Helper):
    pass

class ErrorHelper(Helper):
    def __init__(self, error_type_name, error_message, 
                 frame_globals=None, frame_locals=None):
        
        self.error_type_name = error_type_name
        self.error_message = error_message
        self.frame_globals=frame_globals,
        self.frame_locals=frame_locals

class NameErrorHelper(ErrorHelper):
    def __init__(self, error_type_name, error_message, 
        frame_globals=None, frame_locals=None):
        
        super().__init__(error_type_name, error_message, 
                         frame_globals, frame_locals)
        
        names = re.findall(r"\'.*\'", error_message)
        assert len(names) == 1
        self.name = names[0].strip("'")
    
    def get_intro(self):
        return "Python doesn't know what `%s` stands for." % self.name
    
    def get_suggestions(self):
        return [
            # TODO: only when in suitable context for string
            Suggestion("Did you really mean a variable or you just forgot the quotes?",
                       'If you meant literal text "%s", then surround it with quotes.' % self.name,
                       None,
                       7),
            Suggestion("Did you spell it correctly? Everywhere?",
                       "Compare this name usage with the definition. Don't forget that case of the letters matters too.",
                       "Did you actually mean `liida`?",
                       8),
            Suggestion("Should this variable be imported?",
                       "Some functions/variables need to be imported before they can be used.",
                       # TODO: compare with names in popular modules
                       None,
                       2),
            Suggestion("Is the variable definition given before the usage?",
                       "...",
                       None,
                       2),
            Suggestion("Maybe Python skipped the definition part?",
                       "If your variable's definition is inside a if-statement or loop, then it may have been skipped.",
                       None,
                       2),
            Suggestion("Are you trying to acces a local variable outside of the function?",
                       "...",
                       None,
                       2),
        ]
    
