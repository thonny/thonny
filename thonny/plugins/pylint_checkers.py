import astroid

from pylint.checkers import BaseChecker
from pylint.interfaces import IAstroidChecker


class FileNamingChecker(BaseChecker):
    __implements__ = IAstroidChecker

    name = "file-naming"
    priority = -1
    msgs = {
        "W7401": (
            "Script shadows a library module.",
            "non-unique-returns",
            "All constants returned in a function should be unique.",
        )
    }
    options = (
        (
            "ignore-ints",
            {
                "default": False,
                "type": "yn",
                "metavar": "<y_or_n>",
                "help": "Allow returning non-unique integers",
            },
        ),
    )
