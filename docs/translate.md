# How to translate Thonny

We are using python [gettext](https://docs.python.org/3/library/gettext.html) library to mark and translate strings and the  [babel](http://babel.pocoo.org/en/latest/) library to extract and compile catalog files.

The languages files are inside the `locale` folder: `locale/<LANGUAGE_CODE>/LC_MESSAGES/`
There, you will find the `po` and `mo` files.





## Mark strings
Mark the string to be translated as `_(string_to_be_translated)`.

The shortcut `_()` for `gettext.gettext()` is available everywhere in the project since gettext is installed in `__main__.py` (see [gettext docs](https://docs.python.org/3/library/gettext.html#localizing-your-application)).

## Using Babel to manipulate the catalog files
You will need [babel](http://babel.pocoo.org/en/latest/) installed: `pip install babel`.
We are using Babel command-line interface as documented [here](http://babel.pocoo.org/en/latest/cmdline.html).

### Add a new language
You can extract the strings and render a new `po` catalog file like that:
 `pybabel extract thonny/ --output-file locale/<LANGUAGE_CODE/LC_MESSAGES/thonny.po`

## Update messages for an existing language
You can update a `po` catalog file for a language as follow:
`pybabel update -i locale/<LANGUAGE_CODE>/LC_MESSAGES/thonny.po  -l <LANGUAGE_CODE> -d locale/ -D thonny`

## Compile catalog
You can compile all catalog files into `mo` files as follow:
`pybabel compile -d locale/ -D thonny`
