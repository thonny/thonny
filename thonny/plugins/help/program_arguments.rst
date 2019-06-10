Running your programs with command line arguments 
=================================================

When you are editing *my_program.py* and press F5, Thonny constructs a magic command 
``%Run my_program.py`` and sends it to the shell, which asks Thonny's back-end to run
that script.

When you go to shell and take the ``%Run`` command back (with up-arrow), you can add
*command line arguments* to it. For example change the command to 
``%Run my_program.py first second`` and press ENTER.

When you run your program like this, you can access the arguments from ``sys.argv``:

.. code::

    import sys
    print(sys.argv)

Fixing the command line arguments
---------------------------------
If you need to use same set of arguments several times, it may become tedious to construct
the ``%Run`` by hand. In this case check **Program arguments** in the **View menu**. This 
opens a small entry box next to the toolbar buttons. From now on, everything you type in this
box gets appended to ``%Run <script name>`` each time you press F5.
 	