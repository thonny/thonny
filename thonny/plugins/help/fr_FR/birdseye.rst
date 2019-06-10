L'œil d'oiseau (Birdseye)
=========================

L'Œil d'oiseau est un débogueur Python vraiment *cool* créé par Alex Hall, qui enregistre les valeurs des expressions
quand le programme fonctionne et vous laisse les explorer quand le programme se termine. Voir `https://birdseye.readthedocs.io <https://birdseye.readthedocs.io>`_ pour en savoir plus.

L'Œil d'oiseau n'est pas installé par défaut, mais il est facile de l'installer via *Outils → Gérer les greffons*. Il faut
installer la paquet nommé ``birdseye``.

L'Œil d'oiseau fonctionne d'une façon différente des `débogueurs intégrés à Thonny <debuggers.rst>`_.
Quand on exécute son programme avec *Lancer → Débogage du script courant (Œil d'oiseau)*, l'exécution est un peut plus
longue qu'à l'habitude, mais autrement le programme fonctionne exactement comme si on l'avait exécuté avec
*Lancer le script courant*. Ça signifie que les points d'arrêt sont ignorés et qu'on ne peut pas se déplacer pas-à-pas dans le programme.
Mais quand le programme se termine, Thonny ouvre une page web (servie localement par Œil d'oiseau),
qui vous permet de creuser le processus d'exécution et d'apprendre comment ils résultats finaux ont été composés
à partir des valeurs intermédiaires.

N.B. ! Quand vous utilisez Œil d'oiseau dans Thonny il n'y a pas besoin d'importer ``birdseye.eye`` ou de l'utiliser pour
décorer vos fonctions. Thonny exécute Œil d'oiseau d'une façon telle qu'il enregistre des informations pour toutes les
fonctions.

Le serveur local utilise le port 7777 par défaut. Si celui-ci est utilisé par une autre application, alors on peut configurer
un autre port (Outils → Options → Débogueur) et redémarrer Thonny.

