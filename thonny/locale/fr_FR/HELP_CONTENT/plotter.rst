Le grapheur
===========

Le grapheur est un greffon pour le Shell, qui en extrait les nombres venus
du programme et les affiche comme une courbe. Il peut être utile pour
observer des données de capteurs en direct venant de périphériques ou même pour analyser
des données statiques (si vous hésitez à utiliser des outils plus sérieux). Il est inspiré
du `Mu Python editor <https://codewith.mu/>`__. 

Vous pouvez l'ouvrir depuis le menu « Afficher » ou depuis le menu contextuel du Shell.

Par exemple essayez le programme suivant (on peut l'arrêter avec Ctrl+C ou
avec le bouton Arrêter/Relancer de la barre d'outils) :

.. code::

	from time import sleep
	from random import randint
	
	p1 = 0
	while True:
	    p1 += randint(-1, 1)
	    p2 = randint(-10, 10)
	    print("Marche aléatoire :", p1, " juste aléatoire:", p2)
	    sleep(0.05)


Quand on le lance avec le Grapheur ouvert, on voir un graphique en ligne avec deux courbes qui défilent.
Chaque colonne du graphique correspond à une ligne dans le Shell.
La colonne le plus à droite dans le graphique correspond toujours à la ligne visible en bas du Shell,
même quand on arrête le programme et qu'on se déplace dans le texte du Shell.

Le grapheur commence à tracer des courbes dès qu'il détecte au moins deux lignes consécutives contenant le même motif
de nombres et de texte d'accompagnement. Les nombres sont représentés sous forme de courbes et le texte d'accompagnement
devient la légende dans le coin en bas à droite du Grapheur.


La vitesse de l'animation
-------------------------

À moins que vous ne produisiez un nombre fixe de lignes, c'est une bonne idée d'éviter de noyer
le Shell et le Grapheur sous les données. C'est pourquoi l'exemple ci-dessus
fait une petite pause (``sleep(0.05)``) avant d'afficher la ligne suivante.


Intervalle de l'axe-Y
---------------------

Le Grapheur tente de détecter un intervalle adapté pour votre courbe sans qu'il soit
nécessaire de le changer trop souvent. Pour cette raison, il augmente l'intervalle si besoin est, mais ne
le diminue qu'au début d'une nouvelle série.

Si certaines données extraordinaires rendent l'intervalle trop grand, on peut le rétrécir manuellement
en attendant que les données trop grande sortent de la figure et en cliquant sur le Grapheur.

Si vous voulez rendre l'intervalle plus grand (ou juste comparer vos valeurs à d'autres),
il suffit simplement d'inclure une ou des constantes adéquates dans vos lignes de données, p.ex. :

``print(0, measure1, measure2, 100)``.
