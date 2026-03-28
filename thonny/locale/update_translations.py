#!/usr/bin/env python3
"""Download all Thonny PO files from the POEditor project."""

from __future__ import annotations

import getpass
import json
import sys
from pathlib import Path
from time import sleep
from typing import Any, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_ID = 256075
API_BASE_URL = "https://api.poeditor.com/v2/"
LOCALE_DIR = Path(__file__).resolve().parent
TIMEOUT_SECONDS = 60
MIN_PERCENTAGE = 19
POEDITOR_TO_GETTEXT_CODES = {
    "ar": "ar_SA",
    "az": "az_AZ",
    "be": "be_BY",
    "bg": "bg_BG",
    "ca": "ca_ES",
    "cs": "cs_CZ",
    "da": "da_DK",
    "de": "de_DE",
    "de-at": "de_AT",
    "el": "el_GR",
    "en-gb": "en_GB",
    "en-us": "en_US",
    "es": "es_ES",
    "et": "et_EE",
    "eu": "eu_ES",
    "fa": "fa_IR",
    "fi": "fi_FI",
    "fr": "fr_FR",
    "hi": "hi_IN",
    "hu": "hu_HU",
    "hy": "hy_AM",
    "id": "id_ID",
    "is": "is_IS",
    "it": "it_IT",
    "ja": "ja_JP",
    "ko": "ko_KR",
    "lt": "lt_LT",
    "ml": "ml_IN",
    "nb": "nb_NO",
    "nl": "nl_NL",
    "nn": "nn_NO",
    "pl": "pl_PL",
    "pt": "pt_PT",
    "pt-br": "pt_BR",
    "ro": "ro_RO",
    "ru": "ru_RU",
    "ry": "ry_UA",
    "sk": "sk_SK",
    "sl": "sl_SI",
    "sq": "sq_AL",
    "sv": "sv_SE",
    "ta": "ta_IN",
    "th": "th_TH",
    "tr": "tr_TR",
    "uk": "uk_UA",
    "ur": "ur_PK",
    "uz": "uz_UZ",
    "vi": "vi_VN",
    "zh-cn": "zh_CN",
    "zh-hans": "zh_Hans",
    "zh-hant": "zh_TW",
    "zh-tw": "zh_TW",
}


def prompt_api_token() -> str:
    token = getpass.getpass("POEditor API token: ").strip()
    if not token:
        raise SystemExit("POEditor API token is required")

    return token


def call_poeditor(api_path: str, data: dict[str, Any]) -> dict[str, Any]:
    payload = urlencode(data).encode("utf-8")
    request = Request(
        API_BASE_URL + api_path,
        data=payload,
        headers={"User-Agent": "Thonny locale updater"},
    )

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
    except HTTPError as e:
        details = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"POEditor API request failed with HTTP {e.code}: {details}") from e
    except URLError as e:
        raise RuntimeError(f"POEditor API request failed: {e}") from e

    try:
        payload_json = json.loads(body)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"POEditor API returned invalid JSON: {body!r}") from e

    response_info = payload_json.get("response", {})
    if response_info.get("status") != "success":
        message = response_info.get("message", "Unknown POEditor API error")
        code = response_info.get("code")
        raise RuntimeError(f"POEditor API error {code}: {message}")

    return payload_json


def download_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Thonny locale updater"})

    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return response.read()
    except HTTPError as e:
        details = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Download from {url} failed with HTTP {e.code}: {details}") from e
    except URLError as e:
        raise RuntimeError(f"Download failed: {e}") from e


def resolve_locale_dir_name(language_code: str) -> Optional[str]:
    locale_dir_name = POEDITOR_TO_GETTEXT_CODES.get(language_code.lower())
    return locale_dir_name


def list_project_languages(api_token: str) -> list[dict[str, Any]]:
    result = call_poeditor("languages/list", {"api_token": api_token, "id": PROJECT_ID})["result"]
    print("LANGUAGES:", result)
    languages = result.get("languages", [])
    if not languages:
        raise RuntimeError("POEditor project returned no languages")

    return sorted(languages, key=lambda item: str(item.get("code", "")).lower())


def export_language(api_token: str, language_code: str) -> bytes:
    result = call_poeditor(
        "projects/export",
        {
            "api_token": api_token,
            "id": PROJECT_ID,
            "language": language_code,
            "type": "po",
        },
    )["result"]

    url = result.get("url")
    if not url:
        raise RuntimeError(f"POEditor export for {language_code} did not include a download URL")

    return download_bytes(url)


def main() -> int:
    api_token = prompt_api_token()
    languages = list_project_languages(api_token)

    downloaded_count = 0

    for language in languages:
        language_code = language["code"]
        if language["percentage"] < MIN_PERCENTAGE:
            print(
                f"Warning: Skipping {language_code!r} because of low percentage ({language['percentage']})",
                file=sys.stderr,
            )
        locale_dir_name = resolve_locale_dir_name(language_code)
        if locale_dir_name is None:
            print(
                f"Warning: no gettext locale mapping for POEditor language code {language_code!r}, skipping",
                file=sys.stderr,
            )
            continue

        target_path = LOCALE_DIR / locale_dir_name / "LC_MESSAGES" / "thonny.po"
        target_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Exporting {language_code} -> {target_path.relative_to(LOCALE_DIR)}")
        target_path.write_bytes(export_language(api_token, language_code))
        downloaded_count += 1

        sleep(10)

    print(f"Downloaded {downloaded_count} translation files.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit("Interrupted")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise SystemExit(1)
