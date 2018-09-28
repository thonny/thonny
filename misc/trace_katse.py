import sys


def trace(frame, event, arg):
    if "trace_katse" in frame.f_code.co_filename:
        print(frame, event, sys.exc_info())
    return trace


def f1():
    print(end="")
    print(end="")
    print(end="")
    print(end="")
    f2()
    print(end="")
    print(end="")
    print(end="")
    print(end="")


def f2():
    # pass
    1 / 0


sys.settrace(trace)

try:
    f1()
except:
    pass
