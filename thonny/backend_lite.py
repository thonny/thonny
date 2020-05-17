# -*- coding: utf-8 -*-

import builtins
import io
import os.path
import sys

import __main__  # @UnresolvedImport
import thonny
from thonny.common import (
    BackendEvent,
    InlineCommand,
    InlineResponse,
    InputSubmission,
    ToplevelCommand,
    ToplevelResponse,
    UserError,
    ValueInfo,
    parse_message,
    serialize_message,
    get_exe_dirs,
    EOFCommand,
    execute_system_command,
)
import traceback


_vm = None


_ffi_library_cache = {}


def _get_library_with_ffi(name, maxver, extra=()):
    """MicroPython Unix port may miss some required functions. This function can load them 
    from elsewhere.
    
    Inspired by:
        https://github.com/micropython/micropython-lib/blob/master/ffilib/ffilib.py
        https://github.com/micropython/micropython-lib/blob/master/os/os/__init__.py
    """
    if name in _ffi_library_cache:
        return _ffi_library_cache[name]

    import sys
    import ffi  # @UnresolvedImport

    def libs():
        if sys.platform == "linux":
            yield "%s.so" % name
            for i in range(maxver, -1, -1):
                yield "%s.so.%u" % (name, i)
        elif sys.platform == "darwin":
            for ext in ("dylib", "dll"):
                yield "%s.%s" % (name, ext)
        else:
            raise RuntimeError(sys.platform + " not supported")

        for n in extra:
            yield n

    err = None
    for n in libs():
        try:
            l = ffi.open(n)
            _ffi_library_cache[name] = l
            return l
        except OSError as e:
            err = e
    raise err


def _get_libc():
    return _get_library_with_ffi("libc", 6)


def _check_os_error(ret):
    # Return True is error was EINTR (which usually means that OS call
    # should be restarted).
    import errno

    if ret == -1:
        e = os.errno()
        if e == errno.EINTR:
            return True
        raise OSError(e)


try:
    from os import getcwd
except ImportError:
    _getcwd = _get_libc().func("s", "getcwd", "si")

    def getcwd():
        buf = bytearray(512)
        return _getcwd(buf, 512)


try:
    from os import chdir
except ImportError:
    _chdir = _get_libc().func("i", "chdir", "s")

    def chdir(dir_):
        r = _chdir(dir_)
        _check_os_error(r)


class VM:
    def __init__(self):
        global _vm
        _vm = self

        self._ini = None
        self._command_handlers = {}
        self._object_info_tweakers = []
        self._import_handlers = {}
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._current_executor = None

        # clean up path
        sys.path = [d for d in sys.path if d != ""]

        # start in shell mode
        sys.argv[:] = [""]  # empty "script name"
        sys.path.insert(0, "")  # current dir

        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if not key.startswith("__") or key in {"__file__", "__cached__"}:
                del __main__.__dict__[key]

        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None

    def mainloop(self):
        while True:
            try:
                cmd = self._fetch_command()
                if isinstance(cmd, InputSubmission):
                    raise AssertionError("InputSubmission not supported")
                elif isinstance(cmd, EOFCommand):
                    self.send_message(ToplevelResponse(SystemExit=True))
                    sys.exit()
                else:
                    self.handle_command(cmd)
            except KeyboardInterrupt:
                # Interrupt must always result in waiting_toplevel_command state
                # Don't show error messages, as the interrupted command may have been InlineCommand
                # (handlers of ToplevelCommands in normal cases catch the interrupt and provide
                # relevant message)
                self.send_message(ToplevelResponse())

    def handle_command(self, cmd):
        assert isinstance(cmd, (ToplevelCommand, InlineCommand))

        def create_error_response(**kw):
            if isinstance(cmd, ToplevelCommand):
                return ToplevelResponse(command_name=cmd.name, **kw)
            else:
                return InlineResponse(command_name=cmd.name, **kw)

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
                response = create_error_response(user_exception=self._prepare_user_exception())
            except Exception:
                _report_internal_error()
                response = create_error_response(context_info="other unhandled exception")

        if response is False:
            # Command doesn't want to send any response
            return

        if response is None and isinstance(cmd, ToplevelCommand):
            # create simple default response
            response = ToplevelResponse(command_name=cmd.name)

        self.send_message(response)

    def switch_env_to_script_mode(self, cmd):
        if "" in sys.path:
            sys.path.remove("")  # current directory

        filename = cmd.args[0]
        if os.path.isfile(filename):
            sys.path.insert(0, os.path.abspath(os.path.dirname(filename)))
            __main__.__dict__["__file__"] = filename

    def _cmd_get_environment_info(self, cmd):

        return ToplevelResponse(
            main_dir=self._main_dir,
            path=sys.path,
            usersitepackages=None,
            prefix=None,
            welcome_text="MicroPython " + _get_python_version_string(),
            executable=sys.executable,
            exe_dirs=[],
            in_venv=False,
            python_version=_get_python_version_string(),
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
                raise UserError(str(e))
        else:
            raise UserError("cd takes one parameter")

    def _cmd_Run(self, cmd):
        self.switch_env_to_script_mode(cmd)
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_run(self, cmd):
        return self._execute_file(cmd, SimpleRunner)

    def _cmd_execute_source(self, cmd):
        """Executes Python source entered into shell"""
        self._check_update_tty_mode(cmd)
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
        self._check_update_tty_mode(cmd)
        execute_system_command(cmd)

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
        warnings.warn("_cmd_get_globals is deprecated for CPython")
        try:
            return InlineResponse(
                "get_globals",
                module_name=cmd.module_name,
                globals=self.export_globals(cmd.module_name),
            )
        except Exception as e:
            return InlineResponse("get_globals", module_name=cmd.module_name, error=str(e))

    def _cmd_shell_autocomplete(self, cmd):
        # TODO:
        completions = []
        error = "Could not import jedi"

        return InlineResponse(
            "shell_autocomplete", source=cmd.source, completions=completions, error=error
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

    def _execute_file(self, cmd, executor_class):
        self._check_update_tty_mode(cmd)

        if len(cmd.args) >= 1:
            sys.argv = cmd.args
            filename = cmd.args[0]
            if os.path.isabs(filename):
                full_filename = filename
            else:
                full_filename = os.path.abspath(filename)

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

    def _print_exception(self, e):
        # MicroPython sys has this attribute
        sys.print_exception(e)  # @UndefinedVariable

    def _fetch_command(self):
        line = self._original_stdin.readline()
        if line == "":
            sys.exit()
        cmd = parse_message(line)
        return cmd

    def _getcwd(self):
        if hasattr(os, "getcwd"):
            return os.getcwd()
        else:
            # MicroPython Unix port may not have this method
            return

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = os.getcwd()

        if isinstance(msg, ToplevelResponse) and "globals" not in msg:
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
        for name in variables:
            if not name.startswith("__"):
                result[name] = self.export_value(variables[name], 100)

        return result

    def export_globals(self, module_name="__main__"):
        if module_name in sys.modules:
            return self.export_variables(sys.modules[module_name].__dict__)
        else:
            raise RuntimeError("Module '{0}' is not loaded".format(module_name))

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

        fr_tr = None
        try:
            fr_tr = self._explain_exception_with_friendly_traceback()
        except ImportError:
            print(
                "[Could not import friendly_traceback. You can install it with Tools => Manage packages]\n",
                file=sys.stderr,
            )
        except Exception as e:
            print("[Could not get friendly traceback. Problem: %s]\n" % e, file=sys.stderr)

        return {
            "type_name": e_type.__name__,
            "message": msg,
            "stack": self._export_stack(last_frame),
            "items": format_exception_with_frame_info(e_type, e_value, e_traceback),
            "filename": getattr(e_value, "filename", processed_tb[-1].filename),
            "lineno": getattr(e_value, "lineno", processed_tb[-1].lineno),
            "col_offset": getattr(e_value, "offset", None),
            "line": getattr(e_value, "text", processed_tb[-1].line),
            "friendly_traceback": fr_tr,
        }

    def _show_error(self, msg):
        self._send_output(msg + "\n", "stderr")


class Executor:
    def __init__(self, vm, original_cmd):
        self._vm = vm
        self._original_cmd = original_cmd
        self._main_module_path = None

    def execute_source(self, source, filename, mode, ast_postprocessors):
        if isinstance(source, str):
            # TODO: simplify this or make sure encoding is correct
            source = source.encode("utf-8")

        if os.path.exists(filename):
            self._main_module_path = filename

        global_vars = __main__.__dict__
        statements = expression = None

        try:
            if mode == "exec+eval":
                assert not ast_postprocessors
                # Useful in shell to get last expression value in multi-statement block
                root = self._prepare_ast(source, filename, "exec")
                # https://bugs.python.org/issue35894
                # https://github.com/pallets/werkzeug/pull/1552/files#diff-9e75ca133f8601f3b194e2877d36df0eR950
                module = ast.parse("")
                module.body = root.body[:-1]
                statements = compile(module, filename, "exec")
                expression = compile(ast.Expression(root.body[-1].value), filename, "eval")
            else:
                root = self._prepare_ast(source, filename, mode)
                if mode == "eval":
                    assert not ast_postprocessors
                    expression = compile(root, filename, mode)
                elif mode == "exec":
                    for func in ast_postprocessors:
                        func(root)
                    statements = compile(root, filename, mode)
                else:
                    raise ValueError("Unknown mode")

            return self._execute_prepared_user_code(statements, expression, global_vars)
        except SyntaxError:
            return {"user_exception": self._vm._prepare_user_exception()}
        except SystemExit:
            return {"SystemExit": True}
        except Exception:
            _report_internal_error()
            return {}


def _get_python_version_string(add_word_size=False):
    result = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[3] != "final":
        result += "-" + sys.version_info[3]

    if add_word_size:
        result += " (" + ("64" if sys.maxsize > 2 ** 32 else "32") + " bit)"

    return result


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
                    "thonny/backend" not in entry.filename
                    and "thonny\\backend" not in entry.filename
                    and (
                        not entry.filename.endswith(os.sep + "ast.py")
                        or entry.name != "parse"
                        or etype is not SyntaxError
                    )
                    or in_debug_mode()
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


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()


def get_vm():
    return _vm
