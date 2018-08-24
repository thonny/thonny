import tkinter as tk
from tkinter import ttk
import builtins
from typing import List, Optional, Union, Iterable, Tuple
from thonny import ui_utils, tktextext, get_workbench, running, get_runner,\
    rst_utils
from collections import namedtuple
import re
from thonny.codeview import get_syntax_options_for_tag
from thonny.common import ToplevelResponse
import ast
from thonny.misc_utils import levenshtein_damerau_distance
import token
import tokenize
import io

from pylint import lint
import subprocess
from thonny.running import get_frontend_python
import sys
import logging
import textwrap
from thonny.ui_utils import scrollbar_style


Suggestion = namedtuple("Suggestion", ["title", "body", "relevance"])

class AssistantView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(self, master, 
                                     text_class=rst_utils.RstText, 
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
        
        self._warning_providers = {
            PylintWarningProvider(self._accept_warnings),
            MyPyWarningProvider(self._accept_warnings),
        }
        
        self._accepted_warning_sets = []
        
        self._suggestions = set()
        
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
        
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
    
    def add_error_helper(self, error_type_name, helper_class):
        if error_type_name not in self._error_helper_classes:
            self._error_helper_classes[error_type_name] = []
        self._error_helper_classes[error_type_name].append(helper_class)
    
    def _handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        self._clear()
        
        if "user_exception" in msg:
            self.explain_exception(msg["user_exception"])
        
        if "filename" in msg:
            self._start_warning_analysis(msg["filename"])
    
    def explain_exception(self, error_info):
        "►▸˃✶ ▼▸▾"
        rst = "**%s: %s**\n\n" % (error_info["type_name"], 
                              rst_utils.escape(error_info["message"]))
        
        if error_info["type_name"] not in self._error_helper_classes:
            rst += "No helpers for this error type\n"
        else:
            helpers =[helper_class(error_info)
                  for helper_class in self._error_helper_classes[error_info["type_name"]]]
            
            # TODO: how to select the intro text if there are several helpers?
            rst += helpers[0].get_intro() + "\n\n"
            
            suggestions = [suggestion 
                           for helper in helpers
                           for suggestion in helper.get_suggestions()]
            
            for i, suggestion in enumerate(
                sorted(suggestions, key=lambda s: s.relevance, reverse=True)
                ):
                if suggestion.relevance > 0:
                    rst += self._format_suggestion(suggestion, i==0)
        
        self.text.append_rst(rst)
        #self._append_text(rst)
        
    
    def _format_suggestion(self, suggestion, initially_open):
        return (
            ".. topic:: " + rst_utils.escape(suggestion.title) + "\n"
          + "    :class: toggle%s\n" % (" open" if initially_open else "")
          + "    \n"
          + textwrap.indent(suggestion.body, "    ") + "\n\n"
        )
        
    
    def _append_text(self, chars, tags=()):
        self.text.direct_insert("end", chars, tags=tags)
    
    
    def _clear(self):
        self._suggestions.clear()
        self._accepted_warning_sets.clear()
        for wp in self._warning_providers:
            wp.cancel_analysis()
        self.text.clear()
    
    def _start_warning_analysis(self, filename):
        for wp in self._warning_providers:
            wp.start_analysis(filename)
    
    def _accept_warnings(self, title, warnings):
        self._accepted_warning_sets.append(warnings)
        if len(self._accepted_warning_sets) == len(self._warning_providers):
            # all providers have reported
            all_warnings = [w for ws in self._accepted_warning_sets for w in ws]
            self._present_warnings(all_warnings)
    
    def _present_warnings(self, warnings):
        self._append_text("\n")
        # TODO: show filename when more than one file was analyzed
        # Put main file first
        # TODO: group by file and confidence
        rst = "**Possible mistakes in fstrings.py**\n\n"
        
        for warning in sorted(warnings, key=lambda x: x["lineno"]):
            rst += self._format_warning(warning) + "\n"
        
        self.text.append_rst(rst)
    
    def _format_warning(self, warning):
        title = rst_utils.escape(warning["msg"])
        if warning.get("lineno", False):
            if "col_offset" in warning:
                url = "thonny://%s#%d:%d" % (
                    rst_utils.escape(warning["filename"]),
                    warning["lineno"],
                    warning["col_offset"]
                )
            else:
                url = "thonny://%s#%d" % (
                    rst_utils.escape(warning["filename"]),
                    warning["lineno"]
                )
            title = "`Line %d <%s>`__: %s" % (warning["lineno"], url, title)
        
        return (
            ".. topic:: %s\n" % title
            + "    :class: toggle\n"
            + "    \n"
            + textwrap.indent(warning.get("symbol", "blaa"), "    ") + "\n\n"
        )
    

class Helper:
    def get_intro(self):
        raise NotImplementedError()
    
    def get_suggestions(self) -> Iterable[Suggestion]:
        raise NotImplementedError()

class DebugHelper(Helper):
    pass

class SubprocessWarningProvider:
    def __init__(self, on_completion):
        self._proc = None
        self.completion_handler = on_completion
        
    def start_analysis(self, filename):
        pass
    
    def cancel_analysis(self):
        if self._proc is not None:
            self._proc.kill()
        
        

class PylintWarningProvider(SubprocessWarningProvider):
    
    def start_analysis(self, filename):
        
        relevant_symbols = {
            "function-redefined",
            "method-hidden",
            "no-method-argument",
            "no-self-argument",
            "inherit-non-class",
            "used-before-assignment",
            "undefined-variable",
            "no-name-in-module",
            "unbalanced-tuple-unpacking",
            "unpacking-non-sequence",
            "bad-except-order",
            "raising-bad-type",
            "misplaced-bare-raise", # TODO: "did you forgot exception to raise"
            "raising-non-exception",
            "notimplemented-raised",
            "no-member",
            "not-callable",
            "assignment-from-no-return",
            "assignment-from-none",
            "no-value-for-parameter",
            "unsupported-membership-test",
            "unsubscriptable-object",
            "unsupported-assignment-operation",
            "unsupported-delete-operation",
            "too-many-function-args",
            "unexpected-keyword-arg",
            "redundant-keyword-arg",
            "missing-kwoa",
            "invalid-sequence-index",
            "invalid-slice-index",
            "invalid-unary-operand-type",
            "unsupported-binary-operation",
            "not-an-iterable",
            "not-a-mapping",
            "trailing-comma-tuple",
            "inconsistent-return-statements",
            #"missing-docstring",
            "access-member-before-definition",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        }
        
        style_symbols = {
            # issues that affect readability and may hide bugs
            "invalid-name", # TODO: check only naming styles, not length
            "bad-classmethod-argument", # cls
            "line-too-long", # Remind \ and (), # TODO: use line-margin setting
            "superfluous-parens", # if (...): 
            #"bad-whitespace", # ??? 
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        }
        
        self._proc = ui_utils.popen_with_ui_thread_callback(
            [get_frontend_python(), "-m", 
                "pylint", 
                #"--rcfile=None", # TODO: make it ignore any rcfiles that can be somewhere 
                "--persistent=n", 
                #"--confidence=HIGH", # Leave empty to show all. Valid levels: HIGH, INFERENCE, INFERENCE_FAILURE, UNDEFINED
                #"--disable=all",
                "--enable=all",
                "--disable=missing-docstring,invalid-name,trailing-whitespace",
                #"--enable=" + ",".join(relevant_symbols),
                "--output-format=text",
                "--reports=n",
                "--msg-template={{'filename':{abspath!r}, 'lineno':{line}, 'col_offset':{column}, 'symbol':{symbol!r}, 'msg':{msg!r}, 'msg_id':{msg_id!r}}}",
                filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            on_completion=self._parse_and_output_warnings
        )
        
        
    def _parse_and_output_warnings(self, pylint_proc):
        out = pylint_proc.stdout.read()
        err = pylint_proc.stderr.read()
        #print("COMPL", out, err)
        # get rid of non-error
        err = err.replace("No config file found, using default configuration", "").strip()
        if err:
            print(err, file=sys.stderr)
            #logging.getLogger("thonny").error("Pylint: " + err)
        
        warnings = []
        for line in out.splitlines():
            if line.startswith("{"):
                try:
                    atts = ast.literal_eval(line.strip())
                except SyntaxError:
                    print(line)
                    continue
                else:
                    warnings.append(atts)
        
        self.completion_handler("Pylint warnings", warnings)

class MyPyWarningProvider(SubprocessWarningProvider):
    
    def start_analysis(self, filename):
        args = [get_frontend_python(), "-m", 
                "mypy", 
                "--ignore-missing-imports",
                "--check-untyped-defs",
                "--warn-redundant-casts",
                "--show-column-numbers",
                filename]
        
        from mypy.version import __version__
        try:
            ver = tuple(map(int, __version__.split(".")))
        except:
            ver = (0, 470) # minimum required version
        
        if ver >= (0, 520):
            args.insert(3, "--no-implicit-optional")
             
        if ver >= (0, 590):
            args.insert(3, "--python-executable")
            args.insert(4, get_runner().get_executable()) 
                
        self._proc = ui_utils.popen_with_ui_thread_callback(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            on_completion=self._parse_and_output_warnings
        )
        
        
    def _parse_and_output_warnings(self, pylint_proc):
        out = pylint_proc.stdout.read()
        err = pylint_proc.stderr.read()
        if err:
            print(err, file=sys.stderr)
            #logging.getLogger("thonny").warning("MyPy: " + err)
        #print(out)
        warnings = []
        for line in out.splitlines():
            m = re.match(r"(.*?):(\d+):(\d+):(.*?):(.*)", line.strip())
            if m is not None:
                warnings.append({
                    "filename" : m.group(1),
                    "lineno" : int(m.group(2)),
                    "col_offset" : int(m.group(3))-1,
                    "kind" : m.group(4).strip(),
                    "msg" : m.group(5).strip() + " (MP)",
                })
            else:
                print("Bad MyPy line", line)

        
        self.completion_handler("MyPy warnings", warnings)
        
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
            with tokenize.open(self.last_frame.filename) as fp:
                self.last_frame_module_source = fp.read() 
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
            return "You haven't properly closed a triple-quoted string"
            self.intro_is_enough = True
        else:
            msg = "Python doesn't know how to read your program."
            
            if True: # TODO: check the presence of ^
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
                
        return Suggestion(title, body, relevance)
    
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
            
            Suggestion("Is the variable definition given before the usage?",
                       "TODO:",
                       2),
            Suggestion("Maybe Python skipped the definition part?",
                       "If your variable's definition is inside a if-statement or loop, then it may have been skipped.",
                       2),
        ]
    
    def _sug_missing_quotes(self):
        # TODO: only when in suitable context for string
        if self._is_attribute_value() or self._is_call_function():
            relevance = 0
        else:
            relevance = 5
            
        return Suggestion(
            "Did you really mean a variable or just forgot the quotes?",
            'If you meant literal text "%s", then surround it with quotes.' % self.name,
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
            body = "Are following names meant to be different:\n"
            for name in sorted(similar_names, key=lambda x: x.lower()):
                # TODO: add links to source
                body += "* `%s`\n" % name
            body += "?"
        else:
            body = "Double-check corresponding definition / assignment / documentation!" 
        
        return Suggestion(
            "Did you spell it correctly? Everywhere?",
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
                    body = ("If you meant `%s` from module `%s`, then add `from %s import %s` to the beginning of your script."
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
            body = "If you meant constant π, then add `from math import pi` to the beginning of your script."
            relevance = 8
        elif self.name == "argv":
            body = "If you meant the list with program arguments, then add `from sys import argv` to the beginning of your script."
            relevance = 8
        else:
            relevance = 3
            
        
        if body is None:
            body = "Some functions/variables need to be imported before they can be used."
            
        return Suggestion("Did you forget to import?",
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
            
        return Suggestion("Are you trying to acces a local variable outside of the function?",
                          body,
                          relevance)
    
    def _sug_not_defined_yet(self):
        ...
    
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
        


