import tkinter

from thonny.plugins.global_local_marker import GlobLocHighlighter

TEST_STR1 = """num_cars = 3
def foo():
    print(num_cars + num_cars)
def too():
    num_cars = 4
    print(num_cars + num_cars)
def joo():
    global num_cars
    num_cars = 2
"""


def test_regular_closed():

    expected_global = {('1.0', '1.8'),
                       ('2.4', '2.7'),
                       ('3.4', '3.9'),
                       ('3.10', '3.18'),
                       ('3.21', '3.29'),
                       ('6.4', '6.9'),
                       ('4.4', '4.7'),
                       ('7.4', '7.7'), }
    expected_local = {('5.4', '5.12'),
                      ('6.10', '6.18'),
                      ('6.21', '6.29'),
                      ('8.11', '8.19'),
                      ('9.4', '9.12'),
                      }

    text_widget = tkinter.Text()
    text_widget.insert("end", TEST_STR1)

    highlighter = GlobLocHighlighter(text_widget)

    actual_global, actual_local = highlighter.get_positions()

    assert actual_global == expected_global
    assert actual_local == expected_local
    print("Passed.")


def run_tests():
    test_regular_closed()

if __name__ == "__main__":
    print("Test input: ")
    print(TEST_STR1)
    run_tests()