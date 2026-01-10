"""
MP 1.12

>>> #import uos
>>> #dir(uos)
['__class__', '__name__', 'remove', 'VfsFat', 'VfsLfs2', 'chdir', 'dupterm', 'dupterm_notify',
'getcwd', 'ilistdir', 'listdir', 'mkdir', 'mount', 'rename', 'rmdir', 'stat', 'statvfs', 'umount',
'uname', 'urandom']
>>> import sys
>>> dir(sys)
['__class__', '__name__', 'argv', 'byteorder', 'exit', 'implementation', 'maxsize', 'modules',
'path', 'platform', 'print_exception', 'stderr', 'stdin', 'stdout', 'version', 'version_info']

micro:bit (1.9.2)

>>> import os
>>> dir(os)
['__name__', 'remove', 'listdir', 'size', 'uname']
>>> import sys
>>> dir(sys)
['__name__', 'version', 'version_info', 'implementation', 'platform', 'byteorder', 'exit',
'print_exception']

CP 5.0
>>> dir(os)
['__class__', '__name__', 'chdir', 'getcwd', 'listdir', 'mkdir', 'remove', 'rename', 'rmdir', 'sep',
'stat', 'statvfs', 'sync', 'uname', 'unlink', 'urandom']
>>> import sys
>>> dir(sys)
['__class__', '__name__', 'argv', 'byteorder', 'exit', 'implementation', 'maxsize', 'modules',
'path', 'platform', 'print_exception', 'stderr', 'stdin', 'stdout', 'version', 'version_info']


"""

import ast
import os
import sys
from abc import ABC, abstractmethod
from logging import getLogger
from textwrap import dedent
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from minny.target import (
    EOT,
    FIRST_RAW_PROMPT,
    NORMAL_PROMPT,
    STAT_KIND_INDEX,
    STAT_MTIME_INDEX,
    STAT_SIZE_INDEX,
    ProperTargetManager,
    unix_dirname_basename,
)

from thonny import report_time
from thonny.backend import MainBackend
from thonny.common import (
    BackendEvent,
    CommandToBackend,
    EOFCommand,
    ImmediateCommand,
    InputSubmission,
    MessageFromBackend,
    ToplevelResponse,
    UserError,
    ValueInfo,
)

# How many seconds to wait for something that should appear quickly.
# In other words -- how long to wait with reporting a protocol error
# (hoping that the required piece is still coming)
WAIT_OR_CRASH_TIMEOUT = 5

SECONDS_IN_YEAR = 60 * 60 * 24 * 365


EXTRA_HELPER_CODE = """"
    last_non_none_repl_value = None

    # for object inspector
    inspector_values = builtins.dict()
    @builtins.classmethod
    def print_repl_value(cls, obj):
        if obj is not None:
            cls.builtins.print({start_marker!r} % cls.builtins.id(obj), cls.builtins.repr(obj), {end_marker!r}, sep='')
            cls.last_non_none_repl_value = obj


    @builtins.classmethod
    def repr(cls, obj):
        try:
            s = cls.builtins.repr(obj)
            if cls.builtins.len(s) > 50:
                s = s[:50] + "..."
            return s
        except cls.builtins.Exception as e:
            return "<could not serialize: " + __minny_helper.builtins.str(e) + ">"
"""

logger = getLogger(__name__)


class MicroPythonBackend(MainBackend, ABC):
    def __init__(self, tmgr: ProperTargetManager):
        logger.info("Initializing MicroPythonBackend of type %s", type(self).__name__)
        self._tmgr: ProperTargetManager = tmgr
        MainBackend.__init__(self)
        # Get rid of the welcome text which was printed while searching for prompt
        self.send_message(
            BackendEvent(event_type="HideTrailingOutput", text=self._tmgr._welcome_text)
        )
        self._send_ready_message()
        report_time("sent ready")

        try:
            self.mainloop()
        except ConnectionError as e:
            self.handle_connection_error(e)
        except Exception:
            logger.exception("Exception in MicroPython main method")
            self._report_internal_exception("Internal error")

    def _evaluate(self, script: str) -> Any:
        return self._tmgr._evaluate(script)

    def _execute(self, script: str, capture_output: bool = False) -> Tuple[str, str]:
        return self._tmgr._execute(script, capture_output)

    def _perform_idle_tasks(self):
        read_bytes = self._tmgr.handle_unexpected_output()
        if read_bytes.endswith(NORMAL_PROMPT) or read_bytes.endswith(FIRST_RAW_PROMPT):
            # Means there was a restart. Recreate Thonny prompt
            self.send_message(ToplevelResponse())

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._tmgr._submit_input(msg.data)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        raise NotImplementedError()

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd["name"] == "interrupt":
            self._interrupt()

    def _interrupt(self):
        # don't interrupt while command or input is being written
        with self._interrupt_lock:
            if self._current_command:
                assert self._current_command_interrupt_event is not None
                self._current_command_interrupt_event.set()
            self._tmgr._interrupt()

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        logger.debug("Handling normal command '%s' in micropython backend ", cmd.name)
        report_time("before " + cmd.name)

        if "local_cwd" in cmd:
            self._local_cwd = cmd["local_cwd"]
            if os.path.isdir(self._local_cwd):
                os.chdir(self._local_cwd)

        super()._handle_normal_command(cmd)

        self._tmgr._check_perform_just_in_case_gc()
        report_time("after " + cmd.name)

    def _check_for_connection_error(self) -> None:
        self._tmgr.get_connection().check_for_error()

    def _send_ready_message(self):
        args = dict(cwd=self._tmgr.get_cwd(), board_id=self._tmgr.get_device_id())
        args["welcome_text"] = self._tmgr.get_welcome_text()

        self.send_message(ToplevelResponse(**args))

    def send_message(self, msg: MessageFromBackend) -> None:
        if "cwd" not in msg:
            msg["cwd"] = self._tmgr.get_cwd()

        if "sys_path" not in msg:
            msg["sys_path"] = self._tmgr.get_sys_path()

        if "lib_dirs" not in msg:
            msg["lib_dirs"] = [self._tmgr.get_default_target()]

        super().send_message(msg)

    def _send_error_message(self, msg):
        self._send_output("\n" + msg + "\n", "stderr")

    def _check_for_side_commands(self):
        # NB! EOFCommand gets different treatment depending whether it is read during processing a command
        # (ie. here) or it gets read when REPL is idle (ie. in mainloop)

        # most likely the queue is empty
        if self._incoming_message_queue.empty():
            return

        postponed = []
        while not self._incoming_message_queue.empty():
            cmd = self._incoming_message_queue.get()
            if isinstance(cmd, InputSubmission):
                self._tmgr._submit_input(cmd.data)
            elif isinstance(cmd, EOFCommand):
                # in this context it is not supposed to soft-reboot
                self._tmgr._write(EOT)
            else:
                postponed.append(cmd)

        # put back postponed commands
        while postponed:
            self._incoming_message_queue.put(postponed.pop(0))

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._tmgr._supports_directories():
                raise UserError("This device doesn't have directories")

            self._tmgr.chdir(cmd.args[0])
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_Run(self, cmd) -> Dict[str, Any]:
        return self._cmd_Run_or_run(cmd, True)

    def _cmd_run(self, cmd):
        return self._cmd_Run_or_run(cmd, False)

    def _cmd_Run_or_run(self, cmd, restart_interpreter_before_run):
        """Only for %run $EDITOR_CONTENT. start runs are handled differently."""
        if cmd.get("source"):
            self._tmgr.run_user_program_via_repl(
                cmd["source"],
                restart_interpreter_before_run,
                cmd.get("populate_argv", False),
                cmd.get("args", []),
            )
            return {"source_for_language_server": cmd["source"]}
        else:
            return {}

    def _cmd_execute_source(self, cmd):
        # TODO: clear last object inspector requests dictionary
        if cmd.source:
            self._tmgr.execute_repl_entry(cmd.source)
        # TODO: assign last value to _
        return {}

    @abstractmethod
    def _cmd_execute_system_command(self, cmd) -> Dict[str, Any]: ...

    def _cmd_get_globals(self, cmd):
        if cmd.module_name == "__main__":
            globs = self._evaluate(
                "{name : (__minny_helper.repr(value), __minny_helper.builtins.id(value)) for (name, value) in __minny_helper.builtins.globals().items() if not name.startswith('__')}"
            )
        else:
            globs = self._evaluate(
                dedent(
                    """
                import %s as __mod_for_globs
                __minny_helper.print_mgmt_value(
                    {name : (__minny_helper.repr(__minny_helper.builtins.getattr(__mod_for_globs, name)), 
                             __minny_helper.builtins.id(__minny_helper.builtins.getattr(__mod_for_globs, name)))
                        in __minny_helper.builtins.dir(__mod_for_globs) 
                        if not name.startswith('__')}
                )
                del __mod_for_globs
            """
                )
            )

        value_infos = {}
        for name, pair in globs.items():
            value_infos[name] = ValueInfo(pair[1], pair[0])

        logger.debug("Returning %d globals", len(value_infos))
        return {"module_name": cmd.module_name, "globals": value_infos}

    @abstractmethod
    def _cmd_get_fs_info(self, cmd) -> Dict[str, Any]: ...

    def _cmd_get_object_info(self, cmd):
        context_id = cmd.get("context_id", None)
        basic_info = self._find_basic_object_info(cmd.object_id, context_id)
        if basic_info is None:
            return {"id": cmd.object_id, "error": "object info not available"}

        type_name = basic_info["type"].replace("<class '", "").replace("'>", "").strip()
        info = {
            "id": cmd.object_id,
            "repr": basic_info["repr"],
            "type": basic_info["type"],
            "full_type_name": type_name,
            "attributes": {},
        }

        info.update(self._get_object_info_extras(type_name, repr_str=basic_info["repr"]))
        if cmd.include_attributes:
            info["attributes"] = self._get_object_attributes(cmd.all_attributes)

        # need to keep the reference corresponding to object_id so that it can be later found as next context object
        # remove non-relevant items
        # TODO: add back links
        # TODO: release old links
        # relevant = set([cmd.object_id] + cmd.back_links + cmd.forward_links)
        self._execute(
            dedent(
                """
                if __minny_helper.builtins.id(__minny_helper.object_info) not in __minny_helper.inspector_values:
                    __minny_helper.inspector_values[__minny_helper.builtins.id(__minny_helper.object_info)] = __minny_helper.object_info
            """
            )
        )

        return {"id": cmd.object_id, "info": info}

    def _find_basic_object_info(self, object_id, context_id):
        """If object is found then returns basic info and leaves object reference
        to __minny_helper.object_info.

        Can't leave it in a global object, because when querying globals(),
        repr(globals()) would cause infinite recursion."""

        result = self._evaluate(
            dedent(
                """
                for __minny_helper.object_info in (
                        [__minny_helper.last_non_none_repl_value]
                        + __minny_helper.builtins.list(__minny_helper.builtins.globals().values()) 
                        + __minny_helper.builtins.list(__minny_helper.inspector_values.values())):
                    if __minny_helper.builtins.id(__minny_helper.object_info) == %d:
                        __minny_helper.print_mgmt_value({
                            "repr" : __minny_helper.builtins.repr(__minny_helper.object_info),
                            "type": __minny_helper.builtins.str(__minny_helper.builtins.type(__minny_helper.object_info))
                        })
                        break
                else:
                    __minny_helper.object_info = None
                    __minny_helper.print_mgmt_value(None)
            """
                % object_id
            )
        )

        if result is not None:
            return result
        elif context_id is not None:
            return self._evaluate(
                dedent(
                    """
                __minny_helper.context_value = __minny_helper.inspector_values.get(%d, None)
                
                if __minny_helper.context_value is None:
                    __minny_helper.object_info = None
                    __minny_helper.print_mgmt_value(None)
                else:
                    __minny_helper.context_children = [
                         __minny_helper.builtins.getattr(__minny_helper.context_value, name)
                         for name in __minny_helper.builtins.dir(__minny_helper.context_value)
                    ]
                    if __minny_helper.builtins.isinstance(__minny_helper.context_value, (set, tuple, list)):
                        __minny_helper.context_children += __minny_helper.builtins.list(__minny_helper.context_value)
                    elif __minny_helper.builtins.isinstance(__minny_helper.context_value, __minny_helper.builtins.dict):
                        __minny_helper.context_children += __minny_helper.builtins.list(__minny_helper.context_value.values())
                    
                    for __minny_helper.object_info in __minny_helper.context_children:
                        if __minny_helper.builtins.id(__minny_helper.object_info) == %d:
                            __minny_helper.print_mgmt_value({
                                "repr" : __minny_helper.repr(__minny_helper.object_info),
                                "type": __minny_helper.builtins.str(__minny_helper.builtins.type(__minny_helper.object_info))
                            })
                            break
                    else:
                        __minny_helper.object_info = None
                        __minny_helper.print_mgmt_value(None)
                        
                __minny_helper.context_value = None
                __minny_helper.context_children = None
            """
                    % (context_id, object_id)
                )
            )
        else:
            return None

    def _get_object_attributes(self, all_attributes):
        """object is given in __minny_helper.object_info"""
        atts = self._evaluate(
            "{name : ("
            "   __minny_helper.builtins.id(__minny_helper.builtins.getattr(__minny_helper.object_info, name)),"
            "    __minny_helper.repr(__minny_helper.builtins.getattr(__minny_helper.object_info, name))"
            ") for name in __minny_helper.builtins.dir(__minny_helper.object_info)}"
        )
        return {
            name: ValueInfo(atts[name][0], atts[name][1])
            for name in atts
            if not name.startswith("__") or all_attributes
        }

    def _get_object_info_extras(self, type_name: str, repr_str: str):
        """object is given in __minny_helper.object_info"""
        if type_name in ("list", "tuple", "set"):
            items = self._evaluate(
                "[(__minny_helper.builtins.id(x), __minny_helper.repr(x)) for x in __minny_helper.object_info]"
            )
            return {"elements": [ValueInfo(x[0], x[1]) for x in items]}
        elif type_name == "dict":
            items = self._evaluate(
                "[((__minny_helper.builtins.id(key), __minny_helper.repr(key)), (__minny_helper.builtins.id(__minny_helper.object_info[key]), "
                "__minny_helper.repr(__minny_helper.object_info[key]))) for key in __minny_helper.object_info]"
            )
            return {
                "entries": [
                    (ValueInfo(x[0][0], x[0][1]), ValueInfo(x[1][0], x[1][1])) for x in items
                ]
            }
        elif type_name == "MicroBitImage":
            if repr_str.startswith("Image('") and repr_str.count(":") == 5:
                # ■ █ □ ●*✶•∙
                data = repr_str.replace("Image('", "").replace("')", "")
                content = (
                    data.replace(":", "\n")
                    .replace("0", "  ")
                    .replace("1", " ∙")
                    .replace("2", " ∙")
                    .replace("3", " •")
                    .replace("4", " •")
                    .replace("5", " ✶")
                    .replace("6", " ✶")
                    .replace("7", " *")
                    .replace("8", " *")
                    .replace("9", " ●")
                    + "\n\n"
                    + data.replace(":", "\n")
                    .replace("0", " 0")
                    .replace("1", " 1")
                    .replace("2", " 2")
                    .replace("3", " 3")
                    .replace("4", " 4")
                    .replace("5", " 5")
                    .replace("6", " 6")
                    .replace("7", " 7")
                    .replace("8", " 8")
                    .replace("9", " 9")
                )
                return {"microbit_image": content}
            else:
                return {}
        else:
            return {}

    def _cmd_delete(self, cmd):
        assert cmd.paths
        self._tmgr.delete_recursively(cmd.paths)

    def _cmd_get_active_distributions(self, cmd) -> Dict[str, Any]:
        try:
            current_state = ...  # self._perform_pipkin_operation_and_list(None)
            return dict(
                distributions=current_state,
            )
        except Exception as e:
            logger.exception("Could not get active distributions")
            return dict(error=str(e))

    def _cmd_install_distributions(self, cmd) -> Dict[str, Any]:
        args = cast(List[str], cmd.args[:])
        assert isinstance(args, List)

        if "--upgrade" in args:
            upgrade = True
            args.remove("--upgrade")
        else:
            upgrade = False

        if "-r" in args:
            pos = args.index("-r")
            req_file = args[pos + 1]
            del args[pos + 1]
            del args[pos]
            requirement_files = [req_file]
        else:
            requirement_files = None

        assert not any([arg.startswith("-") for arg in args])
        specs = args

        try:
            print("TODO", specs, requirement_files, args, upgrade)
            """
            new_state = self._perform_pipkin_operation_and_list(
                command="install",
                specs=specs,
                user=user,
                upgrade=upgrade,
                requirement_files=requirement_files,
            )
            """
            new_state = ...

            return {"distributions": new_state}
        except Exception as e:
            logger.exception("Could not install")
            return dict(error=str(e))

    def _cmd_uninstall_distributions(self, cmd):
        try:
            """
            new_state = self._perform_pipkin_operation_and_list(
                command="uninstall", packages=cmd.args, yes=True
            )
            """
            new_state = ...
            return {"distributions": new_state}
        except Exception as e:
            logger.exception("Could not uninstall")
            return dict(error=str(e))

    def _guess_package_pypi_name(self, installed_name) -> str:
        return "micropython-" + installed_name

    def _cmd_mkdir(self, cmd):
        assert self._tmgr._supports_directories()
        assert cmd.path.startswith("/")
        assert not cmd.path.startswith("//")
        self._tmgr._mkdir(cmd.path)

    def _get_path_info(self, path: str) -> Optional[Dict]:
        stat = self._tmgr.try_get_stat(path)

        if stat is None:
            return None

        _, basename = unix_dirname_basename(path)
        return self._expand_stat(stat, basename)

    def _get_dir_children_info(
        self, path: str, include_hidden: bool = False
    ) -> Optional[Dict[str, Dict]]:
        """The key of the result dict is simple name"""
        if self._tmgr._supports_directories():
            raw_data = self._evaluate(
                dedent(
                    """
                __thonny_result = {} 
                try:
                    __thonny_names = __minny_helper.listdir(%r)
                except __minny_helper.builtins.OSError:
                    __minny_helper.print_mgmt_value(None) 
                else:
                    for __thonny_name in __thonny_names:
                        if not __thonny_name.startswith(".") or %r:
                            try:
                                __thonny_result[__thonny_name] = __minny_helper.os.stat(%r + __thonny_name)
                            except __minny_helper.builtins.OSError as e:
                                __thonny_result[__thonny_name] = __minny_helper.builtins.str(e)
                    __minny_helper.print_mgmt_value(__thonny_result)
            """
                )
                % (path, include_hidden, path.rstrip("/") + "/")
            )
            if raw_data is None:
                return None
        elif path == "":
            # used to represent all files in micro:bit
            raw_data = self._evaluate(
                "{name : __minny_helper.os.size(name) for name in __minny_helper.os.listdir()}"
            )
        else:
            return None

        return {name: self._expand_stat(raw_data[name], name) for name in raw_data}

    def handle_connection_error(self, error=None):
        try:
            self._tmgr.handle_unexpected_output("stderr")
        except Exception:
            logger.warning("Could not forward output", exc_info=True)
        super().handle_connection_error(error)

    def _show_error(self, msg, end="\n"):
        self._send_output(msg + end, "stderr")

    def _replace_last_repl_value_variables(self, source: str) -> str:
        try:
            root = ast.parse(source)
        except SyntaxError:
            return source

        load_nodes = []
        has_store_nodes = False
        for node in ast.walk(root):
            if (
                isinstance(node, ast.arg)
                and node.arg == "_"
                or isinstance(node, ast.Name)
                and node.id == "_"
                and isinstance(node.ctx, ast.Store)
            ):
                has_store_nodes = True
            elif isinstance(node, ast.Name) and node.id == "_" and isinstance(node.ctx, ast.Load):
                load_nodes.append(node)

        if not load_nodes:
            return source

        if load_nodes and has_store_nodes:
            print("WARNING: Could not infer REPL _-variables", file=sys.stderr)
            return source

        lines = source.splitlines(keepends=True)
        for node in reversed(load_nodes):
            lines[node.lineno - 1] = (
                lines[node.lineno - 1][: node.col_offset]
                + "__minny_helper.builtins.globals().get('_', __minny_helper.last_non_none_repl_value)"
                + lines[node.lineno - 1][node.col_offset + 1 :]
            )

        new_source = "".join(lines)
        logger.debug("New source with replaced _-s: %r", new_source)
        return new_source

    def _add_expression_statement_handlers(self, source):
        try:
            root = ast.parse(source)

            from thonny.ast_utils import mark_text_ranges

            mark_text_ranges(root, source)
            self._mark_nodes_to_be_guarded_from_instrumentation(root, False)

            expr_stmts = []
            for node in ast.walk(root):
                if isinstance(node, ast.Expr) and not getattr(node, "guarded"):
                    expr_stmts.append(node)

            marker_prefix = "__minny_helper.print_repl_value("
            marker_suffix = ")"

            lines = source.splitlines(keepends=True)
            for node in reversed(expr_stmts):
                lines[node.end_lineno - 1] = (
                    lines[node.end_lineno - 1][: node.end_col_offset]
                    + marker_suffix
                    + lines[node.end_lineno - 1][node.end_col_offset :]
                )

                lines[node.lineno - 1] = (
                    lines[node.lineno - 1][: node.col_offset]
                    + marker_prefix
                    + lines[node.lineno - 1][node.col_offset :]
                )

            new_source = "".join(lines)
            # make sure it parses
            ast.parse(new_source)
            return new_source
        except SyntaxError:
            return source
        except Exception as e:
            logger.warning("Problem adding Expr handlers", exc_info=e)
            return source

    def _mark_nodes_to_be_guarded_from_instrumentation(self, node, guarded_context):
        if not guarded_context and isinstance(node, ast.FunctionDef):
            guarded_context = True

        setattr(node, "guarded", guarded_context)

        for child in ast.iter_child_nodes(node):
            self._mark_nodes_to_be_guarded_from_instrumentation(child, guarded_context)

    def _is_asm_pio_decorator(self, node):
        if not isinstance(node, ast.Call):
            return False

        if isinstance(node.func, ast.Attribute) and node.func.attr == "asm_pio":
            return True

        if isinstance(node.func, ast.Name) and node.func.id == "asm_pio":
            return True

        return False

    def _expand_stat(self, stat: Union[Tuple, int, str], basename: str) -> Dict:
        error = None
        if isinstance(stat, int):
            # file size is only info available for micro:bit files
            size = stat
            modified = None
            kind = "file"
        elif isinstance(stat, str):
            kind = None
            size = None
            modified = None
            error = stat
        else:
            assert isinstance(stat, tuple)
            if stat[STAT_KIND_INDEX] & 0o170000 == 0o040000:
                kind = "dir"
                size = None
            else:
                kind = "file"
                size = stat[STAT_SIZE_INDEX]

            modified = self._tmgr._system_time_to_posix_time(stat[STAT_MTIME_INDEX])

        result = {
            "kind": kind,
            "size_bytes": size,
            "modified_epoch": modified,
            "hidden": basename.startswith("."),
        }
        if error:
            result["error"] = error
        return result

    def _decode(self, data: bytes) -> str:
        return data.decode(encoding="UTF-8", errors="replace")

    def _log_management_error_details(self, e):
        logger.error(
            "ManagementError details:\n" + "SCRIPT: %s\n\n" + "STDOUT: %s\n\n" + "STDERR: %s\n\n",
            e.script,
            e.out,
            e.err,
        )

    def _get_sep(self):
        return self._tmgr.get_dir_sep()
