# -*- coding: utf-8 -*-

import ast
import builtins
import copy
import importlib
import inspect
import io
import logging
import os.path
import pkgutil
import pydoc
import signal
import site
import subprocess
import sys
import tokenize
import traceback
import types
import warnings
from collections import namedtuple
from importlib.machinery import PathFinder, SourceFileLoader

import __main__  # @UnresolvedImport
import _ast
import thonny
from thonny import ast_utils
from thonny.common import (
    BackendEvent,
    DebuggerCommand,
    DebuggerResponse,
    FrameInfo,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    TextRange,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    ValueInfo,
    parse_message,
    path_startswith,
    range_contains_smaller,
    range_contains_smaller_or_equal,
    serialize_message,
)

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

logger = logging.getLogger("thonny.backend")

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


_vm = None


class VM:
    def __init__(self):
        global _vm
        _vm = self

        self._ini = None
        self._command_handlers = {}
        self._object_info_tweakers = []
        self._import_handlers = {}
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._heap = (
            {}
        )  # WeakValueDictionary would be better, but can't store reference to None
        self._source_info_by_frame = {}
        site.sethelper()  # otherwise help function is not available
        pydoc.pager = pydoc.plainpager  # otherwise help command plays tricks
        self._install_fake_streams()
        self._current_executor = None
        self._io_level = 0

        init_msg = self._fetch_command()

        original_argv = sys.argv.copy()
        original_path = sys.path.copy()

        # clean up path
        sys.path = [d for d in sys.path if d != ""]

        # script mode
        if len(sys.argv) > 1:
            special_names_to_remove = set()
            sys.argv[:] = sys.argv[1:]  # shift argv[1] to position of script name
            sys.path.insert(
                0, os.path.abspath(os.path.dirname(sys.argv[0]))
            )  # add program's dir
            __main__.__dict__["__file__"] = sys.argv[0]
            # TODO: inspect.getdoc

        # shell mode
        else:
            special_names_to_remove = {"__file__", "__cached__"}
            sys.argv[:] = [""]  # empty "script name"
            sys.path.insert(0, "")  # current dir

        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if not key.startswith("__") or key in special_names_to_remove:
                del __main__.__dict__[key]

        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None

        self._load_shared_modules(init_msg["frontend_sys_path"])
        self._load_plugins()

        self.send_message(
            ToplevelResponse(
                main_dir=self._main_dir,
                original_argv=original_argv,
                original_path=original_path,
                argv=sys.argv,
                path=sys.path,
                usersitepackages=site.getusersitepackages()
                if site.ENABLE_USER_SITE
                else None,
                prefix=sys.prefix,
                welcome_text="Python " + _get_python_version_string(),
                executable=sys.executable,
                in_venv=(
                    hasattr(sys, "base_prefix")
                    and sys.base_prefix != sys.prefix
                    or hasattr(sys, "real_prefix")
                    and getattr(sys, "real_prefix") != sys.prefix
                ),
                python_version=_get_python_version_string(),
                cwd=os.getcwd(),
            )
        )

        self._install_signal_handler()

    def mainloop(self):
        try:
            while True:
                try:
                    cmd = self._fetch_command()
                    self._source_info_by_frame = {}
                    self.handle_command(cmd)
                except KeyboardInterrupt:
                    logger.exception("Interrupt in mainloop")
                    # Interrupt must always result in waiting_toplevel_command state
                    # Don't show error messages, as the interrupted command may have been InlineCommand
                    # (handlers of ToplevelCommands in normal cases catch the interrupt and provide
                    # relevant message)
                    self.send_message(ToplevelResponse())
        except Exception:
            logger.exception("Crash in mainloop")
            traceback.print_exc()

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

    def get_main_module(self):
        return __main__

    def handle_command(self, cmd):
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        def create_error_response(**kw):
            if isinstance(cmd, ToplevelCommand):
                return ToplevelResponse(command_name=cmd.name, **kw)
            else:
                return InlineResponse(command_name=cmd.name, **kw)

        if cmd.name in self._command_handlers:
            handler = self._command_handlers[cmd.name]
        else:
            handler = getattr(self, "_cmd_" + cmd.name, None)

        if handler is None:
            response = create_error_response(error="Unknown command: " + cmd.name)
        else:
            try:
                response = handler(cmd)
            except SystemExit:
                # Must be caused by Thonny or plugins code
                if isinstance(cmd, ToplevelCommand):
                    traceback.print_exc()
                response = create_error_response(SystemExit=True)
            except UserError as e:
                sys.stderr.write(str(e) + "\n")
                response = create_error_response()
            except KeyboardInterrupt:
                response = create_error_response(
                    user_exception=self._prepare_user_exception()
                )
            except Exception:
                _report_internal_error()
                response = create_error_response(
                    context_info="other unhandled exception"
                )

        if response is False:
            # Command doesn't want to send any response
            return

        if response is None and isinstance(cmd, ToplevelCommand):
            # create simple default response
            response = ToplevelResponse(command_name=cmd.name)

        # TODO: add these in response creation time in a helper function
        if isinstance(response, ToplevelResponse):
            response["gui_is_active"] = (
                self._get_tkinter_default_root() is not None
                or self._get_qt_app() is not None
            )

        self.send_message(response)

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

    def _custom_import(self, *args, **kw):
        module = self._original_import(*args, **kw)

        # module specific handlers
        for handler in self._import_handlers.get(module.__name__, []):
            try:
                handler(module)
            except Exception:
                _report_internal_error()

        # general handlers
        for handler in self._import_handlers.get("*", []):
            try:
                handler(module)
            except Exception:
                _report_internal_error()

        return module

    def _load_shared_modules(self, frontend_sys_path):
        for name in ["parso", "jedi", "thonnycontrib"]:
            load_module_from_alternative_path(name, frontend_sys_path)

    def _load_plugins(self):
        # built-in plugins
        import thonny.plugins.backend  # pylint: disable=redefined-outer-name

        self._load_plugins_from_path(
            thonny.plugins.backend.__path__, "thonny.plugins.backend."
        )

        # 3rd party plugins from namespace package
        try:
            import thonnycontrib.backend  # @UnresolvedImport
        except ImportError:
            # No 3rd party plugins installed
            pass
        else:
            self._load_plugins_from_path(
                thonnycontrib.backend.__path__, "thonnycontrib.backend."
            )

    def _load_plugins_from_path(self, path, prefix):
        load_function_name = "load_plugin"
        for _, module_name, _ in sorted(
            pkgutil.iter_modules(path, prefix), key=lambda x: x[1]
        ):
            try:
                m = importlib.import_module(module_name)
                if hasattr(m, load_function_name):
                    f = getattr(m, load_function_name)
                    sig = inspect.signature(f)
                    if len(sig.parameters) == 0:
                        f()
                    else:
                        f(self)
            except Exception:
                logger.exception("Failed loading plugin '" + module_name + "'")

    def _install_signal_handler(self):
        def signal_handler(signal_, frame):
            raise KeyboardInterrupt("Execution interrupted")

        if os.name == "nt":
            signal.signal(signal.SIGBREAK, signal_handler)
        else:
            signal.signal(signal.SIGINT, signal_handler)

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            path = cmd.args[0]
            try:
                os.chdir(path)
                return ToplevelResponse()
            except FileNotFoundError:
                raise UserError("No such folder: " + path)
        else:
            raise UserError("cd takes one parameter")

    def _cmd_Run(self, cmd):
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_run(self, cmd):
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_FastDebug(self, cmd):
        return self._execute_file(cmd, FastTracer)

    def _cmd_Debug(self, cmd):
        return self._execute_file(cmd, NiceTracer)

    def _cmd_debug(self, cmd):
        return self._execute_file(cmd, NiceTracer)

    def _cmd_execute_source(self, cmd):
        """Executes Python source entered into shell"""
        filename = "<pyshell>"
        ws_stripped_source = cmd.source.strip()
        source = ws_stripped_source.strip("?")
        num_stripped_question_marks = len(ws_stripped_source) - len(source)

        # let's see if it's single expression or something more complex
        try:
            root = ast.parse(source, filename=filename, mode="exec")
        except SyntaxError as e:
            error = "".join(traceback.format_exception_only(type(e), e))
            sys.stderr.write(error)
            return ToplevelResponse()

        assert isinstance(root, ast.Module)

        if len(root.body) == 1 and isinstance(root.body[0], ast.Expr):
            mode = "eval"
        elif len(root.body) > 1 and isinstance(root.body[-1], ast.Expr):
            mode = "exec+eval"
        else:
            mode = "exec"

        result_attributes = self._execute_source(
            source,
            filename,
            mode,
            NiceTracer if getattr(cmd, "debug_mode", False) else SimpleRunner,
            cmd,
        )

        result_attributes["num_stripped_question_marks"] = num_stripped_question_marks

        return ToplevelResponse(command_name="execute_source", **result_attributes)

    def _cmd_execute_system_command(self, cmd):
        # TODO: how to publish stdout as it arrives?
        env = dict(os.environ).copy()
        env["PYTHONIOENCODING"] = "ascii"
        proc = subprocess.Popen(
            cmd.argv,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env,
            universal_newlines=True,
            encoding="ascii",
            errors="backslashreplace",
        )
        out, err = proc.communicate(input="")
        print(out, end="")
        print(err, file=sys.stderr, end="")

    def _cmd_process_gui_events(self, cmd):
        # advance the event loop

        try:
            # First try Tkinter:
            root = self._get_tkinter_default_root()
            if root is not None:
                import tkinter

                # http://bugs.python.org/issue989712
                # http://bugs.python.org/file6090/run.py.diff
                while root.dooneevent(tkinter._tkinter.DONT_WAIT):
                    pass
            else:
                # Try Qt only when Tkinter is not used
                app = self._get_qt_app()
                if app is not None:
                    app.processEvents()

        except Exception:
            pass

        return False

    def _cmd_get_globals(self, cmd):
        warnings.warn("_cmd_get_globals is deprecated for CPython")
        try:
            return InlineResponse(
                "get_globals",
                module_name=cmd.module_name,
                globals=self.export_globals(cmd.module_name),
            )
        except Exception as e:
            return InlineResponse(
                "get_globals", module_name=cmd.module_name, error=str(e)
            )

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
                for dist in pkg_resources.working_set
            }  # pylint: disable=not-an-iterable

            return InlineResponse(
                "get_active_distributions",
                distributions=dists,
                usersitepackages=site.getusersitepackages()
                if site.ENABLE_USER_SITE
                else None,
            )
        except Exception:
            return InlineResponse(
                "get_active_distributions", error=traceback.format_exc()
            )

    def _cmd_get_locals(self, cmd):
        for frame in inspect.stack():
            if id(frame) == cmd.frame_id:
                return InlineResponse(
                    "get_locals", locals=self.export_variables(frame.f_locals)
                )

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
            completions = []
            error = "Could not import jedi"
        else:
            try:
                # with warnings.catch_warnings():
                interpreter = jedi.Interpreter(cmd.source, [__main__.__dict__])
                completions = self._export_completions(interpreter.completions())
            except Exception as e:
                completions = []
                error = "Autocomplete error: " + str(e)

        return InlineResponse(
            "shell_autocomplete",
            source=cmd.source,
            completions=completions,
            error=error,
        )

    def _cmd_editor_autocomplete(self, cmd):
        error = None
        try:
            import jedi

            self._debug(jedi.__file__, sys.path)
            with warnings.catch_warnings():
                script = jedi.Script(cmd.source, cmd.row, cmd.column, cmd.filename)
                completions = self._export_completions(script.completions())

        except ImportError:
            completions = []
            error = "Could not import jedi"
        except Exception as e:
            completions = []
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

    def _cmd_Reset(self, cmd):
        if len(cmd.args) == 0:
            # nothing to do, because Reset always happens in fresh process
            return ToplevelResponse(
                command_name="Reset",
                welcome_text="Python " + _get_python_version_string(),
                executable=sys.executable,
            )
        else:
            raise UserError("Command 'Reset' doesn't take arguments")

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

    def _cmd_get_object_info(self, cmd):
        if (
            isinstance(self._current_executor, NiceTracer)
            and self._current_executor.is_in_past()
        ):
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
                "type_id": id(type(value)),
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

    def _get_tkinter_default_root(self):
        # tkinter._default_root is not None,
        # when window has been created and mainloop isn't called or hasn't ended yet
        tkinter = sys.modules.get("tkinter")
        if tkinter is not None:
            return getattr(tkinter, "_default_root", None)
        else:
            return None

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
            info["entries"].append(
                (self.export_value(key), self.export_value(value[key]))
            )

    def _execute_file(self, cmd, executor_class):
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        # TODO: are they?

        if len(cmd.args) >= 1:
            sys.argv = cmd.args  # TODO: duplicate????????????????????
            filename = cmd.args[0]
            if os.path.isabs(filename):
                full_filename = filename
            else:
                full_filename = os.path.abspath(filename)

            with tokenize.open(full_filename) as fp:
                source = fp.read()

            result_attributes = self._execute_source(
                source, full_filename, "exec", executor_class, cmd
            )
            result_attributes["filename"] = full_filename
            return ToplevelResponse(command_name=cmd.name, **result_attributes)
        else:
            raise UserError("Command '%s' takes at least one argument" % cmd.name)

    def _execute_source(self, source, filename, execution_mode, executor_class, cmd):
        self._current_executor = executor_class(self, cmd)

        try:
            return self._current_executor.execute_source(
                source, filename, execution_mode
            )
        finally:
            self._current_executor = None

    def _install_fake_streams(self):
        self._original_stdin = sys.stdin
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr

        # yes, both out and err will be directed to out (but with different tags)
        # this allows client to see the order of interleaving writes to stdout/stderr
        sys.stdin = VM.FakeInputStream(self, sys.stdin)
        sys.stdout = VM.FakeOutputStream(self, sys.stdout, "stdout")
        sys.stderr = VM.FakeOutputStream(self, sys.stdout, "stderr")

        # fake it properly: replace also "backup" streams
        sys.__stdin__ = sys.stdin
        sys.__stdout__ = sys.stdout
        sys.__stderr__ = sys.stderr

    def _install_custom_import(self):
        self._original_import = builtins.__import__
        builtins.__import__ = self._custom_import

    def _restore_original_import(self):
        builtins.__import__ = self._original_import

    def _fetch_command(self):
        line = self._original_stdin.readline()
        if line == "":
            logger.info("Read stdin EOF")
            sys.exit()
        cmd = parse_message(line)
        return cmd

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = os.getcwd()

        if isinstance(msg, ToplevelResponse) and "globals" not in msg:
            msg["globals"] = self.export_globals()

        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()

    def export_value(self, value, max_repr_length=5000):
        self._heap[id(value)] = value
        rep = repr(value)
        if len(rep) > max_repr_length:
            rep = rep[:max_repr_length] + "…"

        return ValueInfo(id(value), rep)

    def export_variables(self, variables):
        result = {}
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
        logger.debug("VM: " + str(args))

    def _enter_io_function(self):
        self._io_level += 1

    def _exit_io_function(self):
        self._io_level -= 1

    def is_doing_io(self):
        return self._io_level > 0

    def _export_stack(self, newest_frame):
        result = []

        system_frame = newest_frame

        while system_frame is not None:
            module_name = system_frame.f_globals["__name__"]
            code_name = system_frame.f_code.co_name

            source, firstlineno, in_library = self._get_frame_source_info(system_frame)

            result.insert(
                0,
                FrameInfo(
                    # TODO: can this id be reused by a later frame?
                    # Need to store the refernce to avoid GC?
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
                    focus=TextRange(
                        system_frame.f_lineno, 0, system_frame.f_lineno + 1, 0
                    ),
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
        sys.last_type, sys.last_value, sys.last_traceback = (
            e_type,
            e_value,
            e_traceback,
        )

        processed_tb = traceback.extract_tb(e_traceback)

        tb = e_traceback
        while tb.tb_next is not None:
            tb = tb.tb_next
        last_frame = tb.tb_frame

        if e_type is SyntaxError:
            # Don't show ast frame
            while (
                last_frame.f_code.co_filename
                and last_frame.f_code.co_filename == ast.__file__
            ):
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

    class FakeStream:
        def __init__(self, vm, target_stream):
            self._vm = vm
            self._target_stream = target_stream
            self._processed_symbol_count = 0

        def isatty(self):
            return True

        def __getattr__(self, name):
            # TODO: is it safe to perform those other functions without notifying vm
            # via _enter_io_function?
            return getattr(self._target_stream, name)

    class FakeOutputStream(FakeStream):
        def __init__(self, vm, target_stream, stream_name):
            VM.FakeStream.__init__(self, vm, target_stream)
            self._stream_name = stream_name

        def write(self, data):
            try:
                self._vm._enter_io_function()
                if data != "":
                    self._vm.send_message(
                        BackendEvent(
                            "ProgramOutput", stream_name=self._stream_name, data=data
                        )
                    )
                    self._processed_symbol_count += len(data)
            finally:
                self._vm._exit_io_function()

        def writelines(self, lines):
            try:
                self._vm._enter_io_function()
                self.write("".join(lines))
            finally:
                self._vm._exit_io_function()

    class FakeInputStream(FakeStream):
        def _generic_read(self, method, limit=-1):
            try:
                self._vm._enter_io_function()
                self._vm.send_message(
                    BackendEvent("InputRequest", method=method, limit=limit)
                )

                while True:
                    cmd = self._vm._fetch_command()
                    if isinstance(cmd, InputSubmission):
                        self._processed_symbol_count += len(cmd.data)
                        return cmd.data
                    elif isinstance(cmd, InlineCommand):
                        self._vm.handle_command(cmd)
                    else:
                        raise RuntimeError(
                            "Wrong type of command when waiting for input"
                        )
            finally:
                self._vm._exit_io_function()

        def read(self, limit=-1):
            return self._generic_read("read", limit)

        def readline(self, limit=-1):
            return self._generic_read("readline", limit)

        def readlines(self, limit=-1):
            return self._generic_read("readlines", limit)


class Executor:
    def __init__(self, vm, original_cmd):
        self._vm = vm
        self._original_cmd = original_cmd
        self._main_module_path = None

    def execute_source(self, source, filename, mode):
        if isinstance(source, str):
            # TODO: simplify this or make sure encoding is correct
            source = source.encode("utf-8")

        if os.path.exists(filename):
            self._main_module_path = filename

        global_vars = __main__.__dict__

        try:
            if mode == "exec+eval":
                # Useful in shell to get last expression value in multi-statement block
                root = self._prepare_ast(source, filename, "exec")
                statements = compile(ast.Module(body=root.body[:-1]), filename, "exec")
                expression = compile(
                    ast.Expression(root.body[-1].value), filename, "eval"
                )
                return self._prepare_hooks_and_execute(
                    statements, expression, global_vars
                )
            else:
                root = self._prepare_ast(source, filename, mode)
                bytecode = compile(root, filename, mode)
                if mode == "eval":
                    return self._prepare_hooks_and_execute(None, bytecode, global_vars)
                elif mode == "exec":
                    return self._prepare_hooks_and_execute(bytecode, None, global_vars)
                else:
                    raise ValueError("Unknown mode")
        except SyntaxError:
            return {"user_exception": self._vm._prepare_user_exception()}
        except SystemExit:
            return {"SystemExit": True}
        except Exception:
            _report_internal_error()
            return {}

    def _prepare_hooks_and_execute(self, statements, expression, global_vars):
        try:
            sys.meta_path.insert(0, self)
            self._vm._install_custom_import()
            return self._execute_prepared_user_code(statements, expression, global_vars)
        finally:
            del sys.meta_path[0]
            self._vm._restore_original_import()

    def _execute_prepared_user_code(self, statements, expression, global_vars):
        try:
            if statements:
                exec(statements, global_vars)
            if expression:
                value = eval(expression, global_vars)
                if value is not None:
                    builtins._ = value
                return {"value_info": self._vm.export_value(value)}

            return {"context_info": "after normal execution"}
        except Exception:
            return {"user_exception": self._vm._prepare_user_exception()}

    def find_spec(self, fullname, path=None, target=None):
        """override in subclass for custom-loading user modules"""
        return None

    def _prepare_ast(self, source, filename, mode):
        return ast.parse(source, filename, mode)


class SimpleRunner(Executor):
    pass


class Tracer(Executor):
    def __init__(self, vm, original_cmd):
        super().__init__(vm, original_cmd)
        self._thonny_src_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._fresh_exception = None

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

    def _trace(self, frame, event, arg):
        raise NotImplementedError()

    def _frame_is_alive(self, frame_id):
        raise NotImplementedError()

    def _execute_prepared_user_code(self, statements, expression, global_vars):
        try:
            sys.settrace(self._trace)
            if hasattr(sys, "breakpointhook"):
                old_breakpointhook = sys.breakpointhook
                sys.breakpointhook = self._breakpointhook

            return super()._execute_prepared_user_code(
                statements, expression, global_vars
            )
        finally:
            sys.settrace(None)
            if hasattr(sys, "breakpointhook"):
                sys.breakpointhook = old_breakpointhook

    def _should_skip_frame(self, frame):
        # For some reason Pylint doesn't see inspect.CO_GENERATOR and such
        # pylint: disable=no-member
        code = frame.f_code

        return (
            code is None
            or code.co_filename is None
            or not self._is_interesting_module_file(code.co_filename)
            or code.co_flags & inspect.CO_GENERATOR  # @UndefinedVariable
            or sys.version_info >= (3, 5)
            and code.co_flags & inspect.CO_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3, 5)
            and code.co_flags & inspect.CO_ITERABLE_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3, 6)
            and code.co_flags & inspect.CO_ASYNC_GENERATOR  # @UndefinedVariable
            or "importlib._bootstrap" in code.co_filename
            or self._vm.is_doing_io()
        )

    def _is_interesting_module_file(self, path):
        # interesting files are files directly in current directory
        # or under the same directory as main module
        # or the ones with breakpoints
        return (
            path_startswith(path, os.getcwd())
            or self._main_module_path is not None
            and path_startswith(path, os.path.dirname(self._main_module_path))
            or path in self._current_command["breakpoints"]
        )

    def _is_interesting_exception(self, frame):
        # interested only in exceptions in command frame or its parent frames
        return id(frame) == self._current_command[
            "frame_id"
        ] or not self._frame_is_alive(self._current_command["frame_id"])

    def _fetch_next_debugger_command(self):
        while True:
            cmd = self._vm._fetch_command()
            if isinstance(cmd, InlineCommand):
                self._vm.handle_command(cmd)
            else:
                assert isinstance(cmd, DebuggerCommand)
                return cmd

    def _register_affected_frame(self, exception_obj, frame):
        if not hasattr(exception_obj, "_affected_frame_ids_"):
            exception_obj._affected_frame_ids_ = set()
        exception_obj._affected_frame_ids_.add(id(frame))

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
            }
        else:
            return {
                "id": id(exc[1]),
                "msg": str(exc[1]),
                "type_name": exc[0].__name__,
                "lines_with_frame_info": format_exception_with_frame_info(*exc),
                "affected_frame_ids": exc[1]._affected_frame_ids_,
            }

    def _get_breakpoints_with_cursor_position(self, cmd):
        if cmd["cursor_position"] is None:
            return cmd["breakpoints"]
        else:
            result = copy.copy(cmd["breakpoints"])
            path, line = cmd["cursor_position"]
            if path not in result:
                result[path] = set()
            result[path].add(line)
            return result

    def _breakpointhook(self, *args, **kw):
        pass


class FastTracer(Tracer):
    def __init__(self, vm, original_cmd):
        super().__init__(vm, original_cmd)

        self._alive_frame_ids = set()

    def _breakpointhook(self, *args, **kw):
        frame = inspect.currentframe()
        while self._should_skip_frame(frame):
            frame = frame.f_back
        self._report_current_state(frame)
        self._current_command = self._fetch_next_debugger_command()

    def _trace(self, frame, event, arg):

        # is this frame interesting at all?
        if event == "call" and self._should_skip_frame(frame):
            return None

        if event == "call":
            self._fresh_exception = None
            # can we skip this frame?
            if (
                self._current_command.name == "step_over"
                and not self._current_command.breakpoints
            ):
                return None
            else:
                self._alive_frame_ids.add(id(frame))

        elif event == "return":
            self._fresh_exception = None
            self._alive_frame_ids.remove(id(frame))

        elif event == "exception":
            self._fresh_exception = arg
            self._register_affected_frame(arg[1], frame)
            if self._is_interesting_exception(frame):
                # UI doesn't know about separate exception events
                self._report_current_state(frame)
                self._current_command = self._fetch_next_debugger_command()

        elif event == "line":
            self._fresh_exception = None

            handler = getattr(self, "_cmd_%s_completed" % self._current_command.name)
            if handler(frame, self._current_command):
                self._report_current_state(frame)
                self._current_command = self._fetch_next_debugger_command()

        else:
            self._fresh_exception = None

        return self._trace

    def _report_current_state(self, frame):
        msg = DebuggerResponse(
            stack=self._vm._export_stack(frame),
            in_present=True,
            io_symbol_count=None,
            exception_info=self._export_exception_info(),
            tracer_class="FastTracer",
        )

        self._vm.send_message(msg)

    def _cmd_step_into_completed(self, frame, cmd):
        return True

    def _cmd_step_over_completed(self, frame, cmd):
        frame_id = id(frame)
        return (
            frame_id == cmd.frame_id
            or cmd.frame_id not in self._alive_frame_ids
            or self._at_a_breakpoint(frame, cmd)
        )

    def _cmd_step_out_completed(self, frame, cmd):
        return cmd.frame_id not in self._alive_frame_ids or self._at_a_breakpoint(
            frame, cmd
        )

    def _cmd_resume_completed(self, frame, cmd):
        return self._at_a_breakpoint(frame, cmd)

    def _cmd_run_to_cursor_completed(self, frame, cmd):
        return self._at_a_breakpoint(
            frame, cmd, self._get_breakpoints_with_cursor_position(cmd)
        )

    def _at_a_breakpoint(self, frame, cmd, breakpoints=None):
        # TODO: try re-entering same line in loop
        if breakpoints is None:
            breakpoints = cmd.breakpoints

        filename = frame.f_code.co_filename
        return filename in breakpoints and frame.f_lineno in breakpoints[filename]

    def _should_skip_frame(self, frame):
        code = frame.f_code
        return super()._should_skip_frame(frame) or code.co_filename.startswith(
            self._thonny_src_dir
        )

    def _frame_is_alive(self, frame_id):
        return frame_id in self._alive_frame_ids


class NiceTracer(Tracer):
    def __init__(self, vm, original_cmd):
        super().__init__(vm, original_cmd)
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
        self._current_command = self._fetch_next_debugger_command()

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
        root = ast.parse(source, filename, mode)

        ast_utils.mark_text_ranges(root, source)
        self._tag_nodes(root)
        self._insert_expression_markers(root)
        self._insert_statement_markers(root)
        self._insert_for_target_markers(root)
        self._instrumented_files.add(filename)

        return root

    def _should_skip_frame(self, frame):
        code = frame.f_code
        return (
            code.co_name
            not in self.marker_function_names  # never skip marker functions
            and (
                super()._should_skip_frame(frame)
                or code.co_filename not in self._instrumented_files
                or path_startswith(code.co_filename, self._thonny_src_dir)
            )
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
        """
        1) Detects marker calls and responds to client queries in these spots
        2) Maintains a customized view of stack
        """
        # frame skipping test should be done only in new frames
        if event == "call" and self._should_skip_frame(frame):
            return None

        code_name = frame.f_code.co_name

        if event == "call":
            self._fresh_exception = (
                None
            )  # some code is running, therefore exception is not fresh anymore

            if code_name in self.marker_function_names:
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
                    self._handle_progress_event(
                        frame.f_back, event, marker_function_args, node
                    )
                self._try_interpret_as_again_event(
                    frame.f_back, event, marker_function_args, node
                )

            else:
                # Calls to proper functions.
                # Client doesn't care about these events,
                # it cares about "before_statement" events in the first statement of the body
                self._custom_stack.append(CustomStackFrame(frame, "call"))

        elif event == "exception":
            self._fresh_exception = arg
            self._register_affected_frame(arg[1], frame)

            # use the state prepared by previous event
            last_custom_frame = self._custom_stack[-1]
            assert last_custom_frame.system_frame == frame

            assert last_custom_frame.event.startswith("before_")
            pseudo_event = last_custom_frame.event.replace("before_", "after_").replace(
                "_again", ""
            )

            self._handle_progress_event(frame, pseudo_event, {}, last_custom_frame.node)

        elif event == "return":
            self._fresh_exception = None

            if code_name not in self.marker_function_names:
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
        focus = TextRange(
            node.lineno, node.col_offset, node.end_lineno, node.end_col_offset
        )

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
                    (focus, self._vm.export_value(args["value"]))
                )

        # Save the snapshot.
        # Check if we can share something with previous state
        if (
            prev_state is not None
            and id(prev_state_frame.system_frame) == id(frame)
            and prev_state["exception_value"] is self._get_current_exception()[1]
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
                tester = getattr(
                    self, "_cmd_" + self._current_command.name + "_completed"
                )
                cmd_complete = tester(frame, self._current_command)

                if cmd_complete:
                    state["in_client_log"] = True
                    self._report_state(self._current_state_index)
                    self._current_command = self._fetch_next_debugger_command()

            if self._current_command.name == "step_back":
                if self._current_state_index == 0:
                    # Already in first state. Remain in this loop
                    pass
                else:
                    assert self._current_state_index > 0
                    # Current event is no longer present in GUI "undo log"
                    self._saved_states[self._current_state_index][
                        "in_client_log"
                    ] = False
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
        for tframe in state["stack"]:
            system_frame = tframe.system_frame
            module_name = system_frame.f_globals["__name__"]
            code_name = system_frame.f_code.co_name

            source, firstlineno, in_library = self._vm._get_frame_source_info(
                system_frame
            )

            assert firstlineno is not None, "nofir " + str(system_frame)

            new_stack.append(
                FrameInfo(
                    id=id(system_frame),
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

        state["stack"] = new_stack
        state["tracer_class"] = "NiceTracer"

        self._vm.send_message(DebuggerResponse(**state))

    def _try_interpret_as_again_event(
        self, frame, original_event, original_args, original_node
    ):
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

        prev_state_frame = self._saved_states[self._current_state_index - 1]["stack"][
            -1
        ]

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

    def _cmd_run_to_cursor_completed(self, frame, cmd):
        return self._at_a_breakpoint(
            frame, cmd, self._get_breakpoints_with_cursor_position(cmd)
        )

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
                exported_globals_per_module[module_name] = self._vm.export_variables(
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
                    else self._vm.export_variables(system_frame.f_locals),
                    globals=export_globals(module_name, system_frame),
                    event=custom_frame.event,
                    focus=custom_frame.focus,
                    node_tags=custom_frame.node_tags,
                    current_evaluations=custom_frame.current_evaluations.copy(),
                    current_statement=custom_frame.current_statement,
                    current_root_expression=custom_frame.current_root_expression,
                )
            )

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

            # tag last children
            last_child = ast_utils.get_last_child(node)
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

            if isinstance(node, ast.Str):
                add_tag(node, "StringLiteral")
                add_tag(node, "skipexport")

            if hasattr(ast, "JoinedStr") and isinstance(node, ast.JoinedStr):
                # can't present children normally without
                # ast giving correct locations for them
                add_tag(node, "ignore_children")

            elif isinstance(node, ast.Num):
                add_tag(node, "NumberLiteral")
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

            elif isinstance(node, ast.SetComp):
                add_tag(node.elt, "SetComp.elt")

            elif isinstance(node, ast.DictComp):
                add_tag(node.key, "DictComp.key")
                add_tag(node.value, "DictComp.value")

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

            if isinstance(node, ast.comprehension):
                for expr in node.ifs:
                    add_tag(expr, "comprehension.if")

            if isinstance(node, (ast.Assign)):
                # value will be presented in assignment's before_statement_again
                add_tag(node.value, "skip_after_expression")

            if isinstance(
                node, (ast.Expr, ast.While, ast.For, ast.If, ast.Try, ast.With)
            ):
                add_tag(node, "skip_after_statement_again")

            # make sure every node has this field
            if not hasattr(node, "tags"):
                node.tags = set()

    def _should_instrument_as_expression(self, node):
        return (
            isinstance(node, _ast.expr)
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
            if isinstance(value, ast.AST):
                self._insert_statement_markers(value)
            elif isinstance(value, list):
                if len(value) > 0:
                    new_list = []
                    for node in value:
                        if self._should_instrument_as_statement(node):
                            # self._debug("EBFOMA", node)
                            # add before marker
                            new_list.append(
                                self._create_statement_marker(
                                    node, BEFORE_STATEMENT_MARKER
                                )
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
                                self._create_statement_marker(
                                    node, AFTER_STATEMENT_MARKER
                                )
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
                name_load.tags = {
                    "skip_before_expression",
                    "skip_after_expression",
                    "last_child",
                }
                name_load.lineno, name_load.col_offset = (
                    node.iter.lineno,
                    node.iter.col_offset,
                )
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
                ass.tags = {
                    "skip_before_statement"
                }  # before_statement_again will be shown

                name_load.parent_node = ass

                ass_before = self._create_statement_marker(ass, BEFORE_STATEMENT_MARKER)
                node.body.insert(0, ass_before)
                node.body.insert(1, ass)
                node.body.insert(
                    2, self._create_statement_marker(ass, AFTER_STATEMENT_MARKER)
                )

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
                            transformed_node = ast.NodeTransformer.generic_visit(
                                self, node
                            )

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

        return ast.Call(
            func=ast.Name(id=fun_name, ctx=ast.Load()), args=args, keywords=[]
        )

    def _export_node(self, node):
        node_id = id(node)
        self._nodes[node_id] = node
        return ast.Num(node_id)

    def _debug(self, *args):
        logger.debug("TRACER: " + str(args))

    def _execute_prepared_user_code(self, statements, expression, global_vars):
        try:
            return Tracer._execute_prepared_user_code(
                self, statements, expression, global_vars
            )
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


class FancySourceFileLoader(SourceFileLoader):
    """Used for loading and instrumenting user modules during fancy tracing"""

    def __init__(self, fullname, path, tracer):
        super().__init__(fullname, path)
        self._tracer = tracer

    def source_to_code(self, data, path, *, _optimize=-1):
        root = self._tracer._prepare_ast(data, path, "exec")
        return super().source_to_code(root, path)


def _get_frame_prefix(frame):
    return str(id(frame)) + " " + ">" * len(inspect.getouterframes(frame, 0)) + " "


def _get_python_version_string(add_word_size=False):
    result = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[3] != "final":
        result += "-" + sys.version_info[3]

    if add_word_size:
        result += " (" + ("64" if sys.maxsize > 2 ** 32 else "32") + " bit)"

    return result


def _fetch_frame_source_info(frame):
    if frame.f_code.co_filename is None or not os.path.exists(frame.f_code.co_filename):
        return None, None, True

    if frame.f_code.co_name == "<module>":
        # inspect.getsource and getsourcelines don't help here
        with tokenize.open(frame.f_code.co_filename) as fp:
            return fp.read(), 1, _is_library_file(frame.f_code.co_filename)
    else:
        try:
            return (
                inspect.getsource(frame),
                frame.f_code.co_firstlineno,
                _is_library_file(frame.f_code.co_filename),
            )
        except OSError:
            logger.exception("Problem getting source")
            return None, None, True


def format_exception_with_frame_info(
    e_type, e_value, e_traceback, shorten_filenames=False
):
    """Need to suppress thonny frames to avoid confusion"""

    _traceback_message = "Traceback (most recent call last):\n"

    _cause_message = getattr(
        traceback,
        "_cause_message",
        (
            "\nThe above exception was the direct cause "
            + "of the following exception:\n\n"
        ),
    )

    _context_message = getattr(
        traceback,
        "_context_message",
        (
            "\nDuring handling of the above exception, "
            + "another exception occurred:\n\n"
        ),
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
                yield from rec_format_exception_with_frame_info(
                    None, value.__cause__, None
                )
                yield (_cause_message, None, None, None)
            elif value.__context__ is not None and not value.__suppress_context__:
                yield from rec_format_exception_with_frame_info(
                    None, value.__context__, None
                )
                yield (_context_message, None, None, None)

        if tb is not None:
            yield (_traceback_message, None, None, None)
            have_seen_first_relevant_frame = False

            tb_temp = tb
            for entry in traceback.extract_tb(tb):
                assert tb_temp is not None  # actual tb doesn't end before extract_tb
                if (
                    "thonny/backend" not in entry.filename
                    and "thonny\\backend" not in entry.filename
                    and (
                        not entry.filename.endswith(os.sep + "ast.py")
                        or entry.name != "parse"
                        or etype is not SyntaxError
                    )
                    or have_seen_first_relevant_frame
                    or in_debug_mode()
                ):

                    have_seen_first_relevant_frame = True

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


def load_module_from_alternative_path(module_name, path, force=False):
    spec = PathFinder.find_spec(module_name, path)

    if spec is None and not force:
        return

    from importlib.util import module_from_spec

    module = module_from_spec(spec)
    sys.modules[module_name] = module
    if spec.loader is not None:
        spec.loader.exec_module(module)


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


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()


def get_vm():
    return _vm
