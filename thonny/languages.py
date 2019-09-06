BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English"

LANGUAGES_DICT = {
    "de_DE": "Deutsch [ALPHA]",
    "et_EE": "Eesti",
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "es_ES": "Español [ALPHA]",
    "fr_FR": "Français [ALPHA]",
    "nl_NL": "Nederlands [BETA]",
    "pt_PT": "Português (PT) [BETA]",
    "pt_BR": "Português (BR) [ALPHA]",
    "ru_RU": "Русский [BETA]",
    "uk_UA": "Українська [BETA]",
    "zh_TW": "繁體中文-TW [BETA]",
    "zh_CN": "简体中文  [BETA]",
    "ja_JP": "日本語  [ALPHA]",
    "lt_LT": "Lietuvių [BETA]",
}


def get_language_code_by_name(name):
    for code in LANGUAGES_DICT:
        if LANGUAGES_DICT[code] == name:
            return code
