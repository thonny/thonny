import _ast
import ast
import builtins
import dis
import inspect
import os.path
import site
import sys
from collections import namedtuple
from importlib.machinery import PathFinder, SourceFileLoader
from logging import getLogger
from typing import Union

from thonny import report_time
from thonny.common import (
    DebuggerCommand,
    DebuggerResponse,
    FrameInfo,
    InlineCommand,
    InlineResponse,
    TextRange,
    is_same_path,
    path_startswith,
    range_contains_smaller,
    range_contains_smaller_or_equal,
    try_load_modules_with_frontend_sys_path,
)
from thonny.plugins.cpython_backend.cp_back import Executor, format_exception_with_frame_info

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

_CO_GENERATOR = getattr(inspect, "CO_GENERATOR", 0)
_CO_COROUTINE = getattr(inspect, "CO_COROUTINE", 0)
_CO_ITERABLE_COROUTINE = getattr(inspect, "CO_ITERABLE_COROUTINE", 0)
_CO_ASYNC_GENERATOR = getattr(inspect, "CO_ASYNC_GENERATOR", 0)
_CO_WEIRDO = _CO_GENERATOR | _CO_COROUTINE | _CO_ITERABLE_COROUTINE | _CO_ASYNC_GENERATOR


logger = getLogger(__name__)

TempFrameInfo = namedtuple(
    "TempFrameInfo",
    [
        "system_frame",
        "locals",
        "globals",
        "event",
        "focus",
        "node_tags",
        "current_statement",
        "current_root_expression",
        "current_evaluations",
    ],
)


class Tracer(Executor):
    def __init__(self, backend, original_cmd):
        super().__init__(backend, original_cmd)
        self._thonny_src_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._fresh_exception = None
        self._prev_breakpoints = {}
        self._last_reported_frame_ids = set()
        self._affected_frame_ids_per_exc_id = {}
        self._canonic_path_cache = {}
        self._file_interest_cache = {}
        self._file_breakpoints_cache = {}
        self._command_completion_handler = None

        # first (automatic) stepping command depends on whether any breakpoints were set or not
        breakpoints = self._original_cmd.breakpoints
        assert isinstance(breakpoints, dict)
        if breakpoints:
            command_name = "resume"
        else:
            command_name = "step_into"

        self._current_command = DebuggerCommand(
            command_name,
            state=None,
            focus=None,
            frame_id=None,
            exception=None,
            breakpoints=breakpoints,
        )

        self._initialize_new_command(None)

    def _get_canonic_path(self, path):
        # adapted from bdb
        result = self._canonic_path_cache.get(path)
        if result is None:
            if path.startswith("<"):
                result = path
            else:
                result = os.path.normcase(os.path.abspath(path))

            self._canonic_path_cache[path] = result

        return result

    def _trace(self, frame, event, arg):
        raise NotImplementedError()

    def _execute_prepared_user_code(self, statements, global_vars):
        old_breakpointhook = None
        try:
            sys.settrace(self._trace)
            if hasattr(sys, "breakpointhook"):
                old_breakpointhook = sys.breakpointhook
                sys.breakpointhook = self._breakpointhook

            return super()._execute_prepared_user_code(statements, global_vars)
        finally:
            sys.settrace(None)
            if hasattr(sys, "breakpointhook"):
                sys.breakpointhook = old_breakpointhook

    def _is_interesting_frame(self, frame):
        code = frame.f_code

        return not (
            code is None
            or code.co_filename is None
            or not self._is_interesting_module_file(code.co_filename)
            or code.co_flags & _CO_GENERATOR
            and code.co_flags & _CO_COROUTINE
            and code.co_flags & _CO_ITERABLE_COROUTINE
            and code.co_flags & _CO_ASYNC_GENERATOR
            # or "importlib._bootstrap" in code.co_filename
            or code.co_name in ["<listcomp>", "<setcomp>", "<dictcomp>"]
        )

    def _is_interesting_module_file(self, path):
        # interesting files are the files in the same directory as main module
        # or the ones with breakpoints
        # When command is "resume", then only modules with breakpoints are interesting
        # (used to be more flexible, but this caused problems
        # when main script was in ~/. Then user site library became interesting as well)

        result = self._file_interest_cache.get(path, None)
        if result is not None:
            return result

        _, extension = os.path.splitext(path.lower())

        result = (
            self._get_breakpoints_in_file(path)
            or self._main_module_path is not None
            and is_same_path(path, self._main_module_path)
            or extension in (".py", ".pyw")
            and (
                self._current_command.get("allow_stepping_into_libraries", False)
                or (
                    self._main_module_path is not None
                    and path_startswith(path, os.path.dirname(self._main_module_path))
                    # main module may be at the root of the fs
                    and not path_startswith(path, sys.prefix)
                    and not path_startswith(path, sys.base_prefix)
                    and not path_startswith(path, site.getusersitepackages() or "usersitenotexists")
                )
            )
            and not path_startswith(path, self._thonny_src_dir)
        )

        self._file_interest_cache[path] = result

        return result

    def _is_interesting_exception(self, frame, arg):
        return arg[0] not in (StopIteration, StopAsyncIteration)

    def _fetch_next_debugger_command(self, current_frame):
        while True:
            cmd = self._backend._fetch_next_incoming_message()
            if isinstance(cmd, InlineCommand):
                self._backend._handle_normal_command(cmd)
            else:
                assert isinstance(cmd, DebuggerCommand)
                report_time(f"Reading debugger command {cmd}")
                self._prev_breakpoints = self._current_command.breakpoints
                self._current_command = cmd
                self._initialize_new_command(current_frame)
                return

    def _initialize_new_command(self, current_frame):
        self._command_completion_handler = getattr(
            self, "_cmd_%s_completed" % self._current_command.name
        )

        if self._current_command.breakpoints != self._prev_breakpoints:
            self._file_interest_cache = {}  # because there may be new breakpoints
            self._file_breakpoints_cache = {}
            for path, linenos in self._current_command.breakpoints.items():
                self._file_breakpoints_cache[path] = linenos
                self._file_breakpoints_cache[self._get_canonic_path(path)] = linenos

    def _register_affected_frame(self, exception_obj, frame):
        # I used to store the frame ids in a new field inside exception object,
        # but Python 3.8 doesn't allow this (https://github.com/thonny/thonny/issues/1403)
        exc_id = id(exception_obj)
        if exc_id not in self._affected_frame_ids_per_exc_id:
            self._affected_frame_ids_per_exc_id[exc_id] = set()
        self._affected_frame_ids_per_exc_id[exc_id].add(id(frame))

    def _get_breakpoints_in_file(self, filename):
        result = self._file_breakpoints_cache.get(filename, None)

        if result is not None:
            return result

        canonic_path = self._get_canonic_path(filename)
        result = self._file_breakpoints_cache.get(canonic_path, set())
        self._file_breakpoints_cache[filename] = result
        return result

    def _get_current_exception(self):
        if self._fresh_exception is not None:
            return self._fresh_exception
        else:
            return sys.exc_info()

    def _export_exception_info(self):
        exc = self._get_current_exception()

        if exc[0] is None:
            return {
                "id": None,
                "msg": None,
                "type_name": None,
                "lines_with_frame_info": None,
                "affected_frame_ids": set(),
                "is_fresh": False,
            }
        else:
            return {
                "id": id(exc[1]),
                "msg": str(exc[1]),
                "type_name": exc[0].__name__,
                "lines_with_frame_info": format_exception_with_frame_info(*exc),
                "affected_frame_ids": self._affected_frame_ids_per_exc_id.get(id(exc[1]), set()),
                "is_fresh": exc == self._fresh_exception,
            }

    def _breakpointhook(self, *args, **kw):
        pass

    def _check_notify_return(self, frame_id):
        if frame_id in self._last_reported_frame_ids:
            # Need extra notification, because it may be long time until next interesting event
            self._backend.send_message(InlineResponse("debugger_return", frame_id=frame_id))

    def _check_store_main_frame_id(self, frame):
        # initial command doesn't have a frame id
        if self._current_command.frame_id is None and self._get_canonic_path(
            frame.f_code.co_filename
        ) == self._get_canonic_path(self._main_module_path):
            self._current_command.frame_id = id(frame)


class FastTracer(Tracer):
    def __init__(self, backend, original_cmd):
        super().__init__(backend, original_cmd)

        self._command_frame_returned = False
        self._code_linenos_cache = {}
        self._code_breakpoints_cache = {}

    def _initialize_new_command(self, current_frame):
        super()._initialize_new_command(current_frame)
        self._command_frame_returned = False
        if self._current_command.breakpoints != self._prev_breakpoints:
            self._code_breakpoints_cache = {}

            # restore tracing for active frames which were skipped before
            # but have breakpoints now
            frame = current_frame
            while frame is not None:
                if (
                    frame.f_trace is None
                    and frame.f_code is not None
                    and self._get_breakpoints_in_code(frame.f_code)
                ):
                    frame.f_trace = self._trace

                frame = frame.f_back

    def _breakpointhook(self, *args, **kw):
        frame = inspect.currentframe()
        while not self._is_interesting_frame(frame):
            frame = frame.f_back
        self._report_current_state(frame)
        self._fetch_next_debugger_command(frame)

    def _should_skip_frame(self, frame, event):
        if event == "call":
            # new frames
            return (
                (
                    self._current_command.name == "resume"
                    and not self._get_breakpoints_in_code(frame.f_code)
                    or self._current_command.name == "step_over"
                    and not self._get_breakpoints_in_code(frame.f_code)
                    and id(frame) not in self._last_reported_frame_ids
                    or self._current_command.name == "step_out"
                    and not self._get_breakpoints_in_code(frame.f_code)
                )
                or not self._is_interesting_frame(frame)
                or self._backend.is_doing_io()
            )

        else:
            # once we have entered a frame, we need to reach the return event
            return False

    def _trace(self, frame, event, arg):
        if self._should_skip_frame(frame, event):
            return None

        # return None
        # return self._trace

        frame_id = id(frame)

        if event == "call":
            self._check_store_main_frame_id(frame)

            self._fresh_exception = None
            # can we skip this frame?
            if self._current_command.name == "step_over" and not self._current_command.breakpoints:
                return None

        elif event == "return":
            self._fresh_exception = None
            if frame_id == self._current_command["frame_id"]:
                self._command_frame_returned = True
            self._check_notify_return(frame_id)

        elif event == "exception":
            if self._is_interesting_exception(frame, arg):
                self._fresh_exception = arg
                self._register_affected_frame(arg[1], frame)
                # UI doesn't know about separate exception events
                self._report_current_state(frame)
                self._fetch_next_debugger_command(frame)

        elif event == "line":
            self._fresh_exception = None

            if self._command_completion_handler(frame):
                self._report_current_state(frame)
                self._fetch_next_debugger_command(frame)

        else:
            self._fresh_exception = None

        return self._trace

    def _report_current_state(self, frame):
        stack = self._backend._export_stack(frame, self._is_interesting_frame)
        msg = DebuggerResponse(
            stack=stack,
            in_present=True,
            io_symbol_count=None,
            exception_info=self._export_exception_info(),
            tracer_class="FastTracer",
        )

        self._last_reported_frame_ids = set(map(lambda f: f.id, stack))

        self._backend.send_message(msg)

    def _cmd_step_into_completed(self, frame):
        return True

    def _cmd_step_over_completed(self, frame):
        return (
            id(frame) == self._current_command.frame_id
            or self._command_frame_returned
            or self._at_a_breakpoint(frame)
        )

    def _cmd_step_out_completed(self, frame):
        return self._command_frame_returned or self._at_a_breakpoint(frame)

    def _cmd_resume_completed(self, frame):
        return self._at_a_breakpoint(frame)

    def _get_breakpoints_in_code(self, f_code):
        bps_in_file = self._get_breakpoints_in_file(f_code.co_filename)

        code_id = id(f_code)
        result = self._code_breakpoints_cache.get(code_id, None)

        if result is None:
            if not bps_in_file:
                result = set()
            else:
                co_linenos = self._code_linenos_cache.get(code_id, None)
                if co_linenos is None:
                    co_linenos = {pair[1] for pair in dis.findlinestarts(f_code)}
                    self._code_linenos_cache[code_id] = co_linenos

                result = bps_in_file.intersection(co_linenos)

            self._code_breakpoints_cache[code_id] = result

        return result

    def _at_a_breakpoint(self, frame):
        # TODO: try re-entering same line in loop
        return frame.f_lineno in self._get_breakpoints_in_code(frame.f_code)

    def _is_interesting_exception(self, frame, arg):
        return super()._is_interesting_exception(frame, arg) and (
            self._current_command.name in ["step_into", "step_over"]
            and (
                # in command frame or its parent frames
                id(frame) == self._current_command["frame_id"]
                or self._command_frame_returned
            )
        )


class NiceTracer(Tracer):
    def __init__(self, backend, original_cmd):
        super().__init__(backend, original_cmd)
        self._instrumented_files = set()
        self._install_marker_functions()
        self._custom_stack = []
        self._saved_states = []
        self._current_state_index = 0

        from collections import Counter

        self._fulltags = Counter()
        self._nodes = {}

    def _breakpointhook(self, *args, **kw):
        self._report_state(len(self._saved_states) - 1)
        self._fetch_next_debugger_command(None)

    def _install_marker_functions(self):
        # Make dummy marker functions universally available by putting them
        # into builtin scope
        self.marker_function_names = {
            BEFORE_STATEMENT_MARKER,
            AFTER_STATEMENT_MARKER,
            BEFORE_EXPRESSION_MARKER,
            AFTER_EXPRESSION_MARKER,
        }

        for name in self.marker_function_names:
            if not hasattr(builtins, name):
                setattr(builtins, name, getattr(self, name))

    def _prepare_ast(self, source: Union[str, bytes], filename: str, mode: str):
        # ast_utils need to be imported after asttokens
        # is (custom-)imported
        try_load_modules_with_frontend_sys_path(["asttokens", "six", "astroid"])
        from thonny import ast_utils

        root = ast.parse(source, filename, mode)

        ast_utils.mark_text_ranges(root, source)
        self._tag_nodes(root)
        self._insert_expression_markers(root)
        self._insert_statement_markers(root)
        self._insert_for_target_markers(root)
        self._instrumented_files.add(filename)

        return root

    def _should_skip_frame(self, frame, event):
        # nice tracer can't skip any of the frames which need to be
        # shown in the stacktrace
        code = frame.f_code
        if code is None:
            return True

        if event == "call":
            # new frames
            if code.co_name in self.marker_function_names:
                return False

            else:
                return not self._is_interesting_frame(frame) or self._backend.is_doing_io()

        else:
            # once we have entered a frame, we need to reach the return event
            return False

    def _is_interesting_frame(self, frame):
        return (
            frame.f_code.co_filename in self._instrumented_files
            and super()._is_interesting_frame(frame)
        )

    def find_spec(self, fullname, path=None, target=None):
        spec = PathFinder.find_spec(fullname, path, target)

        if (
            spec is not None
            and isinstance(spec.loader, SourceFileLoader)
            and getattr(spec, "origin", None)
            and self._is_interesting_module_file(spec.origin)
        ):
            spec.loader = FancySourceFileLoader(fullname, spec.origin, self)
            return spec
        else:
            return super().find_spec(fullname, path, target)

    def is_in_past(self):
        return self._current_state_index < len(self._saved_states) - 1

    def _trace(self, frame, event, arg):
        try:
            return self._trace_and_catch(frame, event, arg)
        except BaseException:
            logger.exception("Exception in _trace", exc_info=True)
            sys.settrace(None)
            return None

    def _trace_and_catch(self, frame, event, arg):
        """
        1) Detects marker calls and responds to client queries in these spots
        2) Maintains a customized view of stack
        """
        # frame skipping test should be done both in new frames and old ones (because of Resume)
        # Note that intermediate frames can't be skipped when jumping to a breakpoint
        # because of the need to maintain custom stack
        if self._should_skip_frame(frame, event):
            return None

        code_name = frame.f_code.co_name

        if event == "call":
            self._fresh_exception = (
                None  # some code is running, therefore exception is not fresh anymore
            )

            if code_name in self.marker_function_names:
                self._check_store_main_frame_id(frame.f_back)

                # the main thing
                if code_name == BEFORE_STATEMENT_MARKER:
                    event = "before_statement"
                elif code_name == AFTER_STATEMENT_MARKER:
                    event = "after_statement"
                elif code_name == BEFORE_EXPRESSION_MARKER:
                    event = "before_expression"
                elif code_name == AFTER_EXPRESSION_MARKER:
                    event = "after_expression"
                else:
                    raise AssertionError("Unknown marker function")

                marker_function_args = frame.f_locals.copy()
                node = self._nodes[marker_function_args["node_id"]]

                del marker_function_args["self"]

                if "call_function" not in node.tags:
                    self._handle_progress_event(frame.f_back, event, marker_function_args, node)
                self._try_interpret_as_again_event(frame.f_back, event, marker_function_args, node)

                # Don't need any more events from these frames
                return None

            else:
                # Calls to proper functions.
                # Client doesn't care about these events,
                # it cares about "before_statement" events in the first statement of the body
                self._custom_stack.append(CustomStackFrame(frame, "call"))

        elif event == "exception":
            # Note that Nicer can't filter out exception based on current command
            # because it must be possible to go back and replay with different command
            if self._is_interesting_exception(frame, arg):
                self._fresh_exception = arg
                self._register_affected_frame(arg[1], frame)

                # Last command (step_into or step_over) produced this exception
                # Show red after-state for this focus
                # use the state prepared by previous event
                last_custom_frame = self._custom_stack[-1]
                assert last_custom_frame.system_frame == frame

                # TODO: instead of producing an event here, next before_-event
                # should create matching after event for each before event
                # which would remain unclosed because of this exception.
                # Existence of these after events would simplify step_over management

                assert last_custom_frame.event.startswith("before_")
                pseudo_event = last_custom_frame.event.replace("before_", "after_").replace(
                    "_again", ""
                )
                # print("handle", pseudo_event, {}, last_custom_frame.node)
                self._handle_progress_event(frame, pseudo_event, {}, last_custom_frame.node)

        elif event == "return":
            self._fresh_exception = None

            if code_name not in self.marker_function_names:
                frame_id = id(self._custom_stack[-1].system_frame)
                self._check_notify_return(frame_id)
                self._custom_stack.pop()
                if len(self._custom_stack) == 0:
                    # We popped last frame, this means our program has ended.
                    # There may be more events coming from upper (system) frames
                    # but we're not interested in those
                    sys.settrace(None)
            else:
                pass

        else:
            self._fresh_exception = None

        return self._trace

    def _handle_progress_event(self, frame, event, args, node):
        self._save_current_state(frame, event, args, node)
        self._respond_to_commands()

    def _save_current_state(self, frame, event, args, node):
        """
        Updates custom stack and stores the state

        self._custom_stack always keeps last info,
        which gets exported as FrameInfos to _saved_states["stack"]
        """
        focus = TextRange(node.lineno, node.col_offset, node.end_lineno, node.end_col_offset)

        custom_frame = self._custom_stack[-1]
        custom_frame.event = event
        custom_frame.focus = focus
        custom_frame.node = node
        custom_frame.node_tags = node.tags

        if self._saved_states:
            prev_state = self._saved_states[-1]
            prev_state_frame = self._create_actual_active_frame(prev_state)
        else:
            prev_state = None
            prev_state_frame = None

        # store information about current statement / expression
        if "statement" in event:
            custom_frame.current_statement = focus

            if event == "before_statement_again":
                # keep the expression information from last event
                pass
            else:
                custom_frame.current_root_expression = None
                custom_frame.current_evaluations = []
        else:
            assert "expression" in event
            assert prev_state_frame is not None

            # may need to update current_statement, because the parent statement was
            # not the last one visited (eg. with test expression of a loop,
            # starting from 2nd iteration)
            if hasattr(node, "parent_statement_focus"):
                custom_frame.current_statement = node.parent_statement_focus

            # see whether current_root_expression needs to be updated
            prev_root_expression = prev_state_frame.current_root_expression
            if event == "before_expression" and (
                id(frame) != id(prev_state_frame.system_frame)
                or "statement" in prev_state_frame.event
                or prev_root_expression
                and not range_contains_smaller_or_equal(prev_root_expression, focus)
            ):
                custom_frame.current_root_expression = focus
                custom_frame.current_evaluations = []

            if event == "after_expression" and "value" in args:
                # value is missing in case of exception
                custom_frame.current_evaluations.append(
                    (focus, self._backend.export_value(args["value"]))
                )

        # Save the snapshot.
        # Check if we can share something with previous state
        if (
            prev_state is not None
            and id(prev_state_frame.system_frame) == id(frame)
            and prev_state["exception_value"] is self._get_current_exception()[1]
            and prev_state["fresh_exception_id"] == id(self._fresh_exception)
            and ("before" in event or "skipexport" in node.tags)
        ):
            exception_info = prev_state["exception_info"]
            # share the stack ...
            stack = prev_state["stack"]
            # ... but override certain things
            active_frame_overrides = {
                "event": custom_frame.event,
                "focus": custom_frame.focus,
                "node_tags": custom_frame.node_tags,
                "current_root_expression": custom_frame.current_root_expression,
                "current_evaluations": custom_frame.current_evaluations.copy(),
                "current_statement": custom_frame.current_statement,
            }
        else:
            # make full export
            stack = self._export_stack()
            exception_info = self._export_exception_info()
            active_frame_overrides = {}

        msg = {
            "stack": stack,
            "active_frame_overrides": active_frame_overrides,
            "in_client_log": False,
            "io_symbol_count": (
                sys.stdin._processed_symbol_count
                + sys.stdout._processed_symbol_count
                + sys.stderr._processed_symbol_count
            ),
            "exception_value": self._get_current_exception()[1],
            "fresh_exception_id": id(self._fresh_exception),
            "exception_info": exception_info,
        }

        self._saved_states.append(msg)

    def _respond_to_commands(self):
        """Tries to respond to client commands with states collected so far.
        Returns if these states don't suffice anymore and Python needs
        to advance the program"""

        # while the state for current index is already saved:
        while self._current_state_index < len(self._saved_states):
            state = self._saved_states[self._current_state_index]

            # Get current state's most recent frame (together with overrides
            frame = self._create_actual_active_frame(state)

            # Is this state meant to be seen?
            if "skip_" + frame.event not in frame.node_tags:
                # if True:
                # Has the command completed?
                tester = getattr(self, "_cmd_" + self._current_command.name + "_completed")
                cmd_complete = tester(frame, self._current_command)

                if cmd_complete:
                    state["in_client_log"] = True
                    self._report_state(self._current_state_index)
                    self._fetch_next_debugger_command(frame)

            if self._current_command.name == "step_back":
                if self._current_state_index == 0:
                    # Already in first state. Remain in this loop
                    pass
                else:
                    assert self._current_state_index > 0
                    # Current event is no longer present in GUI "undo log"
                    self._saved_states[self._current_state_index]["in_client_log"] = False
                    self._current_state_index -= 1
            else:
                # Other commands move the pointer forward
                self._current_state_index += 1

    def _create_actual_active_frame(self, state):
        return state["stack"][-1]._replace(**state["active_frame_overrides"])

    def _report_state(self, state_index):
        in_present = state_index == len(self._saved_states) - 1
        if in_present:
            # For reported new events re-export stack to make sure it is not shared.
            # (There is tiny chance that sharing previous state
            # after executing BinOp, Attribute, Compare or Subscript
            # was not the right choice. See tag_nodes for more.)
            # Re-exporting reduces the harm by showing correct data at least
            # for present states.
            self._saved_states[state_index]["stack"] = self._export_stack()

        # need to make a copy for applying overrides
        # and removing helper fields without modifying original
        state = self._saved_states[state_index].copy()
        state["stack"] = state["stack"].copy()

        state["in_present"] = in_present
        if not in_present:
            # for past states fix the newest frame
            state["stack"][-1] = self._create_actual_active_frame(state)

        del state["exception_value"]
        del state["active_frame_overrides"]

        # Convert stack of TempFrameInfos to stack of FrameInfos
        new_stack = []
        self._last_reported_frame_ids = set()
        for tframe in state["stack"]:
            system_frame = tframe.system_frame
            module_name = system_frame.f_globals.get("__name__", None)
            code_name = system_frame.f_code.co_name

            source, firstlineno, in_library = self._backend._get_frame_source_info(system_frame)

            assert firstlineno is not None, "nofir " + str(system_frame)
            frame_id = id(system_frame)
            new_stack.append(
                FrameInfo(
                    id=frame_id,
                    filename=system_frame.f_code.co_filename,
                    module_name=module_name,
                    code_name=code_name,
                    locals=tframe.locals,
                    globals=tframe.globals,
                    freevars=system_frame.f_code.co_freevars,
                    source=source,
                    lineno=system_frame.f_lineno,
                    firstlineno=firstlineno,
                    in_library=in_library,
                    event=tframe.event,
                    focus=tframe.focus,
                    node_tags=tframe.node_tags,
                    current_statement=tframe.current_statement,
                    current_evaluations=tframe.current_evaluations,
                    current_root_expression=tframe.current_root_expression,
                )
            )

            self._last_reported_frame_ids.add(frame_id)

        state["stack"] = new_stack
        state["tracer_class"] = "NiceTracer"

        self._backend.send_message(DebuggerResponse(**state))

    def _try_interpret_as_again_event(self, frame, original_event, original_args, original_node):
        """
        Some after_* events can be interpreted also as
        "before_*_again" events (eg. when last argument of a call was
        evaluated, then we are just before executing the final stage of the call)
        """

        if original_event == "after_expression":
            value = original_args.get("value")

            if (
                "last_child" in original_node.tags
                or "or_arg" in original_node.tags
                and value
                or "and_arg" in original_node.tags
                and not value
            ):
                # there may be explicit exceptions
                if (
                    "skip_after_statement_again" in original_node.parent_node.tags
                    or "skip_after_expression_again" in original_node.parent_node.tags
                ):
                    return

                # next step will be finalizing evaluation of parent of current expr
                # so let's say we're before that parent expression
                again_args = {"node_id": id(original_node.parent_node)}
                again_event = (
                    "before_expression_again"
                    if "child_of_expression" in original_node.tags
                    else "before_statement_again"
                )

                self._handle_progress_event(
                    frame, again_event, again_args, original_node.parent_node
                )

    def _cmd_step_over_completed(self, frame, cmd):
        """
        Identifies the moment when piece of code indicated by cmd.frame_id and cmd.focus
        has completed execution (either successfully or not).
        """

        if self._at_a_breakpoint(frame, cmd):
            return True

        # Make sure the correct frame_id is selected
        if id(frame.system_frame) == cmd.frame_id:
            # We're in the same frame
            if "before_" in cmd.state:
                if not range_contains_smaller_or_equal(cmd.focus, frame.focus):
                    # Focus has changed, command has completed
                    return True
                else:
                    # Keep running
                    return False
            elif "after_" in cmd.state:
                if (
                    frame.focus != cmd.focus
                    or "before_" in frame.event
                    or "_expression" in cmd.state
                    and "_statement" in frame.event
                    or "_statement" in cmd.state
                    and "_expression" in frame.event
                ):
                    # The state has changed, command has completed
                    return True
                else:
                    # Keep running
                    return False
        else:
            # We're in another frame
            if self._frame_is_alive(cmd.frame_id):
                # We're in a successor frame, keep running
                return False
            else:
                # Original frame has completed, assumedly because of an exception
                # We're done
                return True

        return True  # not actually required, just to make Pylint happy

    def _cmd_step_into_completed(self, frame, cmd):
        return frame.event != "after_statement"

    def _cmd_step_back_completed(self, frame, cmd):
        # Check if the selected message has been previously sent to front-end
        return (
            self._saved_states[self._current_state_index]["in_client_log"]
            or self._current_state_index == 0
        )

    def _cmd_step_out_completed(self, frame, cmd):
        if self._current_state_index == 0:
            return False

        if frame.event == "after_statement":
            return False

        if self._at_a_breakpoint(frame, cmd):
            return True

        prev_state_frame = self._saved_states[self._current_state_index - 1]["stack"][-1]

        return (
            # the frame has completed
            not self._frame_is_alive(cmd.frame_id)
            # we're in the same frame but on higher level
            # TODO: expression inside statement expression has same range as its parent
            or id(frame.system_frame) == cmd.frame_id
            and range_contains_smaller(frame.focus, cmd.focus)
            # or we were there in prev state
            or id(prev_state_frame.system_frame) == cmd.frame_id
            and range_contains_smaller(prev_state_frame.focus, cmd.focus)
        )

    def _cmd_resume_completed(self, frame, cmd):
        return self._at_a_breakpoint(frame, cmd)

    def _at_a_breakpoint(self, frame, cmd, breakpoints=None):
        if breakpoints is None:
            breakpoints = cmd["breakpoints"]

        return (
            frame.event in ["before_statement", "before_expression"]
            and frame.system_frame.f_code.co_filename in breakpoints
            and frame.focus.lineno in breakpoints[frame.system_frame.f_code.co_filename]
            # consider only first event on a line
            # (but take into account that same line may be reentered)
            and (
                cmd.focus is None
                or (cmd.focus.lineno != frame.focus.lineno)
                or (cmd.focus == frame.focus and cmd.state == frame.event)
                or id(frame.system_frame) != cmd.frame_id
            )
        )

    def _frame_is_alive(self, frame_id):
        for frame in self._custom_stack:
            if id(frame.system_frame) == frame_id:
                return True

        return False

    def _export_stack(self):
        result = []

        exported_globals_per_module = {}

        def export_globals(module_name, frame):
            if module_name not in exported_globals_per_module:
                exported_globals_per_module[module_name] = self._backend.export_variables(
                    frame.f_globals
                )
            return exported_globals_per_module[module_name]

        for custom_frame in self._custom_stack:
            system_frame = custom_frame.system_frame
            module_name = system_frame.f_globals.get("__name__", None)

            result.append(
                TempFrameInfo(
                    # need to store the reference to the frame to avoid it being GC-d
                    # otherwise frame id-s would be reused and this would
                    # mess up communication with the frontend.
                    system_frame=system_frame,
                    locals=None
                    if system_frame.f_locals is system_frame.f_globals
                    else self._backend.export_variables(system_frame.f_locals),
                    globals=export_globals(module_name, system_frame),
                    event=custom_frame.event,
                    focus=custom_frame.focus,
                    node_tags=custom_frame.node_tags,
                    current_evaluations=custom_frame.current_evaluations.copy(),
                    current_statement=custom_frame.current_statement,
                    current_root_expression=custom_frame.current_root_expression,
                )
            )

        assert result  # not empty
        return result

    def _thonny_hidden_before_stmt(self, node_id):
        # The code to be debugged will be instrumented with this function
        # inserted before each statement.
        # Entry into this function indicates that statement as given
        # by the code range is about to be evaluated next.
        return None

    def _thonny_hidden_after_stmt(self, node_id):
        # The code to be debugged will be instrumented with this function
        # inserted after each statement.
        # Entry into this function indicates that statement as given
        # by the code range was just executed successfully.
        return None

    def _thonny_hidden_before_expr(self, node_id):
        # Entry into this function indicates that expression as given
        # by the code range is about to be evaluated next
        return node_id

    def _thonny_hidden_after_expr(self, node_id, value):
        # The code to be debugged will be instrumented with this function
        # wrapped around each expression (given as 2nd argument).
        # Entry into this function indicates that expression as given
        # by the code range was just evaluated to given value
        return value

    def _tag_nodes(self, root):
        """Marks interesting properties of AST nodes"""
        # ast_utils need to be imported after asttokens
        # is (custom-)imported
        try_load_modules_with_frontend_sys_path(["asttokens", "six", "astroid"])
        from thonny import ast_utils

        def add_tag(node, tag):
            if not hasattr(node, "tags"):
                node.tags = set()
                node.tags.add("class=" + node.__class__.__name__)
            node.tags.add(tag)

        # ignore module docstring if it is before from __future__ import
        if (
            isinstance(root.body[0], ast.Expr)
            and isinstance(root.body[0].value, ast.Str)
            and len(root.body) > 1
            and isinstance(root.body[1], ast.ImportFrom)
            and root.body[1].module == "__future__"
        ):
            add_tag(root.body[0], "ignore")
            add_tag(root.body[0].value, "ignore")
            add_tag(root.body[1], "ignore")

        for node in ast.walk(root):
            if not isinstance(node, (ast.expr, ast.stmt)):
                if isinstance(node, ast.comprehension):
                    for expr in node.ifs:
                        add_tag(expr, "comprehension.if")

                continue

            # tag last children
            last_child = ast_utils.get_last_child(node)
            assert last_child in [True, False, None] or isinstance(
                last_child, (ast.expr, ast.stmt, type(None))
            ), ("Bad last child " + str(last_child) + " of " + str(node))
            if last_child is not None:
                add_tag(node, "has_children")

                if isinstance(last_child, ast.AST):
                    last_child.parent_node = node
                    add_tag(last_child, "last_child")
                    if isinstance(node, _ast.expr):
                        add_tag(last_child, "child_of_expression")
                    else:
                        add_tag(last_child, "child_of_statement")

                    if isinstance(node, ast.Call):
                        add_tag(last_child, "last_call_arg")

            # other cases
            if isinstance(node, ast.Call):
                add_tag(node.func, "call_function")
                node.func.parent_node = node

            if isinstance(node, ast.BoolOp) and node.op == ast.Or():
                for child in node.values:
                    add_tag(child, "or_arg")
                    child.parent_node = node

            if isinstance(node, ast.BoolOp) and node.op == ast.And():
                for child in node.values:
                    add_tag(child, "and_arg")
                    child.parent_node = node

            # TODO: assert (it doesn't evaluate msg when test == True)

            if isinstance(node, ast.stmt):
                for child in ast.iter_child_nodes(node):
                    child.parent_node = node
                    child.parent_statement_focus = TextRange(
                        node.lineno, node.col_offset, node.end_lineno, node.end_col_offset
                    )

            if isinstance(node, ast.Str):
                add_tag(node, "skipexport")

            if hasattr(ast, "JoinedStr") and isinstance(node, ast.JoinedStr):
                # can't present children normally without
                # ast giving correct locations for them
                # https://bugs.python.org/issue29051
                add_tag(node, "ignore_children")

            elif isinstance(node, ast.Num):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.List):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Tuple):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Set):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Dict):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Name):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.NameConstant):
                add_tag(node, "skipexport")

            elif hasattr(ast, "Constant") and isinstance(node, ast.Constant):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Expr):
                if not isinstance(node.value, (ast.Yield, ast.YieldFrom)):
                    add_tag(node, "skipexport")

            elif isinstance(node, ast.If):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Return):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.While):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Continue):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Break):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Pass):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.For):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Try):
                add_tag(node, "skipexport")

            elif isinstance(node, ast.ListComp):
                add_tag(node.elt, "ListComp.elt")
                if len(node.generators) > 1:
                    add_tag(node, "ignore_children")

            elif isinstance(node, ast.SetComp):
                add_tag(node.elt, "SetComp.elt")
                if len(node.generators) > 1:
                    add_tag(node, "ignore_children")

            elif isinstance(node, ast.DictComp):
                add_tag(node.key, "DictComp.key")
                add_tag(node.value, "DictComp.value")
                if len(node.generators) > 1:
                    add_tag(node, "ignore_children")

            elif isinstance(node, ast.BinOp):
                # TODO: use static analysis to detect type of left child
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Attribute):
                # TODO: use static analysis to detect type of left child
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Subscript):
                # TODO: use static analysis to detect type of left child
                add_tag(node, "skipexport")

            elif isinstance(node, ast.Compare):
                # TODO: use static analysis to detect type of left child
                add_tag(node, "skipexport")

            if isinstance(node, (ast.Assign)):
                # value will be presented in assignment's before_statement_again
                add_tag(node.value, "skip_after_expression")

            if isinstance(node, (ast.Expr, ast.While, ast.For, ast.If, ast.Try, ast.With)):
                add_tag(node, "skip_after_statement_again")

            # make sure every node has this field
            if not hasattr(node, "tags"):
                node.tags = set()

    def _should_instrument_as_expression(self, node):
        return (
            isinstance(node, _ast.expr)
            and hasattr(node, "end_lineno")
            and hasattr(node, "end_col_offset")
            and not getattr(node, "incorrect_range", False)
            and "ignore" not in node.tags
            and (not hasattr(node, "ctx") or isinstance(node.ctx, ast.Load))
            # TODO: repeatedly evaluated subexpressions of comprehensions
            # can be supported (but it requires some redesign both in backend and GUI)
            and "ListComp.elt" not in node.tags
            and "SetComp.elt" not in node.tags
            and "DictComp.key" not in node.tags
            and "DictComp.value" not in node.tags
            and "comprehension.if" not in node.tags
        )

    def _is_case_pattern(self, node) -> bool:
        if sys.version_info < (3, 10):
            return False
        else:
            return isinstance(
                node,
                (
                    ast.MatchValue,
                    ast.MatchSingleton,
                    ast.MatchSequence,
                    ast.MatchMapping,
                    ast.MatchClass,
                    ast.MatchStar,
                    ast.MatchAs,
                    ast.MatchOr,
                ),
            )

    def _should_instrument_as_statement(self, node):
        return (
            isinstance(node, _ast.stmt)
            and not getattr(node, "incorrect_range", False)
            and "ignore" not in node.tags
            # Shouldn't insert anything before from __future__ import
            # as this is not a normal statement
            # https://bitbucket.org/plas/thonny/issues/183/thonny-throws-false-positive-syntaxerror
            and (not isinstance(node, ast.ImportFrom) or node.module != "__future__")
        )

    def _insert_statement_markers(self, root):
        # find lists of statements and insert before/after markers for each statement
        for name, value in ast.iter_fields(root):
            if isinstance(root, ast.Try) and name == "handlers":
                # contains statements but is not statement itself
                for handler in value:
                    self._insert_statement_markers(handler)
            elif isinstance(value, ast.AST):
                self._insert_statement_markers(value)
            elif isinstance(value, list):
                if len(value) > 0:
                    new_list = []
                    for node in value:
                        if self._should_instrument_as_statement(node):
                            # self._debug("EBFOMA", node)
                            # add before marker
                            new_list.append(
                                self._create_statement_marker(node, BEFORE_STATEMENT_MARKER)
                            )

                        # original statement
                        if self._should_instrument_as_statement(node):
                            self._insert_statement_markers(node)
                        new_list.append(node)

                        if (
                            self._should_instrument_as_statement(node)
                            and "skipexport" not in node.tags
                        ):
                            # add after marker
                            new_list.append(
                                self._create_statement_marker(node, AFTER_STATEMENT_MARKER)
                            )
                    setattr(root, name, new_list)

    def _create_statement_marker(self, node, function_name):
        call = self._create_simple_marker_call(node, function_name)
        stmt = ast.Expr(value=call)
        ast.copy_location(stmt, node)
        ast.fix_missing_locations(stmt)
        return stmt

    def _insert_for_target_markers(self, root):
        """inserts markers which notify assignment to for-loop variables"""
        for node in ast.walk(root):
            if isinstance(node, ast.For):
                old_target = node.target
                # print(vars(old_target))
                temp_name = "__for_loop_var"
                node.target = ast.Name(temp_name, ast.Store())

                name_load = ast.Name(temp_name, ast.Load())
                # value will be visible in parent's before_statement_again event
                name_load.tags = {"skip_before_expression", "skip_after_expression", "last_child"}
                name_load.lineno, name_load.col_offset = (node.iter.lineno, node.iter.col_offset)
                name_load.end_lineno, name_load.end_col_offset = (
                    node.iter.end_lineno,
                    node.iter.end_col_offset,
                )

                before_name_load = self._create_simple_marker_call(
                    name_load, BEFORE_EXPRESSION_MARKER
                )
                after_name_load = ast.Call(
                    func=ast.Name(id=AFTER_EXPRESSION_MARKER, ctx=ast.Load()),
                    args=[before_name_load, name_load],
                    keywords=[],
                )

                ass = ast.Assign([old_target], after_name_load)
                ass.lineno, ass.col_offset = old_target.lineno, old_target.col_offset
                ass.end_lineno, ass.end_col_offset = (
                    node.iter.end_lineno,
                    node.iter.end_col_offset,
                )
                ass.tags = {"skip_before_statement"}  # before_statement_again will be shown

                name_load.parent_node = ass

                ass_before = self._create_statement_marker(ass, BEFORE_STATEMENT_MARKER)
                node.body.insert(0, ass_before)
                node.body.insert(1, ass)
                node.body.insert(2, self._create_statement_marker(ass, AFTER_STATEMENT_MARKER))

                ast.fix_missing_locations(node)

    def _insert_expression_markers(self, node):
        """
        TODO: this docstring is outdated
        each expression e gets wrapped like this:
            _after(_before(_loc, _node_is_zoomable), e, _node_role, _parent_range)
        where
            _after is function that gives the resulting value
            _before is function that signals the beginning of evaluation of e
            _loc gives the code range of e
            _node_is_zoomable indicates whether this node has subexpressions
            _node_role is either 'last_call_arg', 'last_op_arg', 'first_or_arg',
                                 'first_and_arg', 'function' or None
        """
        tracer = self

        class ExpressionVisitor(ast.NodeTransformer):
            def generic_visit(self, node):
                if isinstance(node, _ast.expr):
                    if isinstance(node, ast.Starred):
                        # keep this node as is, but instrument its children
                        return ast.NodeTransformer.generic_visit(self, node)
                    elif tracer._should_instrument_as_expression(node):
                        # before marker
                        before_marker = tracer._create_simple_marker_call(
                            node, BEFORE_EXPRESSION_MARKER
                        )
                        ast.copy_location(before_marker, node)

                        if "ignore_children" in node.tags:
                            transformed_node = node
                        else:
                            transformed_node = ast.NodeTransformer.generic_visit(self, node)

                        # after marker
                        after_marker = ast.Call(
                            func=ast.Name(id=AFTER_EXPRESSION_MARKER, ctx=ast.Load()),
                            args=[before_marker, transformed_node],
                            keywords=[],
                        )
                        ast.copy_location(after_marker, node)
                        ast.fix_missing_locations(after_marker)
                        # further transformations may query original node location from after marker
                        if hasattr(node, "end_lineno"):
                            after_marker.end_lineno = node.end_lineno
                            after_marker.end_col_offset = node.end_col_offset

                        return after_marker
                    else:
                        # This expression (and its children) should be ignored
                        return node
                elif tracer._is_case_pattern(node):
                    # ignore this and children
                    return node
                else:
                    # Descend into statements
                    return ast.NodeTransformer.generic_visit(self, node)

        return ExpressionVisitor().visit(node)

    def _create_simple_marker_call(self, node, fun_name, extra_args=[]):
        args = [self._export_node(node)] + extra_args

        return ast.Call(func=ast.Name(id=fun_name, ctx=ast.Load()), args=args, keywords=[])

    def _export_node(self, node):
        assert isinstance(node, (ast.expr, ast.stmt))
        node_id = id(node)
        self._nodes[node_id] = node
        return ast.Num(node_id)

    def _debug(self, *args):
        logger.debug("TRACER: " + str(args))

    def _execute_prepared_user_code(self, statements, global_vars):
        try:
            return Tracer._execute_prepared_user_code(self, statements, global_vars)
        finally:
            """
            from thonny.misc_utils import _win_get_used_memory
            print("Memory:", _win_get_used_memory() / 1024 / 1024)
            print("States:", len(self._saved_states))
            print(self._fulltags.most_common())
            """


class FancySourceFileLoader(SourceFileLoader):
    """Used for loading and instrumenting user modules during fancy tracing"""

    def __init__(self, fullname, path, tracer):
        super().__init__(fullname, path)
        self._tracer = tracer

    def source_to_code(self, data, path, *, _optimize=-1):
        old_tracer = sys.gettrace()
        sys.settrace(None)
        try:
            root = self._tracer._prepare_ast(data, path, "exec")
            return super().source_to_code(root, path)
        finally:
            sys.settrace(old_tracer)


class CustomStackFrame:
    def __init__(self, frame, event, focus=None):
        self.system_frame = frame
        self.event = event
        self.focus = focus
        self.current_evaluations = []
        self.current_statement = None
        self.current_root_expression = None
        self.node_tags = set()
