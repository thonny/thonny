import re
import json
import urllib.request
from html.parser import HTMLParser
from typing import Set, Dict, List, Tuple

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"


def re_escape_model_name(name: str) -> str:
    return re.escape(name).replace('\\ ', ' ').replace('\\-', '-').replace('\\_', '_')



def find_keywords(page_url: str, selection: Set[str]) -> Set[str]:
    with urlopen_ua(page_url) as fp:
        content = fp.read().decode("utf-8")

    return {kw for kw in selection if kw.lower() in content.lower()}

def find_download_links(page_url: str,
                        stable_pattern: str,
                        max_stable_count: int = 3,
                        unstable_pattern: str = "",
                        max_unstable_count: int = 0) -> List[str]:
    with urlopen_ua(page_url) as fp:
        content = fp.read().decode("utf-8")

    parser = FileLinksParser()
    parser.feed(content)

    stables = []
    unstables = []

    for link in parser.links:
        if len(stables) < max_stable_count and re.search(stable_pattern, link):
            stables.append(link)
        elif len(unstables) < max_unstable_count and re.search(unstable_pattern, link):
            unstables.append(link)

    return stables + unstables





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

def urlopen_ua(url):
    req = urllib.request.Request(
        url,
        data=None,
        headers={
            "User-Agent": FAKE_USER_AGENT,
            "Cache-Control": "no-cache",
        },
    )
    return urllib.request.urlopen(req, timeout=5)

def save_variants(variants, file_path):
    variants.sort(key=lambda b: (b["board_vendor"], b.get("variant_name", b["model_name"])))

    # get rid of temporary/private attributes
    for variant in variants:
        for key in list(variant.keys()):
            if key.startswith("_"):
                del variant[key]

    with open(file_path, mode="w", encoding="utf-8") as fp:
        json.dump(variants, fp, indent=4)
