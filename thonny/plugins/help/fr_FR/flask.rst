Développement Web avec Flask
============================

`Flask <http://flask.pocoo.org/>`__ est une infrastructure populaire pour créer des applications web avec Python.

Les tutoriels Flask indiquent de lancer les programmes Flask en tapant certaines commandes dans un Terminal,
mais ça peut intimider certains débutants. Thonny essaie de rendre les choses plus faciles et permet de lancer les programmes Flask
comme n'importe quel autre programme (avec un simple F5). S'il détecte que vous lancez un programme Flask, il le lance
avec quelques lignes de code en plus, qui démarrent le serveur de développement avec les réglages qui vont bien.


Détails
-------

Thonny lancera le serveur de développement approximativement comme ceci :

.. code::

	os.environ["FLASK_ENV"] = "development"
	app.run(threaded=False, use_reloader=False, debug=False)

``threaded=False`` est utilisé car le débogueur de Thonny ne supporte que les programmes à un seul fil (thread),
``use_reloader=False`` est utilisé car
`le rechargement automatique n'est pas fiable quand Flask est lancé ainsi <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.run>`_
et ``debug=False`` est utilisé car cela semble causer moins d'erreurs "Address already in use".

Si vous voulez un plus grand contrôle sur les réglages, alors il vous faut lancer la méthode ``run`` par vous-même, comme ceci, par exemple :

.. code::

	...
	if __name__ == "__main__":
		app.run(port=5005, threaded=False, use_reloader=True, debug=True)

Dans ce cas Thonny n'ajoutera rien à votre code.
