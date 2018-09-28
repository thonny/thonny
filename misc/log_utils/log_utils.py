"""
For parsing user action logs
"""

import ast
from time import strptime


def parse_log_file(filename):
    f = open(filename, encoding="UTF-8")
    events = []
    for line in f:
        events.append(parse_log_line(line))

    f.close()
    return events


def parse_log_line(line):
    split_pos = line.rfind(" at ")
    assert split_pos > 0
    left = line[0:split_pos]
    right = line[split_pos + 4 :].strip()

    tree = ast.parse(left, mode="eval")
    assert isinstance(tree, ast.Expression)
    assert isinstance(tree.body, ast.Call)

    attributes = {
        "event_kind": tree.body.func.id,
        "event_time": strptime(right, "%Y-%m-%dT%H:%M:%S.%f"),
    }

    for kw in tree.body.keywords:
        attributes[kw.arg] = ast.literal_eval(kw.value)

    return attributes


def get_log_file_time(filename):
    """
    Go from  2014-10-30_10-16-08
    to       2014-10-30T10:16:08
    """

    chars = list(filename[:19])
    try:
        assert chars[10] == "_" and chars[13] == "-" and chars[16] == "-"
    except Exception:
        print(filename)
    chars[10] = "T"
    chars[13] = ":"
    chars[16] = ":"
    return "".join(chars)
