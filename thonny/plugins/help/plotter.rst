Plotter
==========================
Plotter is an add-on for the Shell, which extracts numbers from 
the program output and displays them as line chart. It can be useful for 
observing live sensor data coming from attached devices or even for analyzing 
static data (if you don't bother using more serious tools). It is inspired
by `Mu Python editor <https://codewith.mu/>`__. 

You can open it from the "View" menu or from the Shell's context menu.

For an examply try following program (you can stop it with Ctrl+C or with 
"Stop / reset" button on the toolbar):

.. code::

	from time import sleep
	from random import randint
	
	p1 = 0
	while True:
	    p1 += randint(-1, 1)
	    p2 = randint(-10, 10)
	    print("Random walk:", p1, " just random:", p2)
	    sleep(0.05)

When you run it with Plotter opened, you'll see a line chart with two series forming.
Each column on the chart corresponds to one line in the Shell. 
The rightmost column on the chart always corresponds the bottom-most visible line in the shell,
even if you stop the program and scroll the text in the shell.

Plotter starts drawing when it detects at least two consecutive lines containing same pattern
of numbers and surrounding text. The numbers get plotted and the surrounding
text becomes the legend in the lower-right corner of the Plotter.

Speed of the animation
--------------------------------
Unless you are plotting a fixed number of lines, it is good idea not to flood the 
shell and plotter with data. This is why the example above makes a little pause 
(``sleep(0.05)``) before outputting next line.

Range of the y-axis
-------------------
Plotter tries to detect a suitable range for your plot without having to 
change it too often. For this reason it extends the range if required, but only
shrinks it at the start of a new series. 

If some outliers have made the range too large, then you can manually shrink 
it by waiting until the outliers are out of the picture and clicking on the Plotter. 

If you want make the range larger (or just compare your data against certain values),
then simply include suitable constant(s) in your data lines, eg: 
``print(0, measure1, measure2, 100)``.
