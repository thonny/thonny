Installation de paquets de tierces parties
==========================================

Thonny a deux options pour l'installation de paquets de tierces parties.


Avec pip dans l'interface graphique
-----------------------------------

Depuis le menu « Outils », sélectionnez « Gérer les paquets ... » et suivez les instructions.

Avec pip en ligne de commande
-----------------------------

#. Depuis le menu « Outils », sélectionnez « Ouvrir un Shell système ... ». Vous devriez avoir un nouveau terminal, qui présente le nom correct de la commande *pip* (normalement ``pip`` ou ``pip3``). Par la suite on supposera que le nom de la commande est ``pip``.
#. Entrez ``pip install <package name>`` (p. ex. ``pip install pygame``) et tapez Entrée. Vous devriez voir *pip* qui télécharge et installe le paquet puis affiche son message de succès.
#. Fermez le terminal (facultatif)
#. Revenez à Thonny
#. Réinitialisez l'interpréteur en sélectionnant « Arrêter/relancer » depuis le menu « Lancer » (ceci est nécessaire la première fois que vous faite l'installation pip)
#. Commencez à utiliser la paquet.


Utiliser des paquets Python scientifiques
=========================================

La distribution Python qui vient avec Thonny ne contient pas de bibliothèques de programmation scientifique
(p. ex. `NumPy <http://numpy.org/>`_  et `Matplotlib <http://matplotlib.org/>`_). 

Les versions récentes de la plupart des paquets Python scientifiques (p. ex. numpy, pandas et
matplotlib) sont outillés pour les plate-formes populaires si bien que vous pouvez la plupart du temps les installer
avec pip mais au cas où il y a des problèmes, vous pouvez utiliser Thonny avec une distribution
Python séparée prévue pour le calcul scientifique
(p. ex. `Anaconda <https://www.continuum.io/downloads>`_, `Canopy <https://www.enthought.com/products/canopy/>`_ 
ou `Pyzo <http://www.pyzo.org/>`_).


Exemple: Utilisation d'Anaconda
-------------------------------

Allez à https://www.continuum.io/downloads et téléchargez une distribution binaire appropriée pour
votre plate-forme. La plupart du temps vous voudrez un installeur graphique et une version 64-bits (on peut avoir besoin
d'une version 32-bits avec un très vieux système). **Notez que Thonny ne supporte que Python3, assurez-vous bien de choisir la version pour Python 3 d'Ananconda**.

Installez-la et trouvez où il installe l'exécutable Python (*pythonw.exe* sous Windows et 
*python3* ou *python* sous Linux et Mac).

Dans Thonny ouvrez « Outils » et sélectionnez « Options ... ». Dans le dialogue d'options ouvrez l'onglet « Interpréteur »,
cliquez « Sélectionner l'exécutable » et désignez l'emplacement de l'exécutable Python d'Anaconda.

Après avoir fait ça, la prochaine fois que vous relancerez votre programme, il utilisera le Python d'Anaconda et toutes les bibliothèques installées là sont disponibles.
