from thonny.common import (
    InputSubmission,
    parse_message,
    ToplevelCommand,
    ToplevelResponse,
    InlineCommand,
    InlineResponse,
    UserError,
    serialize_message,
)
import sys
import logging
import traceback
import queue
from thonny.plugins.micropython.connection import ConnectionClosedException
from time import sleep
from textwrap import dedent
import ast

logger = logging.getLogger("thonny.micropython.backend")



class MicroPythonBackend:
    def __init__(self, connection):
        self._connection = connection
        self._cwd = None
        self._welcome_text = None

    def mainloop(self):
        try:
            while True:
                try:
                    cmd = self._fetch_command()
                    if isinstance(cmd, InputSubmission):
                        self._send_input(cmd.data)
                    else:
                        self.handle_command(cmd)
                except KeyboardInterrupt:
                    self._interrupt()
        except Exception:
            logger.exception("Crash in mainloop")
            traceback.print_exc()

    def _interrupt(self):
        try:
            self.idle = False
            self._connection.reset_output_buffer()
            self._connection.write(b"\x03")

            # Wait a bit to avoid the situation where part of the prompt will
            # be treated as output and whole prompt is not detected.
            # (Happened with Calliope)
            sleep(0.1)
        except ConnectionClosedException as e:
            self._handle_connection_closed(e)

    def _fetch_command(self):
        line = self._original_stdin.readline()
        if line == "":
            logger.info("Read stdin EOF")
            sys.exit()
        cmd = parse_message(line)
        return cmd

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

        elif isinstance(response, dict):
            if isinstance(cmd, ToplevelCommand):
                response = ToplevelResponse(command_name=cmd.name, **response)
            elif isinstance(cmd, InlineCommand):
                response = InlineResponse(cmd.name, **response)

        self.send_message(response)

    def _send_input(self, data: str) -> None:

        # TODO: what if there is a previous unused data waiting
        assert self._connection.outgoing_is_empty()

        assert data.endswith("\n")
        if not data.endswith("\r\n"):
            input_str = data[:-1] + "\r\n"

        data = input_str.encode("utf-8")

        try:
            self._connection.write(data)
            # Try to consume the echo

            try:
                echo = self._connection.read(len(data))
            except queue.Empty:
                # leave it.
                logging.warning("Timeout when reading echo")
                return

            if echo != data:
                # because of autoreload? timing problems? interruption?
                # Leave it.
                logging.warning("Unexpected echo. Expected %s, got %s" % (data, echo))
                self._connection.unread(echo)

        except ConnectionClosedException as e:
            self._handle_connection_closed(e)

    def send_message(self, msg):
        if "cwd" not in msg:
            msg["cwd"] = self._cwd

        self._original_stdout.write(serialize_message(msg) + "\n")
        self._original_stdout.flush()

    def _send_output(self, data, stream_name):
        if not data:
            return
        "TODO:"

    def _flush_output(self):
        "TODO: send current stdout and stderr to UI"

    def _handle_connection_closed(self, e):
        self._show_error_connect_again("\nLost connection to the device (%s)." % e)
        self.idle = False
        try:
            self._connection.close()
        except Exception:
            logging.exception("Closing serial")
        finally:
            self._connection = None

    def _execute(self, script):
        # assuming buffers are empty, but ...
        self._flush_output()

        # send command
        self._connection.write(script + "\x04")

        # fetch confirmation
        ok = self._connection.read(2)
        assert ok == b"OK", "Expected OK, got %r, followed by %r" % (
            ok,
            self._connection.read_all(),
        )

        terminator = "\x04>"
        output = self._connection.read_until(terminator)[: -len(terminator)]
        self.idle = True

        # return content of out, err
        return output.split("\x04")

    def _evaluate_to_repr(self, expr, prelude="", cleanup=""):
        # assuming expr really contains an expression
        # separator is for separating side-effect output and printed value
        separator = "[out-val-sep]"
        script = ""
        if prelude:
            script += prelude + "\n"
        script += "print(%r, %s, sep='', end='')" % (separator, expr)

        # assuming cleanup doesn't cause output
        if cleanup:
            script += "\n" + cleanup

        out, err = self._execute(script)
        if out.count(separator) == 1:
            # print did not succeed
            self._send_output(out, "stdout")
            raise ExecutionError(err)

        side_output, value_output = out.split(separator)
        self._send_output(side_output, "stdout")
        self._send_output(err, "stderr")
        return value_output

    def _evaluate(self, expr, prelude="", cleanup=""):
        return ast.literal_eval(self._evaluate_to_repr(expr), prelude, cleanup)

    def _supports_directories(self):
        if "micro:bit" in self._welcome_text.lower():
            return False
        else:
            return True

    def _cmd_cd(self, cmd):
        if len(cmd.args) == 1:
            if not self._supports_directories():
                raise UserError("This device doesn't have directories")

            path = cmd.args[0]
            self._execute("import os as __thonny_os; __module_os.chdir(%r)" % path)
            return {}
        else:
            raise UserError("%cd takes one parameter")

    def _cmd_Run(self, cmd):
        self._clear_environment()
        assert cmd.get("source")
        self._execute(cmd["source"])
        return {}

    def _cmd_execute_source(self, cmd):
        try:
            # Try to parse as expression
            ast.parse(cmd.source, mode="eval")
            # If it didn't fail then source is an expression
            value_repr = self._evaluate_to_repr(cmd.source)
            return {"repr": value_repr}
        except SyntaxError:
            # source is a statement (or invalid syntax)
            self._execute(cmd.source)
            return {}

    def _cmd_get_globals(self, cmd):
        if cmd.module_name == "__main__":
            globs = self._evaluate(
                "{name : repr(value) for (name, value) in globals().items() if not name.startswith('__')}"
            )
        else:
            globs = self._evaluate(
                "{name : repr(getattr(__mod_for_globs, name)) in dir(__mod_for_globs) if not name.startswith('__')}",
                prelude="import %s as __mod_for_globs",
            )
            return {"module_name": cmd.module_name, "globals": globs}

    def _cmd_get_dirs_child_data(self, cmd):
        if "micro:bit" in self._welcome_text.lower():
            data = self._get_dirs_child_data_microbit(cmd)
            dir_separator = ""
        else:
            data = self._get_dirs_child_data_generic(cmd)
            dir_separator = "/"

        return {"node_id": cmd["node_id"], "dir_separator": dir_separator, "data": data}

    def _get_dirs_child_data_microbit(self, cmd):
        """let it be here so micro:bit works with generic proxy as well"""

        assert cmd["paths"] == {""}, "Bad command: " + repr(cmd)
        file_sizes = self._evaluate(
            "{name : __temp_os.size(name) for name in __module_os.listdir()}"
        )
        return {"": file_sizes}

    def _get_dirs_child_data_generic(self, cmd):
        return self._evaluate(
            "__temp_result",
            prelude=dedent(
                """
                import os as __temp_os
                # Init all vars, so that they can be deleted
                # even if the loop makes no iterations
                __temp_result = {}
                __temp_path = None
                __temp_st = None 
                __temp_children = None
                __temp_name = None
                __temp_real_path = None
                __temp_full = None
                
                for __temp_path in %(paths)r:
                    __temp_real_path = __temp_path or '/'
                    __temp_children = {}
                    for __temp_name in __temp_os.listdir(__temp_real_path):
                        if __temp_name.startswith('.') or __temp_name == "System Volume Information":
                            continue
                        __temp_full = (__temp_real_path + '/' + __temp_name).replace("//", "/")
                        # print("processing", __temp_full)
                        __temp_st = __temp_os.stat(__temp_full)
                        if __temp_st[0] & 0o170000 == 0o040000:
                            # directory
                            __temp_children[__temp_name] = None
                        else:
                            __temp_children[__temp_name] = __temp_st[6]
                            
                    __temp_result[__temp_path] = __temp_children                            
            """
            )
            % {"paths": cmd.paths},
            cleanup=dedent(
                """
                del __temp_os
                del __temp_st
                del __temp_children
                del __temp_name
                del __temp_path
                del __temp_full
            """
            ),
        )


class ExecutionError(Exception):
    pass


def _report_internal_error():
    print("PROBLEM WITH THONNY'S BACK-END:\n", file=sys.stderr)
    traceback.print_exc()
