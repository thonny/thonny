import tkinter as tk
from logging import getLogger
from tkinter import messagebox
from typing import List, Optional, Union, cast

from thonny import editor_helpers, get_runner, get_workbench, lsp_types
from thonny.codeview import CodeViewText, SyntaxText, get_syntax_options_for_tag
from thonny.editor_helpers import DocuBox, EditorInfoBox
from thonny.languages import tr
from thonny.lsp_types import CompletionItem, CompletionParams, LspResponse, TextDocumentIdentifier
from thonny.misc_utils import running_on_mac_os
from thonny.shell import ShellText
from thonny.ui_utils import (
    alt_is_pressed_without_char,
    command_is_pressed,
    control_is_pressed,
    ems_to_pixels,
)

logger = getLogger(__name__)

"""
Completions get computed on the backend, therefore getting the completions is
asynchronous.
"""


class CompletionsDetailsBox(DocuBox):
    def __init__(self, completions_box: "CompletionsBox"):
        super().__init__()
        self._completions_box = completions_box

    def _get_related_box(self) -> Optional["EditorInfoBox"]:
        return self._completions_box


class CompletionsBox(EditorInfoBox):
    def __init__(self, completer: "Completer"):
        super().__init__()
        self._completer = completer
        self._listbox = tk.Listbox(
            self,
            font="EditorFont",
            activestyle="dotbox",
            exportselection=False,
            highlightthickness=0,
            borderwidth=0,
            height=5,
        )
        self._listbox.grid()
        self._tweaking_listbox_selection = False
        self._details_box: Optional[CompletionsDetailsBox] = None
        self._completions: List[lsp_types.CompletionItem] = []

        self._listbox.bind("<<ListboxSelect>>", self._on_select_item_via_event, True)

        # for cases when Listbox gets focus
        self.bind("<Return>", self._insert_current_selection)
        self.bind("<Tab>", self._insert_current_selection_replace_suffix)
        self.bind("<Double-Button-1>", self._insert_current_selection)

        self._update_theme()

    def present_completions(
        self, text: SyntaxText, completions: List[lsp_types.CompletionItem]
    ) -> None:
        # Next events need to know this
        for comp in completions:
            print("COMP", comp)
        assert completions
        self._target_text_widget = text
        self._check_bind_for_keypress(text)

        # Check if user typed an underscore,
        # if not then don't show names starting with '_'
        """TODO: try both fuzzy and non-fuzzy completions
        source = text.get("insert linestart", tk.INSERT)
        try:
            current_source_chunk = re.split(r"\W", source)[-1]
        except IndexError:
            current_source_chunk = ""

        if current_source_chunk.startswith("_"):
            filtered_completions = all_completions
        else:
            filtered_completions = [c for c in all_completions if not c.get("name", "_").startswith("_")]
            if len(filtered_completions) < 5:
                filtered_completions = all_completions
        
        self._completions = filtered_completions
        """

        self._completions = completions

        # broadcast logging info
        row, column = editor_helpers.get_cursor_position(text)
        if isinstance(text, ShellText):
            row -= text.get_current_line_ls_offset()
            column -= text.get_current_column_ls_offset()

        get_workbench().event_generate(
            "AutocompleteProposal",
            text_widget=text,
            row=row,
            column=column,
            proposal_count=len(completions),
        )

        # present
        if len(completions) == 0:
            self.hide()
            return

        self._listbox.delete(0, self._listbox.size())
        self._listbox.insert(0, *[c.label for c in completions])
        self._listbox.activate(0)
        self._listbox.selection_set(0)

        max_visible_items = 10
        self._listbox["height"] = min(len(completions), max_visible_items)

        _, _, _, list_row_height = self._listbox.bbox(0)
        # the measurement is not accurate, but good enough for deciding whether
        # the box should be above or below the current line.
        # Actual placement will be managed otherwise
        approx_box_height = round(list_row_height * (self._listbox["height"] + 0.5))

        # TODO: try to align with the start of the word
        # name_start_index = "insert-%dc" % completions[0].prefix_length
        name_start_index = "insert"

        self._show_on_target_text(name_start_index, approx_box_height, "below")

        self._check_request_details()

    def _get_related_box(self) -> Optional["EditorInfoBox"]:
        return self._details_box

    def tweak_first_appearance(self):
        super().tweak_first_appearance()
        if running_on_mac_os():
            self.update()
            self._listbox.grid_remove()
            self._listbox.grid()

    def _get_current_completion_index(self):
        selected = self._listbox.curselection()
        if len(selected) == 0:
            return 0
        else:
            return selected[0]

    def _move_selection(self, delta):
        old_flag = self._tweaking_listbox_selection
        self._tweaking_listbox_selection = True
        try:
            index = self._get_current_completion_index()
            index += delta
            index = max(0, min(self._listbox.size() - 1, index))

            self._listbox.selection_clear(0, self._listbox.size() - 1)
            self._listbox.selection_set(index)
            self._listbox.see(index)
            self._listbox.activate(index)
            self._check_request_details()
        finally:
            self._tweaking_listbox_selection = old_flag

    def _update_theme(self, event=None):
        gutter_opts = get_syntax_options_for_tag("GUTTER")
        text_opts = get_syntax_options_for_tag("TEXT")
        self._listbox["background"] = gutter_opts["background"]
        self._listbox["foreground"] = text_opts["foreground"]

    def _on_select_item_via_event(self, event=None) -> None:
        if self._tweaking_listbox_selection:
            return

        self._check_request_details()

    def _check_request_details(self) -> None:
        if not self.winfo_ismapped():
            # can happen, see https://github.com/thonny/thonny/issues/2162
            return

        if (
            self._details_box
            and self._details_box.is_visible()
            or get_workbench().get_option("edit.automatic_completion_details")
        ):
            self.request_details()

    def _on_text_keypress(self, event=None):
        if not self.is_visible():
            return None

        if event.keysym in ["Up", "KP_Up"]:
            self._move_selection(-1)
            return "break"
        elif event.keysym in ["Down", "KP_Down"]:
            self._move_selection(1)
            return "break"
        elif event.keysym in ["Return", "KP_Enter"]:
            assert self._listbox.size() > 0
            self._insert_current_selection()
            return "break"
        elif event.keysym == "Tab":
            assert self._listbox.size() > 0
            self._insert_current_selection_replace_suffix()
            return "break"
        elif event.keysym in ["BackSpace", "Left", "Right", "KP_Left", "KP_Right"]:
            self.after_idle(
                lambda: self._completer.request_completions_for_text(self._target_text_widget)
            )
        elif (
            event.char
            and not _is_python_name_char(event.char)
            and event.char != "."
            and not control_is_pressed(event)
        ):
            self.hide(event)

        return None

    def _insert_current_selection(self, event=None):
        self._insert_completion(self._get_current_completion(), replace_suffix=False)

    def _insert_current_selection_replace_suffix(self, event=None):
        self._insert_completion(self._get_current_completion(), replace_suffix=True)

    def _get_current_completion(self) -> Optional[CompletionItem]:
        sel = self._listbox.curselection()
        if len(sel) != 1:
            return None

        return self._completions[sel[0]]

    def _insert_completion(self, completion: CompletionItem, replace_suffix: bool) -> None:
        if completion.textEdit is not None:
            raise RuntimeError("TODO: handle textEdit")

        if completion.insertText is not None:
            if completion.insertTextFormat == lsp_types.InsertTextFormat.Snippet:
                raise RuntimeError("TODO support snippets")
            if completion.insertTextMode == lsp_types.InsertTextMode.AdjustIndentation:
                raise RuntimeError("TODO support adjust indentation")
            insert_text = completion.insertText
        else:
            assert completion.label is not None
            insert_text = completion.label

        prefix_start_index = self._find_completion_insertion_index()
        typed_prefix = self._target_text_widget.get(prefix_start_index, "insert")

        get_workbench().event_generate(
            "AutocompleteInsertion",
            text_widget=self._target_text_widget,
            typed_prefix=typed_prefix,
            replace_suffix=replace_suffix,
            completed_name=insert_text,
        )

        # Before insertion need to delete prefix, because it may not be name's prefix
        # (eg. with different case or even more different with fuzzy completions)
        self._target_text_widget.direct_delete(prefix_start_index, "insert")
        self._target_text_widget.insert("insert", insert_text)

        if replace_suffix:
            did_replace_suffix = False
            while _is_python_name_char(self._target_text_widget.get("insert")):
                self._target_text_widget.direct_delete("insert")
                did_replace_suffix = True

            last_char_inserted = self._target_text_widget.get("insert -1 chars")
            if (
                did_replace_suffix
                and last_char_inserted in ["(", "="]
                and self._target_text_widget.get("insert") == last_char_inserted
            ):
                self._target_text_widget.direct_delete("insert")

        get_workbench().event_generate(
            "AutocompletionInserted",
            text_widget=self._target_text_widget,
            typed_prefix=typed_prefix,
            replace_suffix=replace_suffix,
            completed_name=insert_text,
        )

        self.hide()

    def _find_completion_insertion_index(self):
        line, col = map(int, self._target_text_widget.index("insert").split("."))
        while col > 0:
            char_at_left: str = self._target_text_widget.get(f"{line}.{col-1}")
            if not char_at_left.isidentifier():
                break
            col -= 1

        return f"{line}.{col}"

    def request_details(self) -> None:
        completion = self._get_current_completion()

        if not self._details_box:
            self._details_box = CompletionsDetailsBox(self)

        self._details_box.set_content(completion)

        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is not None:
            # TODO: cancel previous request
            ls_proxy.unbind_request_handler(self._handle_details_response)
            ls_proxy.request_resolve_completion_item(completion, self._handle_details_response)

        self._show_next_to_completions()

    def _show_next_to_completions(self):
        self._details_box._show_on_screen(
            self.winfo_rootx() + self.winfo_width() + ems_to_pixels(0.5), self.winfo_rooty()
        )

    def _handle_details_response(self, response: LspResponse[CompletionItem]) -> None:
        if not self.is_visible():
            return

        basic_completion = self._get_current_completion()
        detailed_completion = response.get_result_or_raise()
        logger.debug("Got completion details: %r", detailed_completion)
        if detailed_completion.data != basic_completion.data:
            return

        self._update_completion(details=detailed_completion)

        if not self._details_box:
            self._details_box = CompletionsDetailsBox(self)

        self._details_box.set_content(detailed_completion)

        self._show_next_to_completions()

    def _update_completion(self, details: CompletionItem) -> None:
        # logger.debug("Handling completion details %r", details)
        for i, comp in enumerate(self._completions):
            assert isinstance(comp, CompletionItem)
            if comp.data == details.data:
                comp.label = details.label
                comp.detail = details.detail
                comp.labelDetails = details.labelDetails
                comp.documentation = details.documentation

                sel = self._listbox.curselection()
                old_flag = self._tweaking_listbox_selection
                self._tweaking_listbox_selection = True
                try:
                    self._listbox.delete(i)
                    self._listbox.insert(i, comp.label)
                    if len(sel) == 1:
                        self._listbox.selection_set(sel[0])
                        self._listbox.activate(sel[0])
                    break
                finally:
                    self._tweaking_listbox_selection = old_flag


class Completer:
    """
    Manages completion requests and responses.
    Delegates user interactions with completions to CompletionsBox.
    """

    def __init__(self):
        self._last_request_text: Optional[SyntaxText] = None
        logger.debug("Creating Completer")
        self._completions_box: Optional[CompletionsBox] = None

        get_workbench().bind_class("EditorCodeViewText", "<Key>", self._on_keypress, True)
        get_workbench().bind_class("ShellText", "<Key>", self._on_keypress, True)
        get_workbench().bind(
            "editor_autocomplete_response", self._handle_completions_response, True
        )
        get_workbench().bind("shell_autocomplete_response", self._handle_completions_response, True)

    def request_completions(self, event=None) -> None:
        if self._box_is_visible():
            self._completions_box.request_details()
            return

        text = editor_helpers.get_active_text_widget()
        if text:
            self.request_completions_for_text(text)
        else:
            get_workbench().bell()

    def _should_open_box_automatically(self, event):
        assert isinstance(event.widget, tk.Text)
        if not get_workbench().get_option("edit.automatic_completions"):
            return False

        # Don't autocomplete inside comments
        line_prefix = event.widget.get("insert linestart", "insert")
        if "#" in line_prefix:
            # not very precise (eg. when inside a string), but good enough
            return False

        return True

    def _box_is_visible(self):
        if not self._completions_box:
            return False

        return self._completions_box.is_visible()

    def _close_box(self):
        if self._completions_box:
            self._completions_box.hide()

    def _on_keypress(self, event: tk.Event) -> None:
        self.cancel_active_request()
        runner = get_runner()
        if not runner or runner.is_running():
            return

        if (
            control_is_pressed(event)
            or command_is_pressed(event)
            or alt_is_pressed_without_char(event)
        ):
            return

        widget = event.widget
        if not widget or not isinstance(widget, SyntaxText):
            return

        if not widget.is_python_text():
            return

        if widget.is_read_only():
            return

        if not self._box_is_visible() and not self._should_open_box_automatically(event):
            return

        if event.keysym == "Escape":
            # Closing is handled by the box itself
            return

        if not event.char:
            # movement keypresses are handled by the box
            return

        if (
            not self._box_is_visible()
            and not _is_python_name_char(event.char)
            and not self._is_start_of_an_attribute(event)
        ):
            # non-word chars are allowed only while the box is already open
            return

        widget.after_idle(lambda: self.request_completions_for_text(widget))

    def _is_start_of_an_attribute(self, event: tk.Event) -> bool:
        if event.char != ".":
            return False

        text = cast(tk.Text, event.widget)
        preceding = text.get("insert -2 chars")
        if preceding.isnumeric():
            return False

        return True

    def cancel_active_request(self) -> None:
        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is not None:
            # TODO: actually cancel
            ls_proxy.unbind_request_handler(self._handle_completions_response)

    def request_completions_for_text(self, text: SyntaxText) -> None:
        ls_proxy = get_workbench().get_main_language_server_proxy()
        if ls_proxy is None:
            return

        ls_proxy.unbind_request_handler(self._handle_completions_response)
        # TODO: cancel last unhandled request

        if isinstance(text, ShellText):
            text.send_changes_to_language_server()
            uri = text.get_ls_uri()
            position = editor_helpers.get_cursor_ls_position(
                text, text.get_current_line_ls_offset(), text.get_current_column_ls_offset()
            )
        else:
            editor = get_workbench().get_editor_notebook().get_current_editor()
            if editor.get_text_widget() is not text:
                logger.warning("Unexpected completions request in %r", text)
                return

            editor.send_changes_to_primed_servers()
            uri = editor.get_uri()
            position = editor_helpers.get_cursor_ls_position(text)

        if uri is None:
            # TODO:
            return

        self._last_request_text = text
        ls_proxy.request_completion(
            CompletionParams(textDocument=TextDocumentIdentifier(uri=uri), position=position),
            self._handle_completions_response,
        )

    def _handle_completions_response(
        self,
        response: LspResponse[
            Union[List[lsp_types.CompletionItem], lsp_types.CompletionList, None]
        ],
    ) -> None:
        error = response.get_error()
        if error is not None:
            self._close_box()
            messagebox.showerror("Autocomplete error", error.message, master=get_workbench())
            return

        if not self._last_request_text:
            logger.warning("Completions response without _last_request_text")
            return

        result = response.get_result_or_raise()
        if result is None:
            logger.info("None completions response")
            return

        completions: List[lsp_types.CompletionItem]
        if isinstance(result, list):
            completions = result
            is_incomplete = False
            item_defaults = None
        else:
            completions = result.items
            is_incomplete = result.isIncomplete
            item_defaults = result.itemDefaults

        assert not item_defaults

        if len(completions) == 0:
            # the user typed something which is not completable
            self._close_box()
            return
        else:
            if not self._completions_box:
                self._completions_box = CompletionsBox(self)
            self._completions_box.present_completions(self._last_request_text, completions)

    def patched_perform_midline_tab(self, event):
        self.cancel_active_request()

        if not event or not isinstance(event.widget, SyntaxText):
            return
        text = event.widget

        if text.is_python_text():
            if isinstance(text, ShellText):
                option_name = "edit.tab_request_completions_in_shell"
            else:
                option_name = "edit.tab_request_completions_in_editors"

            if get_workbench().get_option(option_name):
                if not text.has_selection():
                    self.request_completions_for_text(text)
                    return "break"
                else:
                    return None

        return text.perform_dumb_tab(event)


def _is_python_name_char(c: str) -> bool:
    return c.isalnum() or c == "_"


def load_plugin() -> None:
    completer = Completer()

    def can_complete():
        runner = get_runner()
        return runner and not runner.is_running()

    get_workbench().add_command(
        "autocomplete",
        "edit",
        tr("Auto-complete"),
        completer.request_completions,
        default_sequence="<Control-space>",
        tester=can_complete,
    )

    get_workbench().set_default("edit.tab_request_completions_in_editors", False)
    get_workbench().set_default("edit.tab_request_completions_in_shell", True)
    get_workbench().set_default("edit.automatic_completions", False)
    get_workbench().set_default("edit.automatic_completion_details", True)

    CodeViewText.perform_midline_tab = completer.patched_perform_midline_tab
    ShellText.perform_midline_tab = completer.patched_perform_midline_tab
