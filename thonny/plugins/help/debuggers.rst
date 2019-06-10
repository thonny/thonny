Using debuggers
==========================
If you want to see how Python executes your program step-by-step then you 
should run it in "nicer" or "faster" *debug-mode*. You can also run it with `Birdseye <birdseye.rst>`_ and
explore the execution steps later.

"Nicer" mode
------------
This mode is recommended for total beginners.

Start by selecting *Debug current script (nicer)* from the *Run* menu or by pressing 
Ctrl+F5 (`in XFCE you need to use Shift+Ctrl+F5 <https://askubuntu.com/questions/92759/ctrlf5-in-google-chrome-in-xfce>`__). 
You'll see that first statement of the program gets highlighted and nothing more happens. 
In this mode you need to notify Thonny that you're ready to let Python make the next step. 
For this you have two main options:

* *Run → Step over* (or F6) makes big steps, ie. it executes the highlighted code and highlights the next part of the code.
* *Run → Step into* (or F7) tries to make smaller steps. If the highlighted code is made of smaller parts (statements or expressions), then first of these gets highlighted and Thonny waits for next command. If you have reached to a program component which doesn't have any sub-parts (eg. variable name) then *Step into* works like *Step over*, ie. executes (or evaluates) the code.

If you have stepped into the depths of a statement or expression and want to 
move on faster, then you can use *Run → Step out*, which executes 
currently highlighted code and all following program parts on the same level.
There is a bit similar command called *Resume*, which will run the command without stepping
till it completes (or till next breakpoint, see below).

If you accidentally made a big step and stepped over an interesting piece of code,
you can **take back the step** by selecting *Run → Step back*. Thonny will show
the state of program as it was before the last step. Now you can continue with small steps
and zoom into this piece of code. (How does it work? Even when you take a big step, Thonny
saves all intermediate program states, which it can replay after you take the step back.) 

If you want to reach a specific part of the code, then you can speed up the 
process by placing your cursor on that line and selecting *Run → Run to cursor*. 
This makes Thonny automatically step until this line. You can take the command from there.

If you have editor line numbers enabled (Tools → Options → Editor), then you can 
also use **breakpoints**. When you double click next to a statement in the editor left margin, a dot
appears. When you now start the debugger, it doesn't stop before first statement but runs to the 
statement marked with the dot a.k.a breakpoint. You can place as many breakpoints to your programs as 
required. Breakpoints can be removed by double clicking on the dots.


"Faster" mode
-------------
When your programs grow bigger, you may notice that taking big steps with nicer debugger take sometimes long time.
It is because the niceties (eg. possibility of stepping through expression evaluation and taking back steps) 
require heavy and slow machinery.

With *Debug current script (faster)* you lose the niceties but you can step through your program much faster.
You can use same commands (except "Step back") as with nicer debugger. This is the debugging style most professional
programmers are accustomed with.


Different styles for showing the call stack
-------------------------------------------
By default Thonny uses stacked windows for presenting the call stack. This gives good intuition about 
the concept, but it may become cumbersome to use. Therefore, since version 3.0 one can choose between 
two different styles for presenting call stack. In “Tools → Options → Debugger” you can switch to more 
traditional style with a separate view for presenting and switching call frames. Note that both 
styles can be used with both debugging modes.

Birdseye
--------
Command *Debug current script (Birdseye)* is explained at a `separate page <birdseye.rst>`_
 