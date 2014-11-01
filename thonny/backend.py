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
from thonny.common import InputRequest, OutputEvent, DebuggerResponse, TextRange,\
    ToplevelResponse, parse_message, serialize_message, DebuggerCommand,\
    ValueInfo, ToplevelCommand, FrameInfo, InlineCommand, InlineResponse

BEFORE_SUITE_MARKER = "_thonny_hidden_before_suite"
BEFORE_STATEMENT_MARKER = "_thonny_hidden_before_stmt"
BEFORE_EXPRESSION_MARKER = "_thonny_hidden_before_expr"
AFTER_SUITE_MARKER = "_thonny_hidden_after_suite"
AFTER_STATEMENT_MARKER = "_thonny_hidden_after_stmt"
AFTER_EXPRESSION_MARKER = "_thonny_hidden_after_expr"

EXCEPTION_TRACEBACK_LIMIT = 100    

logger = logging.getLogger("thonny.backend")
logger.setLevel(logging.ERROR)
debug = logger.debug
info = logger.info

class VM:
    def __init__(self, src_dir):
        #print(sys.argv, file=sys.stderr)
        self.src_dir = src_dir
        self._heap = {} # TODO: weakref.WeakValueDictionary() ??
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
        
        try:
            handler = getattr(self, "_cmd_" + cmd.command)
        except AttributeError:
            self._send_response(ToplevelResponse(error="Unknown command: %" + cmd.command))
        else:
            try:
                response = handler(cmd)
                
                if response != None:
                
                    # TODO: ask explicitly for them with InlineRequest ??
                    # add state information
                    if hasattr(cmd, "globals_required") and cmd.globals_required:
                        response.globals = {cmd.globals_required : self.export_globals(cmd.globals_required)}
                        
                    if hasattr(cmd, "heap_required") and cmd.heap_required:
                        response.heap = self.export_heap()
                        
                    response.cwd = os.getcwd()
                    
                    self._send_response(response)
                
            except:
                #raise
                # TODO: 
                self._send_response(ToplevelResponse (
                    error="Thonny internal error: {0}".format(traceback.format_exc(EXCEPTION_TRACEBACK_LIMIT))
                ))
        
    
    def _cmd_pass(self, cmd):
        """
        Empty command, used for getting globals for new module
        or when user presses ENTER on shell prompt
        """
        return ToplevelResponse() # globals will be added by mainloop
        
    def _cmd_cd(self, cmd):
        try:
            os.chdir(cmd.path)
            return ToplevelResponse()
        except Exception as e:
            return ToplevelResponse(error=str(e))
    
    
    def _cmd_Reset(self, cmd):
        # nothing to do, because Reset always happens in fresh process
        return ToplevelResponse()
    
    def _cmd_Run(self, cmd):
        return self._execute_file(cmd, False)
    
    def _cmd_run(self, cmd):
        return self._execute_file(cmd, False)
    
    def _cmd_Debug(self, cmd):
        return self._execute_file(cmd, True)
    
    def _cmd_debug(self, cmd):
        return self._execute_file(cmd, True)
    
    def _cmd_python(self, cmd):
        # let's see if it's single expression or something more complex
        
        filename = "<pyshell#{0}>".format(cmd.id)
        
        try:
            root = ast.parse(cmd.cmd_line, filename=filename, mode="exec")
        except SyntaxError as e:
            return ToplevelResponse(error="".join(traceback.format_exception_only(SyntaxError, e)))
            
        assert isinstance(root, ast.Module)
            
        if len(root.body) == 1 and isinstance(root.body[0], ast.Expr):
            mode = "eval"
        else:
            mode = "exec"
        
        return self._execute_source(cmd.cmd_line, filename, mode,
                   hasattr(cmd, "debug_mode") and cmd.debug_mode)
    
    def _cmd_tkupdate(self, cmd):
        tkinter = sys.modules.get("tkinter")
        if (tkinter == None or tkinter._default_root == None):
            return
        else:
            # advance the event loop
            # http://bugs.python.org/issue989712
            # http://bugs.python.org/file6090/run.py.diff
            try:
                while (tkinter._default_root != None 
                       and tkinter._default_root.dooneevent(tkinter._tkinter.DONT_WAIT)):
                    pass 
            except:
                pass
    
    
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
            
            return InlineResponse(object_info=info)
        else:
            return InlineResponse(object_info={'id' : cmd.object_id}, not_found=True)
    
    def _add_file_handler_info(self, value, info):
        try:
            assert isinstance(value.name, str)
            assert value.mode in ("r", "rt", "tr", "br", "rb")
            assert value.errors in ("strict", None)
            assert value.newlines == None or value.tell() > 0
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
        
    def _cmd_get_globals(self, cmd):
        pass
    
    def _cmd_get_locals(self, cmd):
        pass
    
    def _cmd_get_heap(self, cmd):
        pass
    
    def _execute_file(self, cmd, debug_mode):
        source, _ = misc_utils.read_python_file(cmd.filename)
        
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        code_filename = os.path.abspath(cmd.filename)
        return self._execute_source(source, code_filename, "exec", debug_mode)
    
    def _execute_source(self, source, filename, execution_mode, debug_mode):
        if debug_mode:
            self._current_executor = FancyTracer(self, self.src_dir)
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
            if fp != None:
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
        return parse_message(line)

    def _send_response(self, msg):
        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()
        
    def export_value(self, value, skip_None=False):
        if value == None and skip_None:
            return None
        
        self._heap[id(value)] = value
        try:
            type_name = value.__class__.__name__
        except:
            type_name = type(value).__name__ 
            
        result = ValueInfo(id=id(value),
                         short_repr=repr(value), # TODO:
                         type_name=type_name)
        
        return result
    
    def export_globals(self, module_name):
        if not module_name in sys.modules:
            raise ThonnyClientError("Module '{0}' is not loaded".format(module_name))
        return self.export_variables(sys.modules[module_name].__dict__)
    
    def export_heap(self):
        result = {}
        for key in self._heap:
            result[key] = self.export_value(self._heap[key])
            
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
                    self._vm._send_response(OutputEvent(stream_name=self._stream_name, data=data))
            finally:
                self._vm._exit_io_function()
        
        def writelines(self, lines):
            try:
                self._vm._enter_io_function()
                self.write(''.join(lines))
            finally:
                self._vm._exit_io_function()
    
    class FakeInputStream(FakeStream):
        def read(self, limit=-1):
            try:
                self._vm._enter_io_function()
                self._vm._send_response(InputRequest(method="read", limit=limit))
                # TODO: maybe it's better to read as a command-package?
                return self._target_stream.read(limit)
            finally:
                self._vm._exit_io_function()
        
        def readline(self, limit=-1):
            try:
                self._vm._enter_io_function()
                self._vm._send_response(InputRequest(method="readline", limit=limit))
                return self._target_stream.readline(limit)
            finally:
                self._vm._exit_io_function()
        
        def readlines(self, limit=-1):
            try:
                self._vm._enter_io_function()
                self._vm._send_response(InputRequest(method="readlines", limit=limit))
                return self._target_stream.readlines(limit)
            finally:
                self._vm._exit_io_function()
            
    


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
                if value != None:
                    builtins._ = value 
                return ToplevelResponse(value_info=self._vm.export_value(value))
            else:
                assert mode == "exec"
                exec(bytecode, __main__.__dict__)
                return ToplevelResponse()
        except SyntaxError as e:
            return ToplevelResponse(error="".join(traceback.format_exception_only(SyntaxError, e)))
        except ThonnyClientError as e:
            return ToplevelResponse(error=str(e))
        except:
            # other unhandled exceptions (supposedly client program errors) are printed to stderr, as usual
            # for VM mainloop they are not exceptions
            traceback.print_exc(EXCEPTION_TRACEBACK_LIMIT)
            return ToplevelResponse()
        finally:
            sys.settrace(None)

    def _compile_source(self, source, filename, mode):
        return compile(source, filename, mode)


class FancyTracer(Executor):
    """
    ...
    
    * For normal operation _cmd_exec and _cmd_next should be interleaved TODO: not really
    * NB! after_expression / after_statement does not mean successful completion 
    
    ...
    """
    
    def __init__(self, vm, src_dir):
        self._vm = vm
        self._normcase_thonny_src_dir = os.path.normcase(src_dir) 
        self._instrumented_files = misc_utils.PathSet()
        self._interesting_files = misc_utils.PathSet() # only events happening in these files are reported
        self._current_command = None
        self._thread_exception = None
        self._install_marker_functions()
        self._custom_stack = []
        self._expand_call_functions = False # TODO: take it from configuration
    
    def _set_current_command(self, cmd):
        self._current_command = cmd
        #info("TRACER command: %s", cmd)
    
    def execute_source(self, source, filename, mode):
        self._set_current_command(DebuggerCommand(command="step", state=None, focus=None, frame_id=None, exception=None))
        
        response = Executor.execute_source(self, source, filename, mode)
        #assert len(self._custom_stack) == 0
        return response
        
    def _install_marker_functions(self):
        # Make dummy marker functions universally available by putting them
        # into builtin scope        
        self.marker_function_names = {
            BEFORE_SUITE_MARKER,
            AFTER_SUITE_MARKER, 
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
            code == None 
            or code.co_filename == None
            or "importlib._bootstrap" in code.co_filename
            or os.path.normcase(code.co_filename) not in self._instrumented_files 
                and code.co_name not in self.marker_function_names
            or os.path.normcase(code.co_filename).startswith(self._normcase_thonny_src_dir)
                and code.co_name not in self.marker_function_names
            or self._vm.is_doing_io() 
        )
        
    
    def _trace(self, frame, event, arg):
        """
        1) Filters and transforms system trace events
        2) Maintains a customized view of stack
        """
        if not self._may_step_in(frame.f_code):
            return

        #fdebug(frame, "TRACE %s %s", event, 
        #        (frame.f_code.co_filename, frame.f_lineno, frame.f_code.co_name, frame.f_locals))
        
        args = {}
        focus = None
        # Reinterpret the event and update our customized stack representation. 
        code_name = frame.f_code.co_name
        
        
        # disguise marker calls as custom events in caller frame
        if code_name in self.marker_function_names:
            args.update(frame.f_locals)
            focus = TextRange(*args["text_range"])
            del args["text_range"]
            frame = frame.f_back
            
            assert event == "call"
            if code_name == BEFORE_STATEMENT_MARKER:
                event = "before_statement"
            elif code_name == AFTER_STATEMENT_MARKER:
                event = "after_statement"
            elif code_name == BEFORE_SUITE_MARKER:
                event = "before_suite"
            elif code_name == AFTER_SUITE_MARKER:
                event = "after_suite"
            elif code_name == BEFORE_EXPRESSION_MARKER:
                event = "before_expression"
            else:
                assert code_name == AFTER_EXPRESSION_MARKER
                event = "after_expression"
                
                # remember each evaluated call function, zoom command will need them later
                node_tags = args.get("node_tags")
                if node_tags and "call_function" in node_tags:
                    parent_range = TextRange(*args.get("parent_range"))
                    self._custom_stack[-1].call_functions[parent_range] = args["value"] 
            
            
        elif event == "call":
            self._custom_stack.append(FancyTracer.CustomStackFrame(frame, "call"))
                
        elif event == "return":
            args["return_value"] = arg
        
        elif event == "line":
            if frame.f_code.co_filename in self._instrumented_files:
                # don't need line events in instrumented files
                # (but keep stepping in this file, to get "return" and "exception" events
                return self._trace
                
        else:
            assert event == "exception"
            self._thread_exception = arg[1]
            args["exception"] = arg[1]
            
        
        self._custom_stack[-1].last_event = event
        self._custom_stack[-1].focus = focus
        
        try:
            result = self._custom_trace(frame, event, args, focus)
            
            # some after_* events can be interpreted also as 
            # "before_*_again" events (eg. when last argument of a call was 
            # evaluated, then we are just before executing the final stage of the call)
            before_again = self._interpret_as_before_again_event(event, focus, args)
            if before_again != None:
                event, focus, args = before_again
                # store the new state in stack
                self._custom_stack[-1].last_event = event
                self._custom_stack[-1].focus = focus
                # call tracer again with new event and focus
                result = self._custom_trace(frame, event, args, focus)
            
            if result and event not in ("before_statement", "before_statement_again", "after_statement",
                                        "before_suite", "after_suite", 
                                        "before_expression", "before_expression_again", "after_expression"):
                return self._trace
            else:
                return None
            
        finally:
            if event == "return":
                self._custom_stack.pop()
                if len(self._custom_stack) == 0:
                    # We popped last frame, this means our program has ended.
                    # There may be more events coming from upper (system) frames
                    # but we're not interested in those
                    sys.settrace(None)
                    return None
            
            if event == "before_statement" and "first_except_stmt" in args["node_tags"]:
                # We just arrived to an exception handler.
                # this clears current active exception
                self._active_exception = None
                    
        
    
    def _custom_trace(self, frame, event, args, focus):
        """
        Tries to respond to current client's command in this state. 
        If it can't, then it returns, program resumes
        and _standard_trace will call it again in another state.  
        
        Returns True if it wants to continue searching in this frame
        """
        
        if event.startswith("before") or event.startswith("after"):
            assert focus != None 
        
        fdebug(frame, "CUSTR %s %s", event, focus)
        if event == "exception":
            self._current_command.exception = args["exception"]
            # we don't stop at exceptions, just make a note that an exception
            # occured during handling current command.
            return True
        
        else:
            # We have loop because it's possible respond to several denied zoom-ins, 
            # or in-debug eval/exec requests, in one conceptual program state
            while True:
                # Select the correct method according to the command
                handler = getattr(self, "_cmd_" + self._current_command.command)
                response = handler(frame, event, args, focus, self._current_command)
                     
                # If method decides we're in the right place to respond to the command ...
                if isinstance(response, DebuggerResponse):
                    # ... attach some more info to the response ...
                    response.setdefault (
                        frame_id=id(frame),
                        filename=frame.f_code.co_filename,
                        module_name=frame.f_globals["__name__"],
                        code_name=frame.f_code.co_name,
                        focus=focus,
                        state=event,
                        command_exception=self._vm.export_value(self._current_command.exception, True),
                        thread_exception=self._vm.export_value(self._thread_exception, True),
                        stack=self._export_stack(),
                        firstlineno=frame.f_code.co_firstlineno,
                        source=self._get_source(frame),
                        globals={
                            frame.f_globals["__name__"] : self._vm.export_variables(frame.f_globals)
                        },
                        cwd=os.getcwd()
                    )
                    
                    if (hasattr(self._current_command, "heap_required")
                        and self._current_command.heap_required):
                        response.heap = self._vm.export_heap()
                    
                    #assert response.focus != None
                    # ... and send it to the client
                    self._vm._send_response(response)
                    
                    # Read next command (this is a blocking task)
                    cmd = self._vm._fetch_command()
                    
                    # memory requests should be handled by VM
                    while isinstance(cmd, InlineCommand): # or ToplevelCommand???
                        self._vm.handle_command(cmd)
                        cmd = self._vm._fetch_command()
                    
                    assert isinstance(cmd, DebuggerCommand)
                    self._set_current_command(cmd) 
                    fdebug(frame, "COMMAND %s, current event: %s", self._current_command, event)
                    self._current_command.exception = None # start with no blame
                    # ... and continue with the loop
                    
                    
                else:
                    # ... we can't respond to this command at this state
                    
                    # little post-processing
                    if event == "before_statement" and "first_except_stmt" in args["node_tags"]:
                        # We just arrived to an exception handler.
                        # As command handler didn't want to stop here,
                        # we clear the guilt from current command
                        self._current_command.exception = None
                    
                    # resume program
                    if response == "skip": 
                        # nothing to find in this frame
                        return False
                    else: 
                        # keep looking, continue stepping in this frame
                        return True
        
    
    def _interpret_as_before_again_event(self, original_event, original_focus, original_args):
        if original_event == "after_expression":
            node_tags = original_args.get("node_tags")
            value = original_args.get("value")
            
            #self._debug("IAE", node_tags, value)
            if (node_tags != None 
                and ("last_child" in node_tags
                     or "or_arg" in node_tags and value
                     or "and_arg" in node_tags and not value)
                and ("child_of_expression_statement" not in node_tags) # don't want to go to expression statement again
                ):
                
                # next step will be finalizing evaluation of parent of current expr
                # so let's say we're before that parent expression
                parent_range = TextRange(*original_args.get("parent_range"))
                # update the state and focus
                if "child_of_expression" in node_tags: 
                    return "before_expression_again", parent_range, {}
                else:
                    #debug("NOOOOOT" + str(node_tags))
                    return "before_statement_again", parent_range, {}
            else:
                return None
            
        else:
            return None
    
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

         
    
    def _cmd_exec(self, frame, event, args, focus, cmd):
        """
        TODO: needs reworking, make it more similar to step, maybe refactor common code 
        
        Identifies the moment when piece of code indicated by cmd.frame_id and cmd.focus
        has completed execution (either successfully or not).
        
        Can be called only in one of the before_* states.
        Next state will be always one of after_* states.
        """
        assert cmd.state in ("before_expression", "before_expression_again",
                             "before_statement", "before_statement_again")
        
        fdebug(frame, "_cmd_exec %s %s %s", event, focus, cmd)
        if id(frame) != cmd.frame_id:
            fdebug(frame, "wrong frame")
            # We're in a wrong frame,
            # the answer must be in the frame where command was issued
            return "skip" 
        
        elif focus.is_smaller_in(cmd.focus):
            fdebug(frame, "smaller focus %s vs. %s", focus, cmd.focus)
            # we're still in given code range
            return None 
        
        elif focus == cmd.focus:
            fdebug(frame, "same focus")
            if "before" in event:
                # we're just starting
                return None
            
            elif (cmd.state in ("before_expression", "before_expression_again")
                  and event == "after_expression"):
                fdebug(frame, "sending value")
                # normal expression completion
                return DebuggerResponse(value=self._vm.export_value(args["value"]),
                                        tags=args.get("node_tags", ""))
            
            elif (cmd.state in ("before_statement", "before_statement_again")
                  and event == "after_statement"):
                # normal statement completion
                return DebuggerResponse(tags=args.get("node_tags", ""))
            
            elif (cmd.state in ("before_statement", "before_statement_again")
                  and event == "after_expression"):
                # Same code range can contain expression statement and expression.
                # Here we need to run just a bit more
                return None
            
            else:
                # shouldn't be here
                raise AssertionError("Unexpected state in responding to " + str(cmd))
                
        else:
            # current focus must be outside of starting focus
            assert focus == None or focus.not_smaller_in(cmd.focus)
            
            # Anyway, the execution of the focus has completed (maybe unsuccessfully).
            # In response hide the fact that current focus and/or state may have been moved away 
            # from given range.
            # TODO: do I need to hide this? Maybe I just forget about this statement/expression?
            # TODO: what about exception?
            if cmd.state == "before_expression":
                return DebuggerResponse(state="after_expression", 
                                        focus=cmd.focus,
                                        tags="") 
            else:
                return DebuggerResponse(state="after_statement",
                                        focus=cmd.focus,
                                        tags="")
            

    """
    def _cmd_next(self, frame, event, args, focus, cmd):
        Finds the next interesting moment/place after cmd.focus/cmd.frame_id/cmd.state
        That place can be inside cmd.focus.
        
        Normally it's called 
            1) after a successful exec in order focus next statement/subexpression.
               In that case the new state will be a before_* state.
            2) while being before a compound stmt/expr in order to zoom in. 
        
        If called after completing a return statement, it should go to after_expression 
        state of calling expression.
        
        If it's called with cmd state different from actual runtime state
        (eg. cmd.state == after_statement, when actually the statement 
        failed and we're in except handler), then we may be already in the "next" place.
        #fdebug(frame, "_cmd_next %s", (event, args, focus, cmd))
        
        if (focus == cmd.focus and id(frame) == cmd.frame_id and event == cmd.state
            or not event.startswith("before") and not event.startswith("after")):
            return None
        else:
            return DebuggerResponse()
    """

    """
    def _cmd_goto_before(self, frame, event, args, focus, cmd):
        if event in ("before_expression", "before_expression_again",
                     "before_statement", "before_statement_again"):
            return DebuggerResponse()
        elif event == "line":
            raise NotImplementedError
            "TODO: compute proper statement focus. NB! only full lines"
        else:
            return None
        
    def _cmd_goto_after(self, frame, event, args, focus, cmd):
        if event == "after_expression":
            return DebuggerResponse(value=self._vm.export_value(args["value"]))
        elif event == "line":
            raise NotImplementedError
            "TODO: compute proper statement focus. NB! only full lines"
        else:
            return None
    """
        
    
    """
    def _cmd_zoom(self, frame, event, args, focus, cmd):
        fdebug(frame, "_cmd_zoom: %s", (cmd.frame_id, event, cmd.state, focus, cmd.focus))
        if (id(frame) == cmd.frame_id
                and focus.is_smaller_in(cmd.focus) 
                # NB! ast.Expr statement and its child expression can have same code range
                and (focus != cmd.focus or event != cmd.state)):
            
            # successful zoom in the same frame
            self._debug("successful zoom in the same frame", focus != cmd.focus)
            return DebuggerResponse(success=True)
        
        elif id(frame) != cmd.frame_id:
            if event == "before_statement":
                # successful zoom to new frame
                self._debug("successful zoom to new frame")
                response = DebuggerResponse(success=True)
                if hasattr(self._current_command, "function"):
                    response.function = self._vm.export_value(self._current_command.function)
                return response 
            else:
                # TODO: it can be line event in non-instrumented module
                # nothing to find there
                self._debug("zoom almost there (call of new frame)", event)
                # almost there
                return None
        
        elif focus == cmd.focus and event in ("before_expression", "before_statement"):
            if "node_tags" in args and "has_children" in args["node_tags"]:
                self._debug("zoom almost there (same frame)", event)
                return None
            else:
                #self._debug("_cmd_zoom:node_tags", args.get("node_tags"))
                self._debug("failed zoom (no children)")
                return DebuggerResponse(success=False)
            
        # TODO: zoom in to import ???
        elif focus == cmd.focus and event in ("before_expression_again"):
            # we can focus here if it's a call and there is source available
            fun = self._custom_stack[-1].call_functions.get(focus)
            if fun != None and hasattr(fun, "__code__") and self._may_step_in(fun.__code__):
                try:
                    inspect.getsource(fun)
                    self._current_command.function = fun 
                    self._debug("zoom almost there (still in old frame)", event, fun)
                    return None
                except:
                    # can't zoom here
                    self._debug("failed zoom (no source)")
                    return DebuggerResponse(success=False)
            else:
                self._debug("failed zoom (not fun)")
                return DebuggerResponse(success=False)
            
        else:
            # can't zoom here
            self._debug("failed zoom (other reasons)")
            return DebuggerResponse(success=False)
    """
        
    
    def _cmd_step(self, frame, event, args, focus, cmd):
        """
        Command step stops at all interesting places
        """
        if (focus == cmd.focus and id(frame) == cmd.frame_id and event == cmd.state
            or not event.startswith("before") and not event.startswith("after")):
            # We're still in the same situation where the command was issued,
            # so keep running!
            return None
        
        elif event == 'after_expression':
            return DebuggerResponse(value=self._vm.export_value(args["value"]),
                                    tags=args.get("node_tags", ""))
        
        elif event in ('before_statement', 'before_expression',
                       'before_statement_again', 'before_expression_again',
                       'after_statement', 'after_expression'):
            return DebuggerResponse(tags=args.get("node_tags", ""))
        
        elif event in ('before_suite', 'after_suite'):
            return DebuggerResponse(stmt_ranges=list(map(lambda arg: TextRange(*arg), args['stmt_ranges'])))
        
        else:
            # We're not interested in other events when stepping
            return None
            
            
    
    def _cmd_line(self, frame, event, args, focus, cmd):
        if (event in ("before_statement", "before_expression") 
            and eqfn(frame.f_code.co_filename, cmd.target_filename)
            and focus.lineno == cmd.target_lineno
            and (focus != cmd.focus or id(frame) != cmd.frame_id)):
            return DebuggerResponse()
        else:
            return None

    """
    def _cmd_get_globals(self, frame, event, args, focus, cmd):
        return DebuggerResponse(globals={
            cmd.module_name : self._vm.export_globals(cmd.module_name)
        })
    """
            
    
    def _export_stack(self):
        return [FrameInfo (
                id=id(cframe.system_frame),
                filename=cframe.system_frame.f_code.co_filename,
                module_name=cframe.system_frame.f_globals["__name__"],
                code_name=cframe.system_frame.f_code.co_name,
                locals=self._vm.export_variables(cframe.system_frame.f_locals),
                focus=cframe.focus
            ) for cframe in self._custom_stack]

    
    def _thonny_hidden_before_suite(self, text_range, stmt_ranges):
        """
        The code to be debugged will be instrumented with this function
        inserted before each statement suite. 
        """
        return None
    
    def _thonny_hidden_after_suite(self, text_range, stmt_ranges):
        """
        The code to be debugged will be instrumented with this function
        inserted before each statement suite. 
        """
        return None
    
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
            if last_child != None and last_child:
                add_tag(node, "has_children")
                
                if isinstance(last_child, ast.AST):
                    last_child.parent_node = node
                    add_tag(last_child, "last_child")
                    if isinstance(node, _ast.expr):
                        add_tag(last_child, "child_of_expression")
                    else:
                        add_tag(last_child, "child_of_statement")
                    
                    if isinstance(node, ast.Expr):
                        add_tag(last_child, "child_of_expression_statement")
                        
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
            
            # TODO: does assert evaluate msg when test == True ??
            
            if (hasattr(ast, "Try") and isinstance(node, ast.Try) # Python 3 
                or hasattr(ast, "TryExcept") and isinstance(node, ast.TryExcept)): # Python 2
                for handler in node.handlers:
                    add_tag(handler, "first_except_stmt")
            
                
            # make sure every node has this field
            if not hasattr(node, "tags"):
                node.tags = set()
            
    
        
    def _insert_statement_markers(self, root):
        # find lists of statements and insert before/after markers for each statement
        for name, value in ast.iter_fields(root):
            if isinstance(value, ast.AST):
                self._insert_statement_markers(value)
            elif isinstance(value, list):
                new_list = []
                if len(value) > 0:
                    # create before suite
                    if isinstance(value[0], _ast.stmt):
                        new_list.append(self._create_suite_marker(value, BEFORE_SUITE_MARKER))
                
                    # create suite body
                    for node in value:
                        if isinstance(node, _ast.stmt):
                            # add before marker
                            new_list.append(self._create_statement_marker(node, 
                                                                          BEFORE_STATEMENT_MARKER))
                        
                        # original statement
                        self._insert_statement_markers(node)
                        new_list.append(node)
                        
                        if isinstance(node, _ast.stmt):
                            # add after marker
                            new_list.append(self._create_statement_marker(node,
                                                                          AFTER_STATEMENT_MARKER))
                    # create after suite
                    if isinstance(value[0], _ast.stmt):
                        new_list.append(self._create_suite_marker(value, AFTER_SUITE_MARKER))
                    
                setattr(root, name, new_list)
    
    def _create_suite_marker(self, stmt_nodes, function_name):
        stmt_ranges = ast.Tuple(elts=list(map(self._create_location_literal, stmt_nodes)), 
             ctx=ast.Load())
        
        # create a compound range
        nums = []
        for value in (stmt_nodes[0].lineno, stmt_nodes[0].col_offset, 
                      stmt_nodes[-1].end_lineno, stmt_nodes[-1].end_col_offset):
            nums.append(ast.Num(n=value))
        text_range = ast.Tuple(elts=nums, ctx=ast.Load())
        
        stmt = ast.Expr(value=ast.Call (
            func=ast.Name(id=function_name, ctx=ast.Load()),
            args=[text_range, stmt_ranges],
            keywords=[]
        ))
        ast.fix_missing_locations(stmt)
        return stmt

    
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

#                     if "call_function" in node.tags and not tracer._expand_call_functions:
#                         # TODO: test with no-argument calls
#                         
#                         for child in ast.iter_child_nodes(node):
#                             ast.NodeTransformer.generic_visit(self, child)
#                             
#                         return node
#                     else:
                        
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
        if node == None:
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
    
    