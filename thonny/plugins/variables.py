# -*- coding: utf-8 -*-
import logging
from tkinter import messagebox, ttk

from thonny import get_runner, get_workbench
from thonny.common import InlineCommand
from thonny.languages import tr
from thonny.memory import VariablesFrame

logger = logging.getLogger(__name__)


class VariablesView(VariablesFrame):
    # TODO: Indicate invalid state when program or debug command is running more than a second
    def __init__(self, master):
        super().__init__(master)

        ttk.Style().configure("Centered.TButton", justify="center")
        self.back_button = ttk.Button(
            self.tree,
            style="Centered.TButton",
            text=tr("Back to\ncurrent frame"),
            command=self._handle_back_button,
            width=15,
        )

        get_workbench().bind("BackendRestart", self._handle_backend_restart, True)
        get_workbench().bind("ToplevelResponse", self._handle_toplevel_response, True)
        # get_workbench().bind("DebuggerResponse", self._debugger_response, True)
        get_workbench().bind("get_frame_info_response", self._handle_frame_info_event, True)
        get_workbench().bind("get_globals_response", self._handle_get_globals_response, True)

        # records last info from progress messages
        self._last_active_info = None

    def _update_back_button(self, visible):
        if visible:
            assert self._last_active_info is not None
            self.back_button.configure(text=tr("Back to\n%s") % self._last_active_info[-1])
            self.back_button.place(relx=1, x=-5, y=5, anchor="ne")
        else:
            self.back_button.place_forget()

    def _handle_back_button(self):
        assert self._last_active_info is not None
        if len(self._last_active_info) == 2:
            self.show_globals(*self._last_active_info)
        else:
            assert len(self._last_active_info) == 4
            self.show_frame_variables(*self._last_active_info)

    def _handle_backend_restart(self, event):
        self._clear_tree()

    def _handle_get_globals_response(self, event):
        if "error" in event:
            self._handle_error_response(event["error"])
        elif "globals" not in event:
            self._handle_error_response(str(event))
        else:
            self.show_globals(event["globals"], event["module_name"])

    def _handle_error_response(self, error_msg):
        self._clear_tree()
        logger.error("Error querying globals: %s", error_msg)
        self.show_error("Could not query global variables: " + str(error_msg))

    def _handle_toplevel_response(self, event):
        if "globals" in event:
            self.show_globals(event["globals"], "__main__")
        else:
            # MicroPython
            get_runner().send_command(InlineCommand("get_globals", module_name="__main__"))

    def show_globals(self, globals_, module_name, is_active=True):
        self.clear_error()
        # TODO: update only if something has changed
        self.update_variables(globals_)
        if module_name == "__main__":
            self._set_tab_caption(tr("Variables"))
        else:
            self._set_tab_caption(tr("Variables") + " (%s)" % module_name)

        if is_active:
            self._last_active_info = (globals_, module_name)

        self._update_back_button(not is_active)

    def show_frame_variables(self, locals_, globals_, freevars, frame_name, is_active=True):
        # TODO: update only if something has changed
        actual_locals = {}
        nonlocals = {}
        for name in locals_:
            if name in freevars:
                nonlocals[name] = locals_[name]
            else:
                actual_locals[name] = locals_[name]

        groups = [("LOCALS", actual_locals), ("GLOBALS", globals_)]
        if nonlocals:
            groups.insert(1, ("NONLOCALS", nonlocals))

        self.update_variables(groups)
        self._set_tab_caption("Variables (%s)" % frame_name)

        if is_active:
            self._last_active_info = (locals_, globals_, freevars, frame_name)

        self._update_back_button(not is_active)

    def _handle_frame_info_event(self, frame_info):
        if frame_info.get("error"):
            "probably non-existent frame"
            return
        else:
            is_active = frame_info[
                "location"
            ] == "stack" or (  # same __main__ globals can be in different frames
                frame_info["code_name"] == "<module>"
                and frame_info["module_name"] == "__main__"
                and self._last_active_info[-1] == "__main__"
                and self._last_active_info[0] == frame_info["globals"]
            )

            if frame_info["code_name"] == "<module>":
                self.show_globals(frame_info["globals"], frame_info["module_name"], is_active)
            else:
                self.show_frame_variables(
                    frame_info["locals"],
                    frame_info["globals"],
                    frame_info["freevars"],
                    frame_info["code_name"],
                    is_active,
                )

    def _set_tab_caption(self, text):
        # pylint: disable=no-member
        if self.hidden:
            return

        self.home_widget.master.tab(self.home_widget, text=text)


def load_plugin() -> None:
    get_workbench().add_view(VariablesView, tr("Variables"), "ne", default_position_key="AAA")
