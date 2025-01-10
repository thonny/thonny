"""
Downloads: https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/
"""

from html.parser import HTMLParser
from typing import Dict

from update_variants_common import (
    find_keywords,
    find_download_links,
    read_page,
    add_download_link_if_exists,
)
from update_variants_common import get_attr_value, save_variants

base_url = "https://circuitpython.org/downloads"

PREV_RELEVANT_VERSION = "9.1.4"
RELEVANT_FAMILIES = {
    "atmel-samd",
    "esp32",
    "esp32s2",
    "esp32s3",
    "esp32c2",
    "esp32c3",
    "esp32c6",
    "esp32h2",
    "nrf52840",
    "rp2040",
    "rp2350",
}

DAPLINK_BOARDS = {"microbit_v2", "makerdiary_nrf52840_mdk"}


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
                    "vendor": get_attr_value(attrs, "data-manufacturer"),
                    "model": get_attr_value(attrs, "data-name"),
                    "family": get_attr_value(attrs, "data-mcufamily"),
                    "info_url": f"https://circuitpython.org/board/{data_id}/",
                }
            )


parser = IndexParser()


parser.feed(read_page(base_url))

all_variants = list(filter(lambda v: v["family"] in RELEVANT_FAMILIES, parser.variants))

cant_determine_samd = []

for i, variant in enumerate(all_variants):
    print("Processing", i + 1, "of", len(all_variants), variant)

    if variant["_id"] in DAPLINK_BOARDS:
        extensions = ["hex", "combined.hex"]
    elif "esp" in variant["family"]:
        extensions = ["uf2", "bin"]
    else:
        extensions = ["uf2"]

    variant["downloads"] = []
    for extension in extensions:
        variant["downloads"] += find_download_links(
            variant["info_url"],
            r"/adafruit-circuitpython.+en_US-(\d+\.\d+\.\d+)\." + extension,
            1,
            r"/adafruit-circuitpython.+en_US-(\d+\.\d+\.\d+-(?:alpha|beta|rc)\.\d+)\." + extension,
            1,
        )

        prev_major_url = f"https://downloads.circuitpython.org/bin/{variant['_id']}/en_US/adafruit-circuitpython-{variant['_id']}-en_US-{PREV_RELEVANT_VERSION}.{extension}"
        add_download_link_if_exists(variant["downloads"], prev_major_url, PREV_RELEVANT_VERSION)

    if variant["family"] in ["rp2040", "rp2350"]:
        variant["family"] = "rp2"
    elif variant["family"].startswith("nrf52"):
        variant["family"] = "nrf52"
    elif variant["family"] == "atmel-samd":
        if "M0" in variant["model"] or "SAMD21" in variant["model"]:
            variant["family"] = "samd21"
        elif "M4" in variant["model"]:
            variant["family"] = "samd51"
        else:
            try:
                samd_keywords = find_keywords(
                    f"https://raw.githubusercontent.com/adafruit/circuitpython/main/ports/atmel-samd/boards/{variant['_id']}/mpconfigboard.h",
                    {"SAMD21", "SAMD51"},
                )
            except:
                samd_keywords = find_keywords(variant["info_url"], {"SAMD21", "SAMD51"})

            if samd_keywords == {"SAMD21"}:
                variant["family"] = "samd21"
            elif samd_keywords == {"SAMD51"}:
                variant["family"] = "samd51"
            else:
                cant_determine_samd.append(variant)

print(f"Got {len(all_variants)} variants")

for variant in cant_determine_samd:
    print("Could not determine SAMD variant for", variant)

for variant in all_variants:
    # https://github.com/thonny/thonny/discussions/3181
    if variant["model"] == "EDU PICO for Pico W":
        variant["downloads"].append({
                "version": "9.0.0-beta.2",
                "url": "https://downloads.circuitpython.org/bin/cytron_edu_pico_w/en_US/adafruit-circuitpython-cytron_edu_pico_w-en_US-9.0.0-beta.2.uf2"
            })

save_variants(
    all_variants,
    ["uf2"],
    {"rp2", "samd21", "samd51", "nrf51", "nrf52", "esp32s2", "esp32s3"},
    "circuitpython-variants-uf2.json",
)

save_variants(
    all_variants,
    ["hex"],
    {"nrf52"},
    "circuitpython-variants-daplink.json",
)

save_variants(
    all_variants,
    ["bin"],
    {"esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6", "esp32h2"},
    "circuitpython-variants-esptool.json",
)

print("Done")
