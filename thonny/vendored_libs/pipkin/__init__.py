import logging
import subprocess
import sys
import traceback
from typing import List, Optional

from pipkin.adapters import Adapter, DummyAdapter, create_adapter
from pipkin.common import ManagementError, UserError
from pipkin.session import Session

logger = logging.getLogger("pipkin")

__version__ = "1.0b7"


def error(msg):
    msg = "ERROR: " + msg
    print(msg, file=sys.stderr)

    return 1


def main(raw_args: Optional[List[str]] = None) -> int:
    from pipkin import parser

    args = parser.parse_arguments(raw_args)

    if args.verbose:
        logging_level = logging.DEBUG
    elif args.quiet:
        logging_level = logging.ERROR
    else:
        logging_level = logging.INFO

    logger.setLevel(logging_level)
    logger.propagate = True
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging_level)
    logger.addHandler(console_handler)

    args_dict = vars(args)

    try:
        adapter: Adapter
        if args.command == "cache":
            adapter = DummyAdapter()
        else:
            adapter = create_adapter(**args_dict)
        session = Session(adapter)
        try:
            command_handler = getattr(session, args.command)
            command_handler(**args_dict)
        finally:
            session.close()
    except KeyboardInterrupt:
        return 1
    except ManagementError as e:
        logger.error(traceback.format_exc())
        logger.error("SCRIPT: %r", e.script)
        logger.error("OUT=%r", e.out)
        logger.error("ERR=%r", e.err)
    except UserError as e:
        return error(str(e))
    except subprocess.CalledProcessError:
        # assuming the subprocess (pip) already printed the error
        return 1

    return 0
