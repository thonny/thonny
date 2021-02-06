# How to translate Thonny

Thonny's internationalisation is a collaborative effort kindly hosted by [POEditor](https://poeditor.com) to support open source projects. You are very welcome to help us translate it in your language [here](https://poeditor.com/join/project/Gh188fdYH6).

Thonny's help pages are not translated in POEditor but in the main repository. See below for details.

**NB! Don't mark new strings for translation without consulting core developers first! Some strings are left unmarked on purpose (to reduce the amount of translation required or because they may change).**

## Short story for translators
[Thonny project in POEditor](https://poeditor.com/join/project/Gh188fdYH6) is the main source for translations -- it is recommended you use this environment for translation. If you wish to use another tool then don't forget to import your updates to POEditor as well.

NB! Some original terms have explicit linebreaks in them -- these are significant. In these cases try to write your translation such that it has approximately same line lengths.

When you are done with your translation, it is recommended to test it. For this you need to export thonny.po and thonny.mo files from POEditor into appropriate subfolder under `thonny/locale` under Thonny program directory (can be installed or cloned from GitHub). If you created a new language, then you also need to register it in `thonny/languages.py`.

If you noticed a problem (eg. some button is too narrow for your translation), then open an issue.

**Translations will be pulled from POEditor before each release, no need to create a PR.**

## More details for Thonny's maintainers (NB! Not relevant for translators!)

Below are some technicals details for how to handle translation process.

We are using python [gettext](https://docs.python.org/3/library/gettext.html) library to mark and translate strings and the  [babel](http://babel.pocoo.org/en/latest/) library to extract and compile catalog files.

The languages files are inside the `thonny/locale` folder: `thonny/locale/<LANGUAGE_CODE>/LC_MESSAGES/`
There, you will find the `pot`, `po` and `mo` files.

### Mark strings

**NB! Don't mark new strings for translation without consulting core developers first! Some strings are left unmarked on purpose (to reduce the amount of translation required or because they may change).**

Mark the string to be translated as `tr(string_to_be_translated)` (the function `tr` should be imported from `thonny.languages`).

Once new strings have been marked, one should extract messages and then update catalog files (see below).

### Using Babel to manipulate the catalog files
You will need [babel](http://babel.pocoo.org/en/latest/) installed: `pip install babel`.
We are using Babel command-line interface as documented [here](http://babel.pocoo.org/en/latest/cmdline.html).


#### Extract messages to update the `pot` template file
If new strings have been marked you need to extract them to update the `pot` template file:
`pybabel extract thonny/ --keywords=tr --output-file thonny/locale/thonny.pot`

output should be
```
...
...
extracting messages from thonny/test/plugins/test_locals_marker.py
extracting messages from thonny/test/plugins/test_name_highlighter.py
extracting messages from thonny/test/plugins/test_paren_matcher.py
writing PO template file to thonny/locale/thonny.pot
```

### Uploading templates to POEditor

Use POEditor's user interface and import thonny.pot

## Translating Help pages

Original text for help pages comes from .rst files in `thonny/plugins/help`. Translated versions of these files should be put under `thonny/locale/<lang>/HELP_CONTENT`.

Note that you don't have to translate all pages at once. If a page is requested and corresponding file is missing from the translation directory, the page is displayed in English.

