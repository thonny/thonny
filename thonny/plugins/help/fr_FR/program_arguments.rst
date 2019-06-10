Lancer les programmes avec des arguments en ligne de commande
=============================================================

Quand nous éditez *mon_programme.py* et pressez la touche F5, Thonny construit une commande magique
``%Run mon_program.py`` et l'envoie au shell, qui demande à la tâche de fond de Thonny de lancer ce script.

Quand on utilise le shell et qu'on récupère la commande ``%Run`` (avec la flèche vers le haut), on peut y ajouter
*des arguments en ligne de commande*. Par exemple on peut remplacer cette commande par
``%Run mon_programme.py argument1 argument2`` et appuyer sur Entrée.

Quand on lance le programme ainsi, il est possible d'accéder aux arguments à l'aide de ``sys.argv``:

.. code::

    import sys
    print(sys.argv)

Modifier les arguments en ligne de commande
-------------------------------------------

S'il faut utiliser le même ensemble d'arguments plusieurs fois, ça peut devenir ennuyeux de reconstruire
le ``%Run`` à la main. Dans ce cas, vous pouvez cocher **Arguments du programme** dans le **menu Afficher**. Cela
ouvre un petit champ de saisie près des boutons de la barre d'outils. Ensuite, tout ce qu'on tape dans cette
zone de saisie est ajouté au bout du ``%Run <nom du script>`` à chaque fois qu'on presse la touche F5.

 	
