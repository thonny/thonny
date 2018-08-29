import ast
import builtins
import datetime
import gzip
import json
import logging
import os.path
import re
import sys
import tempfile
import textwrap
import tkinter as tk
import token
import tokenize
import urllib.request
import webbrowser
from collections import namedtuple
from tkinter import messagebox, ttk
from typing import Iterable, List, Optional, Tuple, Type, Union  # @UnusedImport

import thonny
from thonny import get_workbench, misc_utils, rst_utils, tktextext, ui_utils
from thonny.common import ToplevelResponse, read_source
from thonny.misc_utils import levenshtein_damerau_distance
from thonny.ui_utils import scrollbar_style

Suggestion = namedtuple("Suggestion", ["symbol", "title", "body", "relevance"])

_program_analyzer_classes = [] # type: List[Type[ProgramAnalyzer]]
_last_feedback_timestamps = {}

class AssistantView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(self, master, 
                                     text_class=AssistantRstText, 
                                     vertical_scrollbar_style=scrollbar_style("Vertical"), 
                                     horizontal_scrollbar_style=scrollbar_style("Horizontal"),
                                     horizontal_scrollbar_class=ui_utils.AutoScrollbar,
                                     read_only=True,
                                     wrap="word",
                                     font="TkDefaultFont",
                                     #cursor="arrow",
                                     padx=10,
                                     pady=0,
                                     insertwidth=0)
        
        self._error_helper_classes = {
            "NameError" : {NameErrorHelper},
            "SyntaxError" : {SyntaxErrorHelper},
        }
        
        self._analyzer_instances = []
        
        self._snapshots_per_main_file = {}
        self._current_snapshot = None
        
        self._accepted_warning_sets = []
        
        self.text.tag_configure("section_title",
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
        self.text.tag_configure("body", font="ItalicTkDefaultFont")
        
        main_font = tk.font.nametofont("TkDefaultFont")
        italic_font = main_font.copy()
        italic_font.configure(slant="italic", size=main_font.cget("size"))
        self.text.tag_configure("feedback_link",
                                #underline=True,
                                justify="right",
                                font=italic_font,
                                #foreground=get_syntax_options_for_tag("hyperlink")["foreground"]
                                )
        self.text.tag_bind("feedback_link", "<ButtonRelease-1>", self._ask_feedback, True)
        
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
    
    def add_error_helper(self, error_type_name, helper_class):
        if error_type_name not in self._error_helper_classes:
            self._error_helper_classes[error_type_name] = []
        self._error_helper_classes[error_type_name].append(helper_class)
    
    def _handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        self._clear()
        
        # prepare for snapshot
        key = msg.get("filename", "<shell>")
        self._current_snapshot = {
            "timestamp" : datetime.datetime.now().isoformat()[:19],
            "main_file_path" : key, 
        }
        self._snapshots_per_main_file.setdefault(key, [])
        self._snapshots_per_main_file[key].append(self._current_snapshot)
        
        if msg.get("user_exception"):
            self._explain_exception(msg["user_exception"])
        
        if msg.get("filename"):
            source = read_source(msg["filename"])
            self._start_program_analyses(msg["filename"],
                                         source,
                                         _get_imported_user_files(msg["filename"], source))
        
    
    def _explain_exception(self, error_info):
        
        rst = (".. default-role:: code\n\n"
               + rst_utils.create_title(error_info["type_name"]
                                        + ": " 
                                        + rst_utils.escape(error_info["message"]))
               + "\n")
        
        if error_info.get("lineno") is not None:
            rst += (
                "`%s, line %d <%s>`__\n\n" % (
                    os.path.basename(error_info["filename"]),
                    error_info["lineno"],
                    self._format_file_url(error_info)
                )
            )
        
        if error_info["type_name"] not in self._error_helper_classes:
            rst += "No helpers for this error type\n"
        else:
            helpers =[helper_class(error_info)
                  for helper_class in self._error_helper_classes[error_info["type_name"]]]
            
            # TODO: how to select the intro text if there are several helpers?
            rst += ("*" 
                    + helpers[0].get_intro().replace("\n\n", "*\n\n*")
                    + "*\n\n")
            
            suggestions = [suggestion 
                           for helper in helpers
                           for suggestion in helper.get_suggestions()]
            suggestions = sorted(suggestions, key=lambda s: s.relevance, reverse=True) 
            
            for i, suggestion in enumerate(suggestions):
                if suggestion.relevance > 0:
                    rst += self._format_suggestion(suggestion, 
                                                   i==len(suggestions)-1,
                                                   False#i==0
                                                   )
        
            self._current_snapshot["exception_suggestions"] = [
                dict(sug._asdict()) for sug in suggestions
            ]
            
        self.text.append_rst(rst)
        self._append_text("\n")
        
        self._current_snapshot["exception_type_name"] = error_info["type_name"]
        self._current_snapshot["exception_message"] = error_info["message"]
        self._current_snapshot["exception_file_path"] = error_info["filename"]
        self._current_snapshot["exception_lineno"] = error_info["lineno"]
        self._current_snapshot["exception_rst"] = rst # for debugging purposes
        
    
    def _format_suggestion(self, suggestion, last, initially_open):
        return (
            # assuming that title is already in rst format
            ".. topic:: " + suggestion.title + "\n"
          + "    :class: toggle%s%s\n" % (
                ", open" if initially_open else "",
                ", tight" if not last else "",
              )
          + "    \n"
          + textwrap.indent(suggestion.body, "    ") + "\n\n"
        )
        
    
    def _append_text(self, chars, tags=()):
        self.text.direct_insert("end", chars, tags=tags)
    
    
    def _clear(self):
        self._accepted_warning_sets.clear()
        for wp in self._analyzer_instances:
            wp.cancel_analysis()
        self._analyzer_instances = []
        self.text.clear()
    
    def _start_program_analyses(self, main_file_path, main_file_source,
                                imported_file_paths):

        for cls in _program_analyzer_classes:
            analyzer = cls(self._accept_warnings)
            analyzer.start_analysis({main_file_path} | set(imported_file_paths)) 
            self._analyzer_instances.append(analyzer)
        
        self._append_text("\nAnalyzing your code ...", ("em",))
        
        # save snapshot of current source
        self._current_snapshot["main_file_path"] = main_file_path
        self._current_snapshot["main_file_source"] = main_file_source
        self._current_snapshot["imported_files"] = {
            name : read_source(name) for name in imported_file_paths
        }
    
    def _accept_warnings(self, analyzer, warnings):
        if analyzer.cancelled:
            return
        
        self._accepted_warning_sets.append(warnings)
        if len(self._accepted_warning_sets) == len(self._analyzer_instances):
            # all providers have reported
            all_warnings = [w for ws in self._accepted_warning_sets for w in ws]
            self._present_warnings(all_warnings)
            self._append_feedback_link()
    
    def _present_warnings(self, warnings):
        self.text.direct_delete("end-2l linestart", "end-1c lineend")
        
        if not warnings:
            return
        
        #self._append_text("\n")
        # TODO: show filename when more than one file was analyzed
        # Put main file first
        # TODO: group by file and confidence
        rst = (
            ".. default-role:: code\n"
            + "\n"
            + rst_utils.create_title("Warnings")
            + "*May be ignored if you are happy with your program.*\n\n"
        )
        
        by_file = {}
        for warning in warnings:
            if warning["filename"] not in by_file:
                by_file[warning["filename"]] = []
            by_file[warning["filename"]].append(warning)
        
        for filename in by_file:
            rst += "`%s <%s>`__\n\n" % (os.path.basename(filename),
                                            self._format_file_url(dict(filename=filename)))
            file_warnings = sorted(by_file[filename], key=lambda x: x["lineno"]) 
            for i, warning in enumerate(file_warnings):
                rst += (
                    self._format_warning(warning, i == len(file_warnings)-1) 
                    + "\n"
                )
            
            rst += "\n"
        
        self.text.append_rst(rst)
        
        # save snapshot
        self._current_snapshot["warnings_rst"] = rst
        self._current_snapshot["warnings"] = warnings
                
    
    def _format_warning(self, warning, last):
        title = rst_utils.escape(warning["msg"].splitlines()[0])
        if warning.get("lineno") is not None:
            url = self._format_file_url(warning)
            title = "`Line %d <%s>`__ : %s" % (warning["lineno"], url, title)
        
        if warning.get("explanation_rst"):
            explanation_rst = warning["explanation_rst"]
        elif warning.get("explanation"):
            explanation_rst = rst_utils.escape(warning["explanation"])
        else:
            explanation_rst = ""
        
        if warning.get("more_info_url"):
            explanation_rst += "\n\n`More info online <%s>`__" % warning["more_info_url"]
        
        explanation_rst = explanation_rst.strip()
        if not explanation_rst:
            explanation_rst = "Perform a web search with 'Python' and the above message for more info."
        
        return (
            ".. topic:: %s\n" % title
            + "    :class: toggle" + ("" if last else ", tight") + "\n"
            + "    \n"
            + textwrap.indent(explanation_rst, "    ") + "\n\n"
        )
    
    def _append_feedback_link(self):
        self._append_text("Was it helpful or confusing?\n", ("a", "feedback_link"))
    
    def _format_file_url(self, atts):
        assert atts["filename"]
        s = "thonny://" + rst_utils.escape(atts["filename"])
        if atts.get("lineno") is not None:
            s += "#" + str(atts["lineno"])
            if atts.get("col_offset") is not None:
                s += ":" + str(atts["col_offset"])
        
        return s
    
    def _ask_feedback(self, event=None):
        
        all_snapshots = self._snapshots_per_main_file[self._current_snapshot["main_file_path"]]
        
        # TODO: select only snapshots which are not sent yet
        snapshots = all_snapshots
        
        ui_utils.show_dialog(FeedbackDialog(get_workbench(),
                                            self._current_snapshot["main_file_path"], 
                                            snapshots))
    
class AssistantRstText(rst_utils.RstText):
    def configure_tags(self):
        rst_utils.RstText.configure_tags(self)
        
        main_font = tk.font.nametofont("TkDefaultFont")
        
        italic_font = main_font.copy()
        italic_font.configure(slant="italic", size=main_font.cget("size"))
        
        h1_font = main_font.copy()
        h1_font.configure(weight="bold", 
                          size=main_font.cget("size"))
        
        self.tag_configure("h1", font=h1_font, spacing3=0, spacing1=10)
        self.tag_configure("topic_title", font="TkDefaultFont")
        
        self.tag_configure("topic_body", font=italic_font)

        self.tag_raise("sel")

class Helper:
    def get_intro(self):
        raise NotImplementedError()
    
    def get_suggestions(self) -> Iterable[Suggestion]:
        raise NotImplementedError()

class ProgramAnalyzer:
    def __init__(self, on_completion):
        self.completion_handler = on_completion
        
    def start_analysis(self, filenames):
        raise NotImplementedError()
    
    def cancel_analysis(self):
        pass

class SubprocessProgramAnalyzer(ProgramAnalyzer):
    def __init__(self, on_completion):
        super().__init__(on_completion)
        self._proc = None
        self.cancelled = False
        
    def cancel_analysis(self):
        self.cancelled = True
        if self._proc is not None:
            self._proc.kill()

        
class ErrorHelper(Helper):
    def __init__(self, error_info):
        
        # TODO: don't repeat all this for all error helpers
        self.intro_is_enough = False
        self.error_info = error_info
        
        self.last_frame = error_info["stack"][-1]
        self.last_frame_ast = None
        if self.last_frame.source:
            try:
                self.last_frame_ast = ast.parse(self.last_frame.source,
                                                self.last_frame.filename)
            except SyntaxError:
                pass
            
        
        self.last_frame_module_source = None 
        self.last_frame_module_ast = None
        if self.last_frame.code_name == "<module>":
            self.last_frame_module_source = self.last_frame.source
            self.last_frame_module_ast = self.last_frame_ast
        elif self.last_frame.filename is not None:
            self.last_frame_module_source = read_source(self.last_frame.filename) 
            try:
                self.last_frame_module_ast = ast.parse(self.last_frame_module_source)
            except SyntaxError:
                pass
        
        

class LibraryErrorHelper(ErrorHelper):
    """Explains exceptions, which doesn't happen in user code"""
    
    def get_intro(self):
        return "This error happened in library code. This may mean a bug in "
    
    def get_suggestions(self):
        return []

class SyntaxErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        ErrorHelper.__init__(self, error_info)
        
        # NB! Stack info is not relevant with SyntaxErrors,
        # use special fields instead

        self.tokens = []
        self.token_error = None
        
        
        if self.error_info["filename"]:
            with open(self.error_info["filename"], mode="rb") as fp:
                try:
                    for t in tokenize.tokenize(fp.readline):
                        self.tokens.append(t)
                except tokenize.TokenError as e:
                    self.token_error = e
            
            assert self.tokens[-1].type == token.ENDMARKER
        else:
            self.tokens = None
            
            
    def get_intro(self):
        if self.error_info["message"] == "EOL while scanning string literal":
            self.intro_is_enough = True
            return ("You haven't properly closed the string on line %s." % self.error_info["lineno"]
                    + "\n(If you want a multi-line string, then surround it with"
                    + " `'''` or `\"\"\"` at both ends.)")
            
        elif self.error_info["message"] == "EOF while scanning triple-quoted string literal":
            # lineno is not useful, as it is at the end of the file and user probably
            # didn't want the string to end there
            self.intro_is_enough = True
            return "You haven't properly closed a triple-quoted string"
        else:
            msg = "Python doesn't know how to read your program."
            
            if "^" in self.error_info["message"]:
                msg += (" Small `^` in the original error message shows where it gave up,"
                        + " but the actual mistake can be before this.") 
            
            return msg
    
    def get_more_info(self):
        return "Even single wrong, misplaced or missing character can cause syntax errors."
    
    def get_suggestions(self) -> Iterable[Suggestion]:
        return [self._sug_missing_or_misplaced_colon()]
    
    def _sug_missing_or_misplaced_colon(self):
        i = 0
        title = "Did you forget the colon?"
        relevance = 0
        body = ""
        while i < len(self.tokens) and self.tokens[i].type != token.ENDMARKER:
            t = self.tokens[i]
            if t.string in ["if", "elif", "else", "while", "for", "with",
                            "try", "except", "finally", 
                            "class", "def"]:
                keyword_pos = i
                while (self.tokens[i].type not in [token.NEWLINE, token.ENDMARKER, 
                                     token.COLON, # colon may be OP 
                                     token.RBRACE]
                        and self.tokens[i].string != ":"):
                    
                    old_i = i
                    if self.tokens[i].string in "([{":
                        i = self._skip_braced_part(i)
                        assert i > old_i
                    else:
                        i += 1
                
                if self.tokens[i].string != ":":
                    relevance = 9
                    body = "`%s` header must end with a colon." % t.string
                    break
            
                # Colon was present, but maybe it should have been right
                # after the keyword.
                if (t.string in ["else", "try", "finally"]
                    and self.tokens[keyword_pos+1].string != ":"):
                    title = "Incorrect use of `%s`" % t.string
                    body = "Nothing is allowed between `%s` and colon." % t.string
                    relevance = 9
                    if (self.tokens[keyword_pos+1].type not in (token.NEWLINE, tokenize.COMMENT)
                        and t.string == "else"):
                        body = "If you want to specify a conditon, then use `elif` or nested `if`."
                    break
                
            i += 1
                
        return Suggestion("missing-or-misplaced-colon", title, body, relevance)
    
    def _sug_wrong_increment_op(self):
        pass
    
    def _sug_wrong_decrement_op(self):
        pass
    
    def _sug_wrong_comparison_op(self):
        pass
    
    def _sug_switched_assignment_sides(self):
        pass
    
    def _skip_braced_part(self, token_index):
        assert self.tokens[token_index].string in "([{"
        level = 1
        while token_index < len(self.tokens):
            token_index += 1
            
            if self.tokens[token_index].string in "([{":
                level += 1
            elif self.tokens[token_index].string in ")]}":
                level -= 1
            
            if level <= 0:
                token_index += 1
                return token_index
        
        assert token_index == len(self.tokens)
        return token_index-1
    
    def _find_first_braces_problem(self):
        #closers = {'(':')', '{':'}', '[':']'}
        openers = {')':'(', '}':'{', ']':'['}
        
        brace_stack = []
        for t in self.tokens:
            if t.string in "([{":
                brace_stack.append(token)
            elif t.string in ")]}":
                if not brace_stack:
                    return (t, "`%s` without preceding matching `%s`" % (t.string, openers[t.string]))
                elif brace_stack[-1].string != openers[t.string]:     
                    return (t, "`%s` when last unmatched opener was `%s`" % (t.string, brace_stack[-1].string))
                else:
                    brace_stack.pop()
        
        if brace_stack:
            return (brace_stack[-1], "`%s` was not closed by the end of the program" % brace_stack[-1].string)
        
        return None
        

class NameErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        
        super().__init__(error_info)
        
        names = re.findall(r"\'.*\'", error_info["message"])
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
            self._sug_not_defined_yet(),
        ]
    
    def _sug_missing_quotes(self):
        # TODO: only when in suitable context for string
        if (self._is_attribute_value() 
            or self._is_call_function()
            or self._is_subscript_value()):
            relevance = 0
        else:
            relevance = 5
            
        return Suggestion(
            "missing-quotes",
            "Did you actually mean string (text)?",
            'If you didn\'t mean a variable but literal text "%s", then surround it with quotes.' % self.name,
            relevance
        )
    
    def _sug_bad_spelling(self):
        
        # Yes, it would be more proper to consult builtins from the backend,
        # but it's easier this way...
        all_names = {name for name in dir(builtins) if not name.startswith("_")}
        all_names |= {"pass", "break", "continue", "return", "yield"}
        
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
            body = "Are following names meant to be different?\n\n"
            for name in sorted(similar_names, key=lambda x: x.lower()):
                # TODO: add links to source
                body += "* `%s`\n\n" % name
        else:
            body = (
                "Compare the name with corresponding definition / assignment / documentation."
                + " Don't forget that case of the letters matters."
            ) 
        
        return Suggestion(
            "bad-spelling",
            "Did you misspell it (somewhere)?",
            body,
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
        
        body = None
         
        if self._is_call_function():
            relevance = 5
            for mod in likely_importable_functions:
                if self.name in likely_importable_functions[mod]:
                    relevance += 3
                    body = ("If you meant `%s` from module `%s`, then add\n\n`from %s import %s`\n\nto the beginning of your script."
                                % (self.name, mod, mod, self.name))
                    break
                
        elif self._is_attribute_value():
            relevance = 5
            body = ("If you meant module `%s`, then add `import %s` to the beginning of your script"
                        % (self.name, self.name))
            
            if self.name in likely_importable_functions:
                relevance += 3
                
                
        elif self._is_subscript_value() and self.name != "argv":
            relevance = 0
        elif self.name == "pi":
            body = "If you meant the constant π, then add `from math import pi` to the beginning of your script."
            relevance = 8
        elif self.name == "argv":
            body = "If you meant the list with program arguments, then add `from sys import argv` to the beginning of your script."
            relevance = 8
        else:
            relevance = 3
            
        
        if body is None:
            body = "Some functions/variables need to be imported before they can be used."
            
        return Suggestion("missing-import",
                          "Did you forget to import it?",
                          body,
                          relevance)
    
    def _sug_local_from_global(self):
        relevance = 0
        body = None
        
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
                body = (
                    ("Name `%s` defined in `%s` is not accessible in the global/module level."
                     % (self.name, " and ".join(function_names)))
                    + "\n\nIf you need that data at the global level, then consider changing the function so that it `return`-s the value.")
            
        return Suggestion(
            "local-from-global",
            "Are you trying to acces a local variable outside of the function?",
            body,
            relevance)
    
    def _sug_not_defined_yet(self):
        return Suggestion(
            "not-defined-yet",
            "Has Python executed the definition?",
            ("Don't forget that name becomes defined when corresponding definition ('=', 'def' or 'import') gets executed."
            + " If the definition comes later in code or is inside an if-statement, Python may not have executed it (yet)."
            + "\n\n"
            + "Make sure Python arrives to the definition before it arrives to this line. When in doubt, use the debugger."),
            1)
    
    def _is_call_function(self):
        return self.name + "(" in (self.error_info["line"]
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
                                   
    def _is_subscript_value(self):
        return self.name + "[" in (self.error_info["line"]
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
                                   
    def _is_attribute_value(self):
        return self.name + "." in (self.error_info["line"]
                                   .replace(" ", "")
                                   .replace("\n", "")
                                   .replace("\r", ""))
        

class FeedbackDialog(tk.Toplevel):
    def __init__(self, master, main_file_path, all_snapshots):
        super().__init__(master=master)
        
        self.main_file_path = main_file_path
        self.snapshots = self._select_unsent_snapshots(all_snapshots)
        
        if misc_utils.running_on_mac_os():
            self.configure(background="systemSheetBackground")
        
        self.title("Send feedback for Assistant")
        
        padx = 15
        
        intro_label = ttk.Label(self,
                                text="Below are the messages Assistant gave you in response to "
                                   + ("using the shell" if main_file_path == "<shell>" 
                                      else "testing '" + os.path.basename(main_file_path)) + "'"
                                   + " since " + self._get_since_str()
                                   + ".\n\n"
                                   + "In order to improve this feature, Thonny developers would love to know how "
                                   + "useful or confusing these messages were. We will only collect version "
                                   + "information and the data you enter or approve on this form.",
                                wraplength=550
                                )
        intro_label.grid(row=1, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15,15))
        
        tree_label = ttk.Label(self, text="Which messages were helpful (H) or confusing (C)?       Click on  [  ]  to mark!")
        tree_label.grid(row=2, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15,0))
        tree_frame = ui_utils.TreeFrame(self,
                                        columns=["helpful", "confusing", "title", "group", "symbol"],
                                        displaycolumns=["helpful", "confusing", "title"], 
                                        height=10,
                                        borderwidth=1,
                                        relief="groove")
        tree_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=padx)
        self.tree = tree_frame.tree
        self.tree.column('helpful', width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column('confusing', width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column('title', width=350, anchor=tk.W, stretch=True)
        
        self.tree.heading('helpful', text='H', anchor=tk.CENTER)
        self.tree.heading('confusing', text='C', anchor=tk.CENTER)
        self.tree.heading('title', text='Group / Message', anchor=tk.W) 
        self.tree['show'] = ('headings',)
        self.tree.bind("<1>", self._on_tree_click, True)
        main_font = tk.font.nametofont("TkDefaultFont")
        bold_font = main_font.copy()
        bold_font.configure(weight="bold", size=main_font.cget("size"))
        self.tree.tag_configure("group", font=bold_font)
        
        self.include_thonny_id_var = tk.IntVar(value=1)
        include_thonny_id_check = ttk.Checkbutton(self, variable=self.include_thonny_id_var,
                                          onvalue=1, offvalue=0,
                                          text="Include Thonny's installation time (allows us to group your submissions)")
        include_thonny_id_check.grid(row=4, column=0, columnspan=3, sticky="nw", padx=padx, pady=(5,0))
        
        self.include_snapshots_var = tk.IntVar(value=1)
        include_snapshots_check = ttk.Checkbutton(self, variable=self.include_snapshots_var,
                                          onvalue=1, offvalue=0,
                                          text="Include snapshots of the code and Assistant responses at each run")
        include_snapshots_check.grid(row=5, column=0, columnspan=3, sticky="nw", padx=padx, pady=(0,0))
        
        comments_label = ttk.Label(self, text="Any comments? Enhancement ideas?")
        comments_label.grid(row=6, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15,0))
        self.comments_text_frame = tktextext.TextFrame(self,vertical_scrollbar_style=scrollbar_style("Vertical"), 
                                            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
                                            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
                                            wrap="word",
                                            font="TkDefaultFont",
                                            #cursor="arrow",
                                            padx=10,
                                            pady=5,
                                            height=4,
                                            borderwidth=1,
                                            relief="groove"
                                            )
        self.comments_text_frame.grid(row=7, column=0, columnspan=3, sticky="nsew", padx=padx)
        
        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1, size=url_font.cget("size"))
        preview_link = ttk.Label(self, text="(Preview the data to be sent)",
                                 style="Url.TLabel",
                                 cursor="hand2",
                                 font=url_font)
        preview_link.bind("<1>", self._preview_submission_data, True)
        preview_link.grid(row=8, column=0, sticky="nw", padx=15, pady=15)
        
        submit_button = ttk.Button(self, text="Submit", width=10, command=self._submit_data)
        submit_button.grid(row=8, column=0, sticky="ne", padx=0, pady=15)
        
        cancel_button = ttk.Button(self, text="Cancel", width=7, command=self._close)
        cancel_button.grid(row=8, column=1, sticky="ne", padx=(10,15), pady=15)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close, True)

        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=3)
        self.rowconfigure(6, weight=2)

        self._empty_box = "[  ]"
        self._checked_box = "[X]"
        self._populate_tree()
    
    def _populate_tree(self):
        groups = {}
        
        for snap in self.snapshots:
            if snap.get("exception_message"):
                group = snap["exception_type_name"]
                groups.setdefault(group, set())
                for sug in snap["exception_suggestions"]:
                    groups[group].add((sug["symbol"], sug["title"]))
            
            # warnings group
            if snap.get("warnings"):
                group = "Warnings"
                groups.setdefault(group, set())
                for w in snap["warnings"]:
                    groups[group].add((w["symbol"], w["msg"]))
        
        for group in sorted(groups.keys(), key=lambda x: x.replace("Warnings", "z")):
            group_id = self.tree.insert("", "end", open=True, tags=("group",))
            self.tree.set(group_id, "title", group)
            
            for symbol, title in sorted(groups[group], key=lambda m:m[1]):
                item_id = self.tree.insert("", "end")
                self.tree.set(item_id, "helpful", self._empty_box)
                self.tree.set(item_id, "confusing", self._empty_box)
                self.tree.set(item_id, "title", title)
                self.tree.set(item_id, "symbol", symbol)
                self.tree.set(item_id, "group", group)
        
        self.tree.see("")
    
    def _on_tree_click(self, event):
        item_id = self.tree.identify("item", event.x, event.y)
        column = self.tree.identify_column(event.x)
        
        if not item_id or not column:
            return
        
        value_index = int(column[1:])-1
        values = list(self.tree.item(item_id, "values"))
        
        if values[value_index] == self._empty_box:
            values[value_index] = self._checked_box
        elif values[value_index] == self._checked_box:
            values[value_index] = self._empty_box
        else:
            return
        
        # update values
        self.tree.item(item_id, values=tuple(values))
    
    def _preview_submission_data(self, event=None):
        temp_path = os.path.join(
            tempfile.mkdtemp(), 
            'ThonnyAssistantFeedback_' + datetime.datetime.now().isoformat().replace(":",".")[:19] + ".txt"
        )
        data = self._collect_submission_data()
        with open(temp_path, "w", encoding="ascii") as fp:
            fp.write(data)
        
        webbrowser.open(temp_path)
    
    def _collect_submission_data(self):
        tree_data = []
        
        for iid in self.tree.get_children():
            values = self.tree.item(iid, "values")
            tree_data.append({
                "helpful" : values[0] == self._checked_box,
                "confusing" : values[1] == self._checked_box,
                "message" : values[2],
                "group" : values[3],
                "symbol" : values[4] 
            })
        
        submission = {
            "feedback_format_version" : 1,
            "thonny_version" : thonny.get_version(), 
            "python_version" : ".".join(map(str, sys.version_info[:3])),
            "message_feedback" : tree_data,
            "comments" : self.comments_text_frame.text.get("1.0", "end")
        }
        
        try:
            import mypy.version 
            submission["mypy_version"] = str(mypy.version.__version__)
        except ImportError:
            logging.exception("Could not get MyPy version")
        
        try:
            import pylint 
            submission["pylint_version"] = str(pylint.__version__)
        except ImportError:
            logging.exception("Could not get Pylint version")
        
        if self.include_snapshots_var.get():
            submission["snapshots"] = self.snapshots
        
        if self.include_thonny_id_var.get():
            submission["thonny_timestamp"] = get_workbench().get_option("general.configuration_creation_timestamp")
        
        return json.dumps(submission, indent=2)
    
    def _submit_data(self):
        json_data = self._collect_submission_data()
        compressed_data = gzip.compress(json_data.encode("ascii"))
        
        def do_work():
            try:
                handle = urllib.request.urlopen(
                    "https://thonny.org/store_assistant_feedback.php", 
                    data=compressed_data,
                    timeout=10
                )
                return handle.read()
            except Exception as e:
                return str(e)
                
        
        result = ui_utils.run_with_waiting_dialog(self, do_work, description="Uploading")
        if result == b"OK":
            if self.snapshots:
                last_timestamp = self.snapshots[-1]["timestamp"]
                _last_feedback_timestamps[self.main_file_path] = last_timestamp
            messagebox.showinfo("Done!", "Thank you for the feedback!\n\nLet us know again when Assistant\nhelps or confuses you!")
            self._close()
        else:
            messagebox.showerror("Problem", "Something went wrong:\n%s\n\nIf you don't mind, then try again later!" % result[:1000])
    
    def _select_unsent_snapshots(self, all_snapshots):
        if self.main_file_path not in _last_feedback_timestamps:
            return all_snapshots
        else:
            return [s for s in all_snapshots 
                    if s["timestamp"] > _last_feedback_timestamps[self.main_file_path]]
    
    def _close(self, event=None):
        self.destroy()
    
    def _get_since_str(self):
        if not self.snapshots:
            assert self.main_file_path in _last_feedback_timestamps
            since = datetime.datetime.strptime(
                _last_feedback_timestamps[self.main_file_path],
                '%Y-%m-%dT%H:%M:%S'
            )
        else:
            since = datetime.datetime.strptime(
                self.snapshots[0]["timestamp"], 
                '%Y-%m-%dT%H:%M:%S'
            )
        
        if (since.date() == datetime.date.today()
            or (datetime.datetime.now()-since) <= datetime.timedelta(hours=5)):
            since_str = since.strftime("%X")
        else:
            # date and time without yer
            since_str = since.strftime("%c").replace(str(datetime.date.today().year), "")
        
        # remove seconds
        if since_str.count(":") == 2:
            i = since_str.rfind(":")
            if i > 0 and len(since_str[i+1:i+3]) == 2 and since_str[i+1:i+3].isnumeric():
                since_str = since_str[:i] + since_str[i+3:] 
        
        return since_str.strip()

def _name_similarity(a, b):
    # TODO: tweak the result values
    a = a.replace("_", "")
    b = b.replace("_", "")
    
    minlen = min(len(a), len(b))
    
    if (a.replace("0", "O").replace("1", "l")
          == b.replace("0", "O").replace("1", "l")):
        if minlen >= 4: 
            return 7
        else:
            return 6
    
    a = a.lower()
    b = b.lower()
    
    if a == b:
        if minlen >= 4: 
            return 7
        else:
            return 6
    
    
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
        

def _get_imported_user_files(main_file, source=None):
    assert os.path.isabs(main_file)
    
    if source is None:
        source = read_source(main_file)
    
    try:
        root = ast.parse(source, main_file)
    except SyntaxError:
        return set()
    
    main_dir = os.path.dirname(main_file)
    module_names = set()
    # TODO: at the moment only considers non-package modules
    for node in ast.walk(root):
        if isinstance(node, ast.Import):
            for item in node.names:
                module_names.add(item.name)
        elif isinstance(node, ast.ImportFrom):
            module_names.add(node.name)
    
    imported_files = set()
    
    for file in {name + ext for ext in [".py", ".pyw"] for name in module_names}:
        possible_path = os.path.join(main_dir, file)
        if os.path.exists(possible_path):
            imported_files.add(possible_path)
    
    return imported_files
    # TODO: add recursion

def add_program_analyzer(cls):
    _program_analyzer_classes.append(cls)
