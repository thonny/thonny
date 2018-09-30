`Home <help.rst>`_

Debugging techniques
====================

If your program is not working properly then don't panic. You have several
possibilities for fixing the situation. For example: 

* Let somebody else fix it.
* Change *something* in the code and try again. 
* Approach the problem in two phases: 1) diagnosing the problem and 2) fixing it.

Asking for help may a very good idea, but it won't give you this sweet sense of accomplishment.
Anyway, it's better not to use this without first putting in some effort on your own.

If your programs are small, then you may hit the jackpot by changing something randomly and 
trying again (repeat many times), but you'll lose even if you win as you won't learn anything.

If you want to become good in programming, then you really need to approach the problem more
systematically. Among other things, this means that you need to pinpoint the reason your program misbehaves
before attempting to fix it. The process of finding the source of the problem is called *debugging*.

Thinking along with Python
--------------------------
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
butter. Move on to the chapter `"Running programs step-wise" <stepping.rst>`_ to learn more.

Losing track during debugging?
------------------------------
"Find you the place where your assumptions break" -- this is definitely easier said than done. In case of 
complex programs it's easy to arrive to the situation where you're not sure anymore what do you assume
and why did you start with this programming thing at all.

In this case it's useful to simplify your task as much as possible and try to implement the simpler problem
first. Take a new editor and either start from scratch or copy existing code and throw out everything that 
is not essential to the problem (eg. assume that user is cooperative and always inputs "good" data). After 
solving the simplified problem you are much better equipped to solve the original task as well.

 


