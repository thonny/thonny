import ast
import datetime
import gzip
import json
import logging
import os.path
import sys
import tempfile
import textwrap
import tkinter as tk
import urllib.request
import webbrowser
from collections import namedtuple
from tkinter import messagebox, ttk
from typing import (
    Dict,# pylint disable=unused-import
    Iterable,
    List,# pylint disable=unused-import
    Optional,# pylint disable=unused-import
    Tuple,  # pylint disable=unused-import
    Type,# pylint disable=unused-import
    Union, # pylint disable=unused-import
)  


import thonny
from thonny import get_workbench, rst_utils, tktextext, ui_utils, get_runner
from thonny.common import ToplevelResponse, read_source
from thonny.misc_utils import levenshtein_damerau_distance, running_on_mac_os
from thonny.ui_utils import scrollbar_style
from thonny.running import CPythonProxy
import subprocess

Suggestion = namedtuple("Suggestion", ["symbol", "title", "body", "relevance"])

_program_analyzer_classes = []  # type: List[Type[ProgramAnalyzer]]
_last_feedback_timestamps = {}  # type: Dict[str, str]
_error_helper_classes = {}  # type: Dict[str, List[Type[ErrorHelper]]]


class AssistantView(tktextext.TextFrame):
    def __init__(self, master):
        tktextext.TextFrame.__init__(
            self,
            master,
            text_class=AssistantRstText,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            read_only=True,
            wrap="word",
            font="TkDefaultFont",
            # cursor="arrow",
            padx=10,
            pady=0,
            insertwidth=0,
        )

        self._analyzer_instances = []

        self._snapshots_per_main_file = {}
        self._current_snapshot = None

        self._accepted_warning_sets = []

        self.text.tag_configure(
            "section_title",
            spacing3=5,
            font="BoldTkDefaultFont",
            # foreground=get_syntax_options_for_tag("stderr")["foreground"]
        )
        self.text.tag_configure(
            "intro",
            # font="ItalicTkDefaultFont",
            spacing3=10,
        )
        self.text.tag_configure("relevant_suggestion_title", font="BoldTkDefaultFont")
        self.text.tag_configure("suggestion_title", lmargin2=16, spacing1=5, spacing3=5)
        self.text.tag_configure("suggestion_body", lmargin1=16, lmargin2=16)
        self.text.tag_configure("body", font="ItalicTkDefaultFont")

        main_font = tk.font.nametofont("TkDefaultFont")
        
        # Underline on font looks better than underline on tag
        italic_underline_font = main_font.copy()
        italic_underline_font.configure(slant="italic", 
                                        size=main_font.cget("size"),
                                        underline=True)
        
        
        
        self.text.tag_configure(
            "feedback_link",
            justify="right",
            font=italic_underline_font,
        )
        self.text.tag_bind(
            "feedback_link", "<ButtonRelease-1>", self._ask_feedback, True
        )
        self.text.tag_configure(
            "python_errors_link",
            justify="right",
            font=italic_underline_font,
        )
        self.text.tag_bind(
            "python_errors_link", "<ButtonRelease-1>",
            lambda e: get_workbench().open_url("errors.rst"),
            True
        )

        get_workbench().bind("ToplevelResponse", self.handle_toplevel_response, True)

        add_error_helper("*", GenericErrorHelper)

    def handle_toplevel_response(self, msg: ToplevelResponse) -> None:
        # Can be called by event system or by Workbench
        # (if Assistant wasn't created yet but an error came)
        self._clear()

        if not isinstance(get_runner().get_backend_proxy(), CPythonProxy):
            # TODO: add some support for MicroPython as well
            return

        # prepare for snapshot
        key = msg.get("filename", "<pyshell>")
        self._current_snapshot = {
            "timestamp": datetime.datetime.now().isoformat()[:19],
            "main_file_path": key,
        }
        self._snapshots_per_main_file.setdefault(key, [])
        self._snapshots_per_main_file[key].append(self._current_snapshot)

        if msg.get("user_exception"):
            self._exception_info = msg["user_exception"]
            self._explain_exception(msg["user_exception"])
            if get_workbench().get_option("assistance.open_assistant_on_errors"):
                get_workbench().show_view("AssistantView", set_focus=False)
        else:
            self._exception_info = None

        if msg.get("filename") and os.path.exists(msg["filename"]):
            self.main_file_path = msg["filename"]
            source = read_source(msg["filename"])
            self._start_program_analyses(
                msg["filename"],
                source,
                _get_imported_user_files(msg["filename"], source),
            )
        else:
            self.main_file_path = None
            self._present_conclusion()

    def _explain_exception(self, error_info):
        rst = (
            self._get_rst_prelude()
            + rst_utils.create_title(
                error_info["type_name"] + ": " + rst_utils.escape(error_info["message"])
            )
            + "\n"
        )

        if error_info.get("lineno") is not None and os.path.exists(
            error_info["filename"]
        ):
            rst += "`%s, line %d <%s>`__\n\n" % (
                os.path.basename(error_info["filename"]),
                error_info["lineno"],
                self._format_file_url(error_info),
            )

        helpers = [
            helper_class(error_info)
            for helper_class in (
                _error_helper_classes.get(error_info["type_name"], [])
                + _error_helper_classes["*"]
            )
        ]

        best_intro = helpers[0]
        for helper in helpers:
            if helper.intro_confidence > best_intro.intro_confidence:
                best_intro = helper

        # intro
        if best_intro.intro_text:
            rst += (
                ".. note::\n"
                + "    "
                + best_intro.intro_text.strip().replace("\n\n", "\n\n    ")
                + "\n\n"
            )

        suggestions = [
            suggestion
            for helper in helpers
            for suggestion in helper.suggestions
            if suggestion is not None
        ]
        suggestions = sorted(suggestions, key=lambda s: s.relevance, reverse=True)

        if suggestions[0].relevance > 1 or best_intro.intro_confidence > 1:
            relevance_threshold = 2
        else:
            # use relevance 1 only when there is nothing better
            relevance_threshold = 1

        suggestions = [s for s in suggestions if s.relevance >= relevance_threshold]

        for i, suggestion in enumerate(suggestions):
            rst += self._format_suggestion(
                suggestion,
                i == len(suggestions) - 1,
                # TODO: is it good if first is preopened?
                # It looks cleaner if it is not.
                False,  # i==0
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
        self._current_snapshot["exception_rst"] = rst  # for debugging purposes

    def _format_suggestion(self, suggestion, last, initially_open):
        return (
            # assuming that title is already in rst format
            ".. topic:: "
            + suggestion.title
            + "\n"
            + "    :class: toggle%s%s\n"
            % (", open" if initially_open else "", ", tight" if not last else "")
            + "    \n"
            + textwrap.indent(suggestion.body, "    ")
            + "\n\n"
        )

    def _append_text(self, chars, tags=()):
        self.text.direct_insert("end", chars, tags=tags)

    def _clear(self):
        self._accepted_warning_sets.clear()
        for wp in self._analyzer_instances:
            wp.cancel_analysis()
        self._analyzer_instances = []
        self.text.clear()

    def _start_program_analyses(
        self, main_file_path, main_file_source, imported_file_paths
    ):

        for cls in _program_analyzer_classes:
            analyzer = cls(self._accept_warnings)
            analyzer.start_analysis(main_file_path, imported_file_paths)
            self._analyzer_instances.append(analyzer)

        self._append_text("\nAnalyzing your code ...", ("em",))

        # save snapshot of current source
        self._current_snapshot["main_file_path"] = main_file_path
        self._current_snapshot["main_file_source"] = main_file_source
        self._current_snapshot["imported_files"] = {
            name: read_source(name) for name in imported_file_paths
        }

    def _accept_warnings(self, analyzer, warnings):
        if analyzer.cancelled:
            return

        self._accepted_warning_sets.append(warnings)
        if len(self._accepted_warning_sets) == len(self._analyzer_instances):
            self._present_warnings()
            self._present_conclusion()

    def _present_conclusion(self):

        if not self.text.get("1.0", "end").strip():
            if self.main_file_path is not None and os.path.exists(self.main_file_path):
                self._append_text("\n")
                self.text.append_rst(
                    "The code in `%s <%s>`__ looks good.\n\n"
                    % (
                        os.path.basename(self.main_file_path),
                        self._format_file_url({"filename": self.main_file_path}),
                    )
                )
                self.text.append_rst(
                    "If it is not working as it should, "
                    + "then consider using some general "
                    + "`debugging techniques <debugging.rst>`__.\n\n",
                    ("em",),
                )
        
        

        if self.text.get("1.0", "end").strip():
            self._append_feedback_link()
        
        if self._exception_info:
            self._append_text("General advice on dealing with errors.\n", ("a", "python_errors_link"))

    def _present_warnings(self):
        warnings = [w for ws in self._accepted_warning_sets for w in ws]
        self.text.direct_delete("end-2l linestart", "end-1c lineend")

        if not warnings:
            return

        if self._exception_info is None:
            intro = "May be ignored if you are happy with your program."
        else:
            intro = "May help you find the cause of the error."

        rst = (
            self._get_rst_prelude()
            + rst_utils.create_title("Warnings")
            + ":remark:`%s`\n\n" % intro
        )

        by_file = {}
        for warning in warnings:
            if warning["filename"] not in by_file:
                by_file[warning["filename"]] = []
            if warning not in by_file[warning["filename"]]:
                # Pylint may give double warnings (eg. when module imports itself)
                by_file[warning["filename"]].append(warning)

        for filename in by_file:
            rst += "`%s <%s>`__\n\n" % (
                os.path.basename(filename),
                self._format_file_url(dict(filename=filename)),
            )
            file_warnings = sorted(
                by_file[filename],
                key=lambda x: (x.get("lineno", 0), -x.get("relevance", 1)),
            )

            for i, warning in enumerate(file_warnings):
                rst += self._format_warning(warning, i == len(file_warnings) - 1) + "\n"

            rst += "\n"

        self.text.append_rst(rst)

        # save snapshot
        self._current_snapshot["warnings_rst"] = rst
        self._current_snapshot["warnings"] = warnings

        if get_workbench().get_option("assistance.open_assistant_on_warnings"):
            get_workbench().show_view("AssistantView")

    def _format_warning(self, warning, last):
        title = rst_utils.escape(warning["msg"].splitlines()[0])
        if warning.get("lineno") is not None:
            url = self._format_file_url(warning)
            if warning.get("lineno"):
                title = "`Line %d <%s>`__ : %s" % (warning["lineno"], url, title)

        if warning.get("explanation_rst"):
            explanation_rst = warning["explanation_rst"]
        elif warning.get("explanation"):
            explanation_rst = rst_utils.escape(warning["explanation"])
        else:
            explanation_rst = ""

        if warning.get("more_info_url"):
            explanation_rst += (
                "\n\n`More info online <%s>`__" % warning["more_info_url"]
            )

        explanation_rst = explanation_rst.strip()
        topic_class = "toggle" if explanation_rst else "empty"
        if not explanation_rst:
            explanation_rst = "n/a"

        return (
            ".. topic:: %s\n" % title
            + "    :class: " + topic_class
            + ("" if last else ", tight")
            + "\n"
            + "    \n"
            + textwrap.indent(explanation_rst, "    ")
            + "\n\n"
        )

    def _append_feedback_link(self):
        self._append_text("Was it helpful or confusing?\n", ("a", "feedback_link"))

    def _format_file_url(self, atts):
        return format_file_url(atts["filename"], atts.get("lineno"), atts.get("col_offset"))

    def _ask_feedback(self, event=None):

        all_snapshots = self._snapshots_per_main_file[
            self._current_snapshot["main_file_path"]
        ]

        # TODO: select only snapshots which are not sent yet
        snapshots = all_snapshots

        ui_utils.show_dialog(
            FeedbackDialog(get_workbench(), self.main_file_path, snapshots)
        )
    
    def _get_rst_prelude(self):
        return (".. default-role:: code\n\n"
                + ".. role:: light\n\n"
                + ".. role:: remark\n\n"
                )

class AssistantRstText(rst_utils.RstText):
    def configure_tags(self):
        super().configure_tags()

        main_font = tk.font.nametofont("TkDefaultFont")

        italic_font = main_font.copy()
        italic_font.configure(slant="italic", size=main_font.cget("size"))

        h1_font = main_font.copy()
        h1_font.configure(weight="bold", size=main_font.cget("size"))

        self.tag_configure("h1", font=h1_font, spacing3=0, spacing1=10)
        self.tag_configure("topic_title", font="TkDefaultFont")

        self.tag_configure("topic_body", font=italic_font, spacing1=10, lmargin1=25, lmargin2=25)

        self.tag_raise("sel")


class Helper:
    def get_intro(self) -> Tuple[str, int]:
        raise NotImplementedError()

    def get_suggestions(self) -> Iterable[Suggestion]:
        raise NotImplementedError()


class ErrorHelper(Helper):
    def __init__(self, error_info):

        # TODO: don't repeat all this for all error helpers
        self.error_info = error_info

        self.last_frame = error_info["stack"][-1]
        self.last_frame_ast = None
        if self.last_frame.source:
            try:
                self.last_frame_ast = ast.parse(
                    self.last_frame.source, self.last_frame.filename
                )
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

        self.intro_confidence = 1
        self.intro_text = ""
        self.suggestions = []


class GenericErrorHelper(ErrorHelper):
    def __init__(self, error_info):
        super().__init__(error_info)

        self.intro_text = "No specific suggestions for this error (yet)."
        self.intro_confidence = 1
        self.suggestions = [
            Suggestion(
                "ask-for-specific-support",
                "Let Thonny developers know",
                "Click on the feedback link at the bottom of this panel to let Thonny developers know "
                + "about your problem. They may add support for "
                + "such cases in future Thonny versions.",
                1,
            ),
        ]
        
        if error_info["message"].lower() != "invalid syntax":
            self.suggestions.append(Suggestion(
                "generic-search-the-web",
                "Search the web",
                "Try performing a web search for\n\n``Python %s: %s``"
                % (
                    self.error_info["type_name"],
                    rst_utils.escape(self.error_info["message"]),
                ),
                1,
            ))

class ProgramAnalyzer:
    def __init__(self, on_completion):
        self.completion_handler = on_completion
        self.cancelled = False

    def start_analysis(self, main_file_path, imported_file_paths):
        raise NotImplementedError()

    def cancel_analysis(self):
        pass


class SubprocessProgramAnalyzer(ProgramAnalyzer):
    def __init__(self, on_completion):
        super().__init__(on_completion)
        self._proc = None

    def cancel_analysis(self):
        self.cancelled = True
        if self._proc is not None:
            self._proc.kill()


class LibraryErrorHelper(ErrorHelper):
    """Explains exceptions, which doesn't happen in user code"""

    def get_intro(self):
        return "This error happened in library code. This may mean a bug in "

    def get_suggestions(self):
        return []


class FeedbackDialog(tk.Toplevel):
    def __init__(self, master, main_file_path, all_snapshots):
        super().__init__(master=master)
        main_frame = ttk.Frame(self)
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.main_file_path = main_file_path
        self.snapshots = self._select_unsent_snapshots(all_snapshots)

        self.title("Send feedback for Assistant")

        padx = 15

        intro_label = ttk.Label(
            main_frame,
            text="Below are the messages Assistant gave you in response to "
            + (
                "using the shell"
                if self._happened_in_shell()
                else "testing '" + os.path.basename(main_file_path) + "'"
            )
            + " since "
            + self._get_since_str()
            + ".\n\n"
            + "In order to improve this feature, Thonny developers would love to know how "
            + "useful or confusing these messages were. We will only collect version "
            + "information and the data you enter or approve on this form.",
            wraplength=550,
        )
        intro_label.grid(
            row=1, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15, 15)
        )

        tree_label = ttk.Label(
            main_frame,
            text="Which messages were helpful (H) or confusing (C)?       Click on  [  ]  to mark!",
        )
        tree_label.grid(
            row=2, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15, 0)
        )
        tree_frame = ui_utils.TreeFrame(
            main_frame,
            columns=["helpful", "confusing", "title", "group", "symbol"],
            displaycolumns=["helpful", "confusing", "title"],
            height=10,
            borderwidth=1,
            relief="groove",
        )
        tree_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=padx)
        self.tree = tree_frame.tree
        self.tree.column("helpful", width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column("confusing", width=30, anchor=tk.CENTER, stretch=False)
        self.tree.column("title", width=350, anchor=tk.W, stretch=True)

        self.tree.heading("helpful", text="H", anchor=tk.CENTER)
        self.tree.heading("confusing", text="C", anchor=tk.CENTER)
        self.tree.heading("title", text="Group / Message", anchor=tk.W)
        self.tree["show"] = ("headings",)
        self.tree.bind("<1>", self._on_tree_click, True)
        main_font = tk.font.nametofont("TkDefaultFont")
        bold_font = main_font.copy()
        bold_font.configure(weight="bold", size=main_font.cget("size"))
        self.tree.tag_configure("group", font=bold_font)

        self.include_thonny_id_var = tk.IntVar(value=1)
        include_thonny_id_check = ttk.Checkbutton(
            main_frame,
            variable=self.include_thonny_id_var,
            onvalue=1,
            offvalue=0,
            text="Include Thonny's installation time (allows us to group your submissions)",
        )
        include_thonny_id_check.grid(
            row=4, column=0, columnspan=3, sticky="nw", padx=padx, pady=(5, 0)
        )

        self.include_snapshots_var = tk.IntVar(value=1)
        include_snapshots_check = ttk.Checkbutton(
            main_frame,
            variable=self.include_snapshots_var,
            onvalue=1,
            offvalue=0,
            text="Include snapshots of the code and Assistant responses at each run",
        )
        include_snapshots_check.grid(
            row=5, column=0, columnspan=3, sticky="nw", padx=padx, pady=(0, 0)
        )

        comments_label = ttk.Label(main_frame, text="Any comments? Enhancement ideas?")
        comments_label.grid(
            row=6, column=0, columnspan=3, sticky="nw", padx=padx, pady=(15, 0)
        )
        self.comments_text_frame = tktextext.TextFrame(
            main_frame,
            vertical_scrollbar_style=scrollbar_style("Vertical"),
            horizontal_scrollbar_style=scrollbar_style("Horizontal"),
            horizontal_scrollbar_class=ui_utils.AutoScrollbar,
            wrap="word",
            font="TkDefaultFont",
            # cursor="arrow",
            padx=5,
            pady=5,
            height=4,
            borderwidth=1,
            relief="groove",
        )
        self.comments_text_frame.grid(
            row=7, column=0, columnspan=3, sticky="nsew", padx=padx
        )

        url_font = tk.font.nametofont("TkDefaultFont").copy()
        url_font.configure(underline=1, size=url_font.cget("size"))
        preview_link = ttk.Label(
            main_frame,
            text="(Preview the data to be sent)",
            style="Url.TLabel",
            cursor="hand2",
            font=url_font,
        )
        preview_link.bind("<1>", self._preview_submission_data, True)
        preview_link.grid(row=8, column=0, sticky="nw", padx=15, pady=15)

        submit_button = ttk.Button(
            main_frame, text="Submit", width=10, command=self._submit_data
        )
        submit_button.grid(row=8, column=0, sticky="ne", padx=0, pady=15)

        cancel_button = ttk.Button(
            main_frame, text="Cancel", width=7, command=self._close
        )
        cancel_button.grid(row=8, column=1, sticky="ne", padx=(10, 15), pady=15)

        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Escape>", self._close, True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=3)
        main_frame.rowconfigure(6, weight=2)

        self._empty_box = "[  ]"
        self._checked_box = "[X]"
        self._populate_tree()

    def _happened_in_shell(self):
        return self.main_file_path is None or self.main_file_path.lower() == "<pyshell>"

    def _populate_tree(self):
        groups = {}

        for snap in self.snapshots:
            if snap.get("exception_message") and snap.get("exception_suggestions"):
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

            for symbol, title in sorted(groups[group], key=lambda m: m[1]):
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

        value_index = int(column[1:]) - 1
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
            "ThonnyAssistantFeedback_"
            + datetime.datetime.now().isoformat().replace(":", ".")[:19]
            + ".txt",
        )
        data = self._collect_submission_data()
        with open(temp_path, "w", encoding="ascii") as fp:
            fp.write(data)

        if running_on_mac_os():
            subprocess.Popen(["open", "-e", temp_path])
        else:
            webbrowser.open(temp_path)

    def _collect_submission_data(self):
        tree_data = []

        for iid in self.tree.get_children():
            values = self.tree.item(iid, "values")
            tree_data.append(
                {
                    "helpful": values[0] == self._checked_box,
                    "confusing": values[1] == self._checked_box,
                    "message": values[2],
                    "group": values[3],
                    "symbol": values[4],
                }
            )

        submission = {
            "feedback_format_version": 1,
            "thonny_version": thonny.get_version(),
            "python_version": ".".join(map(str, sys.version_info[:3])),
            "message_feedback": tree_data,
            "comments": self.comments_text_frame.text.get("1.0", "end"),
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
            submission["thonny_timestamp"] = get_workbench().get_option(
                "general.configuration_creation_timestamp"
            )

        return json.dumps(submission, indent=2)

    def _submit_data(self):
        json_data = self._collect_submission_data()
        compressed_data = gzip.compress(json_data.encode("ascii"))

        def do_work():
            try:
                handle = urllib.request.urlopen(
                    "https://thonny.org/store_assistant_feedback.php",
                    data=compressed_data,
                    timeout=10,
                )
                return handle.read()
            except Exception as e:
                return str(e)

        result = ui_utils.run_with_waiting_dialog(
            self, do_work, description="Uploading"
        )
        if result == b"OK":
            if self.snapshots:
                last_timestamp = self.snapshots[-1]["timestamp"]
                _last_feedback_timestamps[self.main_file_path] = last_timestamp
            messagebox.showinfo(
                "Done!",
                "Thank you for the feedback!\n\nLet us know again when Assistant\nhelps or confuses you!",
                parent=get_workbench()
            )
            self._close()
        else:
            messagebox.showerror(
                "Problem",
                "Something went wrong:\n%s\n\nIf you don't mind, then try again later!"
                % result[:1000],
                parent=get_workbench()
            )

    def _select_unsent_snapshots(self, all_snapshots):
        if self.main_file_path not in _last_feedback_timestamps:
            return all_snapshots
        else:
            return [
                s
                for s in all_snapshots
                if s["timestamp"] > _last_feedback_timestamps[self.main_file_path]
            ]

    def _close(self, event=None):
        self.destroy()

    def _get_since_str(self):
        if not self.snapshots:
            assert self.main_file_path in _last_feedback_timestamps
            since = datetime.datetime.strptime(
                _last_feedback_timestamps[self.main_file_path], "%Y-%m-%dT%H:%M:%S"
            )
        else:
            since = datetime.datetime.strptime(
                self.snapshots[0]["timestamp"], "%Y-%m-%dT%H:%M:%S"
            )

        if since.date() == datetime.date.today() or (
            datetime.datetime.now() - since
        ) <= datetime.timedelta(hours=5):
            since_str = since.strftime("%X")
        else:
            # date and time without yer
            since_str = since.strftime("%c").replace(
                str(datetime.date.today().year), ""
            )

        # remove seconds
        if since_str.count(":") == 2:
            i = since_str.rfind(":")
            if (
                i > 0
                and len(since_str[i + 1 : i + 3]) == 2
                and since_str[i + 1 : i + 3].isnumeric()
            ):
                since_str = since_str[:i] + since_str[i + 3 :]

        return since_str.strip()


def name_similarity(a, b):
    # TODO: tweak the result values
    a = a.replace("_", "")
    b = b.replace("_", "")

    minlen = min(len(a), len(b))

    if a.replace("0", "O").replace("1", "l") == b.replace("0", "O").replace("1", "l"):
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
    if (
        a[-1].isdigit()
        and not a[-2].isdigit()
        and b[-1].isdigit()
        and not b[-2].isdigit()
    ):
        return 0

    # same thing with _ + single char suffixes
    # (eg. location_a and location_b)
    if a[-2] == "_" and b[-2] == "_":
        return 0

    distance = levenshtein_damerau_distance(a, b, 5)

    if minlen <= 5:
        return max(8 - distance * 2, 0)
    elif minlen <= 10:
        return max(9 - distance * 2, 0)
    else:
        return max(10 - distance * 2, 0)


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
            module_names.add(node.module)

    imported_files = set()

    for file in {name + ext for ext in [".py", ".pyw"] for name in module_names}:
        possible_path = os.path.join(main_dir, file)
        if os.path.exists(possible_path):
            imported_files.add(possible_path)

    return imported_files
    # TODO: add recursion


def add_program_analyzer(cls):
    _program_analyzer_classes.append(cls)


def add_error_helper(error_type_name, helper_class):
    _error_helper_classes.setdefault(error_type_name, [])
    _error_helper_classes[error_type_name].append(helper_class)


def format_file_url(filename, lineno, col_offset):
    s = "thonny-editor://" + rst_utils.escape(filename).replace(" ", "%20")
    if lineno is not None:
        s += "#" + str(lineno)
        if col_offset is not None:
            s += ":" + str(col_offset)

    return s


def init():
    get_workbench().set_default("assistance.open_assistant_on_errors", True)
    get_workbench().set_default("assistance.open_assistant_on_warnings", False)
    get_workbench().set_default("assistance.disabled_checks", [])
    get_workbench().add_view(AssistantView, "Assistant", "se", visible_by_default=False)

