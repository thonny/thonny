Assistant
=========

Assistant view assists you in two ways.

If your program ends with an error, it tries
to explain it in simpler terms and offers some advice for finding and fixing the underlying problem.

Sometimes your program may not work as you want even if you don't get any error messages. In this case
sometimes it helps to investigate the code carefully in order to spot certain bad smells or
peculiarities, which may lead to discovering the problem. There are two popular tools, which are used
for such investigations: `Pylint <pylint.pycqa.org>`_ and `Mypy <http://mypy-lang.org/>`_.

Mypy tries to detect certain contradictions in your code, for example when a function seems to
expect an integer argument, but your code calls it with a string. Pylint is not as good with this
kind of checks, but it can do many other checks. The number of Pylint checks is actually so large,
that most users let it skip many checks they don't find relevant. Thonny has picked a bunch of
Pylint checks, which are most likely releavant for beginners. If you want more checks, then you
could run Pylint on your code via command line. If you want to omit certain checks picked by Thonny,
then go to "Tools => Options => Assistant" and enter the name of the check. The list of all Pylint
checks can be seen at https://pylint.pycqa.org/en/latest/messages/messages_list.html
