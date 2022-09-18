import json
import re
from html.parser import HTMLParser
from typing import Set, Dict, List, Union, Optional

import requests

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


def re_escape_model_name(name: str) -> str:
    return re.escape(name).replace("\\ ", " ").replace("\\-", "-").replace("\\_", "_")


def find_keywords(page_url: str, selection: Set[str]) -> Set[str]:
    content = read_page(page_url)
    return {kw for kw in selection if kw.lower() in content.lower()}


def find_download_links(
    page_url: Union[str, List[str]],
    stable_pattern: str,
    max_stable_count: int = 3,
    unstable_pattern: str = "",
    max_unstable_count: int = 0,
    url_prefix="",
) -> List[Dict[str, str]]:
    parser = FileLinksParser()
    if isinstance(page_url, str):
        page_urls = [page_url]
    else:
        assert isinstance(page_url, list)
        page_urls = page_url

    content = ""
    for url in page_urls:
        content += read_page(url)

    parser.feed(content)

    stables = []
    unstables = []

    for link in parser.links:
        link = url_prefix + link
        if len(stables) < max_stable_count and re.search(stable_pattern, link):
            stables.append({"version": re.search(stable_pattern, link).group(1), "url": link})
        elif len(unstables) < max_unstable_count and re.search(unstable_pattern, link):
            unstables.append({"version": re.search(unstable_pattern, link).group(1), "url": link})

    return stables + unstables


def add_download_link_if_exists(links: List[Dict[str, str]], link: str, version: str) -> None:
    response = requests.head(link)
    if response.status_code == 200:
        links.append({"version": version, "url": link})


def get_attr_value(attrs, name):
    for key, value in attrs:
        if key == name:
            return value

    return None


class FileLinksParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.links = []

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "a" and get_attr_value(attrs, "href"):
            self.links.append(get_attr_value(attrs, "href"))


_page_cache = {}


def read_page(url) -> str:
    if url not in _page_cache:
        response = requests.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Status {response.status_code} for {url}")
        _page_cache[url] = response.text

    return _page_cache[url]


def save_variants(variants: List, flasher: str, families: Set[str], file_path:str,
                  latest_prerelease_regex: Optional[str]=None):
    variants = list(
        filter(lambda v: v["_flasher"] == flasher and v["family"] in families, variants)
    )

    for variant in variants:
        title = variant.get("title", variant["model"])
        if (title.lower() + " ").startswith(variant["vendor"].lower()):
            variant["title"] = title[len(variant["vendor"]) :].strip()
        title = variant.get("title", variant["model"])

        # special treatment for Pico
        if variant["vendor"] == "Raspberry Pi":
            if "Pimoroni" not in variant.get("title", ""):
                variant["popular"] = True
            if variant["model"] == "Pico":
                variant["title"] = title.replace("Pico", "Pico / Pico H")
            elif variant["model"] == "Pico W":
                variant["title"] = title.replace("Pico W", "Pico W / Pico WH")

    variants = sorted(
        variants,
        key=lambda b: (b["vendor"].upper(), b.get("title", b["model"]).upper()),
    )

    # get rid of temporary/private attributes
    final_variants = []
    for variant in variants:
        variant = variant.copy()
        if not variant["downloads"]:
            print("No downloads:", variant)
        for key in list(variant.keys()):
            if key.startswith("_"):
                del variant[key]

        final_variants.append(variant)

    if latest_prerelease_regex:
        # This attribute signifies Thonny should look up the version of the latest unstable
        # from the info page of this variant and use it all variants up to the next variant
        # which has this attribute set.
        final_variants[0]["latest_prerelease_regex"] = latest_prerelease_regex

    with open(file_path, mode="w", encoding="utf-8", newline="\n") as fp:
        json.dump(final_variants, fp, indent=4)
