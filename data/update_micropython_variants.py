from html.parser import HTMLParser
from typing import Dict, List

from update_variants_common import (
    get_attr_value,
    save_variants,
    read_page,
    find_download_links,
    add_download_link_if_exists,
)

base_url = "https://micropython.org/download/"

UNSTABLE_VERSION = "20220805-unstable-v1.19.1-240-g9dfabcd6d"
PREV_RELEVANT_VERSION = "1.18"
PREV_RELEVANT_VERSION_IN_URL = "20220117-v1.18"

PIMORONI_LATEST_STABLE_VERSION = "1.19.6"
PIMORONI_LATEST_UNSTABLE_VERSION = "------"
PIMORONI_PREV_RELEVANT_VERSION = "1.18.7"


class IndexParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.variants = []
        self._current_variant = None
        self._current_attribute = None

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "a" and get_attr_value(attrs, "class") == "board-card":
            self._current_variant = {"id": get_attr_value(attrs, "href")}
            self.variants.append(self._current_variant)

        elif (
            tag == "div"
            and get_attr_value(attrs, "class") in ["board-product", "board-vendor"]
            and self._current_variant
        ):
            self._current_attribute = get_attr_value(attrs, "class")

    def handle_endtag(self, tag):
        if tag == "a":
            self._current_variant = None
        elif tag == "div":
            self._current_attribute = None

    def handle_data(self, data):
        if self._current_attribute:
            assert self._current_variant
            self._current_variant[self._current_attribute] = data.strip()


all_variants = []

# mcu_list = "RA4M1, RA4W1, RA6M1, RA6M2, RP2040, STM32H747, cc3200, esp32, esp32c3, esp32s2, esp32s3, esp8266, mimxrt, nRF52840, nrf51, nrf52, nrf91, rp2040, samd21, samd51, stm32, stm32f0, stm32f4, stm32f7, stm32g0, stm32g4, stm32h7, stm32l0, stm32l4, stm32wb, stm32wl"
mcu_list = "RP2040, esp32s2, esp32s3, rp2040, samd21, samd51, nrf51"

for mcu in map(str.strip, mcu_list.split(",")):
    print("Fetching mcu", mcu, end="... ")
    parser = IndexParser()
    parser.feed(read_page(base_url + "?mcu=" + mcu))

    print(f"Adding {len(parser.variants)} boards ..........................................")
    for pvariant in parser.variants:

        if mcu.lower().startswith("nrf51"):
            board_family = "nrf51"
        elif mcu.lower().startswith("nrf52"):
            board_family = "nrf52"
        elif mcu.lower() == "rp2040":
            board_family = "rp2"
        else:
            board_family = mcu

        variant = {
            "_id": pvariant["id"],
            "vendor": pvariant["board-vendor"],
            "model": pvariant["board-product"],
            "family": board_family,
            "info_url": base_url + pvariant["id"],
        }
        variant["downloads"]: List[Dict[str, str]]
        all_variants.append(variant)

pimoroni_variants = [
    {
        "_id": "pimoroni-badger2040",
        "vendor": "Pimoroni",
        "model": "Badger 2040",
        "family": "rp2",
        "_download_url_pattern": rf"/pimoroni-badger2040-v({PIMORONI_LATEST_STABLE_VERSION})-micropython-without-badger-os\.uf2$",
    },
    {
        "_id": "pimoroni-badger2040-with-badger-os",
        "vendor": "Pimoroni",
        "model": "Badger 2040",
        "family": "rp2",
        "variant": "with Pimoroni libraries and BadgerOS",
        "_download_url_pattern": rf"/pimoroni-badger2040-v({PIMORONI_LATEST_STABLE_VERSION})\-micropython\.uf2$",
    },
    {
        "_id": "pimoroni-pico",
        "vendor": "Raspberry Pi",
        "model": "Pico",
        "family": "rp2",
    },
    {
        "_id": "pimoroni-picolipo_16mb",
        "vendor": "Pimoroni",
        "model": "Pimoroni Pico LiPo (16MB)",
        "family": "rp2",
    },
    {
        "_id": "pimoroni-picolipo_4mb",
        "vendor": "Pimoroni",
        "model": "Pimoroni Pico LiPo (4MB)",
        "family": "rp2",
    },
    {
        "_id": "pimoroni-picow",
        "vendor": "Raspberry Pi",
        "model": "Pico W",
        "family": "rp2",
    },
    {
        "_id": "pimoroni-tiny2040",
        "vendor": "Pimoroni",
        "model": "Tiny 2040",
        "family": "rp2",
    },
    {
        "_id": "pimoroni-tufty2040",
        "vendor": "Pimoroni",
        "model": "Tufty 2040",
        "family": "rp2",
    },
]

for variant in pimoroni_variants:
    if "variant" not in variant:
        variant["variant"] = "with Pimoroni libraries"

    stable_url_pattern = variant.get(
        "_download_url_pattern",
        rf"/{variant['_id']}-v({PIMORONI_LATEST_STABLE_VERSION})-micropython.uf2$",
    )

    unstable_url_pattern = stable_url_pattern.replace(
        PIMORONI_LATEST_STABLE_VERSION, PIMORONI_LATEST_UNSTABLE_VERSION
    )
    old_url_pattern = stable_url_pattern.replace(
        PIMORONI_LATEST_STABLE_VERSION, PIMORONI_PREV_RELEVANT_VERSION
    )

    variant["info_url"] = "https://github.com/pimoroni/pimoroni-pico/releases"
    variant["downloads"] = find_download_links(
        "https://github.com/pimoroni/pimoroni-pico/releases",
        stable_url_pattern,
        1,
        unstable_url_pattern,
        1,
        url_prefix="https://github.com",
    )
    variant["downloads"] += find_download_links(
        "https://github.com/pimoroni/pimoroni-pico/releases",
        old_url_pattern,
        1,
        url_prefix="https://github.com",
    )


print(f"Adding {len(pimoroni_variants)} Pimoroni variants")
all_variants += pimoroni_variants

simplified_microbits = [
    {
        "vendor": "BBC",
        "model": "micro:bit v1",
        "family": "nrf51",
        "variant": "original simplified API",
        "info_url": "https://github.com/bbcmicrobit/micropython/releases/",
        "downloads": [
            {
                "version": "1.0.1",
                "url": "https://github.com/bbcmicrobit/micropython/releases/download/v1.0.1/microbit-micropython-v1.0.1.hex",
            }
        ],
    },
    {
        "vendor": "BBC",
        "model": "micro:bit v2",
        "variant": "original simplified API",
        "family": "nrf52",
        "info_url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/",
        "downloads": [
            {
                "version": "2.0.0",
                "url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/download/v2.0.0/micropython-microbit-v2.0.0.hex",
            }
        ],
    },
]
print(f"Adding {len(simplified_microbits)} simplified micro:bit-s")
all_variants += simplified_microbits

print(f"Got {len(all_variants)} boards")

print("Adding mappings")
for i, variant in enumerate(all_variants):
    print("Processing", i + 1, "of", len(all_variants), variant)
    if "micro:bit" in variant["model"]:
        extension = r"hex"
        variant["_flasher"] = "daplink"
    else:
        extension = "uf2"
        variant["_flasher"] = "uf2"

    if not "downloads" in variant:
        variant["downloads"] = find_download_links(
            variant["info_url"],
            r"v(\d+(?:\.\d+)+)\." + extension,
            1,
            rf"({UNSTABLE_VERSION})\." + extension,
            1,
            url_prefix="https://micropython.org/",
        )

        prev_major_url = f"https://micropython.org/resources/firmware/{variant['_id']}-{PREV_RELEVANT_VERSION_IN_URL}.uf2"
        add_download_link_if_exists(variant["downloads"], prev_major_url, PREV_RELEVANT_VERSION)


save_variants(
    all_variants,
    "uf2",
    {"rp2", "samd21", "samd51", "nrf51", "nrf52", "esp32s2", "esp32s3"},
    "micropython-variants-uf2.json",
)


save_variants(
    all_variants,
    "daplink",
    {"rp2", "samd21", "samd51", "nrf51", "nrf52", "esp32s2", "esp32s3"},
    "micropython-variants-daplink.json",
)

print("Done")
