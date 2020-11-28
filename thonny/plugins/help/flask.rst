Web development with Flask
==========================

`Flask <https://palletsprojects.com/p/flask/>`__ is a popular framework for building web apps in Python.

Flask tutorials usually instruct running Flask programs by entering some commands in Terminal, 
but this may intimidate some beginners. Thonny tries make things easeir and allows running Flask programs
just like any other program (with simple F5). If it detects you are running a Flask program, then it executes
it with some lines of code appended, which start the development server with suitable settings.

Debugging
---------
If you want to step through your Flask program, set a breakpoint inside some function and invoke 
the debugger (both nicer and faster work, but faster is ... faster). Reload your page and start 
stepping inside the function. You may want to turn off "Frames in separate windows" (Tools => Options
=> Run & Debug) for more comfortable operation. 

Details
-------
Thonny will start the development server approximately like this:

.. code::

	os.environ["FLASK_ENV"] = "development"
	app.run(threaded=False, use_reloader=False, debug=False)

``threaded=False`` is used because Thonny's debugger supports only single-threaded programs,
``use_reloader=False`` is used because 
`automatic reloading is not reliable when Flask is started like this <https://flask.palletsprojects.com/en/1.0.x/api/#flask.Flask.run>`_
and ``debug=False`` is used because this seems to cause less "Address already in use" errors.

If you want more control over the settings then you should call the ``run``-method yourself,
eg:

.. code::

	...
	if __name__ == "__main__":
		app.run(port=5005, threaded=False, use_reloader=True, debug=True)

In this case Thonny won't add anything to your code.
