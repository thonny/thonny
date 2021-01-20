import _ast
import ast
import builtins
import dis
import functools
import importlib
import inspect
import io
import os.path
import pkgutil
import pydoc
import queue
import re
import site
import subprocess
import sys
import tokenize
import traceback
import types
import warnings
from collections import namedtuple
from importlib.machinery import SourceFileLoader, PathFinder
from typing import Optional, Dict

import __main__

import thonny
from thonny import jedi_utils
from thonny.backend import MainBackend, interrupt_local_process, logger
from thonny.common import (
    InputSubmission,
    EOFCommand,
    ToplevelResponse,
    CommandToBackend,
    ToplevelCommand,
    InlineCommand,
    UserError,
    InlineResponse,
    MessageFromBackend,
    serialize_message,
    ValueInfo,
    path_startswith,
    get_exe_dirs,
    ImmediateCommand,
    get_single_dir_child_data,
    BackendEvent,
    DebuggerCommand,
    execute_system_command,
    FrameInfo,
    is_same_path,
    TextRange,
    range_contains_smaller_or_equal,
    OBJECT_LINK_START,
    OBJECT_LINK_END,
    range_contains_smaller,
    DebuggerResponse,
    get_python_version_string,
    update_system_path,
    get_augmented_system_path,
)

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

_CO_GENERATOR = getattr(inspect, "CO_GENERATOR", 0)
_CO_COROUTINE = getattr(inspect, "CO_COROUTINE", 0)
_CO_ITERABLE_COROUTINE = getattr(inspect, "CO_ITERABLE_COROUTINE", 0)
_CO_ASYNC_GENERATOR = getattr(inspect, "CO_ASYNC_GENERATOR", 0)
_CO_WEIRDO = _CO_GENERATOR | _CO_COROUTINE | _CO_ITERABLE_COROUTINE | _CO_ASYNC_GENERATOR

_REPL_HELPER_NAME = "_thonny_repl_print"

_CONFIG_FILENAME = os.path.join(thonny.THONNY_USER_DIR, "backend_configuration.ini")

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


_backend = None


class MainCPythonBackend(MainBackend):
    def __init__(self, target_cwd):

        MainBackend.__init__(self)

        global _backend
        _backend = self

        self._ini = None
        self._command_handlers = {}
        self._object_info_tweakers = []
        self._import_handlers = {}
        self._input_queue = queue.Queue()
        self._source_preprocessors = []
        self._ast_postprocessors = []
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._heap = {}  # WeakValueDictionary would be better, but can't store reference to None
        self._source_info_by_frame = {}
        site.sethelper()  # otherwise help function is not available
        pydoc.pager = pydoc.plainpager  # otherwise help command plays tricks
        self._install_fake_streams()
        self._install_repl_helper()
        self._current_executor = None
        self._io_level = 0
        self._tty_mode = True
        self._tcl = None

        update_system_path(os.environ, get_augmented_system_path(get_exe_dirs()))

        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if not key.startswith("__") or key in {"__file__", "__cached__"}:
                del __main__.__dict__[key]

        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None

        if "THONNY_FRONTEND_SYS_PATH" in os.environ:
            self._frontend_sys_path = ast.literal_eval(os.environ["THONNY_FRONTEND_SYS_PATH"])
        else:
            self._frontend_sys_path = []
        self._load_shared_modules()
        self._load_plugins()

        # preceding code was run in the directory containing thonny module, now switch to provided
        try:
            os.chdir(os.path.expanduser(target_cwd))
        except OSError:
            try:
                os.chdir(os.path.expanduser("~"))
            except OSError:
                os.chdir("/")  # yes, this works also in Windows

        # ... and replace current-dir path item
        # start in shell mode (may be later switched to script mode)
        # required in shell mode and also required to overwrite thonny location dir
        sys.path[0] = ""
        sys.argv[:] = [""]  # empty "script name"

        if os.name == "nt":
            self._install_signal_handler()

    def _init_command_reader(self):
        # Can't use threaded reader
        # https://github.com/thonny/thonny/issues/1363
        pass

    def _install_signal_handler(self):
        import signal

        def signal_handler(signal_, frame):
            raise KeyboardInterrupt("Execution interrupted")

        if os.name == "nt":
            signal.signal(signal.SIGBREAK, signal_handler)  # pylint: disable=no-member
        else:
            signal.signal(signal.SIGINT, signal_handler)

    def _fetch_next_incoming_message(self, timeout=None) -> CommandToBackend:
        # Reading must be done synchronously
        # https://github.com/thonny/thonny/issues/1363
        self._read_one_incoming_message()
        return self._incoming_message_queue.get()

    def add_command(self, command_name, handler):
        """Handler should be 1-argument function taking command object.

        Handler may return None (in this case no response is sent to frontend)
        or a BackendResponse
        """
        self._command_handlers[command_name] = handler

    def add_object_info_tweaker(self, tweaker):
        """Tweaker should be 2-argument function taking value and export record"""
        self._object_info_tweakers.append(tweaker)

    def add_import_handler(self, module_name, handler):
        if module_name not in self._import_handlers:
            self._import_handlers[module_name] = []
        self._import_handlers[module_name].append(handler)

    def add_source_preprocessor(self, func):
        self._source_preprocessors.append(func)

    def add_ast_postprocessor(self, func):
        self._ast_postprocessors.append(func)

    def get_main_module(self):
        return __main__

    def _read_incoming_msg_line(self) -> str:
        return self._original_stdin.readline()

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._input_queue.put(msg)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        self.send_message(ToplevelResponse(SystemExit=True))
        sys.exit()

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        if isinstance(cmd, ToplevelCommand):
            self._source_info_by_frame = {}
            self._input_queue = queue.Queue()

        if cmd.name in self._command_handlers:
            handler = self._command_handlers[cmd.name]
        else:
            handler = getattr(self, "_cmd_" + cmd.name, None)

        if handler is None:
            response = {"error": "Unknown command: " + cmd.name}
        else:
            try:
                response = handler(cmd)
            except SystemExit as e:
                # Must be caused by Thonny or plugins code
                if isinstance(cmd, ToplevelCommand):
                    logger.exception("Unexpected SystemExit", exc_info=e)
                response = {"SystemExit": True}
            except UserError as e:
                sys.stderr.write(str(e) + "\n")
                response = {}
            except KeyboardInterrupt:
                response = {"user_exception": self._prepare_user_exception()}
            except Exception as e:
                self._report_internal_exception(e)
                response = {"context_info": "other unhandled exception"}

        if response is False:
            # Command doesn't want to send any response
            return

        real_response = self._prepare_command_response(response, cmd)

        if isinstance(real_response, ToplevelResponse):
            real_response["gui_is_active"] = (
                self._get_tcl() is not None or self._get_qt_app() is not None
            )

        self.send_message(real_response)

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        if cmd.name == "interrupt":
            with self._interrupt_lock:
                interrupt_local_process()

    def _should_keep_going(self) -> bool:
        return True

    def get_option(self, name, default=None):
        section, subname = self._parse_option_name(name)
        val = self._get_ini().get(section, subname, fallback=default)
        try:
            return ast.literal_eval(val)
        except Exception:
            return val

    def set_option(self, name, value):
        ini = self._get_ini()
        section, subname = self._parse_option_name(name)
        if not ini.has_section(section):
            ini.add_section(section)
        if not isinstance(value, str):
            value = repr(value)
        ini.set(section, subname, value)
        self.save_settings()

    def _parse_option_name(self, name):
        if "." in name:
            return name.split(".", 1)
        else:
            return "general", name

    def _get_ini(self):
        if self._ini is None:
            import configparser

            self._ini = configparser.ConfigParser(interpolation=None)
            self._ini.read(_CONFIG_FILENAME)

        return self._ini

    def save_settings(self):
        if self._ini is None:
            return

        with open(_CONFIG_FILENAME, "w") as fp:
            self._ini.write(fp)

    def switch_env_to_script_mode(self, cmd):
        if "" in sys.path:
            sys.path.remove("")  # current directory

        filename = cmd.args[0]
        if os.path.isfile(filename):
            sys.path.insert(0, os.path.abspath(os.path.dirname(filename)))
            __main__.__dict__["__file__"] = filename

    def _custom_import(self, *args, **kw):
        module = self._original_import(*args, **kw)

        if not hasattr(module, "__name__"):
            return module

        # module specific handlers
        for handler in self._import_handlers.get(module.__name__, []):
            try:
                handler(module)
            except Exception as e:
                self._report_internal_exception(e)

        # general handlers
        for handler in self._import_handlers.get("*", []):
            try:
                handler(module)
            except Exception as e:
                self._report_internal_exception(e)

        return module

    def _load_shared_modules(self):
        from importlib import import_module

        # these need to be loaded during initialization, because later they may not be in path
        for name in ["parso", "jedi", "thonnycontrib", "six", "asttokens"]:
            try:
                import_module(name)
            except ImportError:
                pass

    def _load_plugins(self):
        # built-in plugins
        try:
            import thonny.plugins.backend  # pylint: disable=redefined-outer-name
        except ImportError:
            # May happen eg. in ssh session
            return

        self._load_plugins_from_path(thonny.plugins.backend.__path__, "thonny.plugins.backend.")

        # 3rd party plugins from namespace package
        try:
            import thonnycontrib.backend  # @UnresolvedImport
        except ImportError:
            # No 3rd party plugins installed
            pass
        else:
            self._load_plugins_from_path(thonnycontrib.backend.__path__, "thonnycontrib.backend.")

    def _load_plugins_from_path(self, path, prefix):
        load_function_name = "load_plugin"
        for _, module_name, _ in sorted(pkgutil.iter_modules(path, prefix), key=lambda x: x[1]):
            try:
                m = importlib.import_module(module_name)
                if hasattr(m, load_function_name):
                    f = getattr(m, load_function_name)
                    sig = inspect.signature(f)
                    if len(sig.parameters) == 0:
                        f()
                    else:
                        f(self)
            except Exception as e:
                logger.exception("Failed loading plugin '" + module_name + "'", exc_info=e)

    def _cmd_get_environment_info(self, cmd):
        return ToplevelResponse(
            main_dir=self._main_dir,
            sys_path=sys.path,
            usersitepackages=site.getusersitepackages() if site.ENABLE_USER_SITE else None,
            prefix=sys.prefix,
            welcome_text="Python " + get_python_version_string(),
            executable=sys.executable,
            exe_dirs=get_exe_dirs(),
            in_venv=(
                hasattr(sys, "base_prefix")
                and sys.base_prefix != sys.prefix
                or hasattr(sys, "real_prefix")
                and getattr(sys, "real_prefix") != sys.prefix
            ),
            python_version=get_python_version_string(),
            cwd=os.getcwd(),
        )

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            path = cmd.args[0]
            try:
                os.chdir(path)
                return ToplevelResponse()
            except FileNotFoundError:
                raise UserError("No such folder: " + path)
            except OSError as e:
                raise UserError("\n".join(traceback.format_exception_only(type(e), e)))
        else:
            raise UserError("cd takes one parameter")

    def _cmd_Run(self, cmd):
        self.switch_env_to_script_mode(cmd)
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_run(self, cmd):
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_FastDebug(self, cmd):
        self.switch_env_to_script_mode(cmd)
        return self._execute_file(cmd, FastTracer)

    def _cmd_Debug(self, cmd):
        self.switch_env_to_script_mode(cmd)
        return self._execute_file(cmd, NiceTracer)

    def _cmd_debug(self, cmd):
        return self._execute_file(cmd, NiceTracer)

    def _cmd_execute_source(self, cmd):
        """Executes Python source entered into shell"""
        self._check_update_tty_mode(cmd)
        filename = "<pyshell>"
        source = cmd.source.strip()

        try:
            root = ast.parse(source, filename=filename, mode="exec")
        except SyntaxError as e:
            error = "".join(traceback.format_exception_only(type(e), e))
            sys.stderr.write(error)
            return ToplevelResponse()

        assert isinstance(root, ast.Module)

        result_attributes = self._execute_source(
            source,
            filename,
            "repl",
            NiceTracer if getattr(cmd, "debug_mode", False) else SimpleRunner,
            cmd,
        )

        return ToplevelResponse(command_name="execute_source", **result_attributes)

    def _cmd_execute_system_command(self, cmd):
        self._check_update_tty_mode(cmd)
        try:
            returncode = execute_system_command(cmd, disconnect_stdin=True)
            return {"returncode": returncode}
        except Exception as e:
            logger.exception("Could not execute system command %s", cmd, exc_info=e)

    def _cmd_process_gui_events(self, cmd):
        # advance the event loop
        try:
            # First try Tkinter.
            # Need to update even when tkinter._default_root is None
            # because otherwise destroyed window will stay up in macOS.

            # When switching between closed user Tk window and another window,
            # the closed window may reappear in IDLE and CLI REPL
            tcl = self._get_tcl()
            if tcl is not None and tcl.has_default_root or tcl.updates_without_root < 1:
                # http://bugs.python.org/issue989712
                # http://bugs.python.org/file6090/run.py.diff
                # https://bugs.python.org/review/989712/diff/4528/Lib/idlelib/run.py
                tcl.eval("update")
                # if not tcl.has_default_root:
                #    tcl.updates_without_root += 1
            else:
                # Try Qt only when Tkinter is not used
                app = self._get_qt_app()
                if app is not None:
                    app.processEvents()

        except Exception:
            pass

        return False

    def _cmd_get_globals(self, cmd):
        # warnings.warn("_cmd_get_globals is deprecated for CPython")
        try:
            return InlineResponse(
                "get_globals",
                module_name=cmd.module_name,
                globals=self.export_globals(cmd.module_name),
            )
        except Exception as e:
            return InlineResponse("get_globals", module_name=cmd.module_name, error=str(e))

    def _cmd_get_frame_info(self, cmd):
        atts = {}
        try:
            # TODO: make it work also in past states
            frame, location = self._lookup_frame_by_id(cmd["frame_id"])
            if frame is None:
                atts["error"] = "Frame not found"
            else:
                atts["code_name"] = frame.f_code.co_name
                atts["module_name"] = frame.f_globals["__name__"]
                atts["locals"] = (
                    None
                    if frame.f_locals is frame.f_globals
                    else self.export_variables(frame.f_locals)
                )
                atts["globals"] = self.export_variables(frame.f_globals)
                atts["freevars"] = frame.f_code.co_freevars
                atts["location"] = location
        except Exception as e:
            atts["error"] = str(e)

        return InlineResponse("get_frame_info", frame_id=cmd.frame_id, **atts)

    def _cmd_get_active_distributions(self, cmd):
        try:
            # if it is called after first installation to user site packages
            # this dir is not yet in sys.path
            if (
                site.ENABLE_USER_SITE
                and site.getusersitepackages()
                and os.path.exists(site.getusersitepackages())
                and site.getusersitepackages() not in sys.path
            ):
                # insert before first site packages item
                for i, item in enumerate(sys.path):
                    if "site-packages" in item or "dist-packages" in item:
                        sys.path.insert(i, site.getusersitepackages())
                        break
                else:
                    sys.path.append(site.getusersitepackages())

            import pkg_resources

            pkg_resources._initialize_master_working_set()
            dists = {
                dist.key: {
                    "project_name": dist.project_name,
                    "key": dist.key,
                    "location": dist.location,
                    "version": dist.version,
                }
                for dist in pkg_resources.working_set  # pylint: disable=not-an-iterable
            }

            return InlineResponse(
                "get_active_distributions",
                distributions=dists,
                usersitepackages=site.getusersitepackages() if site.ENABLE_USER_SITE else None,
            )
        except Exception:
            return InlineResponse("get_active_distributions", error=traceback.format_exc())

    def _cmd_get_locals(self, cmd):
        for frame in inspect.stack():
            if id(frame) == cmd.frame_id:
                return InlineResponse("get_locals", locals=self.export_variables(frame.f_locals))

        raise RuntimeError("Frame '{0}' not found".format(cmd.frame_id))

    def _cmd_get_heap(self, cmd):
        result = {}
        for key in self._heap:
            result[key] = self.export_value(self._heap[key])

        return InlineResponse("get_heap", heap=result)

    def _cmd_shell_autocomplete(self, cmd):
        error = None
        try:
            import jedi
        except ImportError:
            jedi = None
            completions = []
            error = "Could not import jedi"
        else:
            try:
                with warnings.catch_warnings():
                    jedi_completions = jedi_utils.get_interpreter_completions(
                        cmd.source, [__main__.__dict__]
                    )
                    completions = self._export_completions(jedi_completions)
            except Exception as e:
                completions = []
                logger.info("Autocomplete error", exc_info=e)
                error = "Autocomplete error: " + str(e)

        return InlineResponse(
            "shell_autocomplete", source=cmd.source, completions=completions, error=error
        )

    def _cmd_editor_autocomplete(self, cmd):
        error = None
        try:
            import jedi

            self._debug(jedi.__file__, sys.path)
            with warnings.catch_warnings():
                jedi_completions = jedi_utils.get_script_completions(
                    cmd.source, cmd.row, cmd.column, cmd.filename
                )
                completions = self._export_completions(jedi_completions)

        except ImportError:
            jedi = None
            completions = []
            error = "Could not import jedi"
        except Exception as e:
            completions = []
            logger.info("Autocomplete error", exc_info=e)
            error = "Autocomplete error: " + str(e)

        return InlineResponse(
            "editor_autocomplete",
            source=cmd.source,
            row=cmd.row,
            column=cmd.column,
            filename=cmd.filename,
            completions=completions,
            error=error,
        )

    def _cmd_get_object_info(self, cmd):
        if isinstance(self._current_executor, NiceTracer) and self._current_executor.is_in_past():
            info = {"id": cmd.object_id, "error": "past info not available"}

        elif cmd.object_id in self._heap:
            value = self._heap[cmd.object_id]
            attributes = {}
            if cmd.include_attributes:
                for name in dir(value):
                    if not name.startswith("__") or cmd.all_attributes:
                        # attributes[name] = inspect.getattr_static(value, name)
                        try:
                            attributes[name] = getattr(value, name)
                        except Exception:
                            pass

            self._heap[id(type(value))] = type(value)
            info = {
                "id": cmd.object_id,
                "repr": repr(value),
                "type": str(type(value)),
                "full_type_name": str(type(value))
                .replace("<class '", "")
                .replace("'>", "")
                .strip(),
                "attributes": self.export_variables(attributes),
            }

            if isinstance(value, io.TextIOWrapper):
                self._add_file_handler_info(value, info)
            elif isinstance(
                value,
                (
                    types.BuiltinFunctionType,
                    types.BuiltinMethodType,
                    types.FunctionType,
                    types.LambdaType,
                    types.MethodType,
                ),
            ):
                self._add_function_info(value, info)
            elif isinstance(value, (list, tuple, set)):
                self._add_elements_info(value, info)
            elif isinstance(value, dict):
                self._add_entries_info(value, info)
            elif isinstance(value, float):
                self._add_float_info(value, info)
            elif hasattr(value, "image_data"):
                info["image_data"] = value.image_data

            for tweaker in self._object_info_tweakers:
                try:
                    tweaker(value, info, cmd)
                except Exception:
                    logger.exception("Failed object info tweaker: " + str(tweaker))

        else:
            info = {"id": cmd.object_id, "error": "object info not available"}

        return InlineResponse("get_object_info", id=cmd.object_id, info=info)

    def _cmd_mkdir(self, cmd):
        os.mkdir(cmd.path)

    def _cmd_delete(self, cmd):
        for path in cmd.paths:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    import shutil

                    shutil.rmtree(path)
            except Exception as e:
                print("Could not delete %s: %s" % (path, str(e)), file=sys.stderr)

    def _get_sep(self) -> str:
        return os.path.sep

    def _get_dir_children_info(
        self, path: str, include_hidden: bool = False
    ) -> Optional[Dict[str, Dict]]:
        return get_single_dir_child_data(path, include_hidden)

    def _get_path_info(self, path: str) -> Optional[Dict]:

        try:
            if not os.path.exists(path):
                return None
        except OSError:
            pass

        try:
            kind = "dir" if os.path.isdir(path) else "file"
            return {
                "path": path,
                "kind": kind,
                "size": None if kind == "dir" else os.path.getsize(path),
                "modified": os.path.getmtime(path),
                "error": None,
            }
        except OSError as e:
            return {
                "path": path,
                "kind": None,
                "size": None,
                "modified": None,
                "error": str(e),
            }

    def _export_completions(self, jedi_completions):
        result = []
        for c in jedi_completions:
            if not c.name.startswith("__"):
                record = {
                    "name": c.name,
                    "complete": c.complete,
                    "type": c.type,
                    "description": c.description,
                }
                """ TODO: 
                try:
                    if c.type in ["class", "module", "function"]:
                        if c.type == "function":
                            record["docstring"] = c.docstring()
                        else:
                            record["docstring"] = c.description + "\n" + c.docstring()
                except Exception:
                    pass
                """
                result.append(record)
        return result

    def _get_tcl(self):
        if self._tcl is not None:
            return self._tcl

        tkinter = sys.modules.get("tkinter")
        if tkinter is None:
            return None

        if self._tcl is None:
            try:
                self._tcl = tkinter.Tcl()
                self._tcl.updates_without_root = 0
            except Exception as e:
                logger.error("Could not get Tcl", exc_info=e)
                self._tcl = None
                return None

        self._tcl.has_default_root = tkinter._default_root is not None
        return self._tcl

    def _get_qt_app(self):
        mod = sys.modules.get("PyQt5.QtCore")
        if mod is None:
            mod = sys.modules.get("PyQt4.QtCore")
        if mod is None:
            mod = sys.modules.get("PySide.QtCore")
        if mod is None:
            return None

        app_class = getattr(mod, "QCoreApplication", None)
        if app_class is not None:
            try:
                return app_class.instance()
            except Exception:
                return None
        else:
            return None

    def _add_file_handler_info(self, value, info):
        try:
            assert isinstance(value.name, str)
            assert value.mode in ("r", "rt", "tr", "br", "rb")
            assert value.errors in ("strict", None)
            assert value.newlines is None or value.tell() > 0
            # TODO: cache the content
            # TODO: don't read too big files
            with open(value.name, encoding=value.encoding) as f:
                info["file_encoding"] = f.encoding
                info["file_content"] = f.read()
                info["file_tell"] = value.tell()
        except Exception as e:
            info["file_error"] = "Could not get file content, error:" + str(e)

    def _add_function_info(self, value, info):
        try:
            info["source"] = inspect.getsource(value)
        except Exception:
            pass

    def _add_elements_info(self, value, info):
        info["elements"] = []
        for element in value:
            info["elements"].append(self.export_value(element))

    def _add_entries_info(self, value, info):
        info["entries"] = []
        for key in value:
            info["entries"].append((self.export_value(key), self.export_value(value[key])))

    def _add_float_info(self, value, info):
        if not value.is_integer():
            info["as_integer_ratio"] = value.as_integer_ratio()

    def _execute_file(self, cmd, executor_class):
        self._check_update_tty_mode(cmd)

        if len(cmd.args) >= 1:
            sys.argv = cmd.args
            filename = cmd.args[0]
            if filename == "-c" or os.path.isabs(filename):
                full_filename = filename
            else:
                full_filename = os.path.abspath(filename)

            if full_filename == "-c":
                source = cmd.source
            else:
                with tokenize.open(full_filename) as fp:
                    source = fp.read()

            for preproc in self._source_preprocessors:
                source = preproc(source, cmd)

            result_attributes = self._execute_source(
                source, full_filename, "exec", executor_class, cmd, self._ast_postprocessors
            )
            result_attributes["filename"] = full_filename
            return ToplevelResponse(command_name=cmd.name, **result_attributes)
        else:
            raise UserError("Command '%s' takes at least one argument" % cmd.name)

    def _execute_source(
        self, source, filename, execution_mode, executor_class, cmd, ast_postprocessors=[]
    ):
        self._current_executor = executor_class(self, cmd)

        try:
            return self._current_executor.execute_source(
                source, filename, execution_mode, ast_postprocessors
            )
        finally:
            self._current_executor = None

    def _install_repl_helper(self):
        def _handle_repl_value(obj):
            if obj is not None:
                try:
                    obj_repr = repr(obj)
                    if len(obj_repr) > 5000:
                        obj_repr = obj_repr[:5000] + "…"
                except Exception as e:
                    obj_repr = "<repr error: " + str(e) + ">"
                print("%s%s@%s%s" % (OBJECT_LINK_START, obj_repr, id(obj), OBJECT_LINK_END))
                self._heap[id(obj)] = obj
                builtins._ = obj

        setattr(builtins, _REPL_HELPER_NAME, _handle_repl_value)

    def _install_fake_streams(self):
        self._original_stdin = sys.stdin
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # yes, both out and err will be directed to out (but with different tags)
        # this allows client to see the order of interleaving writes to stdout/stderr
        sys.stdin = FakeInputStream(self, sys.stdin)
        sys.stdout = FakeOutputStream(self, sys.stdout, "stdout")
        sys.stderr = FakeOutputStream(self, sys.stdout, "stderr")

        # fake it properly: replace also "backup" streams
        sys.__stdin__ = sys.stdin
        sys.__stdout__ = sys.stdout
        sys.__stderr__ = sys.stderr

    def _install_custom_import(self):
        self._original_import = builtins.__import__
        builtins.__import__ = self._custom_import

    def _restore_original_import(self):
        builtins.__import__ = self._original_import

    def send_message(self, msg: MessageFromBackend) -> None:
        sys.stdout.flush()

        if isinstance(msg, ToplevelResponse):
            if "cwd" not in msg:
                msg["cwd"] = os.getcwd()
            if "globals" not in msg:
                msg["globals"] = self.export_globals()

        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()

    def export_value(self, value, max_repr_length=5000):
        self._heap[id(value)] = value
        try:
            rep = repr(value)
        except Exception:
            # See https://bitbucket.org/plas/thonny/issues/584/problem-with-thonnys-back-end-obj-no
            rep = "??? <repr error>"

        if len(rep) > max_repr_length:
            rep = rep[:max_repr_length] + "…"

        return ValueInfo(id(value), rep)

    def export_variables(self, variables):
        result = {}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            for name in variables:
                if not name.startswith("__"):
                    result[name] = self.export_value(variables[name], 100)

        return result

    def export_globals(self, module_name="__main__"):
        if module_name in sys.modules:
            return self.export_variables(sys.modules[module_name].__dict__)
        else:
            raise RuntimeError("Module '{0}' is not loaded".format(module_name))

    def _debug(self, *args):
        logger.debug("MainCPythonBackend: " + str(args))

    def _enter_io_function(self):
        self._io_level += 1

    def _exit_io_function(self):
        self._io_level -= 1

    def is_doing_io(self):
        return self._io_level > 0

    def _export_stack(self, newest_frame, relevance_checker=None):
        result = []

        system_frame = newest_frame

        while system_frame is not None:
            module_name = system_frame.f_globals["__name__"]
            code_name = system_frame.f_code.co_name

            if not relevance_checker or relevance_checker(system_frame):
                source, firstlineno, in_library = self._get_frame_source_info(system_frame)

                result.insert(
                    0,
                    FrameInfo(
                        # TODO: can this id be reused by a later frame?
                        # Need to store the reference to avoid GC?
                        # I guess it is not required, as id will be required
                        # only for stacktrace inspection, and sys.last_exception
                        # will have the reference anyway
                        # (NiceTracer has its own reference keeping)
                        id=id(system_frame),
                        filename=system_frame.f_code.co_filename,
                        module_name=module_name,
                        code_name=code_name,
                        locals=self.export_variables(system_frame.f_locals),
                        globals=self.export_variables(system_frame.f_globals),
                        freevars=system_frame.f_code.co_freevars,
                        source=source,
                        lineno=system_frame.f_lineno,
                        firstlineno=firstlineno,
                        in_library=in_library,
                        event="line",
                        focus=TextRange(system_frame.f_lineno, 0, system_frame.f_lineno + 1, 0),
                        node_tags=None,
                        current_statement=None,
                        current_evaluations=None,
                        current_root_expression=None,
                    ),
                )

            if module_name == "__main__" and code_name == "<module>":
                # this was last frame relevant to the user
                break

            system_frame = system_frame.f_back

        assert result  # not empty
        return result

    def _lookup_frame_by_id(self, frame_id):
        def lookup_from_stack(frame):
            if frame is None:
                return None
            elif id(frame) == frame_id:
                return frame
            else:
                return lookup_from_stack(frame.f_back)

        def lookup_from_tb(entry):
            if entry is None:
                return None
            elif id(entry.tb_frame) == frame_id:
                return entry.tb_frame
            else:
                return lookup_from_tb(entry.tb_next)

        result = lookup_from_stack(inspect.currentframe())
        if result is not None:
            return result, "stack"

        if getattr(sys, "last_traceback"):
            result = lookup_from_tb(getattr(sys, "last_traceback"))
            if result:
                return result, "last_traceback"

        _, _, tb = sys.exc_info()
        return lookup_from_tb(tb), "current_exception"

    def _get_frame_source_info(self, frame):
        fid = id(frame)
        if fid not in self._source_info_by_frame:
            self._source_info_by_frame[fid] = _fetch_frame_source_info(frame)

        return self._source_info_by_frame[fid]

    def _prepare_user_exception(self):
        e_type, e_value, e_traceback = sys.exc_info()
        sys.last_type, sys.last_value, sys.last_traceback = (e_type, e_value, e_traceback)

        processed_tb = traceback.extract_tb(e_traceback)

        tb = e_traceback
        while tb.tb_next is not None:
            tb = tb.tb_next
        last_frame = tb.tb_frame

        if e_type is SyntaxError:
            # Don't show ast frame
            while last_frame.f_code.co_filename and last_frame.f_code.co_filename == ast.__file__:
                last_frame = last_frame.f_back

        if e_type is SyntaxError:
            msg = (
                traceback.format_exception_only(e_type, e_value)[-1]
                .replace(e_type.__name__ + ":", "")
                .strip()
            )
        else:
            msg = str(e_value)

        return {
            "type_name": e_type.__name__,
            "message": msg,
            "stack": self._export_stack(last_frame),
            "items": format_exception_with_frame_info(e_type, e_value, e_traceback),
            "filename": getattr(e_value, "filename", processed_tb[-1].filename),
            "lineno": getattr(e_value, "lineno", processed_tb[-1].lineno),
            "col_offset": getattr(e_value, "offset", None),
            "line": getattr(e_value, "text", processed_tb[-1].line),
        }

    def _check_update_tty_mode(self, cmd):
        if "tty_mode" in cmd:
            self._tty_mode = cmd["tty_mode"]


class FakeStream:
    def __init__(self, backend: MainCPythonBackend, target_stream):
        self._backend = backend
        self._target_stream = target_stream
        self._processed_symbol_count = 0

    def isatty(self):
        return self._backend._tty_mode and (os.name != "nt" or "click" not in sys.modules)

    def __getattr__(self, name):
        # TODO: is it safe to perform those other functions without notifying backend
        # via _enter_io_function?
        return getattr(self._target_stream, name)


class FakeOutputStream(FakeStream):
    def __init__(self, backend: MainCPythonBackend, target_stream, stream_name):
        FakeStream.__init__(self, backend, target_stream)
        self._stream_name = stream_name

    def write(self, data):
        try:
            self._backend._enter_io_function()
            # click may send bytes instead of strings
            if isinstance(data, bytes):
                data = data.decode(errors="replace")

            if data != "":
                self._backend._send_output(data=data, stream_name=self._stream_name)
                self._processed_symbol_count += len(data)
        finally:
            self._backend._exit_io_function()

    def writelines(self, lines):
        try:
            self._backend._enter_io_function()
            self.write("".join(lines))
        finally:
            self._backend._exit_io_function()


class FakeInputStream(FakeStream):
    def __init__(self, backend: MainCPythonBackend, target_stream):
        super().__init__(backend, target_stream)
        self._buffer = ""
        self._eof = False

    def _generic_read(self, method, original_limit):
        if original_limit is None:
            effective_limit = -1
        elif method == "readlines" and original_limit > -1:
            # NB! size hint is defined in weird way
            # "no more lines will be read if the total size (in bytes/characters)
            # of all lines so far **exceeds** the hint".
            effective_limit = original_limit + 1
        else:
            effective_limit = original_limit

        try:
            self._backend._enter_io_function()
            while True:
                if effective_limit == 0:
                    result = ""
                    break

                elif effective_limit > 0 and len(self._buffer) >= effective_limit:
                    result = self._buffer[:effective_limit]
                    self._buffer = self._buffer[effective_limit:]
                    if method == "readlines" and not result.endswith("\n") and "\n" in self._buffer:
                        # limit is just a hint
                        # https://docs.python.org/3/library/io.html#io.IOBase.readlines
                        extra = self._buffer[: self._buffer.find("\n") + 1]
                        result += extra
                        self._buffer = self._buffer[len(extra) :]
                    break

                elif method == "readline" and "\n" in self._buffer:
                    pos = self._buffer.find("\n") + 1
                    result = self._buffer[:pos]
                    self._buffer = self._buffer[pos:]
                    break

                elif self._eof:
                    result = self._buffer
                    self._buffer = ""
                    self._eof = False  # That's how official implementation does
                    break

                else:
                    self._backend.send_message(
                        BackendEvent("InputRequest", method=method, limit=original_limit)
                    )
                    msg = self._backend._fetch_next_incoming_message()
                    if isinstance(msg, InputSubmission):
                        self._buffer += msg.data
                        self._processed_symbol_count += len(msg.data)
                    elif isinstance(msg, EOFCommand):
                        self._eof = True
                    elif isinstance(msg, InlineCommand):
                        self._backend._handle_normal_command(msg)
                    else:
                        raise RuntimeError(
                            "Wrong type of command (%r) when waiting for input" % (msg,)
                        )

            return result

        finally:
            self._backend._exit_io_function()

    def read(self, limit=-1):
        return self._generic_read("read", limit)

    def readline(self, limit=-1):
        return self._generic_read("readline", limit)

    def readlines(self, limit=-1):
        return self._generic_read("readlines", limit).splitlines(True)

    def __next__(self):
        result = self.readline()
        if not result:
            raise StopIteration

        return result

    def __iter__(self):
        return self


def prepare_hooks(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            sys.meta_path.insert(0, self)
            self._backend._install_custom_import()
            return method(self, *args, **kwargs)
        finally:
            del sys.meta_path[0]
            if hasattr(self._backend, "_original_import"):
                self._backend._restore_original_import()

    return wrapper


def return_execution_result(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
            if result is not None:
                return result
            return {"context_info": "after normal execution"}
        except Exception:
            return {"user_exception": self._backend._prepare_user_exception()}

    return wrapper


class Executor:
    def __init__(self, backend: MainCPythonBackend, original_cmd):
        self._backend = backend
        self._original_cmd = original_cmd
        self._main_module_path = None

    def execute_source(self, source, filename, mode, ast_postprocessors):
        if isinstance(source, str):
            # TODO: simplify this or make sure encoding is correct
            source = source.encode("utf-8")

        if os.path.exists(filename):
            self._main_module_path = filename

        global_vars = __main__.__dict__

        try:
            if mode == "repl":
                assert not ast_postprocessors
                # Useful in shell to get last expression value in multi-statement block
                root = self._prepare_ast(source, filename, "exec")
                # https://bugs.python.org/issue35894
                # https://github.com/pallets/werkzeug/pull/1552/files#diff-9e75ca133f8601f3b194e2877d36df0eR950
                module = ast.parse("")
                module.body = root.body
                self._instrument_repl_code(module)
                statements = compile(module, filename, "exec")
            elif mode == "exec":
                root = self._prepare_ast(source, filename, mode)
                for func in ast_postprocessors:
                    func(root)
                statements = compile(root, filename, mode)
            else:
                raise ValueError("Unknown mode", mode)

            return self._execute_prepared_user_code(statements, global_vars)
        except SyntaxError:
            return {"user_exception": self._backend._prepare_user_exception()}
        except SystemExit:
            return {"SystemExit": True}
        except Exception as e:
            self._backend._report_internal_exception(e)
            return {}

    @return_execution_result
    @prepare_hooks
    def _execute_prepared_user_code(self, statements, global_vars):
        exec(statements, global_vars)

    def find_spec(self, fullname, path=None, target=None):
        """override in subclass for custom-loading user modules"""
        return None

    def _prepare_ast(self, source, filename, mode):
        return ast.parse(source, filename, mode)

    def _instrument_repl_code(self, root):
        # modify all expression statements to print and register their non-None values
        for node in ast.walk(root):
            if (
                isinstance(node, ast.FunctionDef)
                or hasattr(ast, "AsyncFunctionDef")
                and isinstance(node, ast.AsyncFunctionDef)
            ):
                first_stmt = node.body[0]
                if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Str):
                    first_stmt.contains_docstring = True
            if isinstance(node, ast.Expr) and not getattr(node, "contains_docstring", False):
                node.value = ast.Call(
                    func=ast.Name(id=_REPL_HELPER_NAME, ctx=ast.Load()),
                    args=[node.value],
                    keywords=[],
                )
                ast.fix_missing_locations(node)


class SimpleRunner(Executor):
    pass


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
                    path_startswith(path, os.path.dirname(self._main_module_path))
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

    def _prepare_ast(self, source, filename, mode):
        # ast_utils need to be imported after asttokens
        # is (custom-)imported
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
        except BaseException as e:
            logger.exception("Exception in _trace", exc_info=e)
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
                or not range_contains_smaller_or_equal(prev_root_expression, focus)
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
            module_name = system_frame.f_globals["__name__"]
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
            module_name = system_frame.f_globals["__name__"]

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


class CustomStackFrame:
    def __init__(self, frame, event, focus=None):
        self.system_frame = frame
        self.event = event
        self.focus = focus
        self.current_evaluations = []
        self.current_statement = None
        self.current_root_expression = None
        self.node_tags = set()


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


def _get_frame_prefix(frame):
    return str(id(frame)) + " " + ">" * len(inspect.getouterframes(frame, 0)) + " "


def _fetch_frame_source_info(frame):
    if frame.f_code.co_filename is None or not os.path.exists(frame.f_code.co_filename):
        return None, None, True

    is_libra = _is_library_file(frame.f_code.co_filename)

    if frame.f_code.co_name == "<lambda>":
        source = inspect.getsource(frame.f_code)
        return source, frame.f_code.co_firstlineno, is_libra
    elif frame.f_code.co_name == "<module>":
        # inspect.getsource and getsourcelines don't help here
        with tokenize.open(frame.f_code.co_filename) as fp:
            return fp.read(), 1, is_libra
    else:
        # function or class
        try:
            source = inspect.getsource(frame.f_code)

            # inspect.getsource is not reliable, see eg:
            # https://bugs.python.org/issue35101
            # If the code name is not present as definition
            # in the beginning of the source,
            # then play safe and return the whole script
            first_line = source.splitlines()[0]
            if re.search(r"\b(class|def)\b\s+\b%s\b" % frame.f_code.co_name, first_line) is None:
                with tokenize.open(frame.f_code.co_filename) as fp:
                    return fp.read(), 1, is_libra

            else:
                return source, frame.f_code.co_firstlineno, is_libra
        except OSError:
            logger.exception("Problem getting source")
            return None, None, True


def format_exception_with_frame_info(e_type, e_value, e_traceback, shorten_filenames=False):
    """Need to suppress thonny frames to avoid confusion"""

    _traceback_message = "Traceback (most recent call last):\n"

    _cause_message = getattr(
        traceback,
        "_cause_message",
        ("\nThe above exception was the direct cause " + "of the following exception:") + "\n\n",
    )

    _context_message = getattr(
        traceback,
        "_context_message",
        ("\nDuring handling of the above exception, " + "another exception occurred:") + "\n\n",
    )

    def rec_format_exception_with_frame_info(etype, value, tb, chain=True):
        # Based on
        # https://www.python.org/dev/peps/pep-3134/#enhanced-reporting
        # and traceback.format_exception

        if etype is None:
            etype = type(value)

        if tb is None:
            tb = value.__traceback__

        if chain:
            if value.__cause__ is not None:
                yield from rec_format_exception_with_frame_info(None, value.__cause__, None)
                yield (_cause_message, None, None, None)
            elif value.__context__ is not None and not value.__suppress_context__:
                yield from rec_format_exception_with_frame_info(None, value.__context__, None)
                yield (_context_message, None, None, None)

        if tb is not None:
            yield (_traceback_message, None, None, None)

            tb_temp = tb
            for entry in traceback.extract_tb(tb):
                assert tb_temp is not None  # actual tb doesn't end before extract_tb
                if "cpython_backend" not in entry.filename and (
                    not entry.filename.endswith(os.sep + "ast.py")
                    or entry.name != "parse"
                    or etype is not SyntaxError
                ):
                    fmt = '  File "{}", line {}, in {}\n'.format(
                        entry.filename, entry.lineno, entry.name
                    )

                    if entry.line:
                        fmt += "    {}\n".format(entry.line.strip())

                    yield (fmt, id(tb_temp.tb_frame), entry.filename, entry.lineno)

                tb_temp = tb_temp.tb_next

            assert tb_temp is None  # tb was exhausted

        for line in traceback.format_exception_only(etype, value):
            if etype is SyntaxError and line.endswith("^\n"):
                # for some reason it may add several empty lines before ^-line
                partlines = line.splitlines()
                while len(partlines) >= 2 and partlines[-2].strip() == "":
                    del partlines[-2]
                line = "\n".join(partlines) + "\n"

            yield (line, None, None, None)

    items = rec_format_exception_with_frame_info(e_type, e_value, e_traceback)

    return list(items)


def in_debug_mode():
    return os.environ.get("THONNY_DEBUG", False) in [1, "1", True, "True", "true"]


def _is_library_file(filename):
    return (
        filename is None
        or path_startswith(filename, sys.prefix)
        or hasattr(sys, "base_prefix")
        and path_startswith(filename, sys.base_prefix)
        or hasattr(sys, "real_prefix")
        and path_startswith(filename, getattr(sys, "real_prefix"))
        or site.ENABLE_USER_SITE
        and path_startswith(filename, site.getusersitepackages())
    )


def get_backend():
    return _backend
