Utilisation des débogueurs
==========================

Si vous voulez voir comment Python exécute votre programme pas-à-pas alors
il faut le lancer en *mode de débogage* « joli » ou « vite fait ». On peut
aussi le faire à l'aide d'`Œil d'oiseau (Birdseye) <birdseye.rst>`_ et
examiner les étapes d'exécution plus tard.

Le mode « joli »
----------------

Ce mode est recommandé pour les néophytes.

Commencez par sélectionner *Déboguer le script courant (joli)* depuis le
menu *Lancer* ou en appuyant sur les touches Ctrl+F5
(`sous XFCE il faut utiliser Shift+Ctrl+F5 <https://askubuntu.com/questions/92759/ctrlf5-in-google-chrome-in-xfce>`__).
Vous verrez que la première instruction du programme est mise en valeur et que rien d'autre ne se passe.
Dans ce mode il faut notifier Thonny qu'on est prêt à laisser Python faire le pas suivant.
Pour cela, vous avez deux option principales :

* *Lancer → Sauter par dessus* (ou F6) pour faire de grands pas, c'est à dire qu'il exécute le code en évidence puis met en évidence la suite du code.
* *Lancer → Sauter dedans* (ou F7) pour essayer de faire des pas plus petits. Si le code en évidence est composé de morceaux plus petits (déclaration ou instruction), alors la première est mis en valeur et Thonny attend votre commande suivante. Si on est arrivé à un composant du programme qui ne se décompose pas, (p. ex. un nom de variable), alors *Sauter dedans* se comporte comme *Sauter par dessus* c'est à dire qu'il exécute (ou évalue) le code.

Si on a avancé pas-à-pas dans les profondeurs d'une fonction ou d'une expression et qu'on veut avancer plus vite, on peut alors utiliser *Lancer → Ressortir* qui exécute le code couramment mis en valeur et toutes les parties du programme sur le même niveau.
Il y a une commande un peu similaire nommée *Reprendre*, qui lancera la commande sans s'arrêter à chaque pas jusqu'à ce qu'elle se termine (ou jusqu'au nouveau point d'arrêt, vois ci-dessous).

Si par accident vous avez fait un trop grand pas et survolé une partie intéressante du code, 
on peut **défaire cette étape** en sélectionnant *Lancer → Un pas en arrière*. Thonny montrera l'état du programme tel qu'il était avant le dernier pas. Ensuite on peut continuer avec de petits pas
et zoomer ce morceau de code. (Comment ça marche ? Même quand on réalise un grand pas, Thonny
enregistre tous les états intermédiaires du programme, qu'il peut rejouer si on fait un pas en arrière.)

Si on veut atteindre une portion spécifique du code, on peut aller plus vite en plaçant le curseur sur cette ligne et en sélectionnant *Lancer → Exécuter jusqu'au curseur*.
Cela fait avancer Thonny automatiquement en mode pas-à-pas jusqu'à cette ligne. Vous pouvez reprendre la main à partir de là.

Si vous avez activé les numéros de ligne dans l'éditeur (Outils → Options → Éditeur), alors 
on peut aussi utiliser des **points d'arrêt**. Quand on double-clique dans la marque gauche de l'éditeur près d'une ligne, un point
apparaît. Alors, quand on lance le débogueur, il ne s'arrête pas avant la première ligne mais va jusqu'à
la ligne marquée d'un point, qu'on nomme aussi un point d'arrêt. On peut placer autant de points d'arrêt dans le programme
qu'il en faut. Les points d'arrêt peuvent être retirés en cliquant-double dessus.


Le mode « vite fait »
---------------------

Quand votre programme devient plus gros, on observe que le parcours en mode « joli » prend beaucoup de temps.
C'est parce que les ornements (p. ex. la possibilité de faire de petits pas durant l'évaluation d'expressions et de revenir en arrière)
nécessitent une machinerie lourde et lente.

Avec *Débogage du script courant (vite)* on perd les ornements mais on peut avancer dans le programme beaucoup plus vite.
On peut utiliser les mêmes commandes (sauf « Un pas en arrière » comme avec le débogueur en mode joli. C'est le style de débogage que la plupart des programmeurs
professionnels utilisent d'habitude.


Des styles différents pour la présentation de la pile d'appel
-------------------------------------------------------------

Par défaut Thonny utilise des fenêtres empilées pour représenter la pile d'appels. Cela donne une bonne intuition du
concept, mais ça devient encombrant à l'usage. C'est pourquoi, depuis la version 3.0 on peut choisir entre
deux styles différents pour présenter la pile d'appels. Dans « Outils → Options → Débogueur » on peut passer à
un style plus traditionnel avec une vue séparée pour présenter les trames d'appels. Notez que les deux
styles sont utilisables, avec chacun des deux modes de débogage.


L'œil d'oiseau (Birdseye)
-------------------------

La commande *Débogage du script courant (Œil d'oiseau)* est expliquée dans une `page séparée <birdseye.rst>`_
 
