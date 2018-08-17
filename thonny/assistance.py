import tkinter as tk
from tkinter import ttk
import builtins
from typing import List, Optional, Union, Iterable, Tuple
from thonny import ui_utils, tktextext, get_workbench
from collections import namedtuple
import re
from thonny.codeview import get_syntax_options_for_tag
from thonny.common import ToplevelResponse
import ast
from thonny.misc_utils import levenshtein_distance

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
                                font="BoldTkDefaultFont",
                                #foreground=get_syntax_options_for_tag("stderr")["foreground"]
                                )
        self.text.tag_configure("intro", 
                                #font="ItalicTkDefaultFont", 
                                spacing3=10)
        self.text.tag_configure("relevant_suggestion_title", font="BoldTkDefaultFont")
        self.text.tag_configure("suggestion_title", lmargin2=16, spacing1=5, spacing3=5)
        self.text.tag_configure("suggestion_body", lmargin1=16, lmargin2=16)
        self.text.tag_configure("specific", font="ItalicTkDefaultFont")
        
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
    
    def _handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        if "user_exception" in msg:
            self.explain_exception(msg["user_exception"]["error_type_name"],
                                   msg["user_exception"]["error_message"],
                                   msg["user_exception"]["stack"])
    
    def explain_exception(self, error_type_name, error_message, stack):
        "►▸˃✶ ▼▸▾"
        self._clear()
        self._append_text("%s: %s\n" % (error_type_name, error_message),
                          ("error_title",))
        
        #if stack[-1].in_library:
        #    helpers = [LibraryErrorHelper(error_type_name, error_message, stack)]
        #else:
        if error_type_name not in self._error_helper_classes:
            self._append_text("No helpers for this error type")
            return
        else:
            helpers =[helper_class(error_type_name, error_message, stack)
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
        if suggestion.relevance > 0:
            title_tags += ("relevant_suggestion_title",)
        self._append_window(label, title_tags)
        #self._append_image("boxplus", ("suggestion_title", title_tag))
        self._append_text("" + suggestion.title + "\n", title_tags)
        
        if suggestion.general is not None:
            self._append_text(suggestion.general.strip() + "\n",
                              ("suggestion_body", body_id_tag))
        if suggestion.specific is not None:
            self._append_text(suggestion.specific.strip() + "\n",
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
    def __init__(self, error_type_name, error_message, stack=None):
        
        self.error_type_name = error_type_name
        self.error_message = error_message
        self.stack=stack
        
        self.last_frame = stack[-1]
        if self.last_frame.source:
            self.last_frame_ast = ast.parse(self.last_frame.source,
                                            self.last_frame.filename)
            self.last_frame_lines = self.last_frame.source.splitlines()
            print(self.last_frame.code_name, self.last_frame.lineno)
            self.last_frame_line = self.last_frame_lines[self.last_frame.lineno-1]
        else:
            self.last_frame_ast = None
            self.last_frame_lines = None
            self.last_frame_line = None
        
        

class LibraryErrorHelper(ErrorHelper):
    """Explains exceptions, which doesn't happen in user code"""
    
    def get_intro(self):
        return "This error happened in library code. This may mean a bug in "
    
    def get_suggestions(self):
        return []

class NameErrorHelper(ErrorHelper):
    def __init__(self, error_type_name, error_message, stack=None):
        
        super().__init__(error_type_name, error_message, stack)
        
        names = re.findall(r"\'.*\'", error_message)
        assert len(names) == 1
        self.name = names[0].strip("'")
    
    def get_intro(self):
        # TODO: add link to source
        return "Python doesn't know what `%s` stands for." % self.name
    
    def get_suggestions(self):
        
        return [
            self._bad_spelling(),
            self._missing_quotes(),
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
    
    def _missing_quotes(self):
        # TODO: only when in suitable context for string
        return Suggestion(
            "Did you really mean a variable or you just forgot the quotes?",
            'If you meant literal text "%s", then surround it with quotes.' % self.name,
            None,
            7
        )
    
    def _bad_spelling(self):
        all_names = set()
        if self.last_frame.globals is not None:
            all_names |= set(self.last_frame.globals.keys())
        if self.last_frame.locals is not None:
            all_names |= set(self.last_frame.locals.keys())
        
        similar_names = {self.name}
        if all_names:
            relevance = 0
            for name in all_names:
                sim = _name_similarity(name, self.name)
                if sim > 4:
                    similar_names.add(name)
                relevance = max(sim, relevance)
        else:
            relevance = 3
        
        if len(similar_names) > 1:
            general = None
            specific = "Are following names meant to be different:\n"
            for name in sorted(similar_names, key=lambda x: x.lower()):
                # TODO: add links to source
                specific += "* `%s`\n" % name
            specific += "?"
        else:
            general = "Double-check all occurrences of this name!" 
            specific = None
        
        return Suggestion(
            "Did you spell it correctly? Everywhere?",
            general,
            specific,
            relevance
        )
         
            
        
    
def _name_similarity(a, b):
    # TODO: tweak the result values
    a = a.replace("_", "")
    b = b.replace("_", "")
    
    if (a.replace("0", "O").replace("1", "l")
          == b.replace("0", "O").replace("1", "l")):
        return 6
    
    a = a.lower()
    b = b.lower()
    
    if a == b:
        return 6
    
    minlen = min(len(a), len(b))
    
    if minlen <= 2:
        return 0
    
    # if names differ at final isolated digits, 
    # then they are probably different vars, even if their
    # distance is small (eg. location_1 and location_2)
    if (a[-1].isdigit() and not a[-2].isdigit() 
        and b[-1].isdigit() and not b[-2].isdigit()):
        return 0
    
    # same thing with _ + single char suffixes
    # (eg. location_a and location_b)
    if a[-2] == "_" and b[-2] == "_":
        return 0
    
    distance = levenshtein_distance(a, b)
    
    if minlen <= 5:
        return max(8 - distance*2, 0)
    elif minlen <= 10:
        return max(9 - distance*2, 0)
    else:
        return max(10 - distance*2, 0)
        
        
        