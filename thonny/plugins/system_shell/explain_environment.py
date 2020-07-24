import os.path
import platform
import sys
import warnings


def _clear_screen():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def equivalent_realpath(p):
    pdir = os.path.dirname(p)
    if os.path.isfile(os.path.join(pdir, "activate")):
        # it's a virtual environment
        # can use realpath only if it doesn't move out of its dir
        real = os.path.realpath(p)
        if os.path.dirname(real) == pdir:
            return real
        try:
            link = os.readlink(p)
            if not os.path.isabs(link):
                link = os.path.join(pdir, link)
            link = os.path.normpath(link)
            if os.path.dirname(link) == pdir:
                return link
            return p
        except Exception:
            return p
    else:
        return os.path.realpath(p)


def is_virtual_exe(p):
    pdir = os.path.dirname(p)
    return os.path.exists(os.path.join(pdir, "activate")) or os.path.exists(
        os.path.join(pdir, "activate.bat")
    )


def is_bundled_exe(p):
    pdir = os.path.dirname(p)
    return os.path.exists(os.path.join(pdir, "thonny_python.ini"))


def list_commands(prefix, highlighted_reals, highlighted_dirs):
    for suffix in ["", "3", "3.5", "3.6", "3.7", "3.8"]:
        cmd = prefix + suffix
        import shutil

        target = shutil.which(cmd)
        if target is not None:
            target = os.path.abspath(target)
            target = normpath_with_actual_case(target)
            real = equivalent_realpath(target)

            if target == real:
                relation = "=="
            else:
                relation = "->"

            line = " - " + cmd.ljust(9) + " " + relation + " " + real
            if (
                real in highlighted_reals
                or os.path.dirname(real) in highlighted_dirs
                or os.path.dirname(target) in highlight_dirs
            ):
                print(wrap_in_ansi_code(line, "1"))
            else:
                print(wrap_in_ansi_code(line, "2"))


def wrap_in_ansi_code(text, code):
    if can_use_ansi_codes():
        return "\033[" + code + "m" + text + "\033[0m"
    else:
        return text


def can_use_ansi_codes():
    if platform.system() == "Windows":
        ver = platform.win32_ver()
        try:
            return int(ver[0]) >= 10
        except Exception:
            warnings.warn("Can't determine Windows version %s" % (ver,))
            return False
    else:
        return True


def normpath_with_actual_case(name):
    """In Windows return the path with the case it is stored in the filesystem"""
    # copied from thonny.common to make this script independent
    assert os.path.isabs(name) or os.path.ismount(name), "Not abs nor mount: " + name
    assert os.path.exists(name), "Not exists: " + name

    if os.name == "nt":
        # https://stackoverflow.com/questions/2113822/python-getting-filename-case-as-stored-in-windows/2114975
        name = os.path.normpath(name)

        from ctypes import create_unicode_buffer, windll

        buf = create_unicode_buffer(512)
        # GetLongPathNameW alone doesn't fix filename part
        windll.kernel32.GetShortPathNameW(name, buf, 512)  # @UndefinedVariable
        windll.kernel32.GetLongPathNameW(buf.value, buf, 512)  # @UndefinedVariable
        result = buf.value

        if result.casefold() != name.casefold():
            # Sometimes GetShortPathNameW + GetLongPathNameW doesn't work
            # see eg. https://github.com/thonny/thonny/issues/925
            windll.kernel32.GetLongPathNameW(name, buf, 512)  # @UndefinedVariable
            result = buf.value

            if result.casefold() != name.casefold():
                result = name

        if result[1] == ":":
            # ensure drive letter is capital
            return result[0].upper() + result[1:]
        else:
            return result
    else:
        # easy on Linux
        # too difficult on mac
        # https://stackoverflow.com/questions/14515073/in-python-on-osx-with-hfs-how-can-i-get-the-correct-case-of-an-existing-filenam
        # Hopefully only correct case comes into Thonny (eg. via open dialog)
        return os.path.normpath(name)


if __name__ == "__main__":
    _clear_screen()
    print("*" * 80)
    print("Some Python commands in the PATH of this session:")

    sys_real = normpath_with_actual_case(equivalent_realpath(sys.executable))
    sys_executable = normpath_with_actual_case(sys.executable)

    if is_virtual_exe(sys_executable) or is_bundled_exe(sys_executable):
        highlight_dirs = [os.path.dirname(sys_executable)]
    else:
        highlight_dirs = []

    if platform.system() == "Windows":
        # Add Scripts for pip
        highlight_dirs.append(os.path.join(os.path.dirname(sys_real), "Scripts"))
        highlight_dirs.append(os.path.join(os.path.dirname(sys_executable), "Scripts"))

    list_commands("python", [sys_real], highlight_dirs)

    likely_pips = []
    if sys_real[-9:-1] == "python3.":
        likely_pips.append(sys_real[:-9] + "pip3." + sys_real[-1])
    if sys_executable.endswith("/python3"):
        # This is not as likely match as previous, but still quite likely
        likely_pips.append(sys_executable.replace("/python3", "/pip3"))

    list_commands("pip", likely_pips, highlight_dirs)

    print("")
    print("*" * 80)
