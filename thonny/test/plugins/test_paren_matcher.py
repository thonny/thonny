import tkinter

from thonny.plugins.paren_matcher import ParenMatcher

TEST_STR1 = """age = int(input("Enter age: "))
if age > 18:
    l = ["H", "I"]
    print(l)
else:
    print("Hello!", end='')
    print("What's your name?")
"""


def test_regular_closed():
    insert_pos_groups = (
        ("1.9", "1.10", "1.13", "1.31"),
        ("1.30", "1.29", "1.25", "1.15"),
    )
    expected_indices = (("1.9", "1.30", []), ("1.15", "1.29", []))

    text_widget = tkinter.Text()
    text_widget.insert("end", TEST_STR1)

    matcher = ParenMatcher(text_widget)
    matcher.text = text_widget
    for i, group in enumerate(insert_pos_groups):
        for insert_pos in group:
            text_widget.mark_set("insert", insert_pos)

            actual = matcher.find_surrounding("1.0", "end")
            expected = expected_indices[i]

            assert actual == expected, "\nExpected: %s\nGot: %s" % (expected, actual)
        print("\rPassed %d of %d" % (i + 1, len(insert_pos_groups)), end="")
