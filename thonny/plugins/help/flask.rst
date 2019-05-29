`Home <index.rst>`_

Web development with Flask
==========================

`Flask <http://flask.pocoo.org/>`__ is a popular framework for building web apps in Python.

Flask tutorials usually instruct running Flask programs by entering some commands in Terminal, 
but this may intimidate some beginners. Thonny tries make things easeir and allows running Flask programs
just like any other program (with simple F5). If it detects you are running a Flask program, then it executes
it with some lines of code appended, which start the development server with suitable settings:

.. code::

	...
	app.run(threaded=False, debug=False, use_reloader=False)

If you want more control over the settings then you should call the ``run``-method yourself,
eg:


.. code::

	...
	if __name__ == "__main__":
		app.run(threaded=False, debug=True, use_reloader=True)

