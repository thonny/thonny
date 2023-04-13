# Frontend plugin is in cpython_frontend.py
import ast
import builtins
import functools
import importlib.util
import inspect
import io
import os.path
import queue
import re
import site
import subprocess
import sys
import tokenize
import traceback
import types
import warnings
from typing import Dict, List, Optional, Tuple, Union

import __main__
import thonny
from thonny import report_time
from thonny.backend import MainBackend, logger
from thonny.common import (
    OBJECT_LINK_END,
    OBJECT_LINK_START,
    REPL_PSEUDO_FILENAME,
    STRING_PSEUDO_FILENAME,
    BackendEvent,
    CommandToBackend,
    DistInfo,
    EOFCommand,
    FrameInfo,
    ImmediateCommand,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    MessageFromBackend,
    TextRange,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    ValueInfo,
    execute_system_command,
    execute_with_frontend_sys_path,
    get_augmented_system_path,
    get_exe_dirs,
    get_python_version_string,
    get_single_dir_child_data,
    path_startswith,
    serialize_message,
    update_system_path,
)

_REPL_HELPER_NAME = "_thonny_repl_print"

_CONFIG_FILENAME = os.path.join(thonny.THONNY_USER_DIR, "backend_configuration.ini")


_backend = None


class MainCPythonBackend(MainBackend):
    def __init__(self, target_cwd, options):
        report_time("Before MainBackend")
        MainBackend.__init__(self)
        report_time("After MainBackend")

        global _backend
        _backend = self

        self._ini = None
        self._options = options
        self._object_info_tweakers = []
        self._warned_shadow_casters = set()
        self._import_handlers = {}
        self._input_queue = queue.Queue()
        self._source_preprocessors = []
        self._ast_postprocessors = []
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._heap = {}  # WeakValueDictionary would be better, but can't store reference to None
        self._source_info_by_frame = {}
        self._init_help()
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
        __main__.__package__ = None
        __main__.__spec__ = None

        logger.info("Loading plugins")
        report_time("Before loading plugins")
        execute_with_frontend_sys_path(self._load_plugins)
        report_time("After loading plugins")
        if self._options.get("run.warn_module_shadowing", False):
            sys.addaudithook(self.import_audit_hook)

        # preceding code was run in an empty directory, now switch to provided
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
        assert "" not in sys.path  # for avoiding
        sys.path.insert(0, "")
        sys.argv[:] = [""]  # empty "script name"
        self._check_warn_avoided_sys_path_conflicts()

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

    def import_audit_hook(self, event: str, args):
        if event == "import":
            logger.debug("detected Import event with args %r", args)
            module_name = args[0]
            self._check_warn_sys_path_conflict(module_name.split(".")[0])

    def _check_warn_avoided_sys_path_conflicts(self):
        if self._options.get("run.warn_module_shadowing", False):
            return

        for name in sys.modules.keys():
            if name != "__main__":
                self._check_warn_sys_path_conflict(name.split(".")[0])

    def _check_warn_sys_path_conflict(self, root_module_name: str):
        user_dir = sys.path[0]
        if user_dir == "":
            user_dir = os.getcwd()

        # rough test to see if it's worth invoking the finder
        for ext in ["", ".py", ".pyw"]:
            pot_path = os.path.join(user_dir, root_module_name + ext)
            if os.path.exists(pot_path):
                logger.debug("Found import candidate: %r", pot_path)
                break
        else:
            return

        # It looks like a module is about to be imported from the script dir or current dir.
        # Is it shadowing a library module?

        current_spec = importlib.util.find_spec(root_module_name)

        first_entry = sys.path[0]
        del sys.path[0]
        try:
            shadowed_spec = importlib.util.find_spec(root_module_name)
        finally:
            sys.path.insert(0, first_entry)

        if shadowed_spec is None:
            logger.debug("No shadowed spec")
            return

        if shadowed_spec.origin == current_spec.origin:
            logger.debug("Equal current and shadowed spec")
            return

        logger.debug("%r shadows %r", current_spec.origin, shadowed_spec.origin)

        if current_spec.origin in self._warned_shadow_casters:
            return

        if root_module_name in sys.modules:
            # i.e. the method is called for post-import warning
            verb = "can shadow"
        else:
            verb = "is shadowing"

        self._send_output(
            # using backticks, because Shell would present file path in quotes as frame link
            f"WARNING: Your `{current_spec.origin}` {verb} the library module '{root_module_name}'. Consider renaming or moving it!\n",
            "stderr",
        )

        self._warned_shadow_casters.add(current_spec.origin)

    def _read_incoming_msg_line(self) -> str:
        return self._original_stdin.readline()

    def _handle_user_input(self, msg: InputSubmission) -> None:
        self._input_queue.put(msg)

    def _handle_eof_command(self, msg: EOFCommand) -> None:
        sys.exit(0)

    def _handle_normal_command(self, cmd: CommandToBackend) -> None:
        if cmd.name == "process_gui_events":
            # Don't want logging for this cmd
            response = self._prepare_command_response(self._process_gui_events(), cmd)
            self.send_message(response)
            return

        logger.debug("Handling normal command %r in cpython_backend", cmd.name)

        if isinstance(cmd, ToplevelCommand):
            self._source_info_by_frame = {}
            self._input_queue = queue.Queue()

        super()._handle_normal_command(cmd)

    def _prepare_command_response(
        self, response: Union[MessageFromBackend, Dict, None], command: CommandToBackend
    ) -> MessageFromBackend:
        result = super()._prepare_command_response(response, command)
        if isinstance(result, ToplevelResponse):
            result["gui_is_active"] = self._get_tcl() is not None or self._get_qt_app() is not None

        return result

    def _handle_immediate_command(self, cmd: ImmediateCommand) -> None:
        """
        Following is an idea, but it didn't work properly. Also, threaded reading
        was reverted for CPython https://github.com/thonny/thonny/issues/1363.
        Therefore signals are used for interrupting CPython programs.

        if cmd.name == "interrupt":
            with self._interrupt_lock:
                interrupt_local_process()
        """

        raise NotImplementedError()

    def _check_for_connection_error(self) -> None:
        pass

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
            abs_filename = os.path.abspath(filename)
            sys.path.insert(0, os.path.dirname(abs_filename))
            __main__.__dict__["__file__"] = abs_filename

        self._check_warn_avoided_sys_path_conflicts()

    def _custom_import(self, *args, **kw):
        module = self._original_import(*args, **kw)

        if not hasattr(module, "__name__"):
            return module

        # module specific handlers
        for handler in self._import_handlers.get(module.__name__, []):
            try:
                handler(module)
            except Exception:
                msg = f"Could not apply import handler {handler}"
                logger.exception(msg)
                self._report_internal_warning(msg)

        # general handlers
        for handler in self._import_handlers.get("*", []):
            try:
                handler(module)
            except Exception:
                msg = f"Could not apply import handler {handler}"
                logger.exception(msg)
                self._report_internal_warning(msg)

        return module

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
        import pkgutil

        for _, module_name, _ in sorted(pkgutil.iter_modules(path, prefix), key=lambda x: x[1]):
            try:
                m = importlib.import_module(module_name)
                if hasattr(m, load_function_name):
                    logger.info("Loading plugin %r", module_name)
                    f = getattr(m, load_function_name)
                    sig = inspect.signature(f)
                    if len(sig.parameters) == 0:
                        f()
                    else:
                        f(self)
            except Exception as e:
                msg = f"Failed loading plugin {module_name}"
                logger.exception(msg)
                self._report_internal_warning(msg)

    def _cmd_get_environment_info(self, cmd):
        return ToplevelResponse(
            main_dir=self._main_dir,
            sys_path=sys.path,
            usersitepackages=site.getusersitepackages() if site.ENABLE_USER_SITE else None,
            prefix=sys.prefix,
            welcome_text=f"Python {get_python_version_string()} ({sys.executable})",
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
        report_time("Before Run")
        self.switch_env_to_script_mode(cmd)
        try:
            return self._execute_file(cmd, SimpleRunner)
        finally:
            report_time("After Run")

    def _cmd_run(self, cmd):
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_FastDebug(self, cmd):
        self.switch_env_to_script_mode(cmd)
        from thonny.plugins.cpython_backend.cp_tracers import FastTracer

        return self._execute_file(cmd, FastTracer)

    def _cmd_Debug(self, cmd):
        self.switch_env_to_script_mode(cmd)
        report_time("Before importing NiceTracer")
        from thonny.plugins.cpython_backend.cp_tracers import NiceTracer

        report_time("After importing NiceTracer")

        return self._execute_file(cmd, NiceTracer)

    def _cmd_debug(self, cmd):
        from thonny.plugins.cpython_backend.cp_tracers import NiceTracer

        return self._execute_file(cmd, NiceTracer)

    def _cmd_execute_source(self, cmd):
        """Executes Python source entered into shell"""
        self._check_update_tty_mode(cmd)
        filename = REPL_PSEUDO_FILENAME
        source = cmd.source.strip()

        try:
            root = ast.parse(source, filename=filename, mode="exec")
        except SyntaxError as e:
            error = "".join(traceback.format_exception_only(type(e), e))
            sys.stderr.write(error)
            return {}

        assert isinstance(root, ast.Module)

        if getattr(cmd, "debug_mode", False):
            from thonny.plugins.cpython_backend.cp_tracers import NiceTracer

            executor_class = NiceTracer
        else:
            executor_class = SimpleRunner

        return self._execute_source(
            source,
            filename,
            "repl",
            executor_class,
            cmd,
        )

    def _cmd_execute_system_command(self, cmd):
        self._check_update_tty_mode(cmd)
        returncode = execute_system_command(cmd, disconnect_stdin=True)
        return {"returncode": returncode}

    def _process_gui_events(self):
        # advance the event loop
        try:
            # First try Tkinter.
            # Need to update even when tkinter._default_root is None
            # because otherwise destroyed window will stay up in macOS.

            # When switching between closed user Tk window and another window,
            # the closed window may reappear in IDLE and CLI REPL
            tcl = self._get_tcl()
            if tcl is not None:
                # http://bugs.python.org/issue989712
                # http://bugs.python.org/file6090/run.py.diff
                # https://bugs.python.org/review/989712/diff/4528/Lib/idlelib/run.py
                tcl.eval("update")
                return {}
            else:
                # Try Qt only when Tkinter is not used
                app = self._get_qt_app()
                if app is not None:
                    app.processEvents()
                    return {}

        except Exception:
            pass

        return {"gui_is_active": False}

    def _cmd_get_globals(self, cmd):
        # warnings.warn("_cmd_get_globals is deprecated for CPython")
        return dict(
            module_name=cmd.module_name,
            globals=self.export_globals(cmd.module_name),
        )

    def _cmd_get_frame_info(self, cmd):
        atts = {}
        # TODO: make it work also in past states
        frame, location = self._lookup_frame_by_id(cmd["frame_id"])
        if frame is None:
            atts["error"] = "Frame not found"
        else:
            atts["code_name"] = frame.f_code.co_name
            atts["module_name"] = frame.f_globals.get("__name__", None)
            atts["locals"] = (
                None if frame.f_locals is frame.f_globals else self.export_variables(frame.f_locals)
            )
            atts["globals"] = self.export_variables(frame.f_globals)
            atts["freevars"] = frame.f_code.co_freevars
            atts["location"] = location

        return dict(frame_id=cmd.frame_id, **atts)

    def _cmd_get_active_distributions(self, cmd):
        return dict(
            distributions=self._get_distributions_info(),
        )

    def _cmd_install_distributions(self, cmd):
        returncode, new_state = self._perform_pip_operation_and_list(["install"] + cmd.args)
        return {"new_state": new_state, "returncode": returncode}

    def _cmd_uninstall_distributions(self, cmd):
        returncode, new_state = self._perform_pip_operation_and_list(["uninstall", "-y"] + cmd.args)
        return {"new_state": new_state, "returncode": returncode}

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

    def _cmd_get_object_info(self, cmd):
        if self._current_executor and self._current_executor.is_in_past():
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

        return dict(id=cmd.object_id, info=info)

    def _cmd_mkdir(self, cmd):
        os.mkdir(cmd.path)

    def _cmd_delete(self, cmd):
        for path in cmd.paths:
            # TODO: add incremental feedback for each path
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    import shutil

                    shutil.rmtree(path)
            except Exception as e:
                print("Could not delete %s: %s" % (path, str(e)), file=sys.stderr)

    def _perform_pip_operation_and_list(
        self, cmd_line: List[str]
    ) -> Tuple[int, Dict[str, DistInfo]]:
        extra_switches = ["--disable-pip-version-check"]
        proxy = os.environ.get("https_proxy", os.environ.get("http_proxy", None))
        if proxy:
            extra_switches.append("--proxy=" + proxy)

        returncode = subprocess.call([sys.executable, "-m", "pip"] + extra_switches + cmd_line)
        return returncode, self._get_distributions_info()

    def _get_distributions_info(self) -> Dict[str, DistInfo]:
        # Avoiding pip, because pip is slow.
        # If it is called after first installation to user site packages
        # this dir is not yet in sys.path
        # This would be required also when using Python 3.8 and importlib.metadata.distributions()
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

        # TODO: consider using importlib.metadata.distributions()
        pkg_resources._initialize_master_working_set()
        return {
            dist.key: DistInfo(
                key=dist.key,
                project_name=dist.project_name,
                location=dist.location,
                version=dist.version,
            )
            for dist in pkg_resources.working_set  # pylint: disable=not-an-iterable
        }

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

    def _get_tcl(self):
        if self._tcl is not None:
            return self._tcl

        tkinter = sys.modules.get("tkinter")
        if tkinter is None:
            return None

        if self._tcl is None:
            try:
                self._tcl = tkinter.Tcl()
            except Exception as e:
                logger.error("Could not get Tcl", exc_info=e)
                self._tcl = None
                return None

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
        report_time("Starting _execute_file")
        self._check_update_tty_mode(cmd)

        if len(cmd.args) >= 1:
            sys.argv = cmd.args
            filename = cmd.args[0]
            if filename == "-c":
                tweaked_filename = STRING_PSEUDO_FILENAME
            elif os.path.isabs(filename):
                tweaked_filename = filename
            else:
                tweaked_filename = os.path.abspath(filename)

            if tweaked_filename == STRING_PSEUDO_FILENAME:
                source = cmd.source
            else:
                with tokenize.open(tweaked_filename) as fp:
                    source = fp.read()

            for preproc in self._source_preprocessors:
                source = preproc(source, cmd)
            report_time("Done preprocessing")
            result_attributes = self._execute_source(
                source, tweaked_filename, "exec", executor_class, cmd, self._ast_postprocessors
            )
            result_attributes["filename"] = tweaked_filename
            return ToplevelResponse(command_name=cmd.name, **result_attributes)
        else:
            raise UserError("Command '%s' takes at least one argument" % cmd.name)

    def _execute_source(
        self, source, filename, execution_mode, executor_class, cmd, ast_postprocessors=[]
    ):
        self._current_executor = executor_class(self, cmd)
        report_time("Done creating executor")
        try:
            return self._current_executor.execute_source(
                source, filename, execution_mode, ast_postprocessors
            )
        except SystemExit as e:
            sys.exit(e.code)
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
                print(OBJECT_LINK_START % id(obj), obj_repr, OBJECT_LINK_END, sep="")
                self._heap[id(obj)] = obj
                builtins._ = obj

        setattr(builtins, _REPL_HELPER_NAME, _handle_repl_value)

    def _init_help(self):
        import pydoc

        pydoc.pager = pydoc.plainpager
        site.sethelper()  # otherwise help function is not available

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
        report_time(f"Sending message {msg.event_type}")
        sys.stdout.flush()

        if isinstance(msg, ToplevelResponse):
            if "cwd" not in msg:
                msg["cwd"] = os.getcwd()
            if "globals" not in msg:
                msg["globals"] = self.export_globals()

        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()
        if isinstance(msg, ToplevelResponse):
            self._check_load_jedi()

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
            module_name = system_frame.f_globals.get("__name__", None)
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

        if getattr(sys, "last_traceback", None):
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

        if isinstance(e_value, SyntaxError):
            # Don't show ast frame
            while last_frame.f_code.co_filename and last_frame.f_code.co_filename == ast.__file__:
                logger.info("COF %r vs %r", last_frame.f_code.co_filename, ast.__file__)
                last_frame = last_frame.f_back

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

        return len(data)

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
            return {}
        except (Exception, KeyboardInterrupt):
            return {"user_exception": self._backend._prepare_user_exception()}

    return wrapper


class Executor:
    def __init__(self, backend: MainCPythonBackend, original_cmd):
        self._backend = backend
        self._original_cmd = original_cmd
        self._main_module_path = None

    def is_in_past(self):
        return False

    def execute_source(self, source: str, filename, mode, ast_postprocessors):
        assert isinstance(source, str)

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
                report_time("Before preparing ast in executor")
                root = self._prepare_ast(source, filename, mode)
                for func in ast_postprocessors:
                    func(root)
                statements = compile(root, filename, mode)
                report_time("After compiling ast in executor")
            else:
                raise ValueError("Unknown mode", mode)

            return self._execute_prepared_user_code(statements, global_vars)
        except SyntaxError:
            return {"user_exception": self._backend._prepare_user_exception()}

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
                if (
                    "cpython_backend" not in entry.filename
                    and "thonny/backend" not in entry.filename.replace("\\", "/")
                    and (
                        not entry.filename.endswith(os.sep + "ast.py")
                        or entry.name != "parse"
                        or not isinstance(e_value, SyntaxError)
                    )
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
