Comprender los errores
======================

Si tu programa da errores o resultados erróneos, no intentes arreglar nada antes de entender el problema.
Puedes leer una historia más larga en `otra página <debugging.rst>`__, aquí tienes una lista de comprobación rápida para poner en marcha tus ideas.

¿Tienes miedo?
--------------

No lo tengas.
Los mensajes de error están pensados para ayudar.
Si recibes un error no significa que seas una mala persona.
Y no, no has roto el ordenador.
Aunque los mensajes de error pueden parecer un bloque de galimatías al principio, con la práctica es posible extraer información útil de ellos.

¿En qué parte del código se produjo el error?
---------------------------------------------

Los mensajes de error en Thonny tienen enlaces que te llevan al lugar del código que causó el error.
En el caso de varios enlaces, el último suele ser el más relevante.

Si el error ocurrió dentro de una función, entonces el mensaje tiene varios enlaces. 
Intente hacer clic en ellos uno a uno de arriba a abajo y verá cómo Python llegó al lugar del error.
Este conjunto de enlaces se llama *el seguimiento de la pila*.

¿Qué significa el error?
------------------------

La última línea del bloque de error dice cuál fue el problema para Python.
Cuando intentes comprender el mensaje, no olvides el contexto y trata de relacionar algunas partes del mensaje con el lugar vinculado en el código.
A veces el Asistente de Thonny puede explicar el error en términos más sencillos, a veces hay que hacer una búsqueda en internet del mensaje (no olvides añadir "Python" a la búsqueda). 

¿Qué había dentro de las variables en el momento del error?
-----------------------------------------------------------

¡Abre la vista de variables y mira tú mismo!
Si el error ocurrió dentro de una función, entonces puedes ver las variables locales haciendo clic en el seguimiento de la pila.

¿Cómo llegó el programa a este estado?
--------------------------------------

Vea `la página sobre depuración <debugging.rst>`_ o `la página sobre el uso de los depuradores de Thonny <debuggers.rst>`_.
