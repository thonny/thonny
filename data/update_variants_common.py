import re
import json
import urllib.request
from html.parser import HTMLParser
from typing import Set, Dict, List

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


def re_escape_model_name(name: str) -> str:
    return re.escape(name).replace('\\ ', ' ').replace('\\-', '-').replace('\\_', '_')


def get_available_formats(page_url: str) -> Set[str]:
    req = urllib.request.Request(
        page_url,
        data=None,
        headers={
            "User-Agent": FAKE_USER_AGENT,
            "Cache-Control": "no-cache",
        },
    )
    links_parser = FileLinksParser()
    with urllib.request.urlopen(req) as fp:
        links_parser.feed(fp.read().decode("utf-8"))

    return links_parser.extensions & {"hex", "uf2", "bin", "dfu"}


def get_attr_value(attrs, name):
    for key, value in attrs:
        if key == name:
            return value

    return None

def add_mappings(variant, url_keyword):
    formats = list(sorted(get_available_formats(variant["downloads_url"])))
    mappings: List[Dict[str, str]] = []
    if "uf2" in formats:
        if variant["board_family"].upper() in ["RP2040", "RASPBERRYPI"]:
            content_pattern = "^Board-ID: RPI-RP2$"
        else:
            content_pattern = f"^Model: {re_escape_model_name(variant['model_name'])}$"

        mappings.append(
            {
                "msc_file_name": "INFO_UF2.TXT",
                "msc_file_content_pattern": content_pattern,
                "download_url_pattern":
                    variant.get("_download_url_pattern", rf"{url_keyword}.*\.uf2$"),
            }
        )

    if "hex" in formats and variant["model_name"].startswith("micro:bit"):
        if variant["model_name"] == "micro:bit v1":
            content_pattern = "^Unique ID: 990[0-2]"
        elif variant["model_name"] == "micro:bit v2":
            content_pattern = "^Unique ID: 990[3-6]"
        else:
            raise ValueError(f"Unexpected model name {variant['model_name']}")
        mappings.append(
            {
                "msc_file_name": "DETAILS.TXT",
                "msc_file_content_pattern": content_pattern,
                "download_url_pattern": variant.get("_download_url_pattern", rf"{url_keyword}.*\.hex$"),
            }
        )

    variant["mappings"] = mappings


class FileLinksParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.extensions = set()

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "a" and get_attr_value(attrs, "href"):
            href = get_attr_value(attrs, "href")
            if "." in href:
                self.extensions.add(href.split(".")[-1])

def urlopen_ua(url):
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": FAKE_USER_AGENT,
            "Cache-Control": "no-cache",
        },
    )
    return urllib.request.urlopen(req)

def save_variants(variants, file_path):
    variants.sort(key=lambda b: (b["board_vendor"], b.get("variant_name", b["model_name"])))

    # get rid of temporary/private attributes
    for variant in variants:
        for key in list(variant.keys()):
            if key.startswith("_"):
                del variant[key]

    with open(file_path, mode="w", encoding="utf-8") as fp:
        json.dump(variants, fp, indent=4)
