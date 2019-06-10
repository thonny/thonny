Comprendre les erreurs
======================

Si votre programme provoque des erreurs ou des résultats inadéquats ne tentez pas de réparer quoi que ce soit avant d'avoir compris
le problème. On peut en lire plus dans  `une autre page <debugging.rst>`__,
ici vous ne trouverez qu'un rapide revue pour faciliter la mise en place des idées.


Êtes-vous effaré ?
------------------

Il ne faut pas ! Les messages d'erreur sont faits pour aider. Si vous recevez un message d'erreur, ça ne veut pas dire que vous êtes mauvais.
Et non, vous n'avez pas cassé l'ordinateur. Bien que les messages d'erreur puissent ressembler à un sac de
nœuds à première vue, avec de la pratique il est possible d'en tirer des informations utiles.


À quel emplacement du code a eu lieu l'erreur ?
-----------------------------------------------

Les messages d'erreur dans Thonny ont des liens
qui vous amènent à l'emplacement du code qui a causé l'erreur. Dans le cas de plusieurs liens, le dernier
est généralement le plus pertinent.

Si l'erreur est arrivée dans une fonction, alors le message a plusieurs liens.
Essayez de cliquer sur ceux-ci un par une, du haut vers le bas, et vous verrez comment Python est arrivé à l'emplacement
de l'erreur. Un tel ensemble de liens se nomme *la trace de la pile*.


Que signifie l'erreur ?
-----------------------

La dernière ligne du bloc d'erreur dit quel a été le problème pour Python.
Quand vous essayez de comprendre le message, n'oubliez pas le contexte et essayez d'associer
certaines parties du message avec l'emplacement lié dans le code. De temps en temps l'Assistant de Thonny peut expliquer
l'erreur en termes plus simples, et parfois il faut effectuer une recherche sur Internet pour ce message
(n'oubliez pas d'ajouter le mot-clé "Python" pour la recherche).


Qu'y avait-il dans les variables au moment de l'erreur ?
--------------------------------------------------------

Ouvrez la vue des variables et voyez
par vous-même ! Si l'erreur s'est produite dans une fonction on peut voir les variables locales en cliquant les
liens dans la trace de la pile.


Comment le programme est-il arrivé dans cet état ?
--------------------------------------------------
Voir `la page au sujet du débogage <debugging.rst>`_ or `la page au sujet de l'utilisation des débogueurs de Thonny <debuggers.rst>`_.
