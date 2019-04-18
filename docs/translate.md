# How to translate Thonny

We are using python [gettext](https://docs.python.org/3/library/gettext.html) library to mark and translate strings and the  [babel](http://babel.pocoo.org/en/latest/) library to extract and compile catalog files.

The languages files are inside the `locale` folder: `locale/<LANGUAGE_CODE>/LC_MESSAGES/`
There, you will find the `pot`, `po` and `mo` files.


## Mark strings
Mark the string to be translated as `_(string_to_be_translated)`.

The shortcut `_()` for `gettext.gettext()` is available everywhere in the project since gettext is installed in `__main__.py` (see [gettext docs](https://docs.python.org/3/library/gettext.html#localizing-your-application)).

## Using Babel to manipulate the catalog files
You will need [babel](http://babel.pocoo.org/en/latest/) installed: `pip install babel`.
We are using Babel command-line interface as documented [here](http://babel.pocoo.org/en/latest/cmdline.html).


### Extract messages to update the `pot` template file
If new strings have been marked you need to extract them to update the `pot` template file:
`pybabel extract thonny/ --output-file thonny/locale/thonny.pot`

output should be
```
...
...
extracting messages from thonny/test/plugins/test_locals_marker.py
extracting messages from thonny/test/plugins/test_name_highlighter.py
extracting messages from thonny/test/plugins/test_paren_matcher.py
writing PO template file to thonny/locale/thonny.pot
```

### Add a new language
You can extract the strings and render a new `po` catalog file like that:
`pybabel init -D thonny -i thonny/locale/thonny.pot -d thonny/locale/ -l <LANGUAGE_CODE>`

output should be:
`creating catalog thonny/locale/<LANGUAGE_CODE>/LC_MESSAGES/thonny.po based on thonny/locale/thonny.pot`


### Update messages for an existing language
You can update one `po` catalog file for a language as follow:
`pybabel update -i locale/<LANGUAGE_CODE>/LC_MESSAGES/thonny.po  -l <LANGUAGE_CODE> -d locale/ -D thonny`

This will keep all existing translations and add new strings to be translated.


You can also update all existing `po` catalog files with this command:
`pybabel update -D thonny -i thonny/locale/thonny.pot  -d thonny/locale/`

### Compile catalog
You can compile all `po` catalog files into `mo` files as follow:
`pybabel compile -d thonny/locale/ -D thonny`
