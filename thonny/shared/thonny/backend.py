# -*- coding: utf-8 -*-

import sys 
import os.path
import inspect
import ast
import _ast
import _io
import traceback
import types
import logging
import pydoc
import builtins
import site

import __main__  # @UnresolvedImport

from thonny import ast_utils
from thonny.common import TextRange,\
    parse_message, serialize_message, DebuggerCommand,\
    ToplevelCommand, FrameInfo, InlineCommand, InputSubmission
import signal
import warnings

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

EXCEPTION_TRACEBACK_LIMIT = 100
DEBUG = True    

logger = logging.getLogger()
info = logger.info

class VM:
    def __init__(self):
        self._main_dir = os.path.dirname(sys.modules["thonny"].__file__)
        self._heap = {} # WeakValueDictionary would be better, but can't store reference to None
        site.sethelper() # otherwise help function is not available
        pydoc.pager = pydoc.plainpager # otherwise help command plays tricks
        self._install_fake_streams()
        self._current_executor = None
        self._io_level = 0
        
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
        
        # add jedi
        if "JEDI_LOCATION" in os.environ:
            sys.path.append(os.environ["JEDI_LOCATION"])
    
        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if not key.startswith("__") or key in special_names_to_remove:
                del __main__.__dict__[key] 
        
        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None
        
        self.send_message(self.create_message("ToplevelResult",
                          main_dir=self._main_dir,
                          original_argv=original_argv,
                          original_path=original_path,
                          argv=sys.argv,
                          path=sys.path,
                          welcome_text="Python " + _get_python_version_string(),
                          executable=sys.executable,
                          in_venv=hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix,
                          python_version=_get_python_version_string(),
                          cwd=os.getcwd()))
        
        self._install_signal_handler()
        
    def mainloop(self):
        try:
            while True: 
                try:
                    cmd = self._fetch_command()
                    self.handle_command(cmd, "waiting_toplevel_command")
                except KeyboardInterrupt:
                    logger.exception("Interrupt in mainloop")
                    # Interrupt must always result in waiting_toplevel_command state
                    # Don't show error messages, as the interrupted command may have been InlineCommand
                    # (handlers of ToplevelCommands in normal cases catch the interrupt and provide
                    # relevant message)  
                    self.send_message(self.create_message("ToplevelResult"))
        except:
            logger.exception("Crash in mainloop")
            
            
    def handle_command(self, cmd, command_context):
        assert isinstance(cmd, ToplevelCommand) or isinstance(cmd, InlineCommand)
        
        error_response_type = "ToplevelResult" if isinstance(cmd, ToplevelCommand) else "InlineError"
        try:
            handler = getattr(self, "_cmd_" + cmd.command)
        except AttributeError:
            response = self.create_message(error_response_type, error="Unknown command: " + cmd.command)
        else:
            try:
                response = handler(cmd)
            except:
                response = self.create_message(error_response_type,
                    error="Thonny internal error: {0}".format(traceback.format_exc(EXCEPTION_TRACEBACK_LIMIT)))
        
        if response is not None:
            response["command_context"] = command_context
            response["command"] = cmd.command
            if response["message_type"] == "ToplevelResult":
                self._add_tkinter_info(response)
            self.send_message(response)
    
    def _install_signal_handler(self):
        def signal_handler(signal, frame):
            raise KeyboardInterrupt("Execution interrupted")
        
        if os.name == 'nt':
            signal.signal(signal.SIGBREAK, signal_handler)
        else:
            signal.signal(signal.SIGINT, signal_handler)        
    
    def _cmd_cd(self, cmd):
        try:
            os.chdir(cmd.path)
            return self.create_message("ToplevelResult")
        except Exception as e:
            # TODO: should output user error
            return self.create_message("ToplevelResult", error=str(e))
    
    def _cmd_Reset(self, cmd):
        # nothing to do, because Reset always happens in fresh process
        return self.create_message("ToplevelResult",
                                   welcome_text="Python " + _get_python_version_string(),
                                   executable=sys.executable)
    
    def _cmd_Run(self, cmd):
        return self._execute_file(cmd, False)
    
    def _cmd_run(self, cmd):
        return self._execute_file(cmd, False)
    
    def _cmd_Debug(self, cmd):
        return self._execute_file(cmd, True)
    
    def _cmd_debug(self, cmd):
        return self._execute_file(cmd, True)
    
    def _cmd_execute_source(self, cmd):
        return self._execute_source(cmd, "ToplevelResult")
    
    def _cmd_execute_source_inline(self, cmd):
        return self._execute_source(cmd, "InlineResult")
    
    def _cmd_tkupdate(self, cmd):
        # advance the event loop
        # http://bugs.python.org/issue989712
        # http://bugs.python.org/file6090/run.py.diff
        try:
            root = self._get_tkinter_default_root()
            if root is None:
                return
            
            import tkinter
            while root.dooneevent(tkinter._tkinter.DONT_WAIT):
                pass
                 
        except:
            pass
            
        return None
    
    
    def _cmd_get_globals(self, cmd):
        if not cmd.module_name in sys.modules:
            raise ThonnyClientError("Module '{0}' is not loaded".format(cmd.module_name))
        
        return self.create_message("Globals", module_name=cmd.module_name,
                              globals=self.export_variables(sys.modules[cmd.module_name].__dict__))
    
    def _cmd_get_locals(self, cmd):
        for frame in inspect.stack():
            if id(frame) == cmd.frame_id:
                return self.create_message("Locals", locals=self.export_variables(frame.f_locals))
        else:
            raise ThonnyClientError("Frame '{0}' not found".format(cmd.frame_id))
            
    
    def _cmd_get_heap(self, cmd):
        result = {}
        for key in self._heap:
            result[key] = self.export_value(self._heap[key])
            
        return self.create_message("Heap", heap=result)
    
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
        
        return self.create_message("ShellCompletions", 
            source=cmd.source,
            completions=completions,
            error=error
        )
    
    def _cmd_editor_autocomplete(self, cmd):
        error = None
        try:
            import jedi
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
        
        return self.create_message("EditorCompletions", 
                          source=cmd.source,
                          row=cmd.row,
                          column=cmd.column,
                          filename=cmd.filename,
                          completions=completions,
                          error=error)
    
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
        if cmd.object_id in self._heap:
            value = self._heap[cmd.object_id]
            attributes = {}
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
                    'type_id' : id(type(value)),
                    'attributes': self.export_variables(attributes)}
            
            if isinstance(value, _io.TextIOWrapper):
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
            
        else:
            info = {'id' : cmd.object_id,
                    "repr": "<object info not found>",
                    "type" : "object",
                    "type_id" : id(object),
                    "attributes" : {}}
        
        return self.create_message("ObjectInfo", id=cmd.object_id, info=info)
    
    def _get_tkinter_default_root(self):
        tkinter = sys.modules.get("tkinter")
        if tkinter is not None:
            return getattr(tkinter, "_default_root", None)
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
    
    def _add_tkinter_info(self, msg):
        # tkinter._default_root is not None,
        # when window has been created and mainloop isn't called or hasn't ended yet
        msg["tkinter_is_active"] = self._get_tkinter_default_root() is not None
    
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
        
    def _execute_file(self, cmd, debug_mode):
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        result_attributes = self._execute_source_ex(cmd.source, cmd.full_filename, "exec", debug_mode) 
        return self.create_message("ToplevelResult", **result_attributes)
    
    def _execute_source(self, cmd, result_type):
        filename = "<pyshell>"
        
        if hasattr(cmd, "global_vars"):
            global_vars = cmd.global_vars
        elif hasattr(cmd, "extra_vars"):
            global_vars = __main__.__dict__.copy() # Don't want to mess with main namespace
            global_vars.update(cmd.extra_vars)
        else:
            global_vars = __main__.__dict__

        # let's see if it's single expression or something more complex
        try:
            root = ast.parse(cmd.source, filename=filename, mode="exec")
        except SyntaxError as e:
            return self.create_message(result_type,
                error="".join(traceback.format_exception_only(SyntaxError, e)))
            
        assert isinstance(root, ast.Module)
            
        if len(root.body) == 1 and isinstance(root.body[0], ast.Expr):
            mode = "eval"
        else:
            mode = "exec"
            
        result_attributes = self._execute_source_ex(cmd.source, filename, mode,
            hasattr(cmd, "debug_mode") and cmd.debug_mode,
            global_vars)
        
        if "__result__" in global_vars:
            result_attributes["__result__"] = global_vars["__result__"]
        
        if hasattr(cmd, "request_id"):
            result_attributes["request_id"] = cmd.request_id
        else:
            result_attributes["request_id"] = None
        
        return self.create_message(result_type, **result_attributes)
        
    def _execute_source_ex(self, source, filename, execution_mode, debug_mode,
                        global_vars=None):
        if debug_mode:
            self._current_executor = FancyTracer(self)
        else:
            self._current_executor = Executor(self)
        
        try:
            return self._current_executor.execute_source(source, 
                                                         filename,
                                                         execution_mode,
                                                         global_vars)
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
        
    def _fetch_command(self):
        line = self._original_stdin.readline()
        if line == "":
            logger.info("Read stdin EOF")
            sys.exit()
        cmd = parse_message(line)
        return cmd

    def create_message(self, message_type, **kwargs):
        kwargs["message_type"] = message_type
        if "cwd" not in kwargs:
            kwargs["cwd"] = os.getcwd()
            
        return kwargs

    def send_message(self, msg):
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
                    self._vm.send_message(self._vm.create_message("ProgramOutput", stream_name=self._stream_name, data=data))
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
                self._vm.send_message(self._vm.create_message("InputRequest", method=method, limit=limit))
                
                while True:
                    cmd = self._vm._fetch_command()
                    if isinstance(cmd, InputSubmission):
                        return cmd.data
                    elif isinstance(cmd, InlineCommand):
                        self._vm.handle_command(cmd, "waiting_input")
                    else:
                        raise ThonnyClientError("Wrong type of command when waiting for input")
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
    
    def execute_source(self, source, filename, mode, global_vars=None):
        
        if global_vars is None:
            global_vars = __main__.__dict__
        
        try:
            bytecode = self._compile_source(source, filename, mode)
            if hasattr(self, "_trace"):
                sys.settrace(self._trace)    
            if mode == "eval":
                value = eval(bytecode, global_vars)
                if value is not None:
                    builtins._ = value 
                return {"value_info" : self._vm.export_value(value)}
            else:
                assert mode == "exec"
                exec(bytecode, global_vars) # <Marker: remove this line from stacktrace>
                return {"context_info" : "after normal execution", "source" : source, "filename" : filename, "mode" : mode}
        except SyntaxError as e:
            return {"error" : "".join(traceback.format_exception_only(SyntaxError, e))}
        except ThonnyClientError as e:
            return {"error" : str(e)}
        except SystemExit:
            e_type, e_value, e_traceback = sys.exc_info()
            self._print_user_exception(e_type, e_value, e_traceback)
            return {"SystemExit" : True}
        except:
            # other unhandled exceptions (supposedly client program errors) are printed to stderr, as usual
            # for VM mainloop they are not exceptions
            e_type, e_value, e_traceback = sys.exc_info()
            self._print_user_exception(e_type, e_value, e_traceback)
            return {"context_info" : "other unhandled exception"}
        finally:
            sys.settrace(None)
    
    def _print_user_exception(self, e_type, e_value, e_traceback):
        lines = traceback.format_exception(e_type, e_value, e_traceback)

        for line in lines:
            # skip lines denoting thonny execution frame
            if ("thonny/backend" in line 
                or "thonny\\backend" in line
                or "remove this line from stacktrace" in line):
                continue
            else:
                sys.stderr.write(line)

    def _compile_source(self, source, filename, mode):
        return compile(source, filename, mode)


class FancyTracer(Executor):
    
    def __init__(self, vm):
        self._vm = vm
        self._normcase_thonny_src_dir = os.path.normcase(os.path.dirname(sys.modules["thonny"].__file__)) 
        self._instrumented_files = _PathSet()
        self._interesting_files = _PathSet() # only events happening in these files are reported
        self._current_command = None
        self._unhandled_exception = None
        self._install_marker_functions()
        self._custom_stack = []
    
    def execute_source(self, source, filename, mode, global_vars=None):
        self._current_command = DebuggerCommand(command="step", state=None, focus=None, frame_id=None, exception=None)
        
        return Executor.execute_source(self, source, filename, mode, global_vars)
        #assert len(self._custom_stack) == 0
        
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
        
    def _is_interesting_exception(self, frame):
        # interested only in exceptions in command frame or it's parent frames
        cmd = self._current_command
        return (id(frame) == cmd.frame_id
                or not self._frame_is_alive(cmd.frame_id))

    def _compile_source(self, source, filename, mode):
        root = ast.parse(source, filename, mode)
        
        ast_utils.mark_text_ranges(root, source)
        self._tag_nodes(root)        
        self._insert_expression_markers(root)
        self._insert_statement_markers(root)
        self._instrumented_files.add(filename)
        
        return compile(root, filename, mode)
    
    def _may_step_in(self, code):
            
        return not (
            code is None 
            or code.co_filename is None
            or code.co_flags & inspect.CO_GENERATOR  # @UndefinedVariable
            or sys.version_info >= (3,5) and code.co_flags & inspect.CO_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3,5) and code.co_flags & inspect.CO_ITERABLE_COROUTINE  # @UndefinedVariable
            or sys.version_info >= (3,6) and code.co_flags & inspect.CO_ASYNC_GENERATOR  # @UndefinedVariable
            or "importlib._bootstrap" in code.co_filename
            or os.path.normcase(code.co_filename) not in self._instrumented_files 
                and code.co_name not in self.marker_function_names
            or os.path.normcase(code.co_filename).startswith(self._normcase_thonny_src_dir)
                and code.co_name not in self.marker_function_names
            or self._vm.is_doing_io() 
        )
        
    
    def _trace(self, frame, event, arg):
        """
        1) Detects marker calls and responds to client queries in these spots
        2) Maintains a customized view of stack
        """
        if not self._may_step_in(frame.f_code):
            return
        
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
                self._report_state_and_fetch_next_message(frame)

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
        self._debug("Progress event:", event, self._current_command)
        focus = TextRange(*args["text_range"])
        
        self._custom_stack[-1].last_event = event
        self._custom_stack[-1].last_event_focus = focus
        self._custom_stack[-1].last_event_args = args
        
        # Select the correct method according to the command
        tester = getattr(self, "_cmd_" + self._current_command.command + "_completed")
             
        # If method decides we're in the right place to respond to the command ...
        if tester(frame, event, args, focus, self._current_command):
            if event == "after_expression":
                value = self._vm.export_value(args["value"])
            else:
                value = None
            self._report_state_and_fetch_next_message(frame, value)
    
    def _report_state_and_fetch_next_message(self, frame, value=None):
            #self._debug("Completed command: ", self._current_command)
            
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
                exception_lower_stack_description = "".join(interesting_frame_infos)
                exception_msg = str(self._unhandled_exception)
            else:
                exception_lower_stack_description = None 
                exception_msg = None
            
            self._vm.send_message(self._vm.create_message("DebuggerProgress",
                command=self._current_command.command,
                stack=self._export_stack(),
                exception=self._vm.export_value(self._unhandled_exception, True),
                exception_msg=exception_msg,
                exception_lower_stack_description=exception_lower_stack_description,
                value=value,
                command_context="waiting_debugger_command"
            ))
            
            # Fetch next debugger command
            self._current_command = self._vm._fetch_command()
            self._debug("got command:", self._current_command)
            # get non-progress commands out our way
            self._respond_to_inline_commands()  
            assert isinstance(self._current_command, DebuggerCommand)
            
        # Return and let Python run to next progress event
        
    
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
                
    
    def _respond_to_inline_commands(self):
        while isinstance(self._current_command, InlineCommand): 
            self._vm.handle_command(self._current_command, "waiting_debugger_command")
            self._current_command = self._vm._fetch_command()
    
    def _get_frame_source_info(self, frame):
        if frame.f_code.co_name == "<module>":
            obj = inspect.getmodule(frame)
            lineno = 1
        else:
            obj = frame.f_code
            lineno = obj.co_firstlineno
        
        # lineno returned by getsourcelines is not consistent between modules vs functions
        lines, _ = inspect.getsourcelines(obj) 
        return "".join(lines), lineno
        
    
    
    def _cmd_exec_completed(self, frame, event, args, focus, cmd):
        """
        Identifies the moment when piece of code indicated by cmd.frame_id and cmd.focus
        has completed execution (either successfully or not).
        """
        
        # it's meant to be executed in before* state, but if we're not there
        # we'll step there
        
        if cmd.state not in ("before_expression", "before_expression_again",
                             "before_statement", "before_statement_again"):
            return self._cmd_step_completed(frame, event, args, focus, cmd)
        
        
        if id(frame) == cmd.frame_id:
            
            if focus.is_smaller_in(cmd.focus):
                # we're executing a child of command focus,
                # keep running
                return False 
            
            elif focus == cmd.focus:
                
                if event.startswith("before_"):
                    # we're just starting
                    return False
                
                elif (event == "after_expression"
                      and cmd.state in ("before_expression", "before_expression_again")
                      or 
                      event == "after_statement"
                      and cmd.state in ("before_statement", "before_statement_again")):
                    # Normal completion
                    # Maybe there was an exception, but this is forgotten now
                    cmd._unhandled_exception = False
                    self._debug("Exec normal")
                    return True
                
                
                elif (cmd.state in ("before_statement", "before_statement_again")
                      and event == "after_expression"):
                    # Same code range can contain expression statement and expression.
                    # Here we need to run just a bit more
                    return False
                
                else:
                    # shouldn't be here
                    raise AssertionError("Unexpected state in responding to " + str(cmd))
                    
            else:
                # We're outside of starting focus, assumedly because of an exception
                self._debug("Exec outside", cmd.focus, focus)
                return True
        
        else:
            # We're in another frame
            if self._frame_is_alive(cmd.frame_id):
                # We're in a successor frame, keep running
                return False
            else:
                # Original frame has completed, assumedly because of an exception
                # We're done
                self._debug("Exec wrong frame")
                return True
            

    
    def _cmd_step_completed(self, frame, event, args, focus, cmd):
        return True
    
    def _cmd_run_to_before_completed(self, frame, event, args, focus, cmd):
        return event.startswith("before")
    
    def _cmd_out_completed(self, frame, event, args, focus, cmd):
        """Complete current frame"""
        return (
            # the frame has completed
            not self._frame_is_alive(cmd.frame_id)
            # we're in the same frame but on higher level 
            or id(frame) == cmd.frame_id and focus.contains_smaller(cmd.focus)
        )
    
    
    def _cmd_line_completed(self, frame, event, args, focus, cmd):
        return (event == "before_statement" 
            and os.path.normcase(frame.f_code.co_filename) == os.path.normcase(cmd.target_filename)
            and focus.lineno == cmd.target_lineno
            and (focus != cmd.focus or id(frame) != cmd.frame_id))

    
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
            source, firstlineno = self._get_frame_source_info(system_frame)
            
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
        return 
    
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
    
    
    def _create_statement_marker(self, node, function_name):
        call = self._create_simple_marker_call(node, function_name)
        stmt = ast.Expr(value=call)
        ast.copy_location(stmt, node)
        ast.fix_missing_locations(stmt)
        return stmt
        
    
    def _insert_expression_markers(self, node):
        """
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
                        
                        return after_marker
                    else:
                        # This expression (and its children) should be ignored
                        return node
                else:
                    # Descend into statements
                    return ast.NodeTransformer.generic_visit(self, node)
        
        return ExpressionVisitor().visit(node)   
            
    
    def _create_location_literal(self, node):
        if node is None:
            return ast_utils.value_to_literal(None)
        
        assert hasattr(node, "end_lineno")
        assert hasattr(node, "end_col_offset")
        
        nums = []
        for value in node.lineno, node.col_offset, node.end_lineno, node.end_col_offset:
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
    
    def _create_simple_marker_call(self, node, fun_name):
        assert hasattr(node, "end_lineno")
        assert hasattr(node, "end_col_offset")
        
        args = [
            self._create_location_literal(node),
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
        self.focus = None
        
class ThonnyClientError(Exception):
    pass
    

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

class _PathSet:
    "implementation of set whose in operator works well for filenames"
    def __init__(self):
        self._normcase_set = set()
        
    def add(self, name):
        self._normcase_set.add(os.path.normcase(name))
    
    def remove(self, name):
        self._normcase_set.remove(os.path.normcase(name))
    
    def clear(self):
        self._normcase_set.clear()
    
    def __contains__(self, name):
        return os.path.normcase(name) in self._normcase_set

    def __iter__(self):
        for item in self._normcase_set:
            yield item
