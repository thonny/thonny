============
Contributing
============

We are welcoming all kinds of contributions:

* bug reports
* proposals for changes and new features
* documentation
* fixes for the language in GUI and web (Thonny's main developers don't speak English natively)
* translations (consult docs/translate.md first)
* plug-ins (a guide is in the works, see https://bitbucket.org/KauriRaba/thonny-microbit for now)
* bug fixes
* creating and maintaining Linux packages (see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=857042) 
* tests
* refactorings
* ...

NB! For non-trivial contributions you should discuss your plan under a GitHub issue first
to make sure your goals and means align with the vision of Thonny core team.

See the `wiki <https://github.com/thonny/thonny/wiki>`_ for more info.

**NB!** If you want to contribute to Thonny but don't want to or can't register a GitHub account 
(for example because you are younger than 13 years), then 
`get in touch <mailto:aivar.annamaa@gmail.com>`_ and we'll find a way!

Code format
-----------
Thonny uses `Black <https://black.readthedocs.io/en/stable/>`_ to keep code formatting consistent. 
Please format your code with ``black thonny`` before issuing a pull request. Format options are 
specified in pyproject.toml in the root of the repository and will be picked up from there by Black.

In recent PyDev versions you can select Black as your formatter (Preferences => PyDev => Editor => 
Code Style => Code Formatter) and make it run on each save (Preferences => PyDev => Editor => 
Save Actions). See 
`Black's documentation about configuring other IDE-s <https://black.readthedocs.io/en/stable/editor_integration.html>`_.    


