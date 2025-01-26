# -*- coding: utf-8 -*-
import os.path
import re
import time
import tkinter as tk
import warnings
from _tkinter import TclError
from logging import exception, getLogger
from tkinter import messagebox, simpledialog, ttk
from typing import List, Literal, Optional, Union, cast

from thonny import get_runner, get_workbench
from thonny.base_file_browser import ask_backend_path, choose_node_for_file_operations
from thonny.codeview import BinaryFileException, CodeView, CodeViewText
from thonny.common import (
    InlineCommand,
    TextRange,
    ToplevelResponse,
    UserError,
    is_same_path,
    normpath_with_actual_case,
    universal_dirname,
)
from thonny.custom_notebook import CustomNotebook, CustomNotebookPage, CustomNotebookTab
from thonny.languages import tr
from thonny.lsp_proxy import LanguageServerProxy
from thonny.lsp_types import (
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    Position,
    Range,
    RangedTextDocumentContentChangeEvent,
    TextDocumentIdentifier,
    TextDocumentItem,
    VersionedTextDocumentIdentifier,
)
from thonny.misc_utils import (
    PLACEHOLDER_URI,
    UNTITLED_URI_SCHEME,
    ensure_uri,
    format_untitled_uri,
    is_local_uri,
    is_remote_uri,
    is_untitled_uri,
    local_path_to_uri,
    make_legacy_remote_path,
    remote_path_to_uri,
    running_on_mac_os,
    running_on_windows,
    uri_to_legacy_filename,
    uri_to_long_title,
    uri_to_target_path,
)
from thonny.tktextext import rebind_control_a
from thonny.ui_utils import askopenfilename, asksaveasfilename, get_beam_cursor, select_sequence

PYTHON_FILES_STR = tr("Python files")
_dialog_filetypes = [(PYTHON_FILES_STR, ".py .pyw .pyi .pyde .pyx"), (tr("all files"), ".*")]

PYTHON_EXTENSIONS = {"py", "pyw", "pyi", "pyde"}
PYTHONLIKE_EXTENSIONS = {"pyx", "pyde"}
DEBOUNCE_SECONDS = 0.5


logger = getLogger(__name__)


class EditorCodeViewText(CodeViewText):
    """Allows separate class binding for CodeViewTexts which are inside editors"""

    def __init__(self, master=None, cnf={}, **kw):
        super().__init__(
            master=master,
            cnf=cnf,
            **kw,
        )
        self.bindtags(self.bindtags() + ("EditorCodeViewText",))


class BaseEditor(ttk.Frame):
    def __init__(
        self, master, uri: str, propose_remove_line_numbers: bool, suppress_events: bool = False
    ):
        self._uri: str = uri

        ttk.Frame.__init__(self, master)

        self._code_view = CodeView(
            self,
            propose_remove_line_numbers=propose_remove_line_numbers,
            font="EditorFont",
            text_class=EditorCodeViewText,
            cursor=get_beam_cursor(),
            suppress_events=suppress_events,
        )
        self._code_view.grid(row=0, column=0, sticky=tk.NSEW, in_=self)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self._file_source = None
        self.update_file_type()

    def is_untitled(self) -> bool:
        return is_untitled_uri(self.get_uri())

    def is_local(self) -> bool:
        return is_local_uri(self.get_uri())

    def is_remote(self) -> bool:
        return is_remote_uri(self.get_uri())

    def get_uri(self) -> str:
        return self._uri

    def set_uri(self, uri: str) -> None:
        self._uri = uri
        self.update_file_type()
        self.update_appearance()

    def get_target_path(self) -> Optional[str]:
        if self.is_untitled():
            return None

        return uri_to_target_path(self.get_uri())

    def update_appearance(self):
        self._code_view.set_gutter_visibility(
            get_workbench().get_option("view.show_line_numbers") or get_workbench().in_simple_mode()
        )
        self._code_view.set_line_length_margin(
            get_workbench().get_option("view.recommended_line_length")
        )
        self._code_view.text.update_tab_stops()
        self._code_view.text.indent_width = get_workbench().get_option("edit.indent_width")
        self._code_view.text.tab_width = get_workbench().get_option("edit.tab_width")
        self._code_view.text.event_generate("<<UpdateAppearance>>")
        self._code_view.grid_main_widgets()

    def update_file_type(self):
        if self.is_untitled():
            self._code_view.set_file_type("python")
        else:
            ext = self.get_target_path().split(".")[-1].lower()
            if ext in PYTHON_EXTENSIONS:
                file_type = "python"
            elif ext in PYTHONLIKE_EXTENSIONS:
                file_type = "pythonlike"
            else:
                file_type = None

            self._code_view.set_file_type(file_type)

    def is_modified(self):
        return bool(self._code_view.text.edit_modified())

    def get_title(self):
        if self.is_untitled():
            result = format_untitled_uri(self.get_uri())
        elif self.is_remote():
            name = self.get_target_path().split("/")[-1]
            result = "[ " + name + " ]"
        else:
            assert self.is_local()
            result = self.shorten_filename_for_title(self.get_target_path())

        if self.is_modified():
            result += " *"

        return result

    def shorten_filename_for_title(self, path: str) -> str:
        return os.path.basename(path)

    def get_text_widget(self) -> CodeViewText:
        return self._code_view.text

    def get_code_view(self):
        # TODO: try to get rid of this
        return self._code_view


class Editor(BaseEditor):
    def __init__(self, master: "EditorNotebook", uri: str):
        self._initialized_ls_proxies: List[LanguageServerProxy] = (
            get_workbench().get_initialized_ls_proxies()
        )
        self._primed_ls_proxies: List[LanguageServerProxy] = []
        self.containing_notebook: EditorNotebook = master
        super().__init__(master, uri, propose_remove_line_numbers=True)
        get_workbench().event_generate(
            "EditorTextCreated", editor=self, text_widget=self.get_text_widget()
        )

        self._last_change_time: float = 0
        self._unpublished_incremental_changes = []
        self._content_at_server: Optional[str] = None  # for validating incremental updates

        self._last_fully_published_version: Optional[int] = None

        self._last_known_mtime = None

        self._code_view.text.bind("<<Modified>>", self._on_text_modified, True)
        self._code_view.text.bind("<<TextChange>>", self._on_text_change, True)
        self._code_view.text.bind("<Control-Tab>", self._control_tab, True)
        get_workbench().bind("TextInsert", self._register_text_change, True)
        get_workbench().bind("TextDelete", self._register_text_change, True)

        get_workbench().bind("DebuggerResponse", self._listen_debugger_progress, True)
        get_workbench().bind("ToplevelResponse", self._listen_for_toplevel_response, True)
        get_workbench().bind("LanguageServerInitialized", self._language_server_initialized, True)
        get_workbench().bind("LanguageServerInvalidated", self._language_server_invalidated, True)

        self.update_appearance()

        if is_local_uri(self._uri) or is_remote_uri(self._uri):
            successful_load = self._load_file(self._uri)
            if not successful_load:
                # Encoding errors were communicated to the user already during _load_file
                raise UserError(f"Could not load {self._uri}")
        else:
            assert is_untitled_uri(self._uri)
            self._update_language_servers()

    def get_content(self, up_to_end=False) -> str:
        return self._code_view.get_content(up_to_end=up_to_end)

    def get_filename(self, try_hard=False):
        warnings.warn(
            "Editor.get_filename is deprecated. Use get_target_path instead", DeprecationWarning
        )

        if self.is_untitled() and try_hard:
            self.save_file()

        path = self.get_target_path()
        if path is None:
            return None

        if self.is_remote():
            return make_legacy_remote_path(path)
        else:
            return path

    def get_file_source(self):
        return self._file_source

    def set_uri(self, uri: str) -> None:
        old_uri = self._uri
        if old_uri != uri:
            self._disconnect_from_language_servers()

        super().set_uri(uri)
        self.update_title()
        if old_uri != uri:
            self._update_language_servers()

    def check_for_external_changes(self):
        if self.is_untitled() or self.is_remote():
            return

        if self._last_known_mtime is None:
            return

        elif not os.path.exists(self.get_target_path()):
            self.containing_notebook.select(self)

            if messagebox.askyesno(
                tr("File is gone"),
                tr("Looks like '%s' was deleted or moved.") % self.get_target_path()
                + "\n\n"
                + tr("Do you want to also close the editor?"),
                master=self,
            ):
                self.containing_notebook.close_editor(self)
            else:
                self.get_text_widget().edit_modified(True)
                self._last_known_mtime = None

        elif os.path.getmtime(self.get_target_path()) != self._last_known_mtime:
            skip_confirmation = not self.is_modified() and get_workbench().get_option(
                "edit.auto_refresh_saved_files"
            )
            if not skip_confirmation:
                self.containing_notebook.select(self)

            if skip_confirmation or messagebox.askyesno(
                tr("External modification"),
                tr("Looks like '%s' was modified outside of the editor.") % self.get_target_path()
                + "\n\n"
                + tr(
                    "Do you want to discard current editor content and reload the file from disk?"
                ),
                master=self,
            ):
                prev_location = self.get_text_widget().index("insert")
                self._load_file(self.get_uri(), keep_undo=True)
                try:
                    self.get_text_widget().mark_set("insert", prev_location)
                    self.see_line(int(prev_location.split(".")[0]))
                except Exception:
                    logger.exception("Could not restore previous location")

            self._last_known_mtime = os.path.getmtime(self.get_target_path())

    def get_long_description(self):
        result = uri_to_long_title(self._uri)

        try:
            index = self._code_view.text.index("insert")
            if index and "." in index:
                line, col = index.split(".")
                result += "  @  {} : {}".format(line, int(col) + 1)
        except Exception:
            exception("Finding cursor location")

        return result

    def _load_file(self, uri: str, keep_undo=False):
        try:
            if is_remote_uri(uri):
                result = self._load_remote_file(uri_to_target_path(uri))
            else:
                result = self._load_local_file(uri_to_target_path(uri), keep_undo)
            if not result:
                return False
            self.set_uri(uri)

        except BinaryFileException:
            messagebox.showerror(
                tr("Problem"), tr("%s doesn't look like a text file") % (uri,), master=self
            )
            return False
        except SyntaxError as e:
            assert "encoding" in str(e).lower()
            messagebox.showerror(
                tr("Problem loading file"),
                tr(
                    "This file seems to have problems with encoding.\n\n"
                    "Make sure it is in UTF-8 or contains proper encoding hint."
                ),
                master=self,
            )
            return False

        self._update_language_servers()
        self.update_appearance()
        self._update_file_source()
        return True

    def _load_local_file(self, path, keep_undo=False):
        if os.path.exists(path):
            with open(path, "rb") as fp:
                source = fp.read()
                exists = True
        else:
            source = b""
            exists = False

        # Make sure Windows filenames have proper format
        path = normpath_with_actual_case(path)
        if exists:
            self._last_known_mtime = os.path.getmtime(path)

        get_workbench().event_generate(
            "Open", editor=self, uri=local_path_to_uri(path), filename=path
        )
        if not self._code_view.set_content_as_bytes(source, keep_undo):
            return False
        self.get_text_widget().edit_modified(not exists)
        self._code_view.focus_set()
        get_workbench().get_editor_notebook().remember_recent_file(path)
        get_workbench().event_generate(
            "Opened", editor=self, uri=local_path_to_uri(path), filename=path
        )
        return True

    def _load_remote_file(self, remote_path):
        self._code_view.set_content("")
        self._code_view.text.set_read_only(True)

        response = get_runner().send_command_and_wait(
            InlineCommand(
                "read_file", path=remote_path, description=tr("Loading %s") % remote_path
            ),
            dialog_title=tr("Loading"),
        )

        if response.get("error"):
            # TODO: make it softer
            raise RuntimeError(response["error"])

        content = response["content_bytes"]
        self._code_view.text.set_read_only(False)
        if not self._code_view.set_content_as_bytes(content):
            return False
        self.get_text_widget().edit_modified(False)
        return True

    def save_file_enabled(self):
        return self.is_modified() or self.is_untitled()

    def save_file(self, ask_target=False, save_copy=False, node=None) -> Optional[str]:
        if not self.is_untitled() and not ask_target:
            save_uri = self._uri
            get_workbench().event_generate(
                "Save",
                editor=self,
                uri=save_uri,
                filename=uri_to_legacy_filename(save_uri),
            )
        else:
            save_uri = self.ask_new_uri(node)

            if not save_uri:
                return None

            if self.containing_notebook.get_editor(save_uri) is not None:
                messagebox.showerror(
                    tr("File is open"),
                    tr(
                        "This file is already open in Thonny.\n\n"
                        "If you want to save with this name,\n"
                        "close the existing editor first!"
                    ),
                    master=get_workbench(),
                )
                return None

            get_workbench().event_generate(
                "SaveAs",
                editor=self,
                uri=save_uri,
                filename=uri_to_legacy_filename(save_uri),
                save_copy=save_copy,
            )

        content_bytes = self._code_view.get_content_as_bytes()

        if is_remote_uri(save_uri):
            result = self.write_remote_file(uri_to_target_path(save_uri), content_bytes, save_copy)
        else:
            result = self.write_local_file(uri_to_target_path(save_uri), content_bytes, save_copy)

        if not result:
            return None

        if not save_copy:
            self.set_uri(save_uri)

        if not save_copy or self._uri == save_uri:
            self.update_title()
            get_workbench().event_generate(
                "Saved", editor=self, uri=save_uri, filename=uri_to_legacy_filename(save_uri)
            )

        self._update_file_source()
        return save_uri

    def write_local_file(self, target_path, content_bytes, save_copy):
        process_shebang = content_bytes.startswith(b"#!/") and get_workbench().get_option(
            "file.make_saved_shebang_scripts_executable"
        )
        if process_shebang:
            content_bytes = content_bytes.replace(b"\r\n", b"\n")

        try:
            f = open(target_path, mode="wb")
            f.write(content_bytes)
            f.flush()
            # Force writes on disk, see https://learn.adafruit.com/adafruit-circuit-playground-express/creating-and-editing-code#1-use-an-editor-that-writes-out-the-file-completely-when-you-save-it
            os.fsync(f)
            f.close()
            if process_shebang:
                os.chmod(target_path, 0o755)
            if not save_copy or target_path == self.get_target_path():
                self._last_known_mtime = os.path.getmtime(target_path)
            get_workbench().event_generate("LocalFileOperation", path=target_path, operation="save")
        except PermissionError:
            messagebox.showerror(
                tr("Permission Error"),
                tr("Looks like this file or folder is not writable."),
                master=self,
            )
            return False

        if not save_copy or target_path == self.get_target_path():
            self.containing_notebook.remember_recent_file(target_path)

        if not save_copy or target_path == self.get_target_path():
            self._code_view.text.edit_modified(False)

        return True

    def write_remote_file(self, target_path, content_bytes, save_copy):
        if get_runner().ready_for_remote_file_operations(show_message=True):

            result = get_runner().send_command_and_wait(
                InlineCommand(
                    "write_file",
                    path=target_path,
                    content_bytes=content_bytes,
                    editor_id=id(self),
                    blocking=True,
                    description=tr("Saving to %s") % target_path,
                    make_shebang_scripts_executable=get_workbench().get_option(
                        "file.make_saved_shebang_scripts_executable"
                    ),
                ),
                dialog_title=tr("Saving"),
            )

            if result is None:
                result = {"error": "Unknown error"}

            if "error" in result:
                messagebox.showerror(tr("Could not save"), str(result["error"]))
                return False

            if not save_copy:
                self._code_view.text.edit_modified(False)

            self.update_title()

            # NB! edit_modified is not falsed yet!
            get_workbench().event_generate(
                "RemoteFileOperation", path=target_path, operation="save"
            )
            get_workbench().event_generate("RemoteFilesChanged")
            return True
        else:
            messagebox.showerror(tr("Could not save"), tr("Back-end is not ready"))
            return False

    def ask_new_uri(self, node=None) -> Optional[str]:
        if node is None:
            node = choose_node_for_file_operations(self.winfo_toplevel(), tr("Where to save to?"))
        if not node:
            return None

        if node == "local":
            path = self.ask_new_local_path()
            if path is not None:
                return local_path_to_uri(path)
        else:
            assert node == "remote"
            path = self.ask_new_remote_path()
            if path is not None:
                return remote_path_to_uri(path)

        return None

    def ask_new_remote_path(self) -> Optional[str]:
        target_path = ask_backend_path(self.winfo_toplevel(), "save", filetypes=_dialog_filetypes)
        if target_path:
            target_path = self._check_add_py_extension(target_path)
            return make_legacy_remote_path(target_path)
        else:
            return None

    def ask_new_local_path(self) -> Optional[str]:
        if self.is_untitled():
            initialdir = get_workbench().get_local_cwd()
            initialfile = None
        else:
            initialdir = os.path.dirname(self.get_target_path())
            initialfile = os.path.basename(self.get_target_path())

        # https://tcl.tk/man/tcl8.6/TkCmd/getOpenFile.htm
        type_var = tk.StringVar(value="")
        new_filename = asksaveasfilename(
            filetypes=_dialog_filetypes,
            defaultextension=None,
            initialdir=initialdir,
            initialfile=initialfile,
            parent=get_workbench(),
            typevariable=type_var,
        )
        logger.info("Save dialog returned %r with typevariable %r", new_filename, type_var.get())

        # Different tkinter versions may return different values
        if new_filename in ["", (), None]:
            return None

        if running_on_windows():
            # may have /-s instead of \-s and wrong case
            new_filename = os.path.join(
                normpath_with_actual_case(os.path.dirname(new_filename)),
                os.path.basename(new_filename),
            )

        if type_var.get() == PYTHON_FILES_STR or type_var.get() == "":
            new_filename = self._check_add_py_extension(
                new_filename, without_asking=type_var.get() == PYTHON_FILES_STR
            )

        if new_filename.endswith(".py"):
            base = os.path.basename(new_filename)
            mod_name = base[:-3].lower()
            if running_on_windows():
                mod_name = mod_name.lower()

            if mod_name in [
                "math",
                "turtle",
                "random",
                "statistics",
                "pygame",
                "matplotlib",
                "numpy",
            ]:
                # More proper name analysis will be performed by ProgramNamingAnalyzer
                if not tk.messagebox.askyesno(
                    tr("Potential problem"),
                    tr(
                        "If you name your script '%s', "
                        "you won't be able to import the library module named '%s'"
                    )
                    % (base, mod_name)
                    + ".\n\n"
                    + tr("Do you still want to use this name for your script?"),
                    master=self,
                ):
                    return self.ask_new_local_path()

        return new_filename

    def show(self):
        self.containing_notebook.select(self)

    def close(self):
        self._disconnect_from_language_servers()
        self.destroy()

    def _disconnect_from_language_servers(self) -> None:
        for ls_proxy in self._primed_ls_proxies:
            logger.info("Disconnecting from %s", ls_proxy)
            ls_proxy.notify_did_close_text_document(
                DidCloseTextDocumentParams(TextDocumentIdentifier(uri=self.get_uri()))
            )

        self._primed_ls_proxies = []
        self._unpublished_incremental_changes = []
        self._last_fully_published_version = None
        self._content_at_server = None

    def _listen_debugger_progress(self, event):
        # Go read-only
        # TODO: check whether this module is active?
        self._code_view.text.set_read_only(True)

    def _listen_for_toplevel_response(self, event: ToplevelResponse) -> None:
        self._code_view.text.set_read_only(False)

    def _control_tab(self, event):
        if event.state & 1:  # shift was pressed
            direction = -1
        else:
            direction = 1
        self.containing_notebook.select_next_prev_editor(direction)
        return "break"

    def _shift_control_tab(self, event):
        self.containing_notebook.select_next_prev_editor(-1)
        return "break"

    def select_range(self, text_range):
        self._code_view.select_range(text_range)

    def select_line(self, lineno, col_offset=None):
        self._code_view.select_range(TextRange(lineno, 0, lineno + 1, 0))
        self.see_line(lineno)

        if col_offset is None:
            col_offset = 0

        self.get_text_widget().mark_set("insert", "%d.%d" % (lineno, col_offset))

    def see_line(self, lineno):
        # first see an earlier line in order to push target line downwards
        self._code_view.text.see("%d.0" % max(lineno - 4, 1))
        self._code_view.text.see("%d.0" % lineno)

    def focus_set(self):
        self._code_view.focus_set()

    def is_focused(self):
        return self.focus_displayof() == self._code_view.text

    def _on_text_modified(self, event):
        self.update_title()

    def update_title(self):
        if self.containing_notebook.has_content(self):
            self.containing_notebook.update_editor_title(self)

    def _on_text_change(self, event):
        # may not be added to the Notebook yet
        if self.containing_notebook.has_content(self):
            self.update_title()

    def _register_text_change(self, event):
        if self._code_view.text is not event["text_widget"]:
            return

        self._last_change_time = time.time()

        if self._last_fully_published_version is not None:
            # meaning the changes should be collected
            self._unpublished_incremental_changes.append(event)

            self.after(int(DEBOUNCE_SECONDS * 1000), self._consider_sending_changes_to_server)

    def destroy(self):
        get_workbench().unbind("DebuggerResponse", self._listen_debugger_progress)
        get_workbench().unbind("ToplevelResponse", self._listen_for_toplevel_response)
        ttk.Frame.destroy(self)
        get_workbench().event_generate(
            "EditorTextDestroyed", editor=self, text_widget=self.get_text_widget()
        )

    def _check_add_py_extension(self, path: str, without_asking: bool = False) -> str:
        assert path
        parts = re.split(r"[/\\]", path)
        name = parts[-1]
        if "." not in name:
            if without_asking or messagebox.askyesno(
                title=tr("Confirmation"),
                message=tr("Python files usually have .py extension.")
                + "\n\n"
                + tr("Did you mean '%s'?" % (name + ".py")),
                parent=self.winfo_toplevel(),
            ):
                return path + ".py"
            else:
                return path

        return path

    def _update_file_source(self):
        if self.is_remote():
            proxy = get_runner().get_backend_proxy()
            if proxy is not None:
                self._file_source = get_runner().get_backend_proxy().get_machine_id()
            else:
                logger.warning("update_file_source: no proxy, leaving as is")
        else:
            self._file_source = "-"  # should not match any machine id

    def _language_server_initialized(self, ls_proxy: LanguageServerProxy) -> None:
        logger.info("Registering initialized language server %s", ls_proxy)
        self._initialized_ls_proxies.append(ls_proxy)
        self._update_language_servers()

    def _language_server_invalidated(self, ls_proxy: LanguageServerProxy) -> None:
        if ls_proxy in self._initialized_ls_proxies:
            self._initialized_ls_proxies.remove(ls_proxy)

        if ls_proxy in self._primed_ls_proxies:
            self._primed_ls_proxies.remove(ls_proxy)

    def _get_version_to_be_published(self) -> int:
        return (
            1
            if self._last_fully_published_version is None
            else self._last_fully_published_version + 1
        )

    def _update_language_servers(self) -> None:
        self.send_changes_to_primed_servers()

        for ls_proxy in self._initialized_ls_proxies:
            if (
                ls_proxy not in self._primed_ls_proxies
                and self.get_language_id() in ls_proxy.get_supported_language_ids()
            ):
                self._prime_language_server(ls_proxy)

        self._unpublished_incremental_changes = []
        self._content_at_server = self.get_content()
        get_workbench().event_generate("AfterSendingDocumentUpdates", uri=self.get_uri())
        self._last_fully_published_version = self._get_version_to_be_published()

    def _prime_language_server(self, ls_proxy: LanguageServerProxy) -> None:
        logger.info("Connecting %r to language server %s", self.get_uri(), ls_proxy)
        assert ls_proxy not in self._primed_ls_proxies
        current_content = self.get_content(up_to_end=True)
        ls_proxy.notify_did_open_text_document(
            DidOpenTextDocumentParams(
                textDocument=TextDocumentItem(
                    version=self._get_version_to_be_published(),
                    uri=self.get_uri(),
                    text=current_content,
                    languageId=self.get_language_id(),
                )
            )
        )
        self._primed_ls_proxies.append(ls_proxy)

    def _consider_sending_changes_to_server(self, event=None):
        time_since_last_change = time.time() - self._last_change_time

        if time_since_last_change >= DEBOUNCE_SECONDS:
            self.send_changes_to_primed_servers()
        else:
            wait_time = DEBOUNCE_SECONDS - time_since_last_change
            self.after(int(wait_time * 1000), self._consider_sending_changes_to_server)

    def send_changes_to_primed_servers(self) -> None:
        if not self._unpublished_incremental_changes:
            logger.debug("No unpublished changes")
            return

        if not self._primed_ls_proxies:
            logger.debug("No primed proxies, not sending changes")
            return

        logger.debug("Merging changes from %s events", len(self._unpublished_incremental_changes))
        clean_prefix_end_line = 9999999999  # lines before this line have not been modified
        clean_suffix_start_line = -1  # this line and lines after this have not been modified
        line_count_delta = 0

        for change in self._unpublished_incremental_changes:
            if change["sequence"] == "TextInsert":
                insertion_line = int(float(change["index"]))
                num_linebreaks_added = change["text"].count("\n")

                clean_prefix_end_line = min(clean_prefix_end_line, insertion_line)
                clean_suffix_start_line = (
                    max(clean_suffix_start_line, insertion_line + 1) + num_linebreaks_added
                )

                line_count_delta += num_linebreaks_added
            else:
                assert change["sequence"] == "TextDelete"
                del_start_line = int(float(change["index1"]))
                del_end_line = int(float(change["index2"]))
                num_linebreaks_deleted = del_end_line - del_start_line

                clean_prefix_end_line = min(clean_prefix_end_line, del_start_line)
                clean_suffix_start_line = max(
                    clean_suffix_start_line - num_linebreaks_deleted, del_start_line + 1
                )

                line_count_delta -= num_linebreaks_deleted

        # LSP uses 0-based line numbers, hence -1
        orig_zero_based_range_start_line = clean_prefix_end_line - 1
        orig_zero_based_range_end_line = clean_suffix_start_line - line_count_delta - 1
        replacement_text = self.get_text_widget().get(
            f"{clean_prefix_end_line}.0", f"{clean_suffix_start_line}.0"
        )

        # validate
        lines_at_server = self._content_at_server.splitlines(keepends=True)
        unmodified_prefix = "".join(lines_at_server[:orig_zero_based_range_start_line])
        unmodified_suffix = "".join(lines_at_server[orig_zero_based_range_end_line:])
        assembled_content = unmodified_prefix + replacement_text + unmodified_suffix

        current_content = self.get_content(up_to_end=True)
        if assembled_content != current_content:
            raise RuntimeError(
                f"Assembled content doesn't match actual content:"
                f" {assembled_content!r} vs {current_content!r}"
            )

        version = self._get_version_to_be_published()
        for ls_proxy in self._primed_ls_proxies:
            ls_proxy.notify_did_change_text_document(
                DidChangeTextDocumentParams(
                    textDocument=VersionedTextDocumentIdentifier(
                        version=version, uri=self.get_uri()
                    ),
                    contentChanges=[
                        RangedTextDocumentContentChangeEvent(
                            range=Range(
                                start=Position(line=orig_zero_based_range_start_line, character=0),
                                end=Position(line=orig_zero_based_range_end_line, character=0),
                            ),
                            text=replacement_text,
                        )
                    ],
                )
            )

    def get_language_id(self) -> str:
        return self.get_text_widget().file_type


class EditorNotebook(CustomNotebook):
    """
    Manages opened files / modules
    """

    def __init__(self, master):
        super().__init__(master)
        self._untitled_name_counter: int = 0

        get_workbench().set_default("file.reopen_files", True)
        get_workbench().set_default("file.open_files", [])
        get_workbench().set_default("file.current_file", None)
        get_workbench().set_default("file.recent_files", [])
        get_workbench().set_default("view.highlight_current_line", False)
        get_workbench().set_default("view.show_line_numbers", True)
        get_workbench().set_default("view.recommended_line_length", 0)
        get_workbench().set_default("edit.indent_with_tabs", False)
        get_workbench().set_default("edit.auto_refresh_saved_files", True)
        get_workbench().set_default("edit.indent_width", 4)
        get_workbench().set_default("edit.tab_width", 4)
        get_workbench().set_default("file.make_saved_shebang_scripts_executable", True)

        self._recent_menu = tk.Menu(
            get_workbench().get_menu("file"), postcommand=self._update_recent_menu
        )
        self._init_commands()
        self.enable_traversal()

        # open files from last session
        """ TODO: they should go only to recent files
        for filename in prefs["open_files"].split(";"):
            if os.path.exists(filename):
                self._open_file(filename)
        """

        # should be in the end, so that it can be detected when
        # constructor hasn't completed yet
        self._checking_external_changes = False

        get_workbench().bind("WindowFocusIn", self.check_for_external_changes, True)
        get_workbench().bind("ToplevelResponse", self.check_for_external_changes, True)
        self.bind("<<NotebookTabChanged>>", self.on_tab_changed, True)

    def on_tab_changed(self, *args):
        # Required to avoid incorrect sizing of parent panes
        self.update_idletasks()

    def _init_commands(self):
        # TODO: do these commands have to be in EditorNotebook ??
        # Create a module level function install_editor_notebook ??
        # Maybe add them separately, when notebook has been installed ??

        get_workbench().add_command(
            "new_file",
            "file",
            tr("New"),
            self._cmd_new_file,
            caption=tr("New"),
            default_sequence=select_sequence("<Control-n>", "<Command-n>"),
            extra_sequences=["<Control-Greek_nu>"],
            group=10,
            image="new-file",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "open_file",
            "file",
            tr("Open..."),
            self._cmd_open_file,
            caption=tr("Load"),
            default_sequence=select_sequence("<Control-o>", "<Command-o>"),
            extra_sequences=["<Control-Greek_omicron>"],
            group=10,
            image="open-file",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "recents", "file", tr("Recent files"), group=10, submenu=self._recent_menu
        )

        # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
        get_workbench().bind_class("Text", "<Control-o>", self._control_o)
        get_workbench().bind_class("Text", "<Control-Greek_omicron>", self._control_o)
        rebind_control_a(get_workbench())

        get_workbench().add_command(
            "close_file",
            "file",
            tr("Close"),
            self._cmd_close_file,
            default_sequence=select_sequence("<Control-w>", "<Command-w>"),
            extra_sequences=["<Control-Greek_finalsmallsigma>"],
            tester=lambda: self.get_current_editor() is not None,
            group=10,
        )

        get_workbench().add_command(
            "close_files",
            "file",
            tr("Close all"),
            self.close_tabs,
            tester=lambda: self.get_current_editor() is not None,
            default_sequence=select_sequence("<Control-W>", "<Command-Alt-w>"),
            group=10,
        )

        get_workbench().add_command(
            "save_file",
            "file",
            tr("Save"),
            self._cmd_save_file,
            caption=tr("Save"),
            default_sequence=select_sequence("<Control-s>", "<Command-s>"),
            extra_sequences=["<Control-Greek_sigma>"],
            tester=self._cmd_save_file_enabled,
            group=10,
            image="save-file",
            include_in_toolbar=True,
        )

        get_workbench().add_command(
            "save_all_files",
            "file",
            tr("Save All files"),
            self._cmd_save_all_files,
            caption=tr("Save All files"),
            default_sequence=select_sequence("<Control-Alt-s>", "<Command-Alt-s>"),
            tester=self._cmd_save_all_files_enabled,
            group=10,
        )

        get_workbench().add_command(
            "save_file_as",
            "file",
            tr("Save as..."),
            self._cmd_save_file_as,
            default_sequence=select_sequence("<Control-Shift-S>", "<Command-Shift-S>"),
            extra_sequences=["<Control-Greek_SIGMA>"],
            tester=lambda: self.get_current_editor() is not None,
            group=10,
        )

        get_workbench().add_command(
            "save_copy",
            "file",
            tr("Save copy..."),
            self._cmd_save_copy,
            tester=lambda: self.get_current_editor() is not None,
            group=10,
        )

        get_workbench().add_command(
            "move_rename_file",
            "file",
            tr("Move / rename..."),
            self._cmd_move_rename_file,
            tester=self._cmd_move_rename_file_enabled,
            group=10,
        )

        get_workbench().add_command(
            "goto_source_line",
            "edit",
            tr("Go to line..."),
            self._cmd_goto_source_line,
            default_sequence=select_sequence("<Control-g>", "<Command-g>"),
            # tester=,
            # no global switch, or cross plugin switch?
            # todo use same as find and replace -> plugins/find_replace.py
            group=60,
        )

        get_workbench().createcommand("::tk::mac::OpenDocument", self._mac_open_document)

    def load_previous_files(self):
        if get_workbench().get_option("file.reopen_files"):
            filenames = get_workbench().get_option("file.open_files")
        else:
            filenames = []

        shown_files_count = 0
        if len(filenames) > 0:
            for filename in filenames:
                if os.path.exists(filename):
                    self.show_file(filename)
                    shown_files_count += 1

            cur_file = get_workbench().get_option("file.current_file")
            # choose correct active file
            if cur_file and os.path.exists(cur_file):
                self.show_file(cur_file)
                shown_files_count += 1

        if shown_files_count == 0:
            self._cmd_new_file()

    def save_all_named_editors(self):
        all_saved = True
        for editor in self.get_all_editors():
            if not editor.is_untitled() and editor.is_modified():
                success = editor.save_file()
                all_saved = all_saved and success

        return all_saved

    def remember_recent_file(self, filename):
        recents = get_workbench().get_option("file.recent_files")
        if filename in recents:
            recents.remove(filename)
        recents.insert(0, filename)
        relevant_recents = [name for name in recents if os.path.exists(name)][:15]
        get_workbench().set_option("file.recent_files", relevant_recents)
        self._update_recent_menu()

    def _update_recent_menu(self):
        recents = get_workbench().get_option("file.recent_files")
        relevant_recents = [
            path for path in recents if os.path.exists(path) and not self.local_file_is_opened(path)
        ]
        self._recent_menu.delete(0, "end")
        for path in relevant_recents:

            def load(path=path):
                self.show_file(path)

            self._recent_menu.insert_command("end", label=path, command=load)

    def remember_open_files(self):
        if self.get_current_editor() is not None and self.get_current_editor().is_local():
            current_file = self.get_current_editor().get_target_path()
        else:
            current_file = None

        get_workbench().set_option("file.current_file", current_file)

        open_files = [
            cast(Editor, editor).get_target_path()
            for editor in self.get_all_editors()
            if editor.is_local()
        ]
        get_workbench().set_option("file.open_files", open_files)

    def _cmd_new_file(self):
        self.open_new_file()

    def open_new_file(self, target_path=None, remote=False):
        if target_path is None:
            uri = self.create_next_untitled_uri()
        elif remote:
            uri = remote_path_to_uri(target_path)
        else:
            uri = local_path_to_uri(target_path)

        new_editor = Editor(self, uri=uri)
        get_workbench().event_generate("NewFile", editor=new_editor)
        self.add(new_editor, text=new_editor.get_title())
        self.select(new_editor)
        new_editor.focus_set()

    def _cmd_open_file(self):
        node = choose_node_for_file_operations(self.winfo_toplevel(), "Where to open from?")
        if not node:
            return

        if node == "local":
            initialdir = get_workbench().get_local_cwd()
            if (
                self.get_current_editor() is not None
                and not self.get_current_editor().is_untitled()
            ):
                initialdir = os.path.dirname(self.get_current_editor().get_target_path())
            target_path = askopenfilename(
                filetypes=_dialog_filetypes, initialdir=initialdir, parent=get_workbench()
            )
        else:
            assert node == "remote"
            target_path = ask_backend_path(
                self.winfo_toplevel(), "open", filetypes=_dialog_filetypes
            )
            if not target_path:
                return

        if target_path:
            # self.close_single_untitled_unmodified_editor()
            self.show_file(remote_path_to_uri(target_path), propose_dialog=False)

    def _control_o(self, event):
        # http://stackoverflow.com/questions/22907200/remap-default-keybinding-in-tkinter
        self._cmd_open_file()
        return "break"

    def _close_files(self, except_index=None):
        for tab_index in reversed(range(len(self.winfo_children()))):
            if except_index is not None and tab_index == except_index:
                continue
            else:
                editor = self.get_child_by_index(tab_index)
                assert isinstance(editor, Editor)
                self.close_editor(editor, force=False)

    def _cmd_close_file(self):
        self.close_tab(self.index(self.select()))

    def close_tab(self, index_or_tab: Union[int, CustomNotebookTab]):
        if isinstance(index_or_tab, int):
            page = self.pages[index_or_tab]
        else:
            page = self.get_page_by_tab(index_or_tab)

        assert isinstance(page.content, Editor)
        self.close_editor(page.content)

    def close_editor(self, editor: Editor, force=False):
        if not force and not self.check_allow_closing(editor):
            return
        self.forget(editor)
        editor.close()

    def _cmd_save_file(self):
        if self.get_current_editor():
            self.get_current_editor().save_file()
            self.update_editor_title(self.get_current_editor())

    def _cmd_save_file_enabled(self):
        return self.get_current_editor() and self.get_current_editor().save_file_enabled()

    def _cmd_save_all_files(self):
        for editor in self.get_all_editors():
            if editor.save_file_enabled() == True:
                editor.save_file()
                self.update_editor_title(editor)

    def _cmd_save_all_files_enabled(self):
        for editor in self.get_all_editors():
            if editor.save_file_enabled() == True:
                return True
        return False

    def _cmd_save_file_as(self, node=None):
        if not self.get_current_editor():
            return

        self.get_current_editor().save_file(ask_target=True, node=node)
        self.update_editor_title(self.get_current_editor())
        get_workbench().update_title()

    def _cmd_save_copy(self):
        if not self.get_current_editor():
            return

        self.get_current_editor().save_file(ask_target=True, save_copy=True)
        self.update_editor_title(self.get_current_editor())

    def _cmd_save_file_as_enabled(self):
        return self.get_current_editor() is not None

    def _cmd_move_rename_file(self):
        editor = self.get_current_editor()
        assert not editor.is_untitled()

        old_path = editor.get_target_path()

        if editor.is_remote():
            node = "remote"
        else:
            node = "local"

        self._cmd_save_file_as(node=node)

        if editor.get_target_path() != old_path:
            if node == "remote":
                get_runner().send_command_and_wait(
                    InlineCommand(
                        "delete", paths=[old_path], description=tr("Deleting" + old_path)
                    ),
                    dialog_title=tr("Deleting"),
                )
                get_workbench().event_generate(
                    "RemoteFileOperation", path=old_path, operation="delete"
                )
            else:
                os.remove(old_path)
                get_workbench().event_generate(
                    "LocalFileOperation", path=old_path, operation="delete"
                )

    def _cmd_move_rename_file_enabled(self):
        return self.get_current_editor() and not self.get_current_editor().is_untitled()

    def close_single_untitled_unmodified_editor(self):
        editors = cast(List[Editor], self.winfo_children())
        if len(editors) == 1 and not editors[0].is_modified() and editors[0].is_untitled():
            self._cmd_close_file()

    def _cmd_goto_source_line(self):
        editor = self.get_current_editor()
        if editor:
            line_no = simpledialog.askinteger(tr("Go to line"), tr("Line number"))
            if line_no:
                editor.select_line(line_no)

    def _mac_open_document(self, *args):
        for arg in args:
            if isinstance(arg, str) and os.path.exists(arg):
                self.show_file(arg)
        get_workbench().become_active_window()

    def get_current_editor(self) -> Optional[Editor]:
        return self.get_current_child()

    def get_current_editor_content(self):
        editor = self.get_current_editor()
        if editor is None:
            return None
        else:
            return editor.get_content()

    def get_all_editors(self) -> List[Editor]:
        # When workspace is closing, self.winfo_children()
        # may return an unexplainable tkinter.Frame
        return [child for child in self.winfo_children() if isinstance(child, Editor)]

    def select_next_prev_editor(self, direction):
        cur_index = self.index(self.select())
        next_index = (cur_index + direction) % len(self.tabs())
        self.select(self.get_child_by_index(next_index))

    def local_file_is_opened(self, path):
        for editor in self.get_all_editors():
            if editor.is_local() and is_same_path(path, editor.get_target_path()):
                return True

        return False

    def show_file(self, path_or_uri, text_range=None, set_focus=True, propose_dialog=True):
        # self.close_single_untitled_unmodified_editor()
        try:
            editor = self.get_editor(path_or_uri, True)
        except PermissionError:
            logger.exception("Loading " + path_or_uri)
            msg = tr("Got permission error when trying to load\n%s") % (path_or_uri,)
            if running_on_mac_os() and propose_dialog:
                msg += "\n\n" + tr("Try opening it with File => Open.")

            messagebox.showerror(tr("Permission error"), msg, master=self)
            return None

        if editor is None:
            return

        self.select(editor)
        if set_focus:
            editor.focus_set()

        if text_range is not None:
            editor.select_range(text_range)

        return editor

    def show_remote_file(self, target_filename):
        if not get_runner().ready_for_remote_file_operations(show_message=True):
            return None
        else:
            return self.show_file(make_legacy_remote_path(target_filename))

    def show_file_at_line(self, filename, lineno: int, col_offset: Optional[int] = None) -> None:
        editor = self.show_file(filename)
        editor.select_line(lineno, col_offset)

    def update_appearance(self):
        for editor in self.get_all_editors():
            editor.update_appearance()

    def update_editor_title(self, editor, title=None):
        if title is None:
            title = editor.get_title()
        try:
            self.tab(editor, text=title)
        except TclError:
            pass

        try:
            self.indicate_modification()
        except Exception:
            logger.exception("Could not update modification indication")

    def indicate_modification(self):
        if not running_on_mac_os():
            return

        atts = self.winfo_toplevel().wm_attributes()
        if "-modified" in atts:
            i = atts.index("-modified")
            mod = atts[i : i + 2]
            rest = atts[:i] + atts[i + 2 :]
        else:
            mod = ()
            rest = atts

        for editor in self.get_all_editors():
            if editor.is_modified():
                if mod != ("-modified", 1):
                    self.winfo_toplevel().wm_attributes(*(rest + ("-modified", 1)))
                break
        else:
            if mod == ("-modified", 1):
                self.winfo_toplevel().wm_attributes(*(rest + ("-modified", 0)))

    def _open_file(self, uri: str):
        editor = Editor(self, uri=uri)
        self.add(editor, text=editor.get_title())
        return editor

    def get_editor(self, path_or_uri, open_when_necessary=False):
        uri = ensure_uri(path_or_uri)

        if is_local_uri(uri):
            path = uri_to_target_path(uri)
            if os.path.isfile(path_or_uri):
                path = normpath_with_actual_case(os.path.abspath(path))
                uri = local_path_to_uri(path)

        for child in self.get_all_editors():
            if child.get_uri() == uri:
                return child

        if open_when_necessary:
            return self._open_file(uri)
        else:
            return None

    def check_allow_closing(self, editor=None):
        if not editor:
            modified_editors = [e for e in self.get_all_editors() if e.is_modified()]
        else:
            if not editor.is_modified():
                return True
            else:
                modified_editors = [editor]
        if len(modified_editors) == 0:
            return True

        message = tr("Do you want to save files before closing?")
        if editor:
            message = tr("Do you want to save file before closing?")

        confirm = messagebox.askyesnocancel(
            title=tr("Save On Close"), message=message, default=messagebox.YES, master=self
        )

        if confirm:
            for editor_ in modified_editors:
                assert isinstance(editor_, Editor)
                if not editor_.save_file():
                    return False
                else:
                    return False
            return True

        elif confirm is None:
            return False
        else:
            return True

    def check_for_external_changes(self, event=None):
        if self._checking_external_changes:
            # otherwise the method will be re-entered when focus
            # changes because of a confirmation message box
            return

        self._checking_external_changes = True
        try:
            for editor in self.get_all_editors():
                editor.check_for_external_changes()
        finally:
            self._checking_external_changes = False

    def after_insert(
        self,
        pos: Union[int, Literal["end"]],
        page: CustomNotebookPage,
        old_notebook: Optional[CustomNotebook],
    ) -> None:
        super().after_insert(pos, page, old_notebook)
        editor = page.content
        assert isinstance(editor, Editor)
        get_workbench().event_generate(
            "InsertEditorToNotebook", pos=pos, editor=editor, text_widget=editor.get_text_widget()
        )

    def after_forget(
        self, pos: int, page: CustomNotebookPage, new_notebook: Optional[CustomNotebook]
    ) -> None:
        super().after_forget(pos, page, new_notebook)
        editor = page.content
        assert isinstance(editor, Editor)
        get_workbench().event_generate(
            "RemoveEditorFromNotebook", pos=pos, editor=editor, text_widget=editor.get_text_widget()
        )

    def try_close_remote_files_from_another_machine(
        self, dialog_parent, new_machine_id: str
    ) -> bool:
        all_remote_editors_to_be_closed = []
        modified_remote_editors_to_be_closed = []
        modified_remote_files_to_be_closed = []
        for editor in self.get_all_editors():
            if editor.get_file_source() == new_machine_id:
                continue

            if editor.is_remote():
                all_remote_editors_to_be_closed.append(editor)
                if editor.is_modified():
                    modified_remote_editors_to_be_closed.append(editor)
                    modified_remote_files_to_be_closed.append(editor.get_target_path())

        if len(modified_remote_files_to_be_closed) > 0:
            message = (
                tr("All files from %s will be closed before switching the interpreter.")
                % get_runner().get_node_label()
            ) + "\n\n"
            message += tr("Unsaved changes to the following files will be lost:") + "\n"
            message += "\n • " + "\n • ".join(modified_remote_files_to_be_closed)
            message += "\n\n" + tr("Do you still want to continue?")

            confirm = messagebox.askyesno(
                title=tr("Discard unsaved changes?"),
                message=message,
                default=messagebox.NO,
                master=dialog_parent,
            )
            if not confirm:
                return False

        for editor in all_remote_editors_to_be_closed:
            self.close_editor(editor, force=True)

        return True

    def create_next_untitled_uri(self) -> str:
        self._untitled_name_counter += 1
        return f"{UNTITLED_URI_SCHEME}:{self._untitled_name_counter}"


def get_current_breakpoints():
    result = {}

    for editor in get_workbench().get_editor_notebook().get_all_editors():
        if editor.is_local():
            linenos = editor.get_code_view().get_breakpoint_line_numbers()
            if linenos:
                result[editor.get_target_path()] = linenos

    return result


def get_saved_current_script_path(force=True):
    editor = get_workbench().get_editor_notebook().get_current_editor()
    if not editor:
        return None

    if editor.is_untitled() and force:
        editor.save_file()

    path = editor.get_target_path()
    if not path:
        return None

    if editor.is_modified():
        path = editor.save_file()

    return path


def get_target_dir_from_uri(uri: str) -> str:
    if is_local_uri(uri):
        return os.path.dirname(uri_to_target_path(uri))
    else:
        return universal_dirname(uri_to_target_path(uri))
