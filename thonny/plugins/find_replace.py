# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from thonny import get_workbench
from thonny.languages import tr
from thonny.ui_utils import CommonDialog, select_sequence

# TODO - consider moving the cmd_find method to main class in order to pass the editornotebook reference
# TODO - logging
# TODO - instead of text.see method create another one which attempts to center the line where the text was found
# TODO - test on mac and linux

# Handles the find dialog display and the logic of searching.
# Communicates with the codeview that is passed to the constructor as a parameter.

_active_find_dialog = None


class FindDialog(CommonDialog):

    last_searched_word = None

    def __init__(self, master):
        padx = 15
        pady = 15

        super().__init__(master, takefocus=1, background="pink")
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=1, sticky="nsew")
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        self.codeview = master

        # references to the current set of passive found tags e.g. all words that match the searched term but are not the active string
        self.passive_found_tags = set()
        self.active_found_tag = None  # reference to the currently active (centered) found string

        # a tuple containing the start and indexes of the last processed string
        # if the last action was find, then the end index is start index + 1
        # if the last action was replace, then the indexes correspond to the start
        # and end of the inserted word
        self.last_processed_indexes = None
        self.last_search_case = None  # case sensitivity value used during the last search

        # set up window display
        self.geometry(
            "+%d+%d"
            % (
                master.winfo_rootx() + master.winfo_width() // 2,
                master.winfo_rooty() + master.winfo_height() // 2 - 150,
            )
        )

        self.title(tr("Find & Replace"))
        self.resizable(height=tk.FALSE, width=tk.FALSE)
        self.transient(master)
        self.protocol("WM_DELETE_WINDOW", self._ok)

        # Find text label
        self.find_label = ttk.Label(main_frame, text=tr("Find:"))
        self.find_label.grid(column=0, row=0, sticky="w", padx=(padx, 0), pady=(pady, 0))

        # Find text field
        self.find_entry_var = tk.StringVar()
        self.find_entry = ttk.Entry(main_frame, textvariable=self.find_entry_var)
        self.find_entry.grid(column=1, row=0, columnspan=2, padx=(0, 10), pady=(pady, 0))
        if FindDialog.last_searched_word is not None:
            self.find_entry.insert(0, FindDialog.last_searched_word)

        # Replace text label
        self.replace_label = ttk.Label(main_frame, text=tr("Replace with:"))
        self.replace_label.grid(column=0, row=1, sticky="w", padx=(padx, 0))

        # Replace text field
        self.replace_entry = ttk.Entry(main_frame)
        self.replace_entry.grid(column=1, row=1, columnspan=2, padx=(0, 10))

        # Info text label (invisible by default, used to tell user that searched string was not found etc)
        self.infotext_label_var = tk.StringVar()
        self.infotext_label_var.set("")
        self.infotext_label = ttk.Label(
            main_frame, textvariable=self.infotext_label_var, foreground="red"
        )  # TODO - style to conf
        self.infotext_label.grid(column=0, row=2, columnspan=3, pady=3, padx=(padx, 0))

        # Case checkbox
        self.case_var = tk.IntVar()
        self.case_checkbutton = ttk.Checkbutton(
            main_frame, text=tr("Case sensitive"), variable=self.case_var
        )
        self.case_checkbutton.grid(column=0, row=3, padx=(padx, 0), pady=(0, pady))

        # Direction radiobuttons
        self.direction_var = tk.IntVar()
        self.up_radiobutton = ttk.Radiobutton(
            main_frame, text=tr("Up"), variable=self.direction_var, value=1
        )
        self.up_radiobutton.grid(column=1, row=3, pady=(0, pady))
        self.down_radiobutton = ttk.Radiobutton(
            main_frame, text=tr("Down"), variable=self.direction_var, value=2
        )
        self.down_radiobutton.grid(column=2, row=3, pady=(0, pady))
        self.down_radiobutton.invoke()

        # Find button - goes to the next occurrence
        button_width = 17
        self.find_button = ttk.Button(
            main_frame,
            text=tr("Find"),
            width=button_width,
            command=self._perform_find,
            default="active",
        )
        self.find_button.grid(column=3, row=0, sticky=tk.W + tk.E, pady=(pady, 0), padx=(0, padx))
        self.find_button.config(state="disabled")

        # Replace button - replaces the current occurrence, if it exists
        self.replace_button = ttk.Button(
            main_frame, text=tr("Replace"), width=button_width, command=self._perform_replace
        )
        self.replace_button.grid(column=3, row=1, sticky=tk.W + tk.E, padx=(0, padx))
        self.replace_button.config(state="disabled")

        # Replace + find button - replaces the current occurrence and goes to next
        self.replace_and_find_button = ttk.Button(
            main_frame,
            text=tr("Replace+Find"),
            width=button_width,
            command=self._perform_replace_and_find,
        )  # TODO - text to resources
        self.replace_and_find_button.grid(column=3, row=2, sticky=tk.W + tk.E, padx=(0, padx))
        self.replace_and_find_button.config(state="disabled")

        # Replace all button - replaces all occurrences
        self.replace_all_button = ttk.Button(
            main_frame,
            text=tr("Replace all"),
            width=button_width,
            command=self._perform_replace_all,
        )  # TODO - text to resources
        self.replace_all_button.grid(
            column=3, row=3, sticky=tk.W + tk.E, padx=(0, padx), pady=(0, pady)
        )
        if FindDialog.last_searched_word == None:
            self.replace_all_button.config(state="disabled")

        # create bindings
        self.bind("<Escape>", self._ok)
        self.find_entry_var.trace("w", self._update_button_statuses)
        self.find_entry.bind("<Return>", self._perform_find, True)
        self.bind("<F3>", self._perform_find, True)
        self.find_entry.bind("<KP_Enter>", self._perform_find, True)

        self._update_button_statuses()

        global _active_find_dialog
        _active_find_dialog = self
        self.focus_set()

    def focus_set(self):
        self.find_entry.focus_set()
        self.find_entry.selection_range(0, tk.END)

    # callback for text modifications on the find entry object, used to dynamically enable and disable buttons
    def _update_button_statuses(self, *args):
        find_text = self.find_entry_var.get()
        if len(find_text) == 0:
            self.find_button.config(state="disabled")
            self.replace_and_find_button.config(state="disabled")
            self.replace_all_button.config(state="disabled")
        else:
            self.find_button.config(state="normal")
            self.replace_all_button.config(state="normal")
            if self.active_found_tag is not None:
                self.replace_and_find_button.config(state="normal")

    # returns whether the next search is case sensitive based on the current value of the case sensitivity checkbox
    def _is_search_case_sensitive(self):
        return self.case_var.get() != 0

    # returns whether the current search is a repeat of the last searched based on all significant values
    def _repeats_last_search(self, tofind):
        return (
            tofind == FindDialog.last_searched_word
            and self.last_processed_indexes is not None
            and self.last_search_case == self._is_search_case_sensitive()
        )

    # performs the replace operation - replaces the currently active found word with what is entered in the replace field
    def _perform_replace(self):

        # nothing is currently in found status
        if self.active_found_tag == None:
            return

        # get the found word bounds
        del_start = self.active_found_tag[0]
        del_end = self.active_found_tag[1]

        # erase all tags - these would not be correct anyway after new word is inserted
        self._remove_all_tags()
        toreplace = self.replace_entry.get()  # get the text to replace

        # delete the found word
        self.codeview.text.delete(del_start, del_end)
        # insert the new word
        self.codeview.text.insert(del_start, toreplace)
        # mark the inserted word boundaries
        self.last_processed_indexes = (
            del_start,
            self.codeview.text.index("%s+%dc" % (del_start, len(toreplace))),
        )

        get_workbench().event_generate(
            "Replace",
            widget=self.codeview.text,
            old_text=self.codeview.text.get(del_start, del_end),
            new_text=toreplace,
        )

    # performs the replace operation followed by a new find
    def _perform_replace_and_find(self):
        if self.active_found_tag == None:
            return
        self._perform_replace()
        self._perform_find()

    # replaces all occurrences of the search string with the replace string
    def _perform_replace_all(self):

        tofind = self.find_entry.get()
        if len(tofind) == 0:
            self.infotext_label_var.set(tr("Enter string to be replaced."))
            return

        toreplace = self.replace_entry.get()

        self._remove_all_tags()

        currentpos = 1.0
        end = self.codeview.text.index("end")

        while True:
            currentpos = self.codeview.text.search(
                tofind, currentpos, end, nocase=not self._is_search_case_sensitive()
            )
            if currentpos == "":
                break

            endpos = self.codeview.text.index("%s+%dc" % (currentpos, len(tofind)))

            self.codeview.text.delete(currentpos, endpos)

            if toreplace != "":
                self.codeview.text.insert(currentpos, toreplace)

            currentpos = self.codeview.text.index("%s+%dc" % (currentpos, len(toreplace)))

        get_workbench().event_generate(
            "ReplaceAll", widget=self.codeview.text, old_text=tofind, new_text=toreplace
        )

    def _perform_find(self, event=None):
        self.infotext_label_var.set("")  # reset the info label text
        tofind = self.find_entry.get()  # get the text to find
        if len(tofind) == 0:  # in the case of empty string, cancel
            return  # TODO - set warning text to info label?

        search_backwards = (
            self.direction_var.get() == 1
        )  # True - search backwards ('up'), False - forwards ('down')

        if self._repeats_last_search(
            tofind
        ):  # continuing previous search, find the next occurrence
            if search_backwards:
                search_start_index = self.last_processed_indexes[0]
            else:
                search_start_index = self.last_processed_indexes[1]

            if self.active_found_tag is not None:
                self.codeview.text.tag_remove(
                    "current_found", self.active_found_tag[0], self.active_found_tag[1]
                )  # remove the active tag from the previously found string
                self.passive_found_tags.add(
                    (self.active_found_tag[0], self.active_found_tag[1])
                )  # ..and set it to passive instead
                self.codeview.text.tag_add(
                    "found", self.active_found_tag[0], self.active_found_tag[1]
                )

        else:  # start a new search, start from the current insert line position
            if self.active_found_tag is not None:
                self.codeview.text.tag_remove(
                    "current_found", self.active_found_tag[0], self.active_found_tag[1]
                )  # remove the previous active tag if it was present
            for tag in self.passive_found_tags:
                self.codeview.text.tag_remove(
                    "found", tag[0], tag[1]
                )  # and remove all the previous passive tags that were present
            search_start_index = self.codeview.text.index(
                "insert"
            )  # start searching from the current insert position
            self._find_and_tag_all(tofind)  # set the passive tag to ALL found occurrences
            FindDialog.last_searched_word = tofind  # set the data about last search
            self.last_search_case = self._is_search_case_sensitive()

        wordstart = self.codeview.text.search(
            tofind,
            search_start_index,
            backwards=search_backwards,
            forwards=not search_backwards,
            nocase=not self._is_search_case_sensitive(),
        )  # performs the search and sets the start index of the found string
        if len(wordstart) == 0:
            self.infotext_label_var.set(
                tr("The specified text was not found!")
            )  # TODO - better text, also move it to the texts resources list
            self.replace_and_find_button.config(state="disabled")
            self.replace_button.config(state="disabled")
            return

        self.last_processed_indexes = (
            wordstart,
            self.codeview.text.index("%s+1c" % wordstart),
        )  # sets the data about last search
        self.codeview.text.see(wordstart)  # moves the view to the found index
        wordend = self.codeview.text.index(
            "%s+%dc" % (wordstart, len(tofind))
        )  # calculates the end index of the found string
        self.codeview.text.tag_add(
            "current_found", wordstart, wordend
        )  # tags the found word as active
        self.active_found_tag = (wordstart, wordend)
        self.replace_and_find_button.config(state="normal")
        self.replace_button.config(state="normal")

        get_workbench().event_generate(
            "Find",
            widget=self.codeview.text,
            text=tofind,
            backwards=search_backwards,
            case_sensitive=self._is_search_case_sensitive(),
        )

    def _ok(self, event=None):
        """Called when the window is closed. responsible for handling all cleanup."""
        self._remove_all_tags()
        self.destroy()

        global _active_find_dialog
        _active_find_dialog = None

    # removes the active tag and all passive tags
    def _remove_all_tags(self):
        for tag in self.passive_found_tags:
            self.codeview.text.tag_remove("found", tag[0], tag[1])  # removes the passive tags

        if self.active_found_tag is not None:
            self.codeview.text.tag_remove(
                "current_found", self.active_found_tag[0], self.active_found_tag[1]
            )  # removes the currently active tag

        self.active_found_tag = None
        self.replace_and_find_button.config(state="disabled")
        self.replace_button.config(state="disabled")

    # finds and tags all occurrences of the searched term
    def _find_and_tag_all(self, tofind, force=False):
        # TODO - to be improved so only whole words are matched - surrounded by whitespace, parentheses, brackets, colons, semicolons, points, plus, minus

        if (
            self._repeats_last_search(tofind) and not force
        ):  # nothing to do, all passive tags already set
            return

        currentpos = 1.0
        end = self.codeview.text.index("end")

        # searches and tags until the end of codeview
        while True:
            currentpos = self.codeview.text.search(
                tofind, currentpos, end, nocase=not self._is_search_case_sensitive()
            )
            if currentpos == "":
                break

            endpos = self.codeview.text.index("%s+%dc" % (currentpos, len(tofind)))
            self.passive_found_tags.add((currentpos, endpos))
            self.codeview.text.tag_add("found", currentpos, endpos)

            currentpos = self.codeview.text.index("%s+1c" % currentpos)


def load_plugin() -> None:
    def cmd_open_find_dialog():
        if _active_find_dialog is not None:
            _active_find_dialog.focus_set()
        else:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            if editor:
                FindDialog(editor._code_view)

    def find_f3(event):
        if _active_find_dialog is None:
            cmd_open_find_dialog()
        else:
            _active_find_dialog._perform_find(event)

    get_workbench().add_command(
        "OpenFindDialog",
        "edit",
        tr("Find & Replace"),
        cmd_open_find_dialog,
        default_sequence=select_sequence("<Control-f>", "<Command-f>"),
        extra_sequences=["<Control-Greek_phi>"],
    )

    get_workbench().bind("<F3>", find_f3, True)
