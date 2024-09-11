import gettext
import os
from logging import getLogger

logger = getLogger(__name__)

BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English (US) [default]"

# https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes

LANGUAGES_DICT = {
    "be_BY": "Беларуская мова [BETA]",
    "ca_ES": "Català",
    "cs_CZ": "Čeština [BETA]",
    "de_DE": "Deutsch",
    "et_EE": "Eesti",
    "en_GB": "English (UK)",
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "es_ES": "Español",
    "eu_ES": "Euskara [BETA]",
    "fr_FR": "Français",
    "it_IT": "Italiano",
    "lt_LT": "Lietuvių",
    "hu_HU": "Magyar [BETA]",
    "nb_NO": "Norsk (Bokmål)",
    "nn_NO": "Norsk (Nynorsk)",
    "nl_NL": "Nederlands",
    "pl_PL": "Polski",
    "pt_PT": "Português (PT)",
    "pt_BR": "Português (BR)",
    "ro_RO": "Română",
    "ru_RU": "Русский",
    "sl_SI": "Slovenščina",
    "sk_SK": "Slovenčina",
    "fi_FI": "Suomi [BETA]",
    "sv_SE": "Svenska [ALPHA]",
    "sq_AL": "Shqip [BETA]",
    "vi_VN": "Tiếng Việt",
    "tr_TR": "Türkçe [BETA]",
    "uk_UA": "Українська",
    "zh_TW": "繁體中文-TW",
    "zh_CN": "简体中文 ",
    "zh_Hans": "简体中文 (zh-Hans) [BETA]",
    "ja_JP": "日本語",
    "hy_AM": "Հայերէն [BETA]",
    "fa_IR": "فارسی",
    "el_GR": "Ελληνικά",
    "ko_KR": "한국어 [韓國語] [BETA]",
    "ar_AR": "[BETA] عربي",
    "ta_IN": "தமிழ் [BETA]",
    "th_TH": "ภาษาไทย [BETA]",
}

# how many spaces to add to button caption in order to make whole text visible
BUTTON_PADDING_SIZES = {"zh_TW": 4, "zh_CN": 4, "ja_JP": 4}

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
