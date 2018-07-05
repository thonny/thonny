# -*- coding: utf-8 -*-

import sys
import os.path
import inspect
import ast
import _ast
import io
import traceback
import types
import logging
import pydoc
import builtins
import site

import __main__  # @UnresolvedImport

from thonny import ast_utils
from thonny.common import TextRange, parse_message, serialize_message, UserError, \
    DebuggerCommand, ToplevelCommand, FrameInfo, InlineCommand, InputSubmission,\
    ToplevelResponse, InlineResponse, SimpleDebuggerResponse,\
    FancyDebuggerResponse, BackendEvent

import signal
import warnings
import pkgutil
import importlib
import tokenize
import subprocess
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

EXCEPTION_TRACEBACK_LIMIT = 100

logger = logging.getLogger()
info = logger.info

class VM:
    def __init__(self):
        self._command_handlers = {}
        self._value_tweakers = []
        self._object_info_tweakers = []
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._heap = {} # WeakValueDictionary would be better, but can't store reference to None
        site.sethelper() # otherwise help function is not available
        pydoc.pager = pydoc.plainpager # otherwise help command plays tricks
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
            sys.argv[:] = sys.argv[1:] # shift argv[1] to position of script name
            sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0]))) # add program's dir
            __main__.__dict__["__file__"] = sys.argv[0]
            # TODO: inspect.getdoc

        # shell mode
        else:
            special_names_to_remove = {"__file__", "__cached__"}
            sys.argv[:] = [""] # empty "script name"
            sys.path.insert(0, "")   # current dir

        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if not key.startswith("__") or key in special_names_to_remove:
                del __main__.__dict__[key]

        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None

        self._load_shared_modules(init_msg["frontend_sys_path"])
        self._load_plugins()

        self.send_message(ToplevelResponse(
                          main_dir=self._main_dir,
                          original_argv=original_argv,
                          original_path=original_path,
                          argv=sys.argv,
                          path=sys.path,
                          prefix=sys.prefix,
                          welcome_text="Python " + _get_python_version_string(),
                          executable=sys.executable,
                          in_venv=hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix,
                          python_version=_get_python_version_string(),
                          loaded_modules=list(sys.modules.keys()),
                          cwd=os.getcwd()))

        self._install_signal_handler()

    def mainloop(self):
        try:
            while True:
                try:
                    cmd = self._fetch_command()
                    self.handle_command(cmd)
                except KeyboardInterrupt:
                    logger.exception("Interrupt in mainloop")
                    # Interrupt must always result in waiting_toplevel_command state
                    # Don't show error messages, as the interrupted command may have been InlineCommand
                    # (handlers of ToplevelCommands in normal cases catch the interrupt and provide
                    # relevant message)  
                    self.send_message(ToplevelResponse())
        except:
            logger.exception("Crash in mainloop")
            traceback.print_exc()

    def add_command(self, command_name, handler):
        """Handler should be 1-argument function taking command object.
        
        Handler may return None (in this case no response is sent to frontend)
        or a BackendResponse
        """
        self._command_handlers[command_name] = handler

    def add_value_tweaker(self, tweaker):
        """Tweaker should be 2-argument function taking value and export record"""
        self._value_tweakers.append(tweaker)

    def add_object_info_tweaker(self, tweaker):
        """Tweaker should be 2-argument function taking value and export record"""
        self._object_info_tweakers.append(tweaker)

    def add_module_patcher(self, module_name, patcher):
        if module_name not in self._module_patchers:
            self._module_patchers[module_name] = []
        #self.

    def get_main_module(self):
        return __main__

    def handle_command(self, cmd):
        assert isinstance(cmd, ToplevelCommand) or isinstance(cmd, InlineCommand)
        
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
                e_type, e_value, e_traceback = sys.exc_info()
                self._print_user_exception(e_type, e_value, e_traceback)
                response = create_error_response()
            except:
                error="Internal backend error: {0}".format(traceback.format_exc(EXCEPTION_TRACEBACK_LIMIT))
                response = create_error_response(context_info="other unhandled exception",
                                               error=error)

        if response is False:
            # Command doesn't want to send any response
            return

        if response is None and isinstance(cmd, ToplevelCommand):
            # create simple default response
            response = ToplevelResponse(command_name=cmd.name)

        # TODO: add these in response creation time in a helper function
        if isinstance(response, ToplevelResponse):
            response["loaded_modules"] = list(sys.modules.keys())
            response["gui_is_active"] = (
                self._get_tkinter_default_root() is not None
                or self._get_qt_app() is not None
            )
            
        self.send_message(response)

    def _load_shared_modules(self, frontend_sys_path):
        for name in ["parso", "jedi", "thonnycontrib"]:
            load_module_from_alternative_path(name, frontend_sys_path)

    def _load_plugins(self):
        # built-in plugins 
        import thonny.plugins.backend
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
        load_function_name="load_plugin"
        for _, module_name, _ in pkgutil.iter_modules(path, prefix):
            try:
                m = importlib.import_module(module_name)
                if hasattr(m, load_function_name):
                    f = getattr(m, load_function_name)
                    sig = inspect.signature(f)
                    if len(sig.parameters) == 0:
                        f()
                    else:
                        f(self)
            except:
                logging.exception("Failed loading plugin '" + module_name + "'")

    def _install_signal_handler(self):
        def signal_handler(signal, frame):
            raise KeyboardInterrupt("Execution interrupted")

        if os.name == 'nt':
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

    def _cmd_LineDebug(self, cmd):
        return self._execute_file(cmd, SimpleTracer)

    def _cmd_Debug(self, cmd):
        return self._execute_file(cmd, FancyTracer)

    def _cmd_debug(self, cmd):
        return self._execute_file(cmd, FancyTracer)

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

        result_attributes = self._execute_source(source, filename, mode,
            FancyTracer if getattr(cmd, "debug_mode", False) else SimpleRunner,
            global_vars=getattr(cmd, "global_vars", None))

        result_attributes["num_stripped_question_marks"] = num_stripped_question_marks

        return ToplevelResponse(command_name="execute_source", **result_attributes)

    def _cmd_execute_system_command(self, cmd):
        # TODO: how to publish stdout as it arrives?
        env = dict(os.environ).copy()
        env["PYTHONIOENCODING"] = "ascii"
        proc = subprocess.Popen(cmd.argv,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         shell=True,
                         env=env,
                         universal_newlines=True,
                         encoding="ascii",
                         errors='backslashreplace')
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

        except:
            pass

        return False


    def _cmd_get_globals(self, cmd):
        try:
            if self._current_executor is None:
                result = self.export_latest_globals(cmd.module_name)
            else:
                result = self._current_executor.export_globals(cmd.module_name)

            return InlineResponse("get_globals", module_name=cmd.module_name, globals=result)
        except Exception as e:
            return InlineResponse("get_globals", module_name=cmd.module_name, error=str(e))


    def _cmd_get_locals(self, cmd):
        for frame in inspect.stack():
            if id(frame) == cmd.frame_id:
                return InlineResponse("get_locals", locals=self.export_variables(frame.f_locals))
        else:
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
                #with warnings.catch_warnings():
                interpreter = jedi.Interpreter(cmd.source, [__main__.__dict__])
                completions = self._export_completions(interpreter.completions())
            except Exception as e:
                completions = []
                error = "Autocomplete error: " + str(e)
            except:
                completions = []
                error = "Autocomplete error"

        return InlineResponse("shell_autocomplete",
            source=cmd.source,
            completions=completions,
            error=error
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
        except:
            completions = []
            error = "Autocomplete error"

        return InlineResponse("editor_autocomplete",
                          source=cmd.source,
                          row=cmd.row,
                          column=cmd.column,
                          filename=cmd.filename,
                          completions=completions,
                          error=error)

    def _cmd_Reset(self, cmd):
        if len(cmd.args) == 0:
            # nothing to do, because Reset always happens in fresh process
            return ToplevelResponse(command_name="Reset",
                                    welcome_text="Python " + _get_python_version_string(),
                                    executable=sys.executable)
        else:
            raise UserError("Command 'Reset' doesn't take arguments")

    def export_latest_globals(self, module_name):
        if module_name in sys.modules:
            return self.export_variables(sys.modules[module_name].__dict__)
        else:
            raise RuntimeError("Module '{0}' is not loaded".format(module_name))

    def _export_completions(self, jedi_completions):
        result = []
        for c in jedi_completions:
            if not c.name.startswith("__"):
                record = {"name":c.name, "complete":c.complete,
                          "type":c.type, "description":c.description}
                try:
                    """ TODO: 
                    if c.type in ["class", "module", "function"]:
                        if c.type == "function":
                            record["docstring"] = c.docstring()
                        else:
                            record["docstring"] = c.description + "\n" + c.docstring()
                    """
                except:
                    pass
                result.append(record)
        return result


    def _cmd_get_object_info(self, cmd):
        if (isinstance(self._current_executor, FancyTracer)
            and self._current_executor.is_in_past()):
            info = {'id' : cmd.object_id,
                    "error": "past info not available"}

        elif cmd.object_id in self._heap:
            value = self._heap[cmd.object_id]
            attributes = {}
            if cmd.include_attributes:
                for name in dir(value):
                    if not name.startswith("__") or cmd.all_attributes:
                        #attributes[name] = inspect.getattr_static(value, name)
                        try:
                            attributes[name] = getattr(value, name)
                        except:
                            pass

            self._heap[id(type(value))] = type(value)
            info = {'id' : cmd.object_id,
                    'repr' : repr(value),
                    'type' : str(type(value)),
                    'full_type_name' : str(type(value)).replace("<class '", "").replace("'>", "").strip(),
                    'type_id' : id(type(value)),
                    'attributes': self.export_variables(attributes)}

            if isinstance(value, io.TextIOWrapper):
                self._add_file_handler_info(value, info)
            elif (type(value) in (types.BuiltinFunctionType, types.BuiltinMethodType,
                                 types.FunctionType, types.LambdaType, types.MethodType)):
                self._add_function_info(value, info)
            elif (isinstance(value, list)
                  or isinstance(value, tuple)
                  or isinstance(value, set)):
                self._add_elements_info(value, info)
            elif (isinstance(value, dict)):
                self._add_entries_info(value, info)

            for tweaker in self._object_info_tweakers:
                try:
                    tweaker(value, info, cmd)
                except:
                    logger.exception("Failed object info tweaker: " + str(tweaker))

        else:
            info = {'id' : cmd.object_id,
                    "error": "object info not available"}

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
            except:
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
            pass

    def _add_function_info(self, value, info):
        try:
            info["source"] = inspect.getsource(value)
        except:
            pass

    def _add_elements_info(self, value, info):
        info["elements"] = []
        for element in value:
            info["elements"].append(self.export_value(element))

    def _add_entries_info(self, value, info):
        info["entries"] = []
        for key in value:
            info["entries"].append((self.export_value(key),
                                     self.export_value(value[key])))

    def _execute_file(self, cmd, executor_class):
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        # TODO: are they?

        if len(cmd.args) >= 1:
            sys.argv = cmd.args # TODO: duplicate????????????????????
            filename = cmd.args[0]
            if os.path.isabs(filename):
                full_filename = filename
            else:
                full_filename = os.path.abspath(filename)

            with tokenize.open(full_filename) as fp:
                source = fp.read()

            result_attributes = self._execute_source(source, full_filename, "exec", executor_class,
                                                     cmd=cmd)
            return ToplevelResponse(command_name=cmd.name, **result_attributes)
        else:
            raise UserError("Command '%s' takes at least one argument", cmd.name)

    def _execute_source(self, source, filename, execution_mode, executor_class, 
                        global_vars=None, cmd=None):
        self._current_executor = executor_class(self)

        try:
            return self._current_executor.execute_source(source,
                                                         filename,
                                                         execution_mode,
                                                         global_vars,
                                                         cmd)
        finally:
            self._current_executor = None

    def _print_user_exception(self, e_type, e_value, e_traceback):
        lines = traceback.format_exception(e_type, e_value, e_traceback)

        for line in lines:
            # skip lines denoting thonny execution frame
            if not in_debug_mode() and (
                "thonny/backend" in line
                or "thonny\\backend" in line
                or "remove this line from stacktrace" in line):
                continue
            else:
                sys.stderr.write(line)

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
            
        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()

    def export_value(self, value, skip_None=False):
        if value is None and skip_None:
            return None

        self._heap[id(value)] = value
        try:
            type_name = value.__class__.__name__
        except:
            type_name = type(value).__name__

        result = {'id' : id(value),
                  'repr' : repr(value),
                  'type_name'  : type_name}

        for tweaker in self._value_tweakers:
            tweaker(value, result)

        return result

    def export_variables(self, variables):
        result = {}
        for name in variables:
            if not name.startswith("_thonny_hidden_"):
                result[name] = self.export_value(variables[name])

        return result

    def _debug(self, *args):
        print("VM:", *args, file=self._original_stderr)


    def _enter_io_function(self):
        self._io_level += 1

    def _exit_io_function(self):
        self._io_level -= 1

    def is_doing_io(self):
        return self._io_level > 0


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
                    self._vm.send_message(BackendEvent("ProgramOutput", stream_name=self._stream_name, data=data))
                    self._processed_symbol_count += len(data)
            finally:
                self._vm._exit_io_function()

        def writelines(self, lines):
            try:
                self._vm._enter_io_function()
                self.write(''.join(lines))
            finally:
                self._vm._exit_io_function()

    class FakeInputStream(FakeStream):

        def _generic_read(self, method, limit=-1):
            try:
                self._vm._enter_io_function()
                self._vm.send_message(BackendEvent("InputRequest", method=method, limit=limit))

                while True:
                    cmd = self._vm._fetch_command()
                    if isinstance(cmd, InputSubmission):
                        self._processed_symbol_count += len(cmd.data)
                        return cmd.data
                    elif isinstance(cmd, InlineCommand):
                        self._vm.handle_command(cmd)
                    else:
                        raise RuntimeError("Wrong type of command when waiting for input")
            finally:
                self._vm._exit_io_function()

        def read(self, limit=-1):
            return self._generic_read("read", limit)

        def readline(self, limit=-1):
            return self._generic_read("readline", limit)

        def readlines(self, limit=-1):
            return self._generic_read("readlines", limit)


class Executor:
    def __init__(self, vm):
        self._vm = vm

    def execute_source(self, source, filename, mode, global_vars=None, cmd=None):

        if global_vars is None:
            global_vars = __main__.__dict__
        
        def handle_user_exception():
            # other unhandled exceptions (supposedly client program errors) are printed to stderr, as usual
            # for VM mainloop they are not exceptions
            e_type, e_value, e_traceback = sys.exc_info()
            self._vm._print_user_exception(e_type, e_value, e_traceback)
            return {"context_info" : "other unhandled exception"}
        
        try:
            
            if mode == "exec+eval":
                root = ast.parse(source, filename=filename, mode="exec")
                statements = compile(ast.Module(body=root.body[:-1]), filename, "exec")
                expression = compile(ast.Expression(root.body[-1].value), filename, "eval")
                try:
                    exec(statements, global_vars)
                    value = eval(expression, global_vars)
                except Exception:
                    return handle_user_exception()
                
                if value is not None:
                    builtins._ = value
                return {"value_info" : self._vm.export_value(value)}
            else:
                bytecode = self._compile_source(source, filename, mode)
                if hasattr(self, "_trace"):
                    sys.settrace(self._trace)
                if mode == "eval":
                    try:
                        value = eval(bytecode, global_vars)
                    except Exception:
                        return handle_user_exception()
                    
                    if value is not None:
                        builtins._ = value
                    return {"value_info" : self._vm.export_value(value)}
                else:
                    assert mode == "exec"
                    try:
                        exec(bytecode, global_vars) # <Marker: remove this line from stacktrace>
                    except:
                        return handle_user_exception()
                        
                    return {"context_info" : "after normal execution", "source" : source, "filename" : filename, "mode" : mode}
        except SystemExit:
            return {"SystemExit" : True}
        except Exception:
            traceback.print_exc()
            return {"context_info" : "other unhandled exception"}
        finally:
            sys.settrace(None)

    def export_globals(self, module_name):
        return self._vm.export_latest_globals(module_name)

    def module_needs_custom_loader(self, fullname, path):
        return False

    def _compile_source(self, source, filename, mode):
        return compile(source, filename, mode)

class SimpleRunner(Executor):
    pass

class Tracer(Executor):
    def __init__(self, vm):
        self._vm = vm
        self._thonny_src_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._current_command = None
        self._unhandled_exception = None
        
    def execute_source(self, source, filename, mode, global_vars=None, cmd=None):
        if cmd and getattr(cmd, "breakpoints", None):
            command_name = "resume"
            breakpoints = cmd.breakpoints
        else:
            command_name = "step_into"
            breakpoints = {}
            
        self._current_command = DebuggerCommand(command_name, 
                                                state=None,
                                                focus=None,
                                                frame_id=None,
                                                exception=None,
                                                breakpoints=breakpoints)

        return Executor.execute_source(self, source, filename, mode, global_vars, cmd)
        #assert len(self._custom_stack) == 0
    def _should_skip_frame(self, frame):
        code = frame.f_code

        return (
            code is None
            or code.co_filename is None
            or code.co_flags & inspect.CO_GENERATOR  # @UndefinedVariable
            or sys.version_info >= (3,5) and code.co_flags & inspect.CO_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3,5) and code.co_flags & inspect.CO_ITERABLE_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3,6) and code.co_flags & inspect.CO_ASYNC_GENERATOR  # @UndefinedVariable
            or "importlib._bootstrap" in code.co_filename
            or self._vm.is_doing_io()
        )

    def _is_interesting_exception(self, frame):
        # interested only in exceptions in command frame or it's parent frames
        return (id(frame) == self._current_command.frame_id
                or not self._frame_is_alive(self._current_command.frame_id))

    def _respond_to_inline_commands(self):
        while isinstance(self._current_command, InlineCommand):
            self._vm.handle_command(self._current_command)
            self._current_command = self._fetch_command()
    
    def _fetch_command(self):
        return self._vm._fetch_command()
    
    def _save_exception_info(self, frame, arg):
        exc = arg[1]
        if self._unhandled_exception is None:
            # this means it's the first time we see this exception
            exc.causing_frame = frame
        else:
            # this means the exception is propagating to older frames
            # get the causing_frame from previous occurrence
            exc.causing_frame = self._unhandled_exception.causing_frame

        self._unhandled_exception = exc
        
    def _export_exception_info(self, frame):
        result = {
            "exception" : self._vm.export_value(self._unhandled_exception, True)
        }
        if self._unhandled_exception is not None:
            frame_infos = traceback.format_stack(self._unhandled_exception.causing_frame)
            # I want to show frames from current frame to causing_frame
            if frame == self._unhandled_exception.causing_frame:
                interesting_frame_infos = []
            else:
                # c how far is current frame from causing_frame?
                _distance = 0
                _f = self._unhandled_exception.causing_frame
                while _f != frame:
                    _distance += 1
                    _f = _f.f_back
                    if _f == None:
                        break
                interesting_frame_infos = frame_infos[-_distance:]
            result["exception_lower_stack_description"] = "".join(interesting_frame_infos)
            result["exception_msg"] = str(self._unhandled_exception)
        else:
            result["exception_lower_stack_description"] = None
            result["exception_msg"] = None
        
        return result


class SimpleTracer(Tracer):
    def __init__(self, vm):
        super().__init__(vm)
        
        self._alive_frame_ids = set()
    
    def _trace(self, frame, event, arg):
        
        # is this frame interesting at all?
        if self._should_skip_frame(frame):
            return None
        
        if event == "call": 
            self._unhandled_exception = None # some code is running, therefore exception is not propagating anymore
            # can we skip this frame?
            if (self._current_command.name == "step_over"
                and not self._current_command.breakpoints):
                return None
            else:
                self._alive_frame_ids.add(id(frame))
        
        elif event == "return":
            self._alive_frame_ids.remove(id(frame)) 
          
        elif event == "exception":
            self._save_exception_info(frame, arg)
            
            if self._is_interesting_exception(frame):
                self._report_current_state(frame)
                self._current_command = self._fetch_command()
                self._respond_to_inline_commands()
            
        elif event == "line":
            self._unhandled_exception = None # some code is running, therefore exception is not propagating anymore
            
            handler = getattr(self, "_cmd_%s_completed" % self._current_command.name)
            if handler(frame, self._current_command):
                self._report_current_state(frame)
                self._current_command = self._fetch_command()
                self._respond_to_inline_commands()

        return self._trace
    
    def _report_current_state(self, frame):
        msg = SimpleDebuggerResponse(
                               stack=self._export_stack(frame),
                               is_new=True,
                               loaded_modules=list(sys.modules.keys()),
                               stream_symbol_counts=None,
                               **self._export_exception_info(frame)
                               )
        
        self._vm.send_message(msg)
    
    def _cmd_step_into_completed(self, frame, cmd):
        return True

    def _cmd_step_over_completed(self, frame, cmd):
        frame_id = id(frame)
        return (frame_id == cmd.frame_id
                or cmd.frame_id not in self._alive_frame_ids
                or self._at_a_breakpoint(frame, cmd))
        
    def _cmd_step_out_completed(self, frame, cmd):
        return (cmd.frame_id not in self._alive_frame_ids
                or self._at_a_breakpoint(frame, cmd))

    def _cmd_resume_completed(self, frame, cmd):
        return self._at_a_breakpoint(frame, cmd)
    
    def _at_a_breakpoint(self, frame, cmd):
        filename = frame.f_code.co_filename
        return (filename in cmd.breakpoints
                and frame.f_lineno in cmd.breakpoints[filename])

    def _should_skip_frame(self, frame):
        code = frame.f_code
        return (super()._should_skip_frame(frame)
                or code.co_filename.startswith(self._thonny_src_dir))

    def _frame_is_alive(self, frame_id):
        return frame_id in self._alive_frame_ids

    def _export_stack(self, newest_frame):
        result = []
        
        system_frame = newest_frame
        
        while system_frame is not None:
            module_name = system_frame.f_globals["__name__"]
            code_name = system_frame.f_code.co_name
            
            source, firstlineno = _get_frame_source_info(system_frame)

            result.insert(0, FrameInfo(
                id=id(system_frame),
                filename=system_frame.f_code.co_filename,
                module_name=module_name,
                code_name=code_name,
                lineno=system_frame.f_lineno,
                #locals=self._vm.export_variables(system_frame.f_locals),
                source=source,
                firstlineno=firstlineno,
            ))
            
            if module_name == "__main__" and code_name == "<module>":
                # this was last frame relevant to the user
                break
            
            system_frame = system_frame.f_back

        return result
    
class FancyTracer(Tracer):

    def __init__(self, vm):
        super().__init__(vm)
        self._instrumented_files = set()
        self._install_marker_functions()
        self._custom_stack = []
        self._past_messages = []
        self._past_globals = []
        self._current_state = 0


    def export_globals(self, module_name):
        if not self.is_in_past():
            return self._vm.export_latest_globals(module_name)
        elif module_name in self._past_globals[self._current_state]:
            return self._past_globals[self._current_state][module_name]
        else:
            raise RuntimeError("Past state not available for this module")

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

    def _compile_source(self, source, filename, mode):
        root = ast.parse(source, filename, mode)

        ast_utils.mark_text_ranges(root, source)
        self._tag_nodes(root)
        self._insert_expression_markers(root)
        self._insert_statement_markers(root)
        self._insert_for_target_markers(root)
        self._instrumented_files.add(filename)

        return compile(root, filename, mode)

    def _should_skip_frame(self, frame):
        code = frame.f_code
        return (super()._should_skip_frame(frame)
                or code.co_filename not in self._instrumented_files
                    and code.co_name not in self.marker_function_names
                or code.co_filename.startswith(self._thonny_src_dir)
                    and code.co_name not in self.marker_function_names
                )

    def is_in_past(self):
        return self._current_state < len(self._past_messages)-1

    def _trace(self, frame, event, arg):
        """
        1) Detects marker calls and responds to client queries in these spots
        2) Maintains a customized view of stack
        """
        if self._should_skip_frame(frame):
            return None

        code_name = frame.f_code.co_name

        if event == "call":
            self._unhandled_exception = None # some code is running, therefore exception is not propagating anymore

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
                del marker_function_args["self"]

                if "call_function" not in marker_function_args["node_tags"]:
                    self._handle_progress_event(frame.f_back, event, marker_function_args)
                self._try_interpret_as_again_event(frame.f_back, event, marker_function_args)


            else:
                # Calls to proper functions.
                # Client doesn't care about these events,
                # it cares about "before_statement" events in the first statement of the body
                self._custom_stack.append(CustomStackFrame(frame, "call"))

        elif event == "return":
            if code_name not in self.marker_function_names:
                self._custom_stack.pop()
                if len(self._custom_stack) == 0:
                    # We popped last frame, this means our program has ended.
                    # There may be more events coming from upper (system) frames
                    # but we're not interested in those
                    sys.settrace(None)
            else:
                pass

        elif event == "exception":
            exc = arg[1]
            if self._unhandled_exception is None:
                # this means it's the first time we see this exception
                exc.causing_frame = frame
            else:
                # this means the exception is propagating to older frames
                # get the causing_frame from previous occurrence
                exc.causing_frame = self._unhandled_exception.causing_frame

            self._unhandled_exception = exc
            if self._is_interesting_exception(frame):
                self._save_debugger_progress_message(frame)
                self._handle_message_selection()

        # TODO: support line event in non-instrumented files
        elif event == "line":
            self._unhandled_exception = None

        return self._trace


    def _handle_progress_event(self, frame, event, args):
        """
        Tries to respond to current command in this state. 
        If it can't, then it returns, program resumes
        and _trace will call it again in another state.
        Otherwise sends response and fetches next command.  
        """
        #self._debug("Progress event:", event, self._current_command)

        focus = TextRange(*args["text_range"])

        self._custom_stack[-1].last_event = event
        self._custom_stack[-1].last_event_focus = focus
        self._custom_stack[-1].last_event_args = args

        # store information about current statement / expression
        if "statement" in event:
            self._custom_stack[-1].current_statement = focus

            if event == "before_statement_again":
                # keep the expression information from last event
                self._custom_stack[-1].current_root_expression = self._custom_stack[-1].current_root_expression
                self._custom_stack[-1].current_evaluations = self._custom_stack[-1].current_evaluations

            else:
                self._custom_stack[-1].current_root_expression = None
                self._custom_stack[-1].current_evaluations = []
        else:
            # see whether current_root_expression needs to be updated
            assert len(self._past_messages) > 0
            prev_msg_frame = self._past_messages[-1][0]["stack"][-1]
            prev_event = prev_msg_frame.last_event
            prev_root_expression = prev_msg_frame.current_root_expression

            if (event == "before_expression"
                and (id(frame) != prev_msg_frame.id
                     or "statement" in prev_event
                     or focus.not_smaller_eq_in(prev_root_expression))):
                self._custom_stack[-1].current_root_expression = focus
                self._custom_stack[-1].current_evaluations = []

        if event == "after_expression":
            self._custom_stack[-1].current_evaluations.append((focus, self._vm.export_value(args["value"])))

        # Save the current command and frame data
        self._save_debugger_progress_message(frame)

        # Select the correct method according to the command
        self._handle_message_selection()


    def _handle_message_selection(self):
        """
        Selects the correct message according to current command for both past and present states
        :return: Let Python run to the next progress event
        """

        while self._current_state < len(self._past_messages):
            # Get the message data
            current_frame = self._get_frame_from_history()
            frame = current_frame
            event = current_frame.last_event
            args = current_frame.last_event_args
            focus = current_frame.last_event_focus
            cmd = self._current_command
            exc = self._past_messages[self._current_state][0]["exception"]

            # Has the command completed?
            tester = getattr(self, "_cmd_" + cmd.name + "_completed")
            cmd_complete = tester(frame, event, args, focus, cmd)

            if cmd_complete or exc is not None:
                # Last command has completed or a state caused an exception, send message and fetch the next command
                self._past_messages[self._current_state][1] = True  # Add "shown to user" flag
                self._send_and_fetch_next_debugger_progress_message(self._past_messages[self._current_state][0])

            if self._current_command.name == "back":
                # Step back has been chosen, move the pointer backwards
                if self._current_state > 0:  # Don't let the pointer have negative values
                    self._past_messages[self._current_state][1] = False  # Remove "shown to user" flag
                    self._current_state -= 1
            elif exc is None or self._current_state != len(self._past_messages) - 1:
                # Other progress events move the pointer forward,
                # unless we are displaying the last state and an exception occurred
                self._current_state += 1

        # Saved messages are no longer enough, let Python run to the next progress event


    def _get_frame_from_history(self):
        """
        :return: Returns the last frame from the stack of the current state
        """
        return self._past_messages[self._current_state][0]["stack"][-1]


    def _save_debugger_progress_message(self, frame):
        """
        Creates and saves the debugger progress message for possible reporting to the front-end
        :param frame: Current frame, for checking if an exception occurred
        :param value: The returned value of the statement/expression
        :return:
        """

        if len(self._past_messages) > 0:
            self._past_messages[-1][0]["is_new"] = False

        # Count the symbols that have been sent by each stream by now.
        symbols_by_streams = {
            "stdin": sys.stdin._processed_symbol_count,
            "stdout": sys.stdout._processed_symbol_count,
            "stderr": sys.stderr._processed_symbol_count
        }

        # Save the __main__ module's variables
        self._past_globals.append({"__main__":self._vm.export_variables(vars(sys.modules["__main__"]))})

        # If the current module is not __main__, save the current module's variables
        current_module_globals = self._custom_stack[-1].system_frame.f_globals
        if current_module_globals["__name__"] != "__main__":
            self._past_globals[-1][current_module_globals["__name__"]] = self._vm.export_variables(current_module_globals)

        msg = FancyDebuggerResponse(
                                    stack=self._export_stack(),
                                    is_new=True,
                                    loaded_modules=list(sys.modules.keys()),
                                    stream_symbol_counts=symbols_by_streams,
                                    **self._export_exception_info(frame)
                                    )
        
        self._past_messages.append([msg, False])  # 2nd lement is a flag for identifying if the message has been sent to front-end


    def _send_and_fetch_next_debugger_progress_message(self, message):
        """
        Sends a message to the front-end and fetches the next message
        :param message: The message to be sent
        :return:
        """
        self._vm.send_message(message)

        self._debug("Waiting for command")
        # Fetch next debugger command
        self._current_command = self._fetch_command()
        self._debug("Got command:", self._current_command)
        # get non-progress commands out our way
        self._respond_to_inline_commands()
        assert isinstance(self._current_command, DebuggerCommand)


    def _try_interpret_as_again_event(self, frame, original_event, original_args):
        """
        Some after_* events can be interpreted also as 
        "before_*_again" events (eg. when last argument of a call was 
        evaluated, then we are just before executing the final stage of the call)
        """

        if original_event == "after_expression":
            node_tags = original_args.get("node_tags")
            value = original_args.get("value")

            if (node_tags is not None
                and ("last_child" in node_tags
                     or "or_arg" in node_tags and value
                     or "and_arg" in node_tags and not value)):

                # next step will be finalizing evaluation of parent of current expr
                # so let's say we're before that parent expression
                again_args = {"text_range" : original_args.get("parent_range"),
                              "node_tags" : ""}
                again_event = ("before_expression_again"
                               if "child_of_expression" in node_tags
                               else "before_statement_again")

                self._handle_progress_event(frame, again_event, again_args)


    def _cmd_step_over_completed(self, frame, event, args, focus, cmd):
        """
        Identifies the moment when piece of code indicated by cmd.frame_id and cmd.focus
        has completed execution (either successfully or not).
        """
        
        if self._at_a_breakpoint(frame, event, focus, cmd):
            return True

        # Make sure the correct frame_id is selected
        if type(frame) == FrameInfo:
            frame_id = frame.id
        else:
            frame_id = id(frame)

        if frame_id == cmd.frame_id:
            # We're in the same frame
            if "before_" in cmd.state:
                if focus.not_smaller_eq_in(cmd.focus):
                    # Focus has changed, command has completed
                    return True
                else:
                    # Keep running
                    return False
            elif "after_" in cmd.state:
                if focus != cmd.focus or "before_" in event \
                        or "_expression" in cmd.state and "_statement" in event \
                        or "_statement" in cmd.state and "_expression" in event:
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

    def _cmd_step_into_completed(self, frame, event, args, focus, cmd):
        return event != "after_statement"

    def _cmd_step_back_completed(self, frame, event, args, focus, cmd):
        # Check if the selected message has been previously sent to front-end
        return self._past_messages[self._current_state][1]

    def _cmd_step_out_completed(self, frame, event, args, focus, cmd):
        if self._current_state == 0:
            return False

        if event == "after_statement":
            return False

        if self._at_a_breakpoint(frame, event, focus, cmd):
            return True
        
        prev_state_frame = self._past_messages[self._current_state-1][0]["stack"][-1]

        """Complete current frame"""
        if type(frame) == FrameInfo:
            frame_id = frame.id
        else:
            frame_id = id(frame)
        return (
            # the frame has completed
            not self._frame_is_alive(cmd.frame_id)
            # we're in the same frame but on higher level
            # TODO: expression inside statement expression has same range as its parent
            or frame_id == cmd.frame_id and focus.contains_smaller(cmd.focus)
            # or we were there in prev state
            or prev_state_frame.id == cmd.frame_id and prev_state_frame.last_event_focus.contains_smaller(cmd.focus)
        )

    def _cmd_resume_completed(self, frame, event, args, focus, cmd):
        return self._at_a_breakpoint(frame, event, focus, cmd)
    
    def _at_a_breakpoint(self, frame, event, focus, cmd):
        if type(frame) == FrameInfo:
            frame_id = frame.id
        else:
            frame_id = id(frame)
        
        return (event in ["before_statement", "before_expression"]
                and frame.filename in cmd.breakpoints
                and focus.lineno in cmd.breakpoints[frame.filename]
                # consider only first event on a line
                # (but take into account that same line may be reentered)
                and (cmd.focus is None 
                     or (cmd.focus.lineno != focus.lineno)
                     or (cmd.focus == focus and cmd.state == event) 
                     or frame_id != cmd.frame_id
                     )
                )

    def _frame_is_alive(self, frame_id):
        for frame in self._custom_stack:
            if frame.id == frame_id:
                return True
        else:
            return False

    def _export_stack(self):
        result = []

        for custom_frame in self._custom_stack:

            last_event_args = custom_frame.last_event_args.copy()
            if "value" in last_event_args:
                last_event_args["value"] = self._vm.export_value(last_event_args["value"])

            system_frame = custom_frame.system_frame
            source, firstlineno = _get_frame_source_info(system_frame)

            result.append(FrameInfo(
                id=id(system_frame),
                filename=system_frame.f_code.co_filename,
                module_name=system_frame.f_globals["__name__"],
                code_name=system_frame.f_code.co_name,
                locals=self._vm.export_variables(system_frame.f_locals),
                source=source,
                firstlineno=firstlineno,
                last_event=custom_frame.last_event,
                last_event_args=last_event_args,
                last_event_focus=custom_frame.last_event_focus,
                current_evaluations=custom_frame.current_evaluations.copy(),
                current_statement=custom_frame.current_statement,
                current_root_expression=custom_frame.current_root_expression,
            ))

        return result

    def _thonny_hidden_before_stmt(self, text_range, node_tags):
        """
        The code to be debugged will be instrumented with this function
        inserted before each statement. 
        Entry into this function indicates that statement as given
        by the code range is about to be evaluated next.
        """
        return None

    def _thonny_hidden_after_stmt(self, text_range, node_tags):
        """
        The code to be debugged will be instrumented with this function
        inserted after each statement. 
        Entry into this function indicates that statement as given
        by the code range was just executed successfully.
        """
        return None

    def _thonny_hidden_before_expr(self, text_range, node_tags):
        """
        Entry into this function indicates that expression as given
        by the code range is about to be evaluated next
        """
        return text_range

    def _thonny_hidden_after_expr(self, text_range, node_tags, value, parent_range):
        """
        The code to be debugged will be instrumented with this function
        wrapped around each expression (given as 2nd argument). 
        Entry into this function indicates that expression as given
        by the code range was just evaluated to given value
        """
        return value


    def _tag_nodes(self, root):
        """Marks interesting properties of AST nodes"""

        def add_tag(node, tag):
            if not hasattr(node, "tags"):
                node.tags = set()
                node.tags.add("class=" + node.__class__.__name__)
            node.tags.add(tag)

        for node in ast.walk(root):

            # tag last children 
            last_child = ast_utils.get_last_child(node)
            if last_child is not None and last_child:
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

            if isinstance(node, ast.Num):
                add_tag(node, "NumberLiteral")

            if isinstance(node, ast.ListComp):
                add_tag(node.elt, "ListComp.elt")

            if isinstance(node, ast.SetComp):
                add_tag(node.elt, "SetComp.elt")

            if isinstance(node, ast.DictComp):
                add_tag(node.key, "DictComp.key")
                add_tag(node.value, "DictComp.value")

            if isinstance(node, ast.comprehension):
                for expr in node.ifs:
                    add_tag(expr, "comprehension.if")


            # make sure every node has this field
            if not hasattr(node, "tags"):
                node.tags = set()

    def _should_instrument_as_expression(self, node):
        return (isinstance(node, _ast.expr)
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
        return (isinstance(node, _ast.stmt)
                # Shouldn't insert anything before from __future__ import
                # as this is not a normal statement
                # https://bitbucket.org/plas/thonny/issues/183/thonny-throws-false-positive-syntaxerror
                and (not isinstance(node, _ast.ImportFrom)
                     or node.module != "__future__"))

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
                            new_list.append(self._create_statement_marker(node,
                                                                          BEFORE_STATEMENT_MARKER))

                        # original statement
                        if self._should_instrument_as_statement(node):
                            self._insert_statement_markers(node)
                        new_list.append(node)

                        if isinstance(node, _ast.stmt):
                            # add after marker
                            new_list.append(self._create_statement_marker(node,
                                                                          AFTER_STATEMENT_MARKER))
                    setattr(root, name, new_list)


    def _create_statement_marker(self, node, function_name, end_node=None):
        call = self._create_simple_marker_call(node, function_name, end_node)
        stmt = ast.Expr(value=call)
        ast.copy_location(stmt, node)
        ast.fix_missing_locations(stmt)
        return stmt

    def _insert_for_target_markers(self, root):
        """inserts markers which notify assignment to for-loop variables"""
        for node in ast.walk(root):
            if isinstance(node, ast.For):
                old_target = node.target
                #print(vars(old_target))
                temp_name = '__for_loop_var'
                node.target = ast.Name(temp_name, ast.Store())
                name_load = ast.Name(temp_name, ast.Load())
                name_load.dont_trace = True
                before_marker = self._create_statement_marker(old_target, BEFORE_STATEMENT_MARKER,
                                                              end_node=node.iter)
                node.body.insert(0, before_marker)
                node.body.insert(1, ast.Assign([old_target], name_load))
                node.body.insert(2, self._create_statement_marker(old_target, AFTER_STATEMENT_MARKER,
                                                                  end_node=node.iter))
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
                        before_marker = tracer._create_simple_marker_call(node, BEFORE_EXPRESSION_MARKER)
                        ast.copy_location(before_marker, node)

                        # after marker
                        after_marker = ast.Call (
                            func=ast.Name(id=AFTER_EXPRESSION_MARKER, ctx=ast.Load()),
                            args=[
                                before_marker,
                                tracer._create_tags_literal(node),
                                ast.NodeTransformer.generic_visit(self, node),
                                tracer._create_location_literal(node.parent_node if hasattr(node, "parent_node") else None)
                            ],
                            keywords=[]
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


    def _create_location_literal(self, node, end_node=None):
        if node is None:
            return ast_utils.value_to_literal(None)
        
        if end_node is None:
            end_node = node

        assert hasattr(end_node, "end_lineno")
        assert hasattr(end_node, "end_col_offset")

        nums = []
        for value in node.lineno, node.col_offset, end_node.end_lineno, end_node.end_col_offset:
            nums.append(ast.Num(n=value))
        return ast.Tuple(elts=nums, ctx=ast.Load())

    def _create_tags_literal(self, node):
        if hasattr(node, "tags"):
            # maybe set would perform as well, but I think string is faster
            return ast_utils.value_to_literal(",".join(node.tags))
            #self._debug("YESTAGS")
        else:
            #self._debug("NOTAGS " + str(node))
            return ast_utils.value_to_literal("")

    def _create_simple_marker_call(self, node, fun_name, end_node=None):
        args = [
            self._create_location_literal(node, end_node),
            self._create_tags_literal(node),
        ]

        return ast.Call (
            func=ast.Name(id=fun_name, ctx=ast.Load()),
            args=args,
            keywords=[]
        )

    def _debug(self, *args):
        print("TRACER:", *args, file=self._vm._original_stderr)

class CustomStackFrame:
    def __init__(self, frame, last_event, focus=None):
        self.id = id(frame)
        self.system_frame = frame
        self.last_event = last_event
        self.current_evaluations = []
        self.focus = None
        self.current_statement = None
        self.current_root_expression = None

class CustomFinder(PathFinder):
    # https://blog.sqreen.io/dynamic-instrumentation-agent-for-python/
    def __init__(self, vm):
        self._vm = vm

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            loader = CustomLoader(fullname, spec.origin)
            return ModuleSpec(fullname, loader)

class CustomLoader(SourceFileLoader):
    # https://blog.sqreen.io/dynamic-instrumentation-agent-for-python/
    def exec_module(self, module):
        super().exec_module(module)
        # TODO: patch module
        module.function = patcher(module.function)
        return module
    
    def source_to_code(self, data, path, *, _optimize=-1):
        # TODO: parse and/or instrument data
        parse
        return SourceFileLoader.source_to_code(self, data, path)


def fdebug(frame, msg, *args):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(_get_frame_prefix(frame) + msg, *args)


def _get_frame_prefix(frame):
    return str(id(frame)) + " " + ">" * len(inspect.getouterframes(frame, 0)) + " "

def _get_python_version_string(add_word_size=False):
    result = ".".join(map(str, sys.version_info[:3]))
    if sys.version_info[3] != "final":
        result += "-" + sys.version_info[3]

    if add_word_size:
        result += " (" + ("64" if sys.maxsize > 2**32 else "32")+ " bit)"

    return result

def _get_frame_source_info(frame):
    if frame.f_code.co_name == "<module>":
        obj = frame.f_code
        lineno = 1
    else:
        obj = frame.f_code
        lineno = obj.co_firstlineno

    assert obj is not None, (
        "Failed to get source in backend _get_frame_source_info for frame " + str(frame)
        + " with f_code.co_name == " + frame.f_code.co_name
    )

    # lineno returned by getsourcelines is not consistent between modules vs functions
    lines, _ = inspect.getsourcelines(obj)
    return "".join(lines), lineno


def load_module_from_alternative_path(module_name, path, force=False):
    from importlib.machinery import PathFinder
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