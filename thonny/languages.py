BASE_LANGUAGE_CODE = "en_US"
BASE_LANGUAGE_NAME = "English"

LANGUAGES_DICT = {
    "de_DE": "Deutsch [BETA]",
    "et_EE": "Eesti",
    BASE_LANGUAGE_CODE: BASE_LANGUAGE_NAME,
    "es_ES": "Español [BETA]",
    "fr_FR": "Français [BETA]",
    "pt_BR": "Português [BETA]",
    "ru_RU": "Русский [BETA]",
    "zh_TW": "繁體中文-TW [BETA]",
    "ja_JP": "日本語  [BETA]",
}


def get_language_code_by_name(name):
    for code in LANGUAGES_DICT:
        if LANGUAGES_DICT[code] == name:
            return code
