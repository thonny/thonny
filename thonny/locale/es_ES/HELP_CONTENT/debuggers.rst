Uso de depuradores
==================

Si quieres ver cómo Python ejecuta tu programa paso a paso, entonces debes ejecutarlo en el "modo de depuración" o "más rápido". También puedes ejecutarlo con `Birdseye <birdseye.rst>`_ y
explorar los pasos de ejecución más tarde.

Modo "mejor"
------------

Este modo se recomienda para los principiantes totales.

Comience seleccionando *Depura el guión actual (mejor)* en el menú *Ejecutar* o pulsando Ctrl+F5 (`en XFCE necesitas usar Shift+Ctrl+F5 <https://askubuntu.com/questions/92759/ctrlf5-in-google-chrome-in-xfce>`__). 
Verás que la primera sentencia del programa se resalta y no ocurre nada más. 
En este modo necesita notificar a Thonny que está listo para dejar que Python haga el siguiente paso. 
Para ello tienes dos opciones principales:

*Ejecutar → Saltando* (o F6) realiza pasos grandes, es decir, ejecuta el código resaltado y resalta la siguiente parte del código.
*Ejecutar → Entrando* (o F7) intenta dar pasos más pequeños. Si el código resaltado está hecho de partes más pequeñas (declaraciones o expresiones), entonces la primera de ellas se resalta y Thonny espera el siguiente comando. Si ha llegado a un componente del programa que no tiene subpartes (por ejemplo, un nombre de variable) entonces *Paso a* funciona como *Paso a*, es decir, ejecuta (o evalúa) el código.

Si ha entrado en las profundidades de una sentencia o expresión y quiere avanzar más rápido, entonces puede usar *Ejecutar → Saliendo*, que ejecuta el código actualmente resaltado y todas las partes siguientes del programa en el mismo nivel.
Hay un comando un poco similar llamado *Reanudar*, que ejecutará el comando sin salirse hasta que se complete (o hasta el siguiente punto de interrupción, ver más abajo).

Si accidentalmente hiciste un gran paso y pasaste por encima de una parte interesante del código, puede **retroceder el paso** seleccionando *Ejecutar → Volver atrás*.
Thonny mostrará el estado del programa tal y como estaba antes del último paso.
Ahora puede continuar con pequeños pasos y hacer zoom en este trozo de código.
(¿Cómo funciona? Incluso cuando usted da un gran paso, Thonny guarda todos los estados intermedios del programa, que puede reproducir después de dar el paso atrás). 

Si quieres llegar a una parte específica del código, entonces puedes acelerar el proceso colocando el cursor en esa línea y seleccionando *Ejecutar → Ejecutar hasta el cursor*. 
Esto hace que Thonny se desplace automáticamente hasta esa línea. A partir de ahí puede tomar el comando.

Si tiene activados los números de línea del editor (Herramientas → Opciones → Editor), entonces puede también usar **puntos de ruptura**.
Cuando hace doble clic junto a una sentencia en el margen izquierdo del editor, un punto aparece.
Cuando ahora inicie el depurador, no se detendrá antes de la primera sentencia, sino que correrá hasta la declaración marcada con el punto, también conocido como punto de interrupción.
Puede colocar tantos puntos de interrupción en sus programas como necesarios.
Los puntos de interrupción se pueden eliminar haciendo doble clic en los puntos.


Modo "rápido"
-------------

Cuando tus programas crecen, puedes notar que dar grandes pasos con el depurador más bonito lleva a veces mucho tiempo.
Esto se debe a que las sutilezas (por ejemplo, la posibilidad de pasar por la evaluación de expresiones y dar pasos atrás) requieren una maquinaria pesada y lenta.

Con *Depura el script actual (rápidamente)* se pierden las sutilezas pero se puede recorrer el programa mucho más rápido.
Puede usar los mismos comandos (excepto "Paso atrás") que con un depurador más agradable.
Este es el estilo de depuración al que la mayoría de los programadores programadores profesionales están acostumbrados.


Diferentes estilos para mostrar la pila de llamadas
---------------------------------------------------

Por defecto, Thonny utiliza ventanas apiladas para presentar la pila de llamadas.
Esto da una buena intuición sobre el concepto, pero puede llegar a ser engorroso de usar.
Por ello, desde la versión 3.0 se puede elegir entre dos estilos diferentes para presentar la pila de llamadas.
En "Herramientas → Opciones → Ejecutar y Depura" se puede cambiar a un estilo más tradicional con una vista separada para presentar y cambiar los marcos de llamadas.
Tenga en cuenta que ambos estilos se pueden utilizar con ambos modos de depuración.

Birdseye
--------

El comando *Depura el script actual (birdseye)* se explica en una `página separada <birdseye.rst>`_
