Les techniques de débogage
==========================

Si votre programme ne fonctionne pas, pas de panique ! Vous avez plusieurs
possibilités pour corriger la situation. Par exemple :

* La faire corriger par quelqu'un d'autre ;
* Changer *quelque chose* dans le code et réessayer ;
* Approcher le problème en deux phases : 1) diagnostiquer le problème et 2) le réparer.

Demander de l'aide peut être une très bonne idée, mais elle ne vous procurera pas cette douce sensation de réussite.
De toute façon, c'est mieux de ne pas y recourir sans avoir d'abord tenté quelque chose vous-même.

Si vos programmes sont petits, vous pourriez toucher le jackpot en changeant quelque chose au hasard et
en recommençant (plusieurs fois), mais vous allez perdre même si vous gagnez, comme vous n'en aurez rien appris.

Si vous voulez devenir bon en programmation, il vous faut vraiment approcher le problème de façon plus
systématique. Entre autres choses, ça signifie que vous devez trouver la raison pour laquelle votre programme dysfonctionne
avant d'essayer de le corriger. Le processus consistant à trouver la source du problème se nomme *débogage*.


Tracer le flux du programme / penser en même temps que Python
-------------------------------------------------------------

Le plus souvent votre programme n'est pas entièrement mauvais. Il peut y avoir une faute de frappe quelque part ou vous avez manqué
ou mal compris quelque chose. *N.B. ! Ne prenez pas l'habitude de penser que Python vous a mal compris -- c'est une machine qui ne cherche pas à vous comprendre*. La clé du débogage c'est de trouver précisément où
et quand vos conceptions du comportement du programme divergent du comportement réel.

Si votre programme affiche une réponse finale fausse cela vous dit quelque chose au sujet
du comportement du programme, mais ce n'est généralement pas assez pour localiser le problème précisément. Il faut aussi vérifier
lesquelles des **étapes intermédiaires** sont en accord avec vos conceptions et lesquelles non.

Une technique évidente (et très utile) est d'ajouter des **directives d'affichage en plus** dans le code, qui vous diront
où en est Python et ce qu'il a fait jusque-là, par exemple :

.. code::

	print("amis avant la boucle-for", amis)

N.B. ! Quelquefois il faut introduire de nouvelles variables et décomposer des expressions complexes en parties plus simples afin
d'afficher des informations plus détaillées.

Bien que le débogage à base d'affichages soit utilisé aussi par des professionnels (il leur arrive de l'appeler *logging*, journalisation), il y a une alternative,
qui est plus confortable dans la plupart des cas. Elle s'appelle **avancer pas-à-pas dans le code** et c'est le pain béni de Thonny. Allez au chapitre `Utilisation des débogueurs <debuggers.rst>`_ pour en apprendre plus.


Revue du code
-------------

Une autre technique utile est la revue de code. Cela revient à peu près à tracer le flux du programme, mais on le fait dans sa
tête et on essaie de visualiser une figure plus grande au lieu de suivre des petits pas.

Voyez chacune des expressions de votre code et essayez de comprendre son rôle et comment elle est reliée à votre tâche.

Pour chaque **variable** demandez-vous :

* Est-ce que le nom de la variable dit ce qu'elle fait ? Vaut-il mieux utiliser un nom au singulier ou au pluriel ?
* Quel type de valeurs peut se trouver dans cette variable ? Chaînes, entiers, listes de chaînes, liste de flottants, ... ?
* Quel est le rôle de cette variable ? est-elle  prévue pour être mise à jour de façon répétée de façon à contenir quelque information utile ? est-elle prévue pour utiliser la même information à plusieurs endroits et éviter le copier-coller ? Quoi d'autre ?

Pour chaque **boucle** demandez-vous :

* Comment savez-vous que la boucle est nécessaire ?
* Combien de fois le corps de la boucle doit-il être exécuté ? De quoi cela dépend-il ?
* Quel code devrait être dans la boucle et quel code devrait être dehors ?
* Que faut-il faire avant la boucle et que faut-il faire après ?

Pour chaque **expression** complexe demandez-vous :

* Dans quel ordre devraient se faire les étapes d'évaluation de cette expression ? Est-ce que Python fait ainsi ? En cas de doute, utilisez le débogueur ou introduisez des variables auxiliaires et décomposez l'expression en morceaux plus petits.
* Quel type de valeur est censé sortir de cette expression ? Chaîne ? Liste de chaînes ?

Il vous manque peut-être des parties importantes dans votre programme :

* Votre tâche nécessite-t-elle de traiter des situations différente différemment ? Si oui, vous avez probablement besoin d'une construction conditionnelle (**if**) ;
* Votre tâche nécessite-t-elle de faire quelque chose plusieurs fois ? Si oui, il vous faut probablement une boucle.


Encore perdu ?
--------------

« Trouvez-vous l'emplacement ou vos suppositions deviennent fausses » -- ceci est plus simple à dire qu'à faire. Dans le cas de
programmes complexes c'est facile d'arriver à la situation où vous n'êtes plus du tout sûr de savoir ce que vous supposez
ni pourquoi vous avez commencé ce fichu programme.

Dans ce cas c'est utile de simplifier votre tâche autant que possible et d'essayer d'implémenter les problèmes plus simples
en premier. Prenez un autre éditeur, et soit recommencez depuis le début, soit copiez le code existant en jetant tout ce qui
n'est pas essentiel à votre problème. Par exemple, vous pouvez supposer que l'utilisateur est coopératif et saisit toujours de « bonnes » données.
Si la tâche implique de faire quelque chose de façon répétitive, alors jetez la partie « répétitive », si la tâche implique
une condition complexe pour faire quelque chose, rendez la condition plus simple, etc.

Après avoir résolu le problème plus simple vous serez bien mieux équipé pour résoudre aussi la tâche d'origine aussi bien.


