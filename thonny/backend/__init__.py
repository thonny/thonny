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

import __main__  # @UnresolvedImport

from thonny import ast_utils
from thonny import misc_utils
from thonny.misc_utils import eqfn
from thonny.common import TextRange,\
    parse_message, serialize_message, DebuggerCommand,\
    ValueInfo, ToplevelCommand, FrameInfo, InlineCommand, InputSubmission

BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

EXCEPTION_TRACEBACK_LIMIT = 100    

logger = logging.getLogger("thonny.backend")
logger.setLevel(logging.ERROR)
debug = logger.debug
info = logger.info

class VM:
    def __init__(self, main_dir):
        #print(sys.argv, file=sys.stderr)
        self._main_dir = main_dir
        self._heap = {} # WeakValueDictionary would be better, but can't store reference to None
        pydoc.pager = pydoc.plainpager # otherwise help command plays tricks
        self._install_fake_streams()
        self._current_executor = None
        self._io_level = 0

        
        # script mode
        if len(sys.argv) > 1:
            initial_global_names = ("__builtins__", "__name__", "__package__", "__doc__",
                                "__file__", "__cached__", "__loader__")
            sys.argv[:] = sys.argv[1:] # shift argv[1] to position of script name
            sys.path[0] = os.path.dirname(sys.argv[0]) # replace backend's dir with program dir
            __main__.__dict__["__file__"] = sys.argv[0]
            # TODO: inspect.getdoc
        
        # shell mode
        else:
            initial_global_names = ("__builtins__", "__name__", "__package__", "__doc__")
            sys.argv[:] = [""] # empty "script name"
            sys.path[0] = ""   # current dir
    
        # clean __main__ global scope
        for key in list(__main__.__dict__.keys()):
            if key not in initial_global_names:
                del __main__.__dict__[key] 
        
        # unset __doc__, then exec dares to write doc of the script there
        __main__.__doc__ = None
        
    def mainloop(self):
        while True: 
            cmd = self._fetch_command()
            self.handle_command(cmd)
            
            
    def handle_command(self, cmd):
        assert isinstance(cmd, ToplevelCommand) or isinstance(cmd, InlineCommand)
        
        #if cmd.command != "tkupdate":
        #    debug("MAINLOOP: %s", cmd)
        response_type = "ToplevelResult" if isinstance(cmd, ToplevelCommand) else "InlineError"
        try:
            handler = getattr(self, "_cmd_" + cmd.command)
        except AttributeError:
            self.send_message(response_type, error="Unknown command: " + cmd.command)
        else:
            try:
                handler(cmd)
            except:
                self.send_message(response_type,
                    error="Thonny internal error: {0}".format(traceback.format_exc(EXCEPTION_TRACEBACK_LIMIT))
                )
        
    
    def _cmd_cd(self, cmd):
        try:
            os.chdir(cmd.path)
            self.send_message("ToplevelResult")
        except Exception as e:
            self.send_message("ToplevelResult", error=str(e))
    
    
    def _cmd_Reset(self, cmd):
        # nothing to do, because Reset always happens in fresh process
        self.send_message("ToplevelResult")
    
    def _cmd_Run(self, cmd):
        self._execute_file(cmd, False)
    
    def _cmd_run(self, cmd):
        self._execute_file(cmd, False)
    
    def _cmd_Debug(self, cmd):
        self._execute_file(cmd, True)
    
    def _cmd_debug(self, cmd):
        self._execute_file(cmd, True)
    
    def _cmd_python(self, cmd):
        # let's see if it's single expression or something more complex
        filename = "<pyshell>"
        
        try:
            root = ast.parse(cmd.cmd_line, filename=filename, mode="exec")
        except SyntaxError as e:
            self.send_message("ToplevelResult",
                error="".join(traceback.format_exception_only(SyntaxError, e)))
            return
            
        assert isinstance(root, ast.Module)
            
        if len(root.body) == 1 and isinstance(root.body[0], ast.Expr):
            mode = "eval"
        else:
            mode = "exec"
        
        self._execute_source(cmd.cmd_line, filename, mode,
            hasattr(cmd, "debug_mode") and cmd.debug_mode)
    
    def _cmd_tkupdate(self, cmd):
        tkinter = sys.modules.get("tkinter")
        if (tkinter is None or tkinter._default_root is None):
            return
        else:
            # advance the event loop
            # http://bugs.python.org/issue989712
            # http://bugs.python.org/file6090/run.py.diff
            try:
                while (tkinter._default_root is not None 
                       and tkinter._default_root.dooneevent(tkinter._tkinter.DONT_WAIT)):
                    pass 
            except:
                pass
    
    
    def _cmd_get_globals(self, cmd):
        if not cmd.module_name in sys.modules:
            raise ThonnyClientError("Module '{0}' is not loaded".format(cmd.module_name))
        
        self.send_message("Globals", module_name=cmd.module_name,
                              globals=self.export_variables(sys.modules[cmd.module_name].__dict__))
    
    def _cmd_get_locals(self, cmd):
        for frame in inspect.stack():
            if id(frame) == cmd.frame_id:
                self.send_message("Locals", locals=self.export_variables(frame.f_locals))
        else:
            raise ThonnyClientError("Frame '{0}' not found".format(cmd.frame_id))
            
    
    def _cmd_get_heap(self, cmd):
        result = {}
        for key in self._heap:
            result[key] = self.export_value(self._heap[key])
            
        self.send_message("Heap", heap=result)
    
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
        
        self.send_message("ObjectInfo", id=cmd.object_id, info=info)
    
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
        except:
            pass
        
    def _add_function_info(self, value, info):
        try:
            info["source"] = inspect.getsource(value)
            # findsource gives code for modules???
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
        source, _ = misc_utils.read_python_file(cmd.filename)
        
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        code_filename = os.path.abspath(cmd.filename)
        return self._execute_source(source, code_filename, "exec", debug_mode)
    
    def _execute_source(self, source, filename, execution_mode, debug_mode):
        if debug_mode:
            self._current_executor = FancyTracer(self, self._main_dir)
        else:
            self._current_executor = Executor(self)
        
        try:
            return self._current_executor.execute_source(source, filename, execution_mode)
        finally:
            self._current_executor = None
    
    def _get_source(self, filename):
        fp = None
        try:
            fp, _ = misc_utils.open_py_file(filename)
            return fp.read()
        finally:
            if fp is not None:
                fp.close()
    
        
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
        cmd = parse_message(line)
        return cmd

    def send_message(self, message_type, **kwargs):
        
        kwargs["message_type"] = message_type
        if "cwd" not in kwargs:
            kwargs["cwd"] = os.getcwd()
        
        self._original_stdout.write(repr(kwargs) + "\n")
        self._original_stdout.flush()
        
    def export_value(self, value, skip_None=False):
        if value is None and skip_None:
            return None
        
        self._heap[id(value)] = value
        try:
            type_name = value.__class__.__name__
        except:
            type_name = type(value).__name__ 
            
        result = ValueInfo(id=id(value),
                         repr=repr(value), 
                         type_name=type_name)
        
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
                    self._vm.send_message("ProgramOutput", stream_name=self._stream_name, data=data)
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
                self._vm.send_message("InputRequest", method=method, limit=limit)
                
                while True:
                    cmd = self._vm._fetch_command()
                    if isinstance(cmd, InputSubmission):
                        return cmd.data
                    elif isinstance(cmd, InlineCommand):
                        self._vm.handle_command(cmd)
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
    
    def execute_source(self, source, filename, mode):
        
        try:
            bytecode = self._compile_source(source, filename, mode)
            if hasattr(self, "_trace"):
                sys.settrace(self._trace)    
            if mode == "eval":
                value = eval(bytecode, __main__.__dict__)
                if value is not None:
                    builtins._ = value 
                self._vm.send_message("ToplevelResult", value_info=self._vm.export_value(value))
            else:
                assert mode == "exec"
                exec(bytecode, __main__.__dict__) # <Marker: remove this line from stacktrace>
                self._vm.send_message("ToplevelResult")
        except SyntaxError as e:
            self._vm.send_message("ToplevelResult", error="".join(traceback.format_exception_only(SyntaxError, e)))
        except ThonnyClientError as e:
            self._vm.send_message("ToplevelResult", error=str(e))
        except:
            # other unhandled exceptions (supposedly client program errors) are printed to stderr, as usual
            # for VM mainloop they are not exceptions
            e_type, e_value, e_traceback = sys.exc_info()
            self._print_user_exception(e_type, e_value, e_traceback)
            self._vm.send_message("ToplevelResult")
        finally:
            sys.settrace(None)
    
    def _print_user_exception(self, e_type, e_value, e_traceback):
        lines = traceback.format_exception(e_type, e_value, e_traceback)
        if "thonny" in lines[1]:
            "del lines[1]"
            #del lines[1]

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
    
    def __init__(self, vm, main_dir):
        self._vm = vm
        self._normcase_thonny_src_dir = os.path.normcase(main_dir) 
        self._instrumented_files = misc_utils.PathSet()
        self._interesting_files = misc_utils.PathSet() # only events happening in these files are reported
        self._current_command = None
        self._unhandled_exception = None
        self._install_marker_functions()
        self._custom_stack = []
    
    def execute_source(self, source, filename, mode):
        self._current_command = DebuggerCommand(command="step", state=None, focus=None, frame_id=None, exception=None)
        
        Executor.execute_source(self, source, filename, mode)
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
        

    def _compile_source(self, source, filename, mode):
        root = ast.parse(source, filename, mode)
        
        ast_utils.mark_text_ranges(root, source)
        self._tag_nodes(root)        
        self._insert_expression_markers(root)
        self._insert_statement_markers(root)
        self._instrumented_files.add(filename)
        
        return compile(root, filename, mode)
    
    def _may_step_in(self, code):
#        print ("MAYSET", code.co_filename if code else '---',
#               os.path.normcase(code.co_filename) not in self._instrumented_files)
#        for file in self._instrumented_files:
#            print("*", file)
            
        return not (
            code is None 
            or code.co_filename is None
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

        if event == "call":
            self._unhandled_exception = None # some code is running, therefore exception is not propagating anymore
            
            code_name = frame.f_code.co_name
            
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
                
                self._handle_progress_event(frame.f_back, event, frame.f_locals)
                self._try_interpret_as_again_event(frame.f_back, event, frame.f_locals)
                
                
            else:
                # Calls to proper functions.
                # Client doesn't care about these events,
                # it cares about "before_statement" events in the first statement of the body
                self._custom_stack.append(FancyTracer.CustomStackFrame(frame, "call"))
        
        elif event == "return":
            self._custom_stack.pop()
            if len(self._custom_stack) == 0:
                # We popped last frame, this means our program has ended.
                # There may be more events coming from upper (system) frames
                # but we're not interested in those
                sys.settrace(None)
                
        elif event == "exception":
            self._unhandled_exception = arg[1]

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
        focus = TextRange(*args["text_range"])
        
        self._custom_stack[-1].last_event = event
        self._custom_stack[-1].last_event_focus = focus
        self._custom_stack[-1].last_event_args = args
        
        # Select the correct method according to the command
        tester = getattr(self, "_cmd_" + self._current_command.command + "_completed")
             
        # If method decides we're in the right place to respond to the command ...
        if tester(frame, event, args, focus, self._current_command):
            
            self._vm.send_message("DebuggerProgress",
                command=self._current_command.command,
                stack=self._export_stack(),
                exception=self._vm.export_value(self._unhandled_exception, True),
                value=self._vm.export_value(args["value"]) 
                    if event == "after_expression"
                    else None
            )
            
            # Fetch next debugger command
            self._current_command = self._vm._fetch_command()
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
                again_args = {"text_range" : original_args.get("parent_range")}
                again_event = ("before_expression_again" 
                               if "child_of_expression" in node_tags
                               else "before_statement_again")
                
                self._handle_progress_event(frame, again_event, again_args)
                
    
    def _respond_to_inline_commands(self):
        while isinstance(self._current_command, InlineCommand): 
            self._vm.handle_command(self._current_command)
            self._current_command = self._vm._fetch_command()
            
    
    def _get_source(self, frame):
        try:
            if frame.f_code.co_name == "<module>":
                return None
                """
                # in case you need source for modules as well:
                # getsource doesn't give correct source for modules
                # findsource does
                lines, _ = inspect.findsource(frame.f_code)
                return "".join(lines)
                """
            else:
                return inspect.getsource(frame.f_code)
        except:
            return None

    
    def _cmd_exec_completed(self, frame, event, args, focus, cmd):
        """
        Identifies the moment when piece of code indicated by cmd.frame_id and cmd.focus
        has completed execution (either successfully or not).
        """
        
        assert cmd.state in ("before_expression", "before_expression_again",
                             "before_statement", "before_statement_again")
        
        
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
                return True
        
        else:
            # We're in another frame
            if self._frame_is_alive(cmd.frame_id):
                # We're in a successor frame, keep running
                return False
            else:
                # Original frame has completed, assumedly because of an exception
                # We're done
                return True
            

    
    def _cmd_step_completed(self, frame, event, args, focus, cmd):
        return True
    
    
    def _cmd_line_completed(self, frame, event, args, focus, cmd):
        return (event in ("before_statement", "before_expression") 
            and eqfn(frame.f_code.co_filename, cmd.target_filename)
            and focus.lineno == cmd.target_lineno
            and (focus != cmd.focus or id(frame) != cmd.frame_id))

    
    def _frame_is_alive(self, frame_id):
        for frame in self._custom_stack:
            if frame.id == frame_id:
                return True
        else:
            return False 
    
    def _export_stack(self):
        return [FrameInfo (
                id=id(custom_frame.system_frame),
                filename=custom_frame.system_frame.f_code.co_filename,
                module_name=custom_frame.system_frame.f_globals["__name__"],
                code_name=custom_frame.system_frame.f_code.co_name,
                locals=self._vm.export_variables(custom_frame.system_frame.f_locals),
                source=self._get_source(custom_frame.system_frame),
                firstlineno=custom_frame.system_frame.f_code.co_firstlineno,
                last_event=custom_frame.last_event,
                last_event_args=custom_frame.last_event_args,
                last_event_focus=custom_frame.last_event_focus,
            ) for custom_frame in self._custom_stack]

    
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
            
                
            # make sure every node has this field
            if not hasattr(node, "tags"):
                node.tags = set()
            
    
        
    def _insert_statement_markers(self, root):
        # find lists of statements and insert before/after markers for each statement
        for name, value in ast.iter_fields(root):
            if isinstance(value, ast.AST):
                self._insert_statement_markers(value)
            elif isinstance(value, list):
                if len(value) > 0:
                    new_list = []
                    for node in value:
                        if isinstance(node, _ast.stmt):
                            # add before marker
                            new_list.append(self._create_statement_marker(node, 
                                                                          BEFORE_STATEMENT_MARKER))
                        
                        # original statement
                        if isinstance(node, _ast.stmt):
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
                if (isinstance(node, _ast.expr)
                    and (not hasattr(node, "ctx") or isinstance(node.ctx, ast.Load))):

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
            self.system_frame = frame
            self.last_event = last_event
            self.focus = None
            self.call_functions = {} # will be updated with evaluated call functions
        
class ThonnyClientError(Exception):
    pass

    
def finfo(frame, msg, *args):
    if logger.isEnabledFor(logging.INFO):
        logger.info(_get_frame_prefix(frame) + msg, *args)
        

def fdebug(frame, msg, *args):
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(_get_frame_prefix(frame) + msg, *args)
    
    
def _get_frame_prefix(frame):
    return str(id(frame)) + " " + ">" * len(inspect.getouterframes(frame, 0)) + " "
    
    