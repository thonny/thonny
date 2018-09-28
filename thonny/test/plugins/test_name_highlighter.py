import tkinter
from typing import Sequence, Set  # @UnusedImport

from thonny.plugins.highlight_names import VariablesHighlighter

TEST_STR1 = """def foo():
    foo()
    pass
def boo(narg):
    foo = 2  # line 5
    boo = foo + 4
    print(narg + 2)
for i in range(5):
    boo()
narg = 2  # line 10
def bar():
    x + x
def blarg():
    x = 2
"""
# tuple of tuples, where an inner tuple corresponds to a group of insert positions
# that should produce the same output (corresponding expected output is in the
# expected_indices tuple at the same index)
#
# consider TEST_STR1:
#
# The first group is four indices, where we would expect the two locations of the name "foo"
# to be returned. Those expected two locations are specified at index 0 of tuple expected_indices.
#
# Second tuple is a group of one index, where we would expect output with the locations for "boo"
# And if the insert location is at "pass", we would expect an empty set for output
CURSOR_POSITIONS1 = (
    ("1.4", "1.5", "1.7", "2.5"),
    ("4.6",),
    ("3.4",),
    ("5.7", "6.12"),
    ("4.10", "7.11"),
    ("10.2",),
    ("12.5", "12.9"),
    ("14.5",),
)

EXPECTED_INDICES1 = [
    {("1.4", "1.7"), ("2.4", "2.7")},
    {("4.4", "4.7"), ("9.4", "9.7")},
    set(),
    {("5.4", "5.7"), ("6.10", "6.13")},
    {("4.8", "4.12"), ("7.10", "7.14")},
    {("10.0", "10.4")},
    {("12.4", "12.5"), ("12.8", "12.9")},
    {("14.4", "14.5")},
]  # type: Sequence[Set[Sequence[str]]]

TEST_STR2 = """import too
def foo():
    foo = too + 4
    x = foo + bow
# 5
class TestClass:
    def foo(self):
        pass
    def add3(self):
        self.foo()  # 10
        foo()
"""
CURSOR_POSITIONS2 = (("1.8", "3.10"), ("2.4", "2.5", "11.10"), ("3.5", "4.9"))
EXPECTED_INDICES2 = (
    {("1.7", "1.10"), ("3.10", "3.13")},
    {("2.4", "2.7"), ("11.8", "11.11")},
    {("3.4", "3.7"), ("4.8", "4.11")},
)

TEST_GROUPS = (
    (CURSOR_POSITIONS1, EXPECTED_INDICES1, TEST_STR1),
    (CURSOR_POSITIONS2, EXPECTED_INDICES2, TEST_STR2),
)


def test_all():
    for i, test in enumerate(TEST_GROUPS):
        print("Running test group %d: " % (i + 1))
        _assert_returns_correct_indices(test[0], test[1], test[2])


def _assert_returns_correct_indices(insert_pos_groups, expected_indices, input_str):
    text_widget = tkinter.Text()
    text_widget.insert("end", input_str)

    nh = VariablesHighlighter(text_widget)
    for i, group in enumerate(insert_pos_groups):
        for insert_pos in group:
            text_widget.mark_set("insert", insert_pos)

            actual = nh.get_positions()
            expected = expected_indices[i]

            assert actual == expected, (
                "\nInsert position: %s"
                "\nExpected: %s"
                "\nGot: %s" % (insert_pos, expected, actual)
            )
        print("\rPassed %d of %d" % (i + 1, len(insert_pos_groups)), end="")
    print()
