Debugging techniques
====================

If your program is not working properly then don't panic. You have several
possibilities for fixing the situation. For example: 

* Let somebody else fix it.
* Change *something* in the code and try again. 
* Approach the problem in two phases: 1) diagnosing the problem and 2) fixing it.

Asking for help may be a very good idea, but it won't give you this sweet sense of accomplishment.
Anyway, it's better not to use this without first putting in some effort on your own.

If your programs are small, then you may hit the jackpot by changing something randomly and 
trying again (repeat many times), but you'll lose even if you win as you won't learn anything.

If you want to become good in programming, then you really need to approach the problem more
systematically. Among other things, this means that you need to pinpoint the reason your program misbehaves
before attempting to fix it. The process of finding the source of the problem is called *debugging*.

Tracing the program flow / thinking along with Python
------------------------------------------------------
Most likely your program isn't entirely wrong. There may be a typo somewhere or you overlooked 
or misunderstood something. *NB! Don't get into the habit of thinking that Python misunderstood you -- it
is a machine that doesn't even try to understand you.* The key to debugging is finding out precisely where
and when your assumptions about program behavior diverge from the actual behavior.

If your program prints out wrong final answer then this tells you something about
the program behavior, but it is usually not enough to locate the problem precisely. You need to also check 
which of the **intermediate steps** align with your assumptions and which don't.

One obvious (and very useful) technique is to add **extra print statements** into the code, which tell you
where Python is and what it has accomplished so far, eg. 

.. code::

	print("friends before for-loop", friends)

NB! Sometimes you need to introduce new variables and break complex expressions into smaller parts in order
to print out more detailed information.

Although print-debugging is used even by the professionals (they may call it *logging*), there is an alternative,
which is more comfortable in most cases. It's called **stepping through the code** and it is Thonny's bread and
butter. Move on to the chapter `Using debuggers <debuggers.rst>`_ to learn more.


Code review
---------------------
Another useful technique is code review. It is somewhat similar to tracing the program flow, but you do it in your
head and you are trying to see the bigger picture instead of following small steps.

Look at each of the statements in your code and try understand its purpose and how it relates to your task.

For each **variable** ask yourself:

* Does the name of the variable reaveal its purpose? Is it better to name it in singular or in plural?
* Which type of values can end up in this variable? Strings, integers, lists of strings, lists of floats, ...?
* What is the role of the variable? Is it meant to updated repeatedly so that it eventually contain useful information? Is it meant to use same information in several places and reduce copy-pasting? Anything else? 

For each **loop** ask yourself:

* How do you know the loop is required?
* How many times should the body of the loop be executed? What does this depend of?
* Which code should be inside the loop and which should be outside?
* What must be done before loop and what must be done after it?

For each complex **expression** ask yourself:

* In which order should be the steps of evaluating this expression? Does Python agree with this? When in doubt, use the debugger or introduce helper variables and break the expression into smaller parts.
* What type of value should come out of this expression? String? List of strings?

You may be also missing some important parts in your program:

* Does your task require treating different situations differently? If yes, then you probably need an if-statement.
* Does the task require doing something several times? If yes, then you probably need a loop.

Still losing track?
------------------------------
"Find you the place where your assumptions break" -- this is definitely easier said than done. In case of 
complex programs it's easy to arrive to the situation where you're not sure anymore what do you assume
and why did you start with this programming thing at all.

In this case it's useful to simplify your task as much as possible and try to implement the simpler problem
first. Take a new editor and either start from scratch or copy existing code and throw out everything that 
is not essential to the problem. For example, you can assume that user is cooperative and always inputs "good" data.
If the task requires doing something repeatedly, then throw out the "repeatedly" part, if the task involves
a complex condition for doing something, make the condition simpler etc.

After solving the simplified problem you are much better equipped to solve the original task as well.

 


