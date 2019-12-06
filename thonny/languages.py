from thonny import get_workbench

BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English"

# http://www.internationalphoneticalphabet.org/languages/language-names-in-native-language/

LANGUAGES_DICT = {
    "de_DE": "Deutsch [ALPHA]",
    "et_EE": "Eesti",
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "es_ES": "Español [ALPHA]",
    "fr_FR": "Français [BETA]",
    "it_IT": "Italiano [ALPHA]",
    "nl_NL": "Nederlands [BETA]",
    "pl_PL": "Polski [BETA]",
    "pt_PT": "Português (PT) [BETA]",
    "pt_BR": "Português (BR) [ALPHA]",
    "ru_RU": "Русский",
    "tr_TR": "Türkçe [BETA]",
    "uk_UA": "Українська",
    "zh_TW": "繁體中文-TW",
    "zh_CN": "简体中文 ",
    "ja_JP": "日本語  [ALPHA]",
    "lt_LT": "Lietuvių",
    "el_GR": "Ελληνικά [BETA]",
}

# how many spaces to add to button caption in order to make whole text visible
BUTTON_PADDING_SIZES = {"zh_TW": 4, "zh_CN": 4, "ja_JP": 4}


def get_button_padding():
    code = get_workbench().get_option("general.language")
    if code in BUTTON_PADDING_SIZES:
        return BUTTON_PADDING_SIZES[code] * " "
    else:
        return ""


def get_language_code_by_name(name):
    for code in LANGUAGES_DICT:
        if LANGUAGES_DICT[code] == name:
            return code
