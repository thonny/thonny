import tkinter

from thonny.plugins.coloring import SyntaxColorer

TEST_STR1 = """def my_function():
    str1 = "aslas'"
    str2 = 'asdasd"asda
    str3 = '''asdasdasd
    asdas
    sdsds'''
"""


def test_open_closed_strings():

    text_widget = tkinter.Text()
    text_widget.insert("insert", TEST_STR1)

    colorer = SyntaxColorer(text_widget)
    colorer._update_coloring()

    open_ranges = text_widget.tag_ranges("open_string")
    closed_ranges = text_widget.tag_ranges("string") + text_widget.tag_ranges("string3")

    expected_open_ranges = {("3.11", "4.0")}
    expected_closed_ranges = {("2.11", "2.19"), ("4.11", "6.12")}

    open_ranges_set = {
        (str(open_ranges[i]), str(open_ranges[i + 1]))
        for i in range(0, len(open_ranges), 2)
    }
    closed_ranges_set = {
        (str(closed_ranges[i]), str(closed_ranges[i + 1]))
        for i in range(0, len(closed_ranges), 2)
    }

    assert open_ranges_set == expected_open_ranges
    assert closed_ranges_set == expected_closed_ranges
    print("test passed")
