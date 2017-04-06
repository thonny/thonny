# -*- coding: utf-8 -*-

import sys 

from thonny.common import\
    parse_message, serialize_message,\
    ValueInfo, ToplevelCommand, InlineCommand, InputSubmission

DEBUG = True    

class VM:
    def __init__(self):
        self._install_fake_streams()
        
        # clean __main__ global scope
        globs = globals()
        for key in globs:
            if not key.startswith("__"):
                del globs[key]
        
        # only special variable on microbit is "__name__"
        globs["__name__"] = "__main__" 
        
        # TODO: make it leaner
        self.send_message("Ready",
                          main_dir="", # TODO:
                          original_argv=[],
                          original_path=[],
                          argv=[],
                          path=[],
                          python_version="micropython" + ".".join(list(map(str, sys.version_info))),
                          python_executable=None,
                          cwd="")
        
    def mainloop(self):
        while True: 
            cmd = self._fetch_command()
            self.handle_command(cmd)
            
            
    def handle_command(self, cmd):
        assert isinstance(cmd, ToplevelCommand) or isinstance(cmd, InlineCommand)
        
        error_response_type = "ToplevelResult" if isinstance(cmd, ToplevelCommand) else "InlineError"
        try:
            handler = getattr(self, "_cmd_" + cmd.command)
        except AttributeError:
            self.send_message(error_response_type, error="Unknown command: " + cmd.command)
        else:
            try:
                handler(cmd)
            except:
                # TODO:
                self.send_message(error_response_type,
                    error="Thonny internal error"
                )
        
    
    def _cmd_cd(self, cmd):
        "ignore this command"
    
    def _cmd_Reset(self, cmd):
        # nothing to do, because Reset always happens in fresh process
        self.send_message("ToplevelResult")
    
    def _cmd_Run(self, cmd):
        self._execute_file_and_send_result(cmd, False)
    
    def _cmd_run(self, cmd):
        self._execute_file_and_send_result(cmd, False)
    
    def _cmd_Debug(self, cmd):
        "For now Debug works same as Run"
        self._execute_file_and_send_result(cmd, False)
    
    def _cmd_debug(self, cmd):
        "For now debug works same as run"
        self._execute_file_and_send_result(cmd, False)
    
    def _cmd_execute_source(self, cmd):
        if isinstance(cmd, ToplevelCommand):
            result_type = "ToplevelResult"
        elif isinstance(cmd, InlineCommand):
            result_type = "InlineResult"
        else:
            raise Exception("Unsuitable command type for execute_source")
        
        result_attributes = self._execute_source(cmd.source)
        self.send_message(result_type, **result_attributes)

    def _cmd_get_globals(self, cmd):
        if cmd.module_name != "__main__":
            raise ThonnyClientError("Only globals from __main__ are supported")
        
        self.send_message("Globals", module_name=cmd.module_name,
                              globals=self.export_variables(globals()))
    
    def _cmd_get_locals(self, cmd):
        "ignore"
    
    def _cmd_get_heap(self, cmd):
        "ignore (can't waste memory for heap)"
    
    def _cmd_shell_autocomplete(self, cmd):
        """
        TODO: try to find completion for cmd.source
        according to information in globals()
        
        Format:
        completions = [{"name" : full_name, "complete" : missing_part_of_the name},
                       {"name" : full_name, "complete" : missing_part_of_the name},
                       ...]
        """
        
        error = None 
        completions = []
        
        self.send_message("ShellCompletions", 
            source=cmd.source,
            completions=completions,
            error=error
        )
        
    
    def _cmd_editor_autocomplete(self, cmd):
        # This command should never reach the backend
        # BackendProxy should take care of this
        self.send_message("EditorCompletions", 
                          source=cmd.source,
                          row=cmd.row,
                          column=cmd.column,
                          filename=cmd.filename,
                          completions=[],
                          error="Editor completions not supported by the backend")
        
    
    def _cmd_get_object_info(self, cmd):
        "ignore"
    
    def _execute_file_and_send_result(self, cmd, debug_mode):
        result_attributes = self._execute_file(cmd, debug_mode)
        self.send_message("ToplevelResult", **result_attributes)
    
    def _execute_file(self, cmd, debug_mode):
        assert hasattr(cmd, "source")
        source = cmd.source
        
        # args are accepted only in Run and Debug,
        # and were stored in sys.argv already in VM.__init__
        return self._execute_source(source)
    
    def _execute_source(self, source):
        try:
            value = eval(source)
            return {"value_info" : self.export_value(value)}
        except SyntaxError:
            # Try exec
            try:
                exec(source)
            except SyntaxError as e:
                return {"error" : "Syntax error"}
            except ThonnyClientError as e:
                return {"error" : str(e)}
            except:
                # other unhandled exceptions (supposedly client program errors) are printed to stderr, as usual
                # for VM mainloop they are not exceptions
                # TODO: return exc
                return {"context_info" : "other unhandled exception"}
            
        
    def _install_fake_streams(self):
        global print, input
        
        self._original_print = print
        self._original_input = input
        
        # TODO: patch user-facing functions
        
    def _fetch_command(self):
        line = self._original_input()
        cmd = parse_message(line)
        return cmd

    def send_message(self, message_type, **kwargs):
        kwargs["message_type"] = message_type
        if "" not in kwargs:
            kwargs["cwd"] = ""
        
        self._original_print(serialize_message(kwargs) + "\n")
        
    def export_value(self, value, skip_None=False):
        if value is None and skip_None:
            return None
        
        # <class 'X'>
        type_name = str(type(value))[8:-2] 
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
    

class ThonnyClientError(Exception):
    pass