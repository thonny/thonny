Técnicas de depuración
======================

Si tu programa no funciona correctamente, no te asustes. Tienes varias posibilidades para arreglar la situación. Por ejemplo:

* Dejar que otra persona lo arregle.
* Cambiar *algo* en el código y volver a intentarlo.
* Aborda el problema en dos fases: 1) diagnosticar el problema y 2) solucionarlo.

Pedir ayuda puede ser una muy buena idea, pero no te dará esta dulce sensación de logro. De todos modos, es mejor no usar esto sin antes hacer un esfuerzo por tu cuenta.

Si tus programas son pequeños, puede que te toque el premio gordo cambiando algo al azar e intentándolo de nuevo (repite muchas veces), pero perderás aunque ganes ya que no aprenderás nada.

Si quieres llegar a ser bueno en la programación, entonces realmente necesitas abordar el problema de forma más sistemática. Esto significa, entre otras cosas, que tienes que identificar la razón por la que tu programa se comporta mal antes de intentar arreglarlo. El proceso de encontrar el origen del problema se llama *depuración*.

Rastrear el flujo del programa / pensar con Python
--------------------------------------------------

Lo más probable es que tu programa no esté del todo mal. Puede haber un error tipográfico en alguna parte o que hayas pasado por alto o malinterpretado algo. *¡NB! No te acostumbres a pensar que Python te ha malinterpretado -- es una máquina que ni siquiera intenta entenderte*. La clave de la depuración es encontrar precisamente dónde y cuándo tus suposiciones sobre el comportamiento del programa divergen del comportamiento real.

Si su programa imprime una respuesta final incorrecta, esto le dice algo sobre el comportamiento del programa, pero normalmente no es suficiente para localizar el problema con precisión. También debe comprobar qué **pasos intermedios** se ajustan a sus suposiciones y cuáles no.

Una técnica obvia (y muy útil) es añadir **sentencias de impresión adicionales** en el código, que te digan dónde está Python y qué ha logrado hasta ahora, por ejemplo

.. code::

       print("amigos antes del bucle for", amigos)

NOTA. A veces es necesario introducir nuevas variables y dividir expresiones complejas en partes más pequeñas para imprimir información más detallada.

Aunque la *depuración con prints* es utilizada incluso por los profesionales (pueden llamarlo *logging*), hay una alternativa, que es más cómoda en la mayoría de los casos. Se llama **recorrer el código** y es el pan de cada día de Thonny. Pasa al capítulo `Uso de depuradores <debuggers.rst>`_ para saber más.

Revisión de código
------------------

Otra técnica útil es la revisión del código. Es algo similar a trazar el flujo del programa, pero lo haces en tu cabeza y estás tratando de ver la imagen más grande en lugar de seguir pequeños pasos.

Observa cada una de las sentencias de tu código e intenta comprender su propósito y cómo se relaciona con tu tarea.

Para cada **variable**, pregúntate:

* ¿El nombre de la variable revela su propósito? ¿Es mejor nombrarla en singular o en plural?
* ¿Qué tipo de valores puede contener esta variable? ¿Cadenas, enteros, listas de cadenas, listas de flotantes, ...?
* ¿Cuál es la función de la variable? ¿Está destinada a actualizarse repetidamente para que eventualmente contenga información útil? ¿Está pensada para utilizar la misma información en varios lugares y reducir el copiado? ¿Algo más?

Para cada **bucle**, pregúntate:

* ¿Cómo sabes que el bucle es necesario?
* ¿Cuántas veces debe ejecutarse el cuerpo del bucle? ¿De qué depende esto?
* ¿Qué código debe estar dentro del bucle y cuál fuera?
* ¿Qué debe hacerse antes del bucle y qué debe hacerse después?

Para cada **expresión** compleja pregúntese

* ¿En qué orden deben estar los pasos de evaluación de esta expresión? ¿Está Python de acuerdo con esto? En caso de duda, utilice el depurador o introduzca variables de ayuda y divida la expresión en partes más pequeñas.
* ¿Qué tipo de valor debería salir de esta expresión? ¿Cadenas? ¿Lista de cadenas?

También es posible que te falten algunas partes importantes en tu programa:

* ¿Su tarea requiere tratar diferentes situaciones de forma diferente? Si la respuesta es afirmativa, es probable que necesite una sentencia if.
* ¿La tarea requiere hacer algo varias veces? En caso afirmativo, probablemente necesite un bucle.

¿Sigue perdiendo el hilo?
-------------------------

"Encuentre el lugar donde se rompen sus suposiciones" - esto es definitivamente más fácil de decir que de hacer. En el caso de programas complejos es fácil llegar a la situación en la que ya no estás seguro de lo que asumes y de por qué empezaste con esto de la programación.

En este caso es útil simplificar tu tarea tanto como sea posible y tratar de implementar el problema más simple primero. Toma un nuevo editor y empieza desde cero o copia el código existente y desecha todo lo que no sea esencial para el problema. Por ejemplo, puedes asumir que el usuario es cooperativo y que siempre introduce datos "buenos". Si la tarea requiere hacer algo repetidamente, entonces elimine la parte "repetidamente", si la tarea implica una condición compleja para hacer algo, haga la condición más simple, etc.

Después de resolver el problema simplificado, estarás mucho mejor equipado para resolver también la tarea original.
