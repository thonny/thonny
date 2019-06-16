Shell 
=====

Shell is the primary means for running and communicating with your program. It mostly looks like
official Python REPL (Read-Evaluate-Print Loop), but there are some differences and extra features.

Python commands
---------------
Just like the official Python REPL, Thonny's Shell accepts Python expressions and statements, both
single-line and multiline. If you press ENTER, then Thonny uses some heuristics to predict 
whether you wanted to submit the command or continue typing the command on the next line. 
If you want to submit the command but Thonny offers you a new line, then check whether you forgot
to close some parentheses.   

Magic commands
--------------
If you select "Run => Run current script" or press F5, then you'll see how Thonny inserts a command
starting with ``%Run`` into Shell. Commands starting with ``%`` are called *magic commands* (just 
like in `IPython <https://ipython.org/>`_ and they perform certain actions, which can't be
(easily) expressed as Python commands. Thonny's magic commands usually have
corresponding menu commands so you don't need write them by hand.

System commands
---------------
If you need to quickly run a simple system command then you don't have to start a Terminal. Just
prefix the command with ``!`` (eg. ``!pytest my-script.py``) and enter it into Thonny's shell.

Command history
---------------
If you want to issue same or similar command several times, then you don't need to type it each time --
use Up-key to fetch previous command from the command history. Another Up-press brings you the command
before that and so on. Use Down-key to move in the opposite direction in history.  

Colored output
--------------
If you have your Shell in Terminal emulation mode (see Tools => Options => Shell), then you can
use `ANSI codes <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ to produce colored output. 

Try the following example:

.. code::

	print("\033[31m" + "Red" + "\033[m")
	print("\033[1;3;33;46m" + "Bright&bold italic yellow text on cyan background" + "\033[m")
	 
You may want to use a package like `colorama <https://pypi.org/project/colorama/>`_ for producing 
the color codes.

Overwriting output lines
------------------------
Proper terminal emulators support ANSI codes which allow writing to arbitrary positions in the terminal
screen. Thonny's Shell is not so capable, but it does support a couple of simpler tricks.

Try the following program:

.. code::

	from time import sleep
	
	for i in range(100):
	    print(i, "%", end="")
	    sleep(0.05)
	    print("\r", end="")
	
	print("Done!")
	
The trick relies on character ``"\r"``, which causes the output cursor to go back to the beginning of current 
line, so that next print will overwrite previously printed text. Note how we used ``print(..., end="")``
to avoid creating a new line.

The cousin of ``"\r"`` is ``"\b"``, which moves the output cursor leftwards by one character. 
It doesn't do anything if it is already at the first position on the line. 
		
Making sound
------------
When Shell is in terminal emulation mode, then you can produce a bell (or "ding") sound by outputting
character ``"\a"``.

Displaying images
-----------------
You can display images in the shell by encoding your GIF or PNG file with Base64 and printing it 
as single-line data URL:

.. code::

	print("data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==")
		
 
Plotting series of numbers
--------------------------
You can visualize series of numbers printed to the Shell by using the `Plotter <plotter.rst>`_.
