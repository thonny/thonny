from html.parser import HTMLParser
from typing import Dict

from data.update_variants_common import find_keywords, find_download_links
from update_variants_common import get_attr_value, urlopen_ua, save_variants

base_url = "https://circuitpython.org/downloads"


class IndexParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.variants = []

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "div" and get_attr_value(attrs, "class") == "download":
            data_id = get_attr_value(attrs, "data-id")
            self.variants.append(
                {
                    "_id": get_attr_value(attrs, "data-id"),
                    "board_vendor": get_attr_value(attrs, "data-manufacturer"),
                    "model_name": get_attr_value(attrs, "data-name"),
                    "board_family": get_attr_value(attrs, "data-mcufamily"),
                    "_downloads_page_url": f"https://circuitpython.org/board/{data_id}/",
                }
            )


parser = IndexParser()

with urlopen_ua(base_url) as fp:
    parser.feed(fp.read().decode("utf-8"))

all_variants = parser.variants.copy()[:5]

cant_determine_samd = []

for i, variant in enumerate(all_variants):

    print("Processing", i+1, variant)
    variant["download_urls"] = find_download_links(variant["_downloads_page_url"],
                                                   r"/adafruit-circuitpython.+\.uf2")

    if variant["board_family"] == "raspberrypi":
        variant["board_family"] = "rp2040"
    elif variant["board_family"].startswith("nrf52"):
        variant["board_family"] = "nrf52"
    elif variant["board_family"] == "atmel-samd":
        if "M0" in variant["model_name"] or "SAMD21" in variant["model_name"]:
            variant["board_family"] = "samd21"
        elif "M4" in variant["model_name"]:
            variant["board_family"] = "samd51"
        else:
            try:
                samd_keywords = find_keywords(
                    f"https://raw.githubusercontent.com/adafruit/circuitpython/main/ports/atmel-samd/boards/{variant['_id']}/mpconfigboard.h",
                    {"SAMD21", "SAMD51"})
            except:
                samd_keywords = find_keywords(variant["downloads_url"], {"SAMD21", "SAMD51"})

            if samd_keywords == {"SAMD21"}:
                variant["board_family"] = "samd21"
            elif samd_keywords == {"SAMD51"}:
                variant["board_family"] = "samd51"
            else:
                cant_determine_samd.append(variant)

print(f"Got {len(all_variants)} variants")

for variant in cant_determine_samd:
    print("Could not determine SAMD variant for", variant)

save_variants(all_variants, "circuitpython-variants.json")

print("Done")
