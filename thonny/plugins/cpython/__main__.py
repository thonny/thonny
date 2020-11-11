# -*- coding: utf-8 -*-

"""
This file is run by CPythonProxy

(Why separate file for launching? I want to have clean global scope
in toplevel __main__ module (because that's where user scripts run), but backend's global scope
is far from clean.
I could also do python -c "from backend import MainCPythonBackend: MainCPythonBackend().mainloop()", but looks like this
gives relative __file__-s on imported modules.)
"""

if __name__ == "__main__":
    import platform
    import sys
    import thonny
    from thonny.plugins.cpython.cpython_backend import MainCPythonBackend

    if platform.system() == "Darwin":
        import os

        try:
            os.getcwd()
        except Exception:
            print(
                "\nNB! Potential problems detected, see\nhttps://github.com/thonny/thonny/wiki/MacOSX#catalina\n",
                file=sys.stderr,
            )

    if not sys.version_info > (3, 5):
        print(
            "Thonny only supports Python 3.5 and later.\n"
            + "Choose another interpreter from Tools => Options => Interpreter",
            file=sys.stderr,
        )
        sys.exit()

    thonny.prepare_thonny_user_dir()
    thonny.configure_backend_logging()
    thonny.set_dpi_aware()

    target_cwd = sys.argv[1]
    MainCPythonBackend(target_cwd).mainloop()
