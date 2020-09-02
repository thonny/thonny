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

    import logging
    import os.path

    # set up logging
    logger = logging.getLogger("thonny")
    logger.propagate = False
    logFormatter = logging.Formatter("%(levelname)s: %(message)s")
    file_handler = logging.FileHandler(
        os.path.join(thonny.THONNY_USER_DIR, "backend.log"), encoding="UTF-8", mode="w"
    )
    file_handler.setFormatter(logFormatter)
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)

    # Don't litter user stderr with thonny logging
    # TODO: Can I somehow send the log to front-end's stderr?
    """
    stream_handler = logging.StreamHandler(stream=sys.stderr)
    stream_handler.setLevel(logging.INFO);
    stream_handler.setFormatter(logFormatter)
    logger.addHandler(stream_handler)
    """

    logger.setLevel(logging.INFO)

    import faulthandler

    fault_out = open(os.path.join(thonny.THONNY_USER_DIR, "backend_faults.log"), mode="w")
    faulthandler.enable(fault_out)

    # Disable blurry scaling in Windows
    thonny.set_dpi_aware()

    target_cwd = sys.argv[1]
    MainCPythonBackend(target_cwd).mainloop()
