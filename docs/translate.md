# How to translate Thonny

Thonny's internationalisation is a collaborative effort kindly hosted by [POEditor](https://poeditor.com) to support open source projects. You are very welcome to help us translate it in your language [here](https://poeditor.com/join/project/Gh188fdYH6).

Thonny's help pages are not translated in POEditor but in the main repository. See below for details.

**NB! Don't mark new strings for translation without consulting core developers first! Some strings are left unmarked on purpose (to reduce the amount of translation required or because they may change).**

## Short story for translators
[Thonny project in POEditor](https://poeditor.com/join/project/Gh188fdYH6) is the main source for translations -- it is recommended you use this environment for translation. If you wish to use another tool then don't forget to import your updates to POEditor as well.

NB! Some original terms have explicit linebreaks in them -- these are significant. In these cases try to write your translation such that it has approximately same line lengths.

When you are done with your translation, it is recommended to test it. For this you need to export thonny.po and thonny.mo files from POEditor into appropriate subfolder under `thonny/locale` under Thonny program directory (can be installed or cloned from GitHub). If you created a new language, then you also need to register it in `thonny/languages.py`.

If you noticed a problem (eg. some button is too narrow for your translation), then open an issue.

If you are happy with the translation, then please make a pull request with your updates. If you don't know how to do it then open an issue (in this case it may take longer for your translation to end up in Thonny).

## More details for code contributors

Below are some technicals details for how to handle translation process.

We are using python [gettext](https://docs.python.org/3/library/gettext.html) library to mark and translate strings and the  [babel](http://babel.pocoo.org/en/latest/) library to extract and compile catalog files.

The languages files are inside the `thonny/locale` folder: `thonny/locale/<LANGUAGE_CODE>/LC_MESSAGES/`
There, you will find the `pot`, `po` and `mo` files.

### Mark strings

**NB! Don't mark new strings for translation without consulting core developers first! Some strings are left unmarked on purpose (to reduce the amount of translation required or because they may change).**

Mark the string to be translated as `_(string_to_be_translated)`.

The shortcut `_()` for `gettext.gettext()` is available everywhere in the project since gettext is installed in `__main__.py` (see [gettext docs](https://docs.python.org/3/library/gettext.html#localizing-your-application)).

Once new strings have been marked, one should extract messages and then update catalog files (see below).

### Using Babel to manipulate the catalog files
You will need [babel](http://babel.pocoo.org/en/latest/) installed: `pip install babel`.
We are using Babel command-line interface as documented [here](http://babel.pocoo.org/en/latest/cmdline.html).


#### Extract messages to update the `pot` template file
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

#### Update messages for an existing language
Once the `pot` template file have been added, one should update all the `po` catalog files
This will keep all existing translations and add new strings to be translated.

To do this run:
`pybabel update -D thonny -i thonny/locale/thonny.pot  -d thonny/locale/`

You can also update one `po` catalog file for a language as follow:
`pybabel update -i locale/<LANGUAGE_CODE>/LC_MESSAGES/thonny.po  -l <LANGUAGE_CODE> -d locale/ -D thonny`


#### Add a new language
You can render a new `po` catalog file for a  new language like that:
`pybabel init -D thonny -i thonny/locale/thonny.pot -d thonny/locale/ -l <LANGUAGE_CODE>`

output should be:
`creating catalog thonny/locale/<LANGUAGE_CODE>/LC_MESSAGES/thonny.po based on thonny/locale/thonny.pot`

NB! One should not forget to add a the new language in `thonny/languages.py` so it's available in the configuration page.

#### Compile catalog
You can compile all `po` catalog files into `mo` files as follow:
`pybabel compile -d thonny/locale/ -D thonny`


### How to update translations
Translations have move forwards? New language have been added? That's great news!

0. If it's a new language, follow the "Add a new language" paragraphe above. If not, move to next point.
1. Download the `po` file from POEditor. See this [documentation](https://poeditor.com/kb/importing-and-exporting-strings) if needed.
2. Replace the proper `po` file in the `thonny/locale/` folder.
3. Compile it into a `mo` file (see above).i want to do more deblopment in it
4. Add both `po` and `mo` files to git and commit or PR.
5. Done!

### How to push new strings to POEditor
When new strings have been marked, you have extract it into the `pot` template file and update all existing `po` files, you want to push the new strings to POEditor. Please see this [documentation](https://poeditor.com/kb/importing-and-exporting-strings) on how to import files to POEditor. Just import the `pot` template file.

## Translating Help pages

Original text for help pages comes from .rst files in `thonny/plugins/help`. Translated versions of these files should be put under `thonny/locale/<lang>/HELP_CONTENT`.

Note that you don't have to translate all pages at once. If a page is requested and corresponding file is missing from the translation directory, the page is displayed in English.

