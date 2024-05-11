import gettext
import os
from logging import getLogger

logger = getLogger(__name__)

BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English (US) [default]"

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

LANGUAGES_DICT = {
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "zh_CN": "简体中文 ",
}

# how many spaces to add to button caption in order to make whole text visible
BUTTON_PADDING_SIZES = {"zh_CN": 4}

_translation = gettext.NullTranslations()


def get_button_padding():
    from thonny import get_workbench

    code = get_workbench().get_option("general.language")
    if code in BUTTON_PADDING_SIZES:
        return BUTTON_PADDING_SIZES[code] * " "
    else:
        return ""


def get_language_code_by_name(name):
    for code in LANGUAGES_DICT:
        if LANGUAGES_DICT[code] == name:
            return code

    raise RuntimeError("Unknown language name '%s'" % name)


def tr(message: str) -> str:
    return _translation.gettext(message)


def set_language(language_code: str) -> None:
    global _translation
    try:
        path = os.path.join(os.path.dirname(__file__), "locale")
        _translation = gettext.translation("thonny", path, [language_code])
    except Exception as e:
        logger.exception("Could not set language to '%s", language_code, exc_info=e)
        _translation = gettext.NullTranslations()
