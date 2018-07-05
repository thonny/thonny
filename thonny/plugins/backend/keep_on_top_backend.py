from logging import info
import sys

def hook(*args, **kw):
    info("args: %r, kw, %r", args, kw)
    raise ImportError()

def load_plugin(vm):
    sys.path_hooks.insert(0, hook)
    info(repr(sys.path_hooks))