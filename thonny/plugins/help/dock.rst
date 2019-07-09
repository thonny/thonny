Docking user windows
====================
When developing your Turtle (or other Tkinter) programs, you may want to look at the window
from last run while fixing something in the code. If you have large or several screens, 
it's not hard to fit your window next to Thonny's, 
but on the next run the window manager may position it somewhere else and you need
to arrange the windows again. 
 
**Dock user windows** in the **Run menu** is meant to help you in this situation. If you 
check it and run your Tkinter program, Thonny performs following magic tricks:

* It remembers where you position your window. Next time it places the window at the same position.
* It makes your window stay on top even if you click on Thonny window to start modifying the code. In fact, after your Tkinter window becomes visible, Thonny automatically focuses its own window so that you can continue editing the script without grabbing the mouse. When you're done, just press F5 again and old window gets replaced with the new one.
 
*Staying on top currently does not work with turtle programs on macOS (https://github.com/thonny/thonny/issues/798)*
