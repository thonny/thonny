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
from thonny.misc_utils import levenshtein_damerau_distance
import tokenize

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
            if suggestion.relevance > 0:
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
        
        # TODO: don't repeat all this for all error helpers
        self.error_type_name = error_type_name
        self.error_message = error_message
        self.stack=stack
        
        self.last_frame = stack[-1]
        if self.last_frame.source:
            self.last_frame_ast = ast.parse(self.last_frame.source,
                                            self.last_frame.filename)
            self.last_frame_lines = self.last_frame.source.splitlines()
            self.last_frame_line = self.last_frame_lines[self.last_frame.lineno-1]
        else:
            self.last_frame_ast = None
            self.last_frame_lines = None
            self.last_frame_line = None
        
        if self.last_frame.code_name == "<module>":
            self.last_frame_module_source = self.last_frame.source
            self.last_frame_module_ast = self.last_frame_ast
        elif self.last_frame.filename is not None:
            with tokenize.open(self.last_frame.filename) as fp:
                self.last_frame_module_source = fp.read() 
            
            self.last_frame_module_ast = ast.parse(self.last_frame_module_source)
        
        

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
            self._sug_bad_spelling(),
            self._sug_missing_quotes(),
            self._sug_missing_import(),
            self._sug_local_from_global(),
            
            Suggestion("Is the variable definition given before the usage?",
                       "...",
                       None,
                       2),
            Suggestion("Maybe Python skipped the definition part?",
                       "If your variable's definition is inside a if-statement or loop, then it may have been skipped.",
                       None,
                       2),
        ]
    
    def _sug_missing_quotes(self):
        # TODO: only when in suitable context for string
        if self._is_attribute_value() or self._is_call_function():
            relevance = 0
        else:
            relevance = 7
            
        return Suggestion(
            "Did you really mean a variable or just forgot the quotes?",
            None,
            'If you meant literal text "%s", then surround it with quotes.' % self.name,
            relevance
        )
    
    def _sug_bad_spelling(self):
        
        # Yes, it would be more proper to consult builtins from the backend,
        # but it's easier this way...
        all_names = {name for name in dir(builtins) if not name.startswith("_")}
        
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
            general = "Double-check corresponding definition / assignment / documentation!" 
            specific = None
        
        return Suggestion(
            "Did you spell it correctly? Everywhere?",
            general,
            specific,
            relevance
        )
    
    def _sug_missing_import(self):
        likely_importable_functions = {
            "math" : {"ceil", "floor", "sqrt", "sin", "cos", "degrees"},  
            "random" : {"randint"},
            "turtle" : {"left", "right", "forward", "fd", 
                        "goto", "setpos", "Turtle",
                        "penup", "up", "pendown", "down",
                        "color", "pencolor", "fillcolor",
                        "begin_fill", "end_fill", "pensize", "width"},
            "re" : {"search", "match", "findall"},
            "datetime" : {"date", "time", "datetime", "today"},
            "statistics" : {"mean", "median", "median_low", "median_high", "mode", 
                            "pstdev", "pvariance", "stdev", "variance"},
            "os" : {"listdir"},
            "time" : {"time", "sleep"},
        }
        
        specific = None
         
        if self._is_call_function():
            relevance = 6
            for mod in likely_importable_functions:
                if self.name in likely_importable_functions[mod]:
                    relevance += 2
                    specific = ("If you meant `%s` from module `%s`, then add `from %s import %s` to the beginning of your script."
                                % (self.name, mod, mod, self.name))
                    break
                
        elif self._is_attribute_value():
            relevance = 6
            specific = ("If you meant module `%s`, then add `import %s` to the beginning of your script"
                        % (self.name, self.name))
            
            if self.name in likely_importable_functions:
                relevance += 2
                
                
        elif self._is_subscript_value() and self.name != "argv":
            relevance = 0
        elif self.name == "pi":
            specific = "If you meant constant π, then add `from math import pi` to the beginning of your script."
            relevance = 8
        elif self.name == "argv":
            specific = "If you meant the list with program arguments, then add `from sys import argv` to the beginning of your script."
            relevance = 8
        else:
            relevance = 3
            
        
        if specific is None:
            general = "Some functions/variables need to be imported before they can be used."
        else:
            general = None
            
        return Suggestion("Did you forget to import?",
                           general,
                           specific,
                           relevance)
    
    def _sug_local_from_global(self):
        relevance = 0
        specific = None
        
        if self.last_frame.code_name == "<module>":
            function_names = set()
            for node in ast.walk(self.last_frame_module_ast):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if self.name in map(lambda x: x.arg, node.args.args):
                        function_names.add(node.name)
                    # TODO: varargs, kw, ...
                    declared_global = False
                    for localnode in ast.walk(node):
                        #print(node.name, localnode)
                        if (isinstance(localnode, ast.Name)
                            and localnode.id == self.name
                            and isinstance(localnode.ctx, ast.Store)
                            ):
                            function_names.add(node.name)
                        elif (isinstance(localnode, ast.Global)
                              and self.name in localnode.names):
                            declared_global = True
                    
                    if node.name in function_names and declared_global:
                        function_names.remove(node.name)
            
            if function_names:
                relevance = 9
                specific = (
                    ("Name `%s` defined in `%s` is not accessible in the global/module level."
                     % (self.name, " and ".join(function_names)))
                    + "\n\nIf you need that data at the global level, then consider changing the function so that it `return`-s the value.")
            
        return Suggestion("Are you trying to acces a local variable outside of the function?",
                          None,
                          specific,
                          relevance)
    
    def _sug_not_defined_yet(self):
        ...
    
    def _is_call_function(self):
        return self.name + "(" in (self.last_frame_line
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
                                   
    def _is_subscript_value(self):
        return self.name + "[" in (self.last_frame_line
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
                                   
    def _is_attribute_value(self):
        return self.name + "." in (self.last_frame_line
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
        
    
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
    
    distance = levenshtein_damerau_distance(a, b, 5)
    
    if minlen <= 5:
        return max(8 - distance*2, 0)
    elif minlen <= 10:
        return max(9 - distance*2, 0)
    else:
        return max(10 - distance*2, 0)
        
                        