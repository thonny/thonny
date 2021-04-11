에러에 대한 이해
====================

If your program gives errors or wrong results then don't try to fix anything before understanding
the problem. You can read a longer story on `another page <debugging.rst>`__,
here is a quick checklist for getting your ideas going.

혹시 두려우신가요?
---------------
Don't be! Error messages are meant to help. If you get an error it doesn't mean you are a bad 
person. And no, you did not break the computer. Although error messages may seem like block of 
gibberish af first, with practice it is possible to extract useful information from them.

에러가 발생한 곳은 어디인가요?
-------------------------------------
Error messages in Thonny have link(s)
which bring you to the place in code which caused the error. In case of several links, the last
one is usually most relevant.

If the error happened inside a function, then the message has several links. 
Try clicking them one-by-one from top to bottom and you'll see how Python arrived to the place
of error. Such set of links is called *the stack trace*.

어떤 것을 의미하는 에러인가요?
-------------------------
The last line of the error block says what was the problem for Python.
When trying to comprehend the message, don't forget the context and try to match
some parts of the message with the linked place in code. Sometimes Thonny's Assistant can explain 
the error in simpler terms, sometimes you need to make an internet search for the message
(don't forget to add "Python" to the search). 

에러 상황에서의 변수는 어떤 값을 가지고 있나요?
---------------------------------------------------------
Open the variables view and see 
yourself! If the error happened inside a function then you can see local variables by clicking the 
links in the stack trace.

프로그램이 그 상태에 어떻게 도달했나요?
---------------------------------------
See `the page about debugging <debugging.rst>`_ or `the page about using Thonny's debuggers <debuggers.rst>`_.
