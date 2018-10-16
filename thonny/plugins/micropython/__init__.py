import ast
import logging
import io
import os
import platform
import queue
import re
import subprocess
import sys
import textwrap
import threading
import time
import tokenize
import traceback
import webbrowser
from pathlib import Path
from queue import Queue
from textwrap import dedent
from time import sleep
from tkinter import ttk
from thonny.ui_utils import askopenfilename
from typing import Optional

import jedi
import serial.tools.list_ports
from serial import SerialException

from thonny import common, get_runner, get_shell, get_workbench
from thonny.common import (
    BackendEvent,
    InlineResponse,
    MessageFromBackend,
    ToplevelCommand,
    ToplevelResponse,
)
from thonny.config_ui import ConfigurationPage
from thonny.misc_utils import find_volumes_by_name
from thonny.plugins.backend_config_page import BackendDetailsConfigPage
from thonny.running import BackendProxy
from thonny.ui_utils import SubprocessDialog, create_string_var, show_dialog

EOT = b"\x04"
NORMAL_PROMPT = b">>> "
# first prompt when switching to raw mode (or after soft reboot in raw mode)
FIRST_RAW_PROMPT = b"raw REPL; CTRL-B to exit\r\n>"
RAW_PROMPT = b">"
TIMEOUT = 0.1
EOT_WITH_RAW_PROMPT = "\x04>"
THONNY_START = "<ForThonny>"
THONNY_END = "</ForThonny>"
THONNY_MSG_START = b"\x02"
NEWLINE = "\n"

# TODO: Current code has some preparations in place to make automatic initial interrupt optional
# It's not so easy, though (initial interrupt also fetches some required info etc)
_AUTOMATIC_INTERRUPT = True


class MicroPythonProxy(BackendProxy):
    def __init__(self, clean):
        super().__init__(clean)
        self._non_serial_msg_queue = Queue()
        self._last_toplevel_command = None
        self._has_been_idle = False
        self._ctrl_c_notice_has_been_removed = False

        self._baudrate = 115200

        self._reading_cancelled = False
        self._welcome_text = None
        self._discarded_bytes = bytearray()
        self._builtins_info = self._get_builtins_info()
        # TODO: provide default builtins for script completion
        self._builtin_modules = []

        self.__idle = False

        self._serial = self._create_serial()

        if self._serial is not None and (clean or _AUTOMATIC_INTERRUPT):
            try:
                self._interrupt_to_prompt(clean)
                self._builtin_modules = self._fetch_builtin_modules()
            except TimeoutError:
                read_bytes = bytes(self._discarded_bytes + self._serial._read_buffer)
                self._show_error_connect_again(
                    "Could not connect to REPL.\n"
                    + "Make sure your device has suitable firmware and is not in bootloader mode!\n"
                    + "Bytes read: "
                    + str(read_bytes)
                    + "\nDisconnecting."
                )
                self.disconnect()
            except:
                self.disconnect()
                raise

        self._start_time = time.time()

    def send_command(self, cmd):
        if isinstance(cmd, ToplevelCommand):
            self._last_toplevel_command = cmd

        if cmd.name in ["editor_autocomplete", "cd", "dump_api_info", "lsdevice"]:
            # Works even without connection to the board
            return super().send_command(cmd)
        elif self._serial is None:
            return "discard"
        elif self.idle:
            try:
                if not self._serial.buffers_are_empty():
                    discarded = self._serial.read_all()
                    self._send_error_to_shell(
                        "Warning: when issuing %r,\nincoming was not emtpy: %r"
                        % (cmd, discarded)
                    )
                return super().send_command(cmd)
            except SerialException as e:
                self._handle_serial_exception(e)
                return "discard"
        else:
            return "postpone"

    def send_program_input(self, data: str) -> None:

        # TODO: what if there is a previous unused data waiting
        assert self._serial.outgoing_is_empty()

        assert data.endswith("\n")
        if not data.endswith("\r\n"):
            input_str = data[:-1] + "\r\n"

        data = input_str.encode("utf-8")

        try:
            self._serial.write(data)
            # Try to consume the echo

            try:
                echo = self._serial.read(len(data))
            except queue.Empty:
                # leave it.
                logging.warning("Timeout when reading echo")
                return

            if echo != data:
                # because of autoreload? timing problems? interruption?
                # Leave it.
                logging.warning("Unexpected echo. Expected %s, got %s" % (data, echo))
                self._serial.unread(echo)

        except SerialException as e:
            self._handle_serial_exception(e)

    def fetch_next_message(self):
        if not self._non_serial_msg_queue.empty():
            msg = self._non_serial_msg_queue.get_nowait()

        elif self._serial is not None:
            # Provide guidance for Ctrl-C
            if time.time() - self._start_time > 0.5:
                if not self._has_been_idle:
                    """TODO: get_shell().set_notice("Use Ctrl-C to interrupt the program and/or enter the REPL")"""
                else:
                    if not self._ctrl_c_notice_has_been_removed:
                        """TODO: get_shell().set_notice(None)"""
                        self._ctrl_c_notice_has_been_removed = True
                        # TODO: fetch required info if automatic interrupt is disabled

            # get the message
            try:
                msg = self._read_next_serial_message()
            except SerialException as e:
                self._handle_serial_exception(e)
                return None
        else:
            msg = None

        return self.transform_message(msg)

    def interrupt(self):
        if self._serial is None:
            return

        try:
            self.idle = False
            self._serial.reset_output_buffer()
            self._serial.write(b"\x03")

            # Wait a bit to avoid the situation where part of the prompt will
            # be treated as output and whole prompt is not detected.
            # (Happened with Calliope)
            sleep(0.1)
        except SerialException as e:
            self._handle_serial_exception(e)

    def destroy(self):
        self.disconnect()

    def disconnect(self):
        if self._serial is not None:
            try:
                self._serial.close()
                self._send_text_to_shell(
                    "\n\nConnection closed.\nSelect Run → Stop/Restart or press Ctrl+F2 to connect again.",
                    "stdout",
                )
            except Exception as e:
                logging.exception("Problem when closing serial")
                self._send_error_to_shell(
                    "Problem when closing serial connection: " + str(e)
                )

            self._serial = None

    def is_connected(self):
        return self._serial is not None

    def is_functional(self):
        return self.is_connected()

    def _create_serial(self):
        self.port = get_workbench().get_option(self.backend_name + ".port")

        if self.port is None:
            self._send_text_to_shell(
                'Not connected. Choose "Tools → Options → Backend" to change.', "stdout"
            )
            return None

        if self.port == "auto":
            potential = self._detect_potential_ports()
            if len(potential) == 1:
                self.port = potential[0][0]
            else:
                message = dedent(
                    """\
                    Couldn't find the device automatically. 
                    Check the connection (making sure the device is not in bootloader mode)
                    or choose "Tools → Options → Backend" to select the port manually."""
                )

                if len(potential) > 1:
                    _, descriptions = zip(*potential)
                    message += "\n\nLikely candidates are:\n * " + "\n * ".join(
                        descriptions
                    )

                self._show_error_connect_again(message)
                return None

        try:
            return SerialHelper(self.port, baudrate=self._baudrate)
        except SerialException as error:
            traceback.print_exc()
            message = (
                "Unable to connect to " + self.port + "\n" + "Error: " + str(error)
            )

            # TODO: check if these error codes also apply to Linux and Mac
            if error.errno == 13 and platform.system() == "Linux":
                # TODO: check if user already has this group
                message += "\n\n" + dedent(
                    """\
                Try adding yourself to the 'dialout' group:
                > sudo usermod -a -G dialout <username>
                (NB! This needs to be followed by reboot or logging out and logging in again!)"""
                )

            elif "PermissionError" in message:
                message += "\n\n" + dedent(
                    """\
                If you have serial connection to the device from another program,
                then disconnect it there."""
                )

            elif error.errno == 16:
                message += "\n\n" + "Try restarting the device."

            self._show_error_connect_again(message)

            return None

    def _show_error_connect_again(self, msg):
        self._send_error_to_shell(
            msg
            + "\n\nCheck the configuration, select Run → Stop/Restart or press Ctrl+F2 to try again."
            + "\n(On some occasions it helps to wait before trying again.)"
        )

    def _detect_potential_ports(self):
        all_ports = list_serial_ports()
        """
        for p in all_ports:
            print(p.description,
                  p.device,
                  None if p.vid is None else hex(p.vid),
                  None if p.pid is None else hex(p.pid),
                  )
        """
        return [
            (p.device, p.description)
            for p in all_ports
            if (p.vid, p.pid) in self.known_usb_vids_pids
            or p.description in self.known_port_descriptions
            or ("USB" in p.description and "serial" in p.description.lower())
            or "UART" in p.description
            or "DAPLink" in p.description
        ]

    @property
    def idle(self):
        return self.__idle

    @idle.setter
    def idle(self, value):
        if self.__idle != value:
            logging.debug("Serial idle %s => %s", self.__idle, value)

        self.__idle = value
        if value:
            self._has_been_idle = True

    def _fetch_builtin_modules(self):
        assert self.idle
        out, err = self._execute_and_get_response("help('modules')")
        assert err == b"", "Error was: %r" % err
        modules_str = (
            out.decode("utf-8")
            .replace("Plus any modules on the filesystem", "")
            .replace("/__init__", "")
            .replace("/", ".")
        )
        return modules_str.split()

    def _fetch_uname(self):
        assert self.idle
        res = self._execute_and_parse_value(
            "import os as __os_; print(repr(tuple(__os_.uname()))); del __os_"
        )
        return {
            "sysname": res[0],
            "nodename": res[1],
            "release": res[2],
            "version": res[3],
            "machine": res[4],
        }

    def _interrupt_to_prompt(self, clean, timeout=8):
        assert self._serial is not None

        timer = TimeHelper(timeout)

        # NB! Sometimes disconnecting and reconnecting (on macOS?)
        # too quickly causes anomalies. See CalliopeMiniProxy for more details

        for delay in [0.05, 0.5, 2.0, 3.0]:
            # Interrupt several times, because with some drivers first interrupts seem to vanish
            self._serial.reset_output_buffer()
            self._serial.write(b"\x03")  # interrupt
            self._serial.write(b"\x01")  # raw mode
            sleep(delay)
            self._discarded_bytes += self._serial.read_all()
            if self._discarded_bytes.endswith(
                FIRST_RAW_PROMPT
            ) or self._discarded_bytes.endswith(b"\r\n>"):
                break
        else:
            raise TimeoutError("Can't get to raw prompt")

        welcome_text = self._get_welcome_text_in_raw_mode(timer.time_left)

        if clean:
            self._clean_environment_during_startup(timer.time_left)

        self._finalize_repl()

        # report ready
        self._non_serial_msg_queue.put(
            ToplevelResponse(welcome_text=welcome_text.strip())
        )

        self.idle = True

    def _clean_environment_during_startup(self, time_left):
        # In MP Ctrl+D doesn't run user code, in CP it does
        self._serial.write(b"\x04")
        self._discarded_bytes = self._serial.read_until(
            [FIRST_RAW_PROMPT, RAW_PROMPT], time_left
        )

    def _get_welcome_text_in_raw_mode(self, timeout):
        timer = TimeHelper(timeout)
        # get welcome text with Ctrl+B
        self._serial.write(b"\x02")
        welcome_text = (
            self._serial.read_until(NORMAL_PROMPT, timer.time_left)
            .strip(b"\r\n >")
            .decode("utf-8", "replace")
        )
        if os.name != "nt":
            welcome_text = welcome_text.replace("\r\n", "\n")

        # Go back to raw prompt
        self._serial.write(b"\x01")
        self._serial.read_until((FIRST_RAW_PROMPT, b"\x04>"), timer.time_left)

        return welcome_text + " [backend=" + self.get_backend_name() + "]"

    def _finalize_repl(self):
        pass

    def _soft_reboot_and_run_main(self):
        if self._serial is None:
            return

        if not self.idle:
            # TODO: ignore??
            # self._serial.write(b"\r\x03")
            self.interrupt()

        get_runner()._set_state("running")
        self.idle = False
        # Need to go to normal mode. MP doesn't run user code in raw mode
        # (CP does, but it doesn't hurt to do it there as well)
        self._serial.write(b"\x02")
        self._serial.read_until(NORMAL_PROMPT)

        self._serial.write(b"\x04")

        # Returning to the raw prompt will be handled by
        # _read_next_serial_message

    def _clear_environment(self):
        assert self.idle
        # TODO: Ctrl+D in raw repl is perfect for MicroPython
        # but on CircuitPython it runs main.py

        # TODO: which is better:
        # self._execute_async(dedent("""
        #    for name in globals():
        #        if not name.startswith("__"):
        #            del globals()[name]
        # """).strip())
        # or
        out, err = self._execute_and_get_response(
            dedent(
                """
            globals().clear()
            __name__ == '__main__'
        """
            ).strip()
        )

        assert out == b""
        assert err == b""

    def _handle_serial_exception(self, e):
        logging.exception("MicroPython serial error")
        self._show_error_connect_again("\nLost connection to the device (%s)." % e)
        self.idle = False
        try:
            self._serial.close()
        except Exception:
            logging.exception("Closing serial")
        finally:
            self._serial = None

    def _execute_async(self, script):
        """Executes given MicroPython script on the device"""
        assert self._serial.buffers_are_empty()

        command_bytes = script.encode("utf-8")
        self._serial.write(command_bytes + b"\x04")
        self.idle = False

        # fetch confirmation
        ok = self._serial.read(2)
        assert ok == b"OK", "Expected OK, got %s, followed by %s" % (
            ok,
            self._serial.read_all(),
        )

    def _execute_and_get_response(self, script):
        self._execute_async(script)
        terminator = b"\x04>"
        output = self._serial.read_until(terminator)[: -len(terminator)]
        self.idle = True
        return output.split(b"\x04")

    def _execute_and_parse_value(self, script):
        out, err = self._execute_and_get_response(script)

        if err:
            # display script on error
            self._send_text_to_shell(script, "stderr") 

        # TODO: report the error to stderr
        assert len(err) == 0, "Error was " + repr(err)
        return ast.literal_eval(out.strip().decode("utf-8"))

    def _execute_and_expect_empty_response(self, script):
        out, err = self._execute_and_get_response(script)

        if out or err:
            # display script on error
            self._send_text_to_shell(script, "stderr")    

        assert len(out) == 0, "Output was " + repr(out)
        assert len(err) == 0, "Error was " + repr(err)

    def _cmd_cd(self, cmd):
        assert len(cmd.args) == 1
        path = cmd.args[0]
        if os.path.exists(path):
            self._non_serial_msg_queue.put(ToplevelResponse(cwd=path))
        else:
            self._non_serial_msg_queue.put(
                ToplevelResponse(error="Path doesn't exist: %s" % path)
            )

    def _cmd_Run(self, cmd):
        self._clear_environment()

        if not hasattr(cmd, "source"):
            assert len(cmd.args) == 1
            filename = cmd.args[0]
            if os.path.isabs(filename):
                full_filename = filename
            else:
                full_filename = os.path.join(get_workbench().get_cwd(), filename)
                cmd.script_path = full_filename

            with tokenize.open(full_filename) as fp:
                source = fp.read()
        else:
            source = cmd.source

        self._execute_async(source)

    def _cmd_execute_source(self, cmd):
        try:
            # Try to parse as expression
            ast.parse(cmd.source, mode="eval")
            # If it didn't fail then source is an expression
            msg_template = """{'message_class':'ToplevelResponse', 'value_info':(id(v), repr(v))}"""
            self._execute_async(
                "print('\\x04\\x02', [%s for v in [%s]][0])"
                % (msg_template, cmd.source.strip())
            )
        except SyntaxError:
            # source is a statement (or invalid syntax)
            self._execute_async(cmd.source)

    def _cmd_get_globals(self, cmd):
        if not get_runner().is_waiting_toplevel_command():
            return "postpone"

        try:
            if cmd.module_name == "__main__":
                self._execute_async(
                    "print('\\x04\\x02', {'message_class' : 'InlineResponse', 'command_name':'get_globals', 'module_name' : '__main__', 'globals':{x:repr(globals()[x]) for x in globals() if not x.startswith('__')}})"
                )
            else:
                self._execute_async(
                    dedent(
                        """
                    try:
                        import %(mod_name)s as __modForGlobs
                        print('\\x04\\x02', {'message_class' : 'InlineResponse', 'command_name':'get_globals', 'module_name' : '%(mod_name)s', 'globals':{name : repr(getattr(__modForGlobs, name)) for name in dir(__modForGlobs) if not name.startswith('__')}})
                        del __modForGlobs
                    except Exception as e:
                        print('\\x04\\x02', {'message_class' : 'InlineResponse', 'command_name':'get_globals', 'module_name' : '%(mod_name)s', 'globals':{}, 'error' : 'Error querying globals:\\n' + str(e)})
                    """
                        % {"mod_name": cmd.module_name}
                    )
                )
        except Exception:
            self._non_serial_msg_queue.put(
                InlineResponse(
                    command_name="get_globals",
                    module_name=cmd.module_name,
                    globals={},
                    error="Error requesting globals:\\n" + traceback.format_exc(),
                )
            )

        return None

    def _cmd_editor_autocomplete(self, cmd):
        # template for the response
        msg = InlineResponse(
            command_name="editor_autocomplete",
            source=cmd.source,
            row=cmd.row,
            column=cmd.column,
            error=None,
        )

        try:
            script = jedi.Script(
                cmd.source, cmd.row, cmd.column, sys_path=[self._get_api_stubs_path()]
            )
            completions = script.completions()
        except Exception:
            msg["error"] = "Autocomplete error"
            self._non_serial_msg_queue.put(msg)
            return

        msg["completions"] = self.filter_completions(completions)
        self._non_serial_msg_queue.put(msg)

    def filter_completions(self, completions):
        # filter out completions not applicable to MicroPython
        result = []
        for completion in completions:
            if completion.name.startswith("__"):
                continue

            parent_name = completion.parent().name
            name = completion.name
            root = completion.full_name.split(".")[0]

            # jedi proposes names from CPython builtins
            if root in self._builtins_info and name not in self._builtins_info[root]:
                continue

            if parent_name == "builtins" and name not in self._builtins_info:
                continue

            result.append({"name": name, "complete": completion.complete})

        return result

    def _cmd_shell_autocomplete(self, cmd):
        source = cmd.source

        # TODO: combine dynamic results and jedi results
        if source.strip().startswith("import ") or source.strip().startswith("from "):
            # this needs the power of jedi
            msg = InlineResponse(
                command_name="shell_autocomplete", source=cmd.source, error=None
            )

            try:
                # at the moment I'm assuming source is the code before cursor, not whole input
                lines = source.split("\n")
                script = jedi.Script(
                    source,
                    len(lines),
                    len(lines[-1]),
                    sys_path=[self._get_api_stubs_path()],
                )
                completions = script.completions()
                msg["completions"] = self.filter_completions(completions)
            except Exception:
                msg["error"] = "Autocomplete error"

            self._non_serial_msg_queue.put(msg)
        else:
            # use live data
            regex = re.search(
                r"(\w+\.)*(\w+)?$", source
            )  # https://github.com/takluyver/ubit_kernel/blob/master/ubit_kernel/kernel.py
            if regex:
                n = regex.group()
                # the response format is not the same as expected by the gui
                # but it will be transformed later
                if "." in n:
                    obj, n = n.rsplit(".", 1)
                    self._execute_async(
                        "print('\\x04\\x02', {'message_class' : 'InlineResponse', 'command_name': 'shell_autocomplete', 'match':"
                        + repr(n)
                        + ", 'source':"
                        + repr(source)
                        + ", 'names':dir("
                        + obj
                        + ")})"
                    )
                else:
                    self._execute_async(
                        "print('\\x04\\x02', {'message_class' : 'InlineResponse', 'command_name': 'shell_autocomplete', 'match':"
                        + repr(n)
                        + ", 'source':"
                        + repr(source)
                        + ", 'names':dir()})"
                    )

    def _cmd_dump_api_info(self, cmd):
        "For use during development of the plug-in"
        try:
            self._execute_and_expect_empty_response(
                dedent(
                    """
                def __print_object_atts(obj):
                    import gc
                    result = []
                    errors = []
                    for name in dir(obj):
                        try:
                            val = getattr(obj, name)
                            result.append((name, repr(val), repr(type(val))))
                        except BaseException as e:
                            errors.append("Couldn't get attr '%s' from object '%r', Err: %r" % (name, obj, e))
                    print((result, errors))
                    gc.collect()
            """
                )
            )
            for module_name in sorted(self._fetch_builtin_modules()):
                if (
                    not module_name.startswith("_")
                    # and not module_name.startswith("ada")
                    # and not module_name == "builtins"
                ):
                    # self._send_text_to_shell("Dumping " + module_name + "\n", "stdout")
                    file_name = os.path.join(
                        self._get_api_stubs_path(),
                        module_name.replace(".", "/") + ".py",
                    )
                    self._dump_module_stubs(module_name, file_name)
        finally:
            self._non_serial_msg_queue.put(ToplevelResponse())

    def _dump_module_stubs(self, module_name, file_name):
        _, err = self._execute_and_get_response("import {0}".format(module_name))
        if err:
            print("FAILED IMPORTING MODULE:", module_name, "\nErr: " + repr(err))
            return

        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with io.open(file_name, "w", encoding="utf-8", newline="\n") as fp:
            if module_name not in [
                "webrepl",
                "_webrepl",
                "gc",
                "http_client",
                "http_client_ssl",
                "http_server",
                "framebuf",
                "example_pub_button",
                "flashbdev",
            ]:
                self._dump_object_stubs(fp, module_name, "")

        _, err = self._execute_and_get_response("del {0}".format(module_name))

    def _dump_object_stubs(self, fp, object_expr, indent):
        if object_expr in [
            "docs.conf",
            "pulseio.PWMOut",
            "adafruit_hid",
            "upysh",
            # "webrepl",
            # "gc",
            # "http_client",
            # "http_server",
        ]:
            print("SKIPPING problematic name:", object_expr)
            return

        print("DUMPING", indent, object_expr)
        items, errors = self._execute_and_parse_value(
            "__print_object_atts({0})".format(object_expr)
        )

        if errors:
            print("ERRORS", errors)

        for name, rep, typ in sorted(items, key=lambda x: x[0]):
            if name.startswith("__"):
                continue

            print("DUMPING", indent, object_expr, name)
            self._send_text_to_shell("  * " + name + " : " + typ, "stdout")

            if typ in ["<class 'function'>", "<class 'bound_method'>"]:
                fp.write(indent + "def " + name + "():\n")
                fp.write(indent + "    pass\n\n")
            elif typ in ["<class 'str'>", "<class 'int'>", "<class 'float'>"]:
                fp.write(indent + name + " = " + rep + "\n")
            elif typ == "<class 'type'>" and indent == "":
                # full expansion only on toplevel
                fp.write("\n")
                fp.write(indent + "class " + name + ":\n")  # What about superclass?
                fp.write(indent + "    ''\n")
                self._dump_object_stubs(
                    fp, "{0}.{1}".format(object_expr, name), indent + "    "
                )
            else:
                # keep only the name
                fp.write(indent + name + " = None\n")

    def _cmd_cat(self, cmd):
        if len(cmd.args) != 1:
            self._send_error_to_shell("Command requires one argument")
            return

        source = cmd.args[0]
        mount = self._get_fs_mount()
        if mount is None:
            self._cat_via_serial(source)
        else:
            source = os.path.join(mount, source.strip("/"))
            self._cat_via_mount(source)

    def _cmd_lsdevice(self, cmd):
        try:
            items = self._list_files()
            out = "\n".join(items) + "\n"
            self._send_text_to_shell(out, "stdout")
        finally:
            self._non_serial_msg_queue.put(ToplevelResponse())

    def _cmd_upload(self, cmd):
        # Target is interpreted relative to the root
        if len(cmd.args) == 1:
            source = cmd.args[0]
            # target is at root
            target = os.path.basename(source)
        elif len(cmd.args) == 2:
            source = cmd.args[0]
            target = cmd.args[1]
        else:
            # TODO: test this case
            raise RuntimeError("Command requires 1 or 2 arguments")

        if not os.path.isabs(source):
            source = os.path.join(get_workbench().get_cwd(), source)

        if not os.path.isfile(source):
            raise IOError("No such file: %s" % source)

        target = target.replace("\\", "/")
        # Only prepend slash if it is known that device supports directories
        # (it's probably safe to omit slash anyway)
        if self._supports_directories() and not target.startswith("/"):
            target = "/" + target

        try:
            self._check_and_upload(source, target)
        finally:
            self._non_serial_msg_queue.put(ToplevelResponse())
            # TODO: Output confirmation ? (together with file size)
            # Or should the confirmation be given in terms of mount path?

    def _check_and_upload(self, source, target):
        # if target is a py file,
        # then give warning if source has syntax errors

        # Note that it's incomplete solution --
        # if current Python version is later than 3.5, then it may
        # accept source which gives syntax errors on MP.

        if target.endswith(".py"):
            with tokenize.open(source) as fp:
                src = fp.read()
                try:
                    ast.parse(src, source)
                except SyntaxError as e:
                    self._send_error_to_shell(
                        "%s has syntax errors:\n%s\n\nFile will not be uploaded."
                        % (source, e)
                    )
                    return
        try:
            self._upload(source, target)
        except Exception:
            self._send_error_to_shell(traceback.format_exc())

    def _upload(self, source, target):
        mount = self._get_fs_mount()
        if mount is None:
            self._upload_via_serial(source, target)
        else:
            virtual_path = os.path.join(mount, target.strip("/"))
            self._upload_via_mount(source, virtual_path)

    def _upload_via_serial(self, source, target):
        assert self.idle

        with open(source, "rb") as local:
            content = local.read()

        self._execute_and_expect_empty_response("__upf = open(%r, 'wb')" % target)

        BLOCK_SIZE = 64
        for i in range(0, len(content), BLOCK_SIZE):
            self._execute_and_expect_empty_response(
                "__upf.write(%r)" % content[i : i + BLOCK_SIZE]
            )

        self._execute_and_expect_empty_response("__upf.close()")
        self._execute_and_expect_empty_response("del __upf")

    def _upload_via_mount(self, source, target):
        with open(source, "rb") as fp:
            content = fp.read()

        try:
            with open(target, "wb") as fp:
                fp.write(content)
                # Force writes to the device to avoid data corruption
                # when user resets or plugs out the device
                os.fsync(fp)
        except OSError as e:
            self._report_upload_via_mount_error(source, target, e)
            return

    def _report_upload_via_mount_error(self, source, target, error):
        self._send_error_to_shell(
            "Couldn't write to %s\nOriginal error: %s\n\nIf the target directory exists then it may be corrupted."
            % (target, error)
        )

    def _cat_via_serial(self, source):
        try:
            out, err = self._execute_and_get_response(
                dedent(
                    """
                    with open(%r, "r") as fp:
                        print(fp.read())
                    """
                    % source
                ).strip()
            )
            if out:
                self._send_text_to_shell(
                    out.decode("utf-8", errors="replace"), "stdout"
                )
            if err:
                self._send_text_to_shell(
                    err.decode("utf-8", errors="replace"), "stderr"
                )
        except Exception:
            self._send_error_to_shell(traceback.format_exc())
        finally:
            self._non_serial_msg_queue.put(ToplevelResponse())

    def _cat_via_mount(self, source):
        try:
            with open(source, "r", encoding="UTF-8", errors="replace") as fp:
                self._send_text_to_shell(fp.read(), "stdout")

        except Exception:
            self._send_error_to_shell(traceback.format_exc())
        finally:
            self._non_serial_msg_queue.put(ToplevelResponse())

    def _list_files(self):
        mount = self._get_fs_mount()
        if mount is None:
            return self._execute_and_parse_value(
                "import os as __os_; print(__os_.listdir()); del __os_"
            )
        else:
            return os.listdir(mount)

    def _supports_directories(self):
        return None

    def _get_fs_mount_name(self):
        return None

    def _get_bootloader_mount_name(self):
        return None

    def _get_fs_mount(self):
        if self._get_fs_mount_name() is None:
            return None
        else:
            candidates = find_volumes_by_name(self._get_fs_mount_name())
            if len(candidates) == 0:
                raise RuntimeError("Could not find volume " + self._get_fs_mount_name())
            elif len(candidates) > 1:
                raise RuntimeError(
                    "Found several possible mount points: %s" % candidates
                )
            else:
                return candidates[0]

    def _read_next_serial_message(self) -> Optional[MessageFromBackend]:
        new_bytes = self._serial.read_all()

        if len(new_bytes) == 0:
            return None

        # TODO: Handle the case where part of the prompt was already published in previous message

        # Look for the first marker (EOT anywhere or NORMAL_PROMPT in the end of the seq)
        match = re.search(
            b"("
            + EOT
            + b"|"
            + NORMAL_PROMPT
            + b"$"  # Consider prompts only if they're at the end of output
            + b"|"
            + FIRST_RAW_PROMPT
            + b"$"
            + b")",
            new_bytes,
        )

        if match is None:
            # normal output (possibly partial)
            return self._read_output_message(new_bytes, False)

        elif match.start() > 0:
            # starts with block of normal output
            self._serial.unread(new_bytes[match.start() :])
            return self._read_output_message(new_bytes[: match.start()], True)

        elif match.group() == FIRST_RAW_PROMPT:
            assert new_bytes == FIRST_RAW_PROMPT
            self.idle = True
            return ToplevelResponse()

        elif match.group() == NORMAL_PROMPT:
            # Go to raw prompt
            assert new_bytes == NORMAL_PROMPT, "Got %s" % new_bytes
            return self._enter_raw_repl(True)

        else:
            assert match.group() == EOT
            assert match.start() == 0

            if len(new_bytes) == 1:
                # can't decide anything yet
                self._serial.unread(new_bytes)
                return None
            elif new_bytes[1:2] == RAW_PROMPT:
                # must be end of the response to a non-Thonny command
                # Only treat as raw prompt if it ends the output
                if new_bytes[1:] == RAW_PROMPT:
                    assert self._serial.incoming_is_empty()  # TODO: what about Ctlr-? ?
                    self.idle = True
                    return ToplevelResponse()
                else:
                    # Looks like the prompt was discarded by a soft reboot (or some other reason?)
                    # hide it and forget it
                    self._serial.unread(new_bytes[2:])
                    return None
            elif new_bytes[1:2] == THONNY_MSG_START:
                # must be followed by empty error block and raw prompt
                # read the message, following exception block and next prompt
                terminator = b"\r\n" + EOT + EOT + RAW_PROMPT
                term_loc = new_bytes.find(terminator)
                if term_loc == -1:
                    # not complete yet
                    self._serial.unread(new_bytes)
                    return None

                elif term_loc == len(new_bytes) - len(terminator):
                    # This terminator ends the bytes
                    # The normal, completed case
                    assert self._serial.incoming_is_empty()
                    msg_bytes = new_bytes[2 : -len(terminator)]
                    self.idle = True
                    return self._parse_message(msg_bytes)
                else:
                    # There is something following the terminator
                    # I guess this can be caused by interrupt
                    # This means the message is stale
                    logging.info(
                        "disregarding out of date Thonny message: %r", new_bytes
                    )
                    # Unread following stuff
                    self._serial.unread(new_bytes[term_loc + len(terminator) :])

            else:
                # exception block
                # this is followed by EOT and can/should be read in one piece
                next_eot_loc = new_bytes.find(EOT, 1)
                if next_eot_loc == -1:
                    # the block isn't complete yet
                    self._serial.unread(new_bytes)
                    return None
                else:
                    # block is complete
                    block_bytes = new_bytes[1:next_eot_loc]
                    leftover_bytes = new_bytes[next_eot_loc:]  # should be EOT + >
                    self._serial.unread(leftover_bytes)

                    if len(block_bytes) > 0:
                        # non-empty exception block
                        return BackendEvent(
                            event_type="ProgramOutput",
                            stream_name="stderr",
                            data=self.transform_output(
                                block_bytes.decode("utf-8", "replace"), "stderr"
                            ),
                        )
                    else:
                        return None

        return None

    def _parse_message(self, msg_bytes):
        msg_str = msg_bytes.decode("utf-8", "replace").strip()
        msg = ast.literal_eval(msg_str)
        assert isinstance(msg, dict)

        class_name = msg["message_class"]
        del msg["message_class"]

        assert class_name in globals()
        class_ = globals()[class_name]
        return class_(**msg)

    def _read_output_message(self, out_bytes, complete) -> Optional[BackendEvent]:

        if complete:
            out_str = out_bytes.decode("utf-8", "replace")
        else:
            # out_bytes may end with a partial utf-8 char
            while True:
                try:
                    out_str = out_bytes.decode("utf-8", "replace")
                    break
                except UnicodeDecodeError:
                    # unread last byte and try again
                    self._serial.unread(out_bytes[-1:])
                    out_bytes = out_bytes[:-1]

        if len(out_str) == 0:
            return None
        else:
            transformed = self.transform_output(out_str, "stdout")
            return BackendEvent(
                event_type="ProgramOutput", stream_name="stdout", data=transformed
            )

    def transform_output(self, s, stream_name):
        if os.name != "nt":
            #
            s = s.replace("\r\n", "\n")

        # replace "<stdin>" in error messages with script name
        if (
            stream_name == "stderr"
            and self._last_toplevel_command
            and self._last_toplevel_command.name in ["Run", "run"]
            and hasattr(self._last_toplevel_command, "script_path")
        ):
            s = s.replace('"<stdin>"', '"%s"' % self._last_toplevel_command.script_path)

        # TODO: get rid of raw prompts (may occur after soft reboot)
        # TOOD: move it to CircuitPython subclass
        return s.replace(
            "Press any key to enter the REPL. Use CTRL-D to reload.",
            "Press CTRL-C to enter the REPL. Use CTRL-D to reload.",
        )

    def _get_main_script_path(self):
        if self._supports_directories():
            return "/main.py"
        else:
            return "main.py"

    def _get_boot_script_path(self):
        if self._supports_directories():
            return "/boot.py"
        else:
            return "boot.py"

    def _get_script_path(self):
        script_path = (
            get_workbench().get_editor_notebook().get_current_editor().save_file(False)
        )
        script_path = Path(script_path)
        assert script_path.is_file(), "File not found: %s" % script_path

        filename = script_path.name

        if self._supports_directories():
            return "/%s" % filename
        else:
            return filename

    def transform_message(self, msg):
        if msg is None:
            return None

        if isinstance(msg.get("value_info", None), tuple):
            msg["value_info"] = common.ValueInfo(*msg["value_info"])

        if (
            getattr(msg, "command_name", None) == "shell_autocomplete"
            and "completions" not in msg
        ):
            names = msg["names"]
            match = msg["match"]
            del msg["names"]
            matches = [
                {"name": n, "complete": n[len(match) :]}
                for n in names
                if n.startswith(match) and not n.startswith("__")
            ]
            msg["completions"] = matches
            return msg
        else:
            return msg

    def _enter_raw_repl(self, strict):
        if strict:
            assert self._serial.buffers_are_empty()

        discarded_data = b""

        for delay in [0.01, 0.05, 0.1, 0.5]:
            self._serial.write(b"\x03")
            sleep(delay / 3)
            self._serial.write(b"\x01")
            sleep(delay)
            # Consume the raw repl introduction + prompt
            discarded_data += self._serial.read_all()
            if discarded_data.endswith(b"\r\n>"):
                self.idle = True
                return ToplevelResponse()

        self._send_error_to_shell(
            "Couldn't connect to the raw REPL. Serial output: " + str(discarded_data)
        )

        self.idle = False
        return None

    def _send_error_to_shell(self, message_text):
        self._send_text_to_shell(message_text, "stderr")

    def _send_text_to_shell(self, message_text, stream_name):
        if not message_text.endswith("\n"):
            message_text += "\n"

        self._non_serial_msg_queue.put(
            BackendEvent(
                event_type="ProgramOutput", stream_name=stream_name, data=message_text
            )
        )

    def _get_builtins_info(self):
        """
        for p in self._get_api_stubs_path():
            builtins_file = os.path.join(p, "__builtins__.py")
            if os.path.exists(builtins_file):
                return parse_api_information(builtins_file)
        """
        path = os.path.join(self._get_api_stubs_path(), "builtins.py")
        if os.path.exists(path):
            return parse_api_information(path)
        else:
            return {}

    def _get_api_stubs_path(self):
        import inspect

        return os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), "api_stubs"
        )

    @property
    def firmware_filetypes(self):
        return [("all files", ".*")]

    @property
    def micropython_upload_enabled(self):
        return self.port is not None

    def select_and_upload_micropython(self):
        firmware_path = askopenfilename(
            filetypes=self.firmware_filetypes,
            initialdir=get_workbench().get_option("run.working_directory"),
        )
        if firmware_path:
            self.upload_micropython(firmware_path)

    def upload_micropython(self, firmware_path):
        cmd = self.construct_firmware_upload_command(firmware_path)
        self.disconnect()
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        dlg = SubprocessDialog(
            get_workbench(),
            proc,
            "Uploading firmware",
            autoclose=False,
            conclusion="Done.\nNB! If opening REPL fails on first trial\nthen wait a second and try again.",
        )
        show_dialog(dlg)

    def construct_firmware_upload_command(self, firmware_path):
        raise NotImplementedError()

    @property
    def known_usb_vids_pids(self):
        """Return set of pairs of USB device VID, PID"""
        return set()

    @property
    def known_port_descriptions(self):
        return set()


class MicroPythonConfigPage(BackendDetailsConfigPage):
    backend_name = None  # Will be overwritten on Workbench.add_backend

    def __init__(self, master):
        super().__init__(master)
        label = ttk.Label(
            self, text='Port (look for your device name, "USB Serial" or "UART")'
        )
        label.grid(row=0, column=0, sticky="nw")

        self._ports_by_desc = {
            p.description
            if p.device in p.description
            else p.description + " (" + p.device + ")": p.device
            for p in list_serial_ports()
        }
        self._ports_by_desc["< Try to detect automatically >"] = "auto"
        self._ports_by_desc["< None / don't connect at all >"] = None

        def port_order(p):
            _, name = p
            if name is None:
                return ""
            elif name.startswith("COM") and len(name) == 4:
                # Make one-digit COM ports go before COM10
                return name.replace("COM", "COM0")
            else:
                return name

        # order by port, auto first
        port_descriptions = [
            key for key, _ in sorted(self._ports_by_desc.items(), key=port_order)
        ]

        self._port_desc_variable = create_string_var(self.current_port_desc)
        self._port_combo = ttk.Combobox(
            self,
            exportselection=False,
            textvariable=self._port_desc_variable,
            values=port_descriptions,
        )
        self._port_combo.state(["!disabled", "readonly"])

        self._port_combo.grid(row=1, column=0, sticky="new")
        self.columnconfigure(0, weight=1)

    @property
    def current_port_desc(self):
        name = get_workbench().get_option(self.backend_name + ".port")
        for desc in self._ports_by_desc:
            if self._ports_by_desc[desc] == name:
                return desc

        return ""

    def should_restart(self):
        return self._port_desc_variable.modified  # pylint: disable=no-member

    def apply(self):
        if not self._port_desc_variable.modified:  # pylint: disable=no-member
            return

        else:
            port_desc = self._port_desc_variable.get()
            port_name = self._ports_by_desc[port_desc]
            get_workbench().set_option(self.backend_name + ".port", port_name)


class GenericMicroPythonProxy(MicroPythonProxy):
    @property
    def known_usb_vids_pids(self):
        """Return set of pairs of USB device (VID, PID)"""
        return {
            # Generic MicroPython Board, see http://pid.codes/org/MicroPython/
            (0x1209, 0xADDA)
        }


class GenericMicroPythonConfigPage(MicroPythonConfigPage):
    pass


class SerialHelper:
    """Utility class for using Serial connection
    
    Uses background thread to read from serial as soon as possible
    to avoid loss of data (because buffer overflow or the device discarding 
    unread data).

    Allows writing with delays after each n bytes.
    
    Allows unreading data.    
    """

    def __init__(self, port, baudrate):
        self._read_queue = Queue()  # populated by reader thread
        self._read_buffer = bytearray()  # used for unreading and postponing bytes
        self._serial = serial.Serial(port, baudrate=baudrate, timeout=None)
        self.num_bytes_received = 0
        self._error = None

        self._reading_thread = threading.Thread(target=self._listen_serial, daemon=True)
        self._reading_thread.start()

    def read(self, size, timeout=1):
        if timeout == 0:
            raise TimeoutError()

        timer = TimeHelper(timeout)

        while len(self._read_buffer) < size:
            self._check_for_error()

            try:
                self._read_buffer.extend(self._read_queue.get(True, timer.time_left))
            except queue.Empty:
                raise TimeoutError(
                    "Reaction timeout. Bytes read: %s" % self._read_buffer
                )

        try:
            data = self._read_buffer[:size]
            return data
        finally:
            del self._read_buffer[:size]

    def read_until(self, terminators, timeout=2):
        if timeout == 0:
            raise TimeoutError()

        timer = TimeHelper(timeout)
        if not isinstance(terminators, (set, list, tuple)):
            terminators = [terminators]

        terminator = None
        while True:
            self._check_for_error()

            found = False
            for terminator in terminators:
                if terminator in self._read_buffer:
                    found = True
                    break
            if found:
                break

            try:
                data = self._read_queue.get(True, timer.time_left)
                assert len(data) > 0
                self._read_buffer.extend(data)
            except queue.Empty:
                raise TimeoutError(
                    "Reaction timeout. Bytes read: %s" % self._read_buffer
                )

        assert terminator is not None
        size = self._read_buffer.index(terminator) + len(terminator)

        try:
            data = self._read_buffer[:size]
            return data
        finally:
            del self._read_buffer[:size]

    def read_all(self):
        while not self._read_queue.empty():
            self._read_buffer.extend(self._read_queue.get(True))

        if len(self._read_buffer) == 0:
            self._check_for_error()

        try:
            return self._read_buffer
        finally:
            self._read_buffer = bytearray()

    def _check_for_error(self):
        if self._error:
            raise SerialException("EOF")

    def unread(self, data):
        self._read_buffer = data + self._read_buffer

    def write(self, data, block_size=32, delay=0.01):
        for i in range(0, len(data), block_size):
            block = data[i : i + block_size]
            # self._log_data(b"[" + block + b"]")
            size = self._serial.write(block)
            assert size == len(block)
            time.sleep(delay)
        return len(data)

    def _listen_serial(self):
        "NB! works in background thread"
        try:
            while True:
                b = self._serial.read(1)  # To avoid busy loop
                if len(b) == 0:
                    self._error = "EOF"
                    # print("LISTEN EOFFFFFFFFFF")
                    break
                data = b + self._serial.read_all()
                self.num_bytes_received += len(data)
                self._read_queue.put(data)
                # self._log_data(data)

        except SerialException as e:
            logging.exception("Error while reading from serial")
            self._error = str("Serial reading error: %s" % e)

    def _log_data(self, data):
        print(
            data.decode("Latin-1")
            .replace("\r\n", "\n")
            .replace("\x01", "①")
            .replace("\x02", "②")
            .replace("\x03", "③")
            .replace("\x04", "④"),
            end="",
        )

    def incoming_is_empty(self):
        return (
            self._serial.in_waiting == 0
            and self._read_queue.empty()
            and len(self._read_buffer) == 0
        )

    def outgoing_is_empty(self):
        return self._serial.out_waiting == 0

    def buffers_are_empty(self):
        return self.incoming_is_empty() and self.outgoing_is_empty()

    def reset_input_buffer(self):
        return self.read_all()

    def reset_output_buffer(self):
        self._serial.reset_output_buffer()

    def close(self):
        if self._serial is not None:
            try:
                self._serial.cancel_read()
                self._reading_thread.join()
            finally:
                try:
                    self._serial.close()
                    self._serial = None
                except Exception:
                    logging.exception("Couldn't close serial")


class TimeHelper:
    def __init__(self, time_allowed):
        self.start_time = time.time()
        self.time_allowed = time_allowed

    @property
    def time_spent(self):
        return time.time() - self.start_time

    @property
    def time_left(self):
        return max(self.time_allowed - self.time_spent, 0)


def parse_api_information(file_path):
    with tokenize.open(file_path) as fp:
        source = fp.read()

    tree = ast.parse(source)

    defs = {}

    # TODO: read also docstrings ?

    for toplevel_item in tree.body:
        if isinstance(toplevel_item, ast.ClassDef):
            class_name = toplevel_item.name
            member_names = []
            for item in toplevel_item.body:
                if isinstance(item, ast.FunctionDef):
                    member_names.append(item.name)
                elif isinstance(item, ast.Assign):
                    # TODO: check Python 3.4
                    "TODO: item.targets[0].id"

            defs[class_name] = member_names

    return defs


def list_serial_ports():
    # serial.tools.list_ports.comports() can be too slow
    # because os.path.islink can be too slow (https://github.com/pyserial/pyserial/pull/303)
    # Workarond: temporally patch os.path.islink
    try:
        old_islink = os.path.islink
        if platform.system() == "Windows":
            os.path.islink = lambda _: False
        return list(serial.tools.list_ports.comports())
    finally:
        os.path.islink = old_islink


def add_micropython_backend(name, proxy_class, description, config_page):
    get_workbench().set_default(name + ".port", "auto")
    get_workbench().add_backend(name, proxy_class, description, config_page)


def load_plugin():
    add_micropython_backend(
        "GenericMicroPython",
        GenericMicroPythonProxy,
        "MicroPython on a generic device",
        GenericMicroPythonConfigPage,
    )

    def _upload_as(target_provider_method):
        source_path = (
            get_workbench().get_editor_notebook().get_current_editor().save_file(False)
        )
        if source_path is None:
            return

        proxy = get_runner().get_backend_proxy()
        assert isinstance(proxy, MicroPythonProxy)

        if os.path.isabs(source_path):
            source_path = os.path.relpath(source_path, get_workbench().get_cwd())

        target = getattr(proxy, target_provider_method)()
        get_shell().submit_magic_command(["%upload", source_path, target])

    def _cat(source_provider_method):
        proxy = get_runner().get_backend_proxy()
        assert isinstance(proxy, MicroPythonProxy)

        source = getattr(proxy, source_provider_method)()
        get_shell().submit_magic_command(["%cat", source])

    def _upload_as_main_script():
        _upload_as("_get_main_script_path")

    def _upload_as_boot_script():
        _upload_as("_get_boot_script_path")

    def _upload_script():
        _upload_as("_get_script_path")

    def _cat_main_script():
        _cat("_get_main_script_path")

    def _cat_boot_script():
        _cat("_get_boot_script_path")

    def soft_reboot():
        proxy = get_runner().get_backend_proxy()
        if hasattr(proxy, "_soft_reboot_and_run_main"):
            return proxy._soft_reboot_and_run_main()
        return None

    def soft_reboot_enabled():
        proxy = get_runner().get_backend_proxy()
        return (
            proxy
            and proxy.is_functional()
            and hasattr(proxy, "_soft_reboot_and_run_main")
        )

    def disconnect():
        proxy = get_runner().get_backend_proxy()
        assert hasattr(proxy, "disconnect")
        proxy.disconnect()

    def disconnect_enabled():
        proxy = get_runner().get_backend_proxy()
        return hasattr(proxy, "disconnect")

    def file_commands_enabled():
        proxy = get_runner().get_backend_proxy()
        return (
            isinstance(proxy, MicroPythonProxy)
            and get_workbench().get_editor_notebook().get_current_editor() is not None
            and get_runner().is_waiting_toplevel_command()
        )

    get_workbench().add_command(
        "softreboot",
        "device",
        "Soft reboot",
        soft_reboot,
        soft_reboot_enabled,
        group=10,
        default_sequence="<Control-d>",
        extra_sequences=["<<CtrlDInText>>"],
    )

    get_workbench().add_command(
        "uploadmainscript",
        "device",
        "Upload current script as main script",
        _upload_as_main_script,
        tester=file_commands_enabled,
        default_sequence="<Control-u>",
        group=20,
    )

    get_workbench().add_command(
        "uploadbootscript",
        "device",
        "Upload current script as boot script",
        _upload_as_boot_script,
        tester=file_commands_enabled,
        group=20,
    )

    get_workbench().add_command(
        "uploadscript",
        "device",
        "Upload current script with current name",
        _upload_script,
        tester=file_commands_enabled,
        group=20,
    )

    get_workbench().add_command(
        "catmainscript",
        "device",
        "Show device's main script",
        _cat_main_script,
        tester=file_commands_enabled,
        group=20,
    )

    get_workbench().add_command(
        "catbootscript",
        "device",
        "Show device's boot script",
        _cat_boot_script,
        tester=file_commands_enabled,
        group=20,
    )

    get_workbench().add_command(
        "disconnectserial",
        "device",
        "Close serial connection",
        disconnect,
        disconnect_enabled,
        group=100,
    )
