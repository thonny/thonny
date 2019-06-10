Le Shell
========

Le Shell est le moyen principal pour lancer et communiquer avec votre programme. Il ressemble pour l'essentiel à
la boucle REPL (Read-Evaluate-Print Loop) officielle de Python, mais il y a quelques différences et propriétés supplémentaires.


Les commandes Python
--------------------

Tout comme l'invite REPL officielle de Python, le Shell de Thonny accepte des expressions et des commandes Python, qu'elles soient
sur une seule ligne ou sur plusieurs. Si on presse la touche Entrée, Thonny utilise quelques heuristiques pour prédire
si on veut lancer la commande ou continuer à taper la commande sur la ligne suivante.
Si vous voulez lancer la commande mais que Thonny vous offre une nouvelle ligne, vérifiez si vous avez oublié
de refermer quelques parenthèses.


Les commandes magiques
----------------------

Si on sélectionne "Lancer => Lancer le script courant" ou qu'on presse la touche F5, on voit que Thonny insère une commande
commençant par ``%Run`` dans le Shell. Les commandes qui commencent par ``%`` sont appelées *commandes magiques* (tout
comme dans `IPython <https://ipython.org/>`_ et elles réalisent certaines actionnes, qui ne peuvent pas
(facilement) s'exprimer par des commandes Python. Les commandes magiques de Thonny ont d'habitude
des commandes correspondantes dans le menu si bien qu'il est inutile de les écrire à la main.

Les commandes système
---------------------

Si on doit rapidement lancer une simple commande système il n'est pas nécessaire de démarrer un Terminal. Il suffit de
préfixer la commande par ``!`` (p. ex. ``!pytest mon-script.py``) et de la saisir dans le Shell de Thonny.


L'historique des commandes
--------------------------

Si on veut relancer la même commande ou presque plusieurs fois, il n'est pas nécessaire de la retaper à chaque fois --
on utilisera la flèche vers le haut pour récupérer la commande précédente dans l'historique. Une nouvelle action sur la même touche récupère le commande
précédente et ainsi de suite. On utilise la touche flèche vers le bas pour se déplacer dans l'historique en sens opposé.


Sortie colorisée
----------------

Si votre Shell est en mode émulation de Terminal (voir Outils => Options => Shell), on peut
utiliser des `codes ANSI <https://en.wikipedia.org/wiki/ANSI_escape_code>`_ pour produire une sortie colorisée.

Essayez l'exemple suivant :

.. code::

	print("\033[31m" + "Red" + "\033[m")
	print("\033[1;3;33;46m" + "Texte brillant et gras, italique, en jaune sur fond cyan" + "\033[m")

Vous pouvez avoir envie d'utiliser un paquet comme `colorama <https://pypi.org/project/colorama/>`_ pour produire
Les codes couleur.


Réécrire par-dessus les lignes de sortie
----------------------------------------

Les bons émulateurs de terminal supportent des codes ANSI autorisant l'écriture à une position arbitraire sur l'écran
du terminal. Le Shell de Thonny ne peut pas en faire autant, mais il supporte cependant quelques trucs et astuces.

Essayez le programme suivant :

.. code::

	from time import sleep
	
	for i in range(100):
	    print(i, "%", end="")
	    sleep(0.05)
	    print("\r", end="")
	
	print("Terminé !")

Le truc est d'utiliser le caractère ``"\r"``, qui fait revenir le curseur de sortie au début de la ligne
courante, si bien que les caractères suivants seront affichés en écrasant le texte précédent. Notez bien l'usage de ``print(..., end="")``
pour éviter de créer une nouvelle ligne.

Le cousin de ``"\r"`` est ``"\b"``, qui déplace le curseur de sortie à gauche d'un caractère.
Cela ne fait rien s'il est déjà à la première position de la ligne.

		
Émettre un son
--------------

Quand le Shell est en mode émulation de terminal, on peut faire sonner (ou émettre un tintement) en sortant un caractère ``"\a"``.
 
 
Mettre en graphique une série de nombres
----------------------------------------

On peut visualiser les séries de nombres envoyées vers le Shell à l'aide du `Grapheur <plotter.rst>`_.
