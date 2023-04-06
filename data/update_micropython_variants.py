from html.parser import HTMLParser
from typing import Dict, List

from data.update_variants_common import add_defaults_and_downloads_to_variants
from update_variants_common import (
    get_attr_value,
    save_variants,
    read_page,
    find_download_links,
    add_download_link_if_exists,
)

base_url = "https://micropython.org/download/"

UNSTABLE_VERSION = r"\d{8}-unstable-v1.19.1-\d+-[a-z0-9]{10}"
PREV_RELEVANT_VERSION = "1.18"
PREV_RELEVANT_VERSION_IN_URL = "20220117-v1.18"


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
mcu_list = "RP2040, esp8266, esp32, esp32s2, esp32s3, esp32c3, rp2040, samd21, samd51, nrf51"

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
            "downloads": [],
        }
        variant["downloads"]: List[Dict[str, str]]
        all_variants.append(variant)

print("Adding micropython.org downloads")
for i, variant in enumerate(all_variants):
    print("Processing", i + 1, "of", len(all_variants), variant)
    if "micro:bit" in variant["model"]:
        extensions = ["hex"]
    elif variant["family"] in {"esp32s2", "esp32s3"}:
        extensions = ["uf2", "bin"]
    elif "esp" in variant["family"]:
        extensions = ["bin"]
    else:
        extensions = ["uf2"]

    for extension in extensions:
        variant["downloads"] += find_download_links(
            variant["info_url"],
            r"v(\d+(?:\.\d+)+)\." + extension,
            1,
            rf"({UNSTABLE_VERSION})\." + extension,
            1,
            url_prefix="https://micropython.org",
        )

        prev_major_url = f"https://micropython.org/resources/firmware/{variant['_id']}-{PREV_RELEVANT_VERSION_IN_URL}.{extension}"
        add_download_link_if_exists(variant["downloads"], prev_major_url, PREV_RELEVANT_VERSION)

########################################################
badger_variants = [
    {
        "_id": "pimoroni-badger2040",
        "model": "Badger 2040",
    },
    {
        "_id": "pimoroni-badger2040-with-badger-os",
        "model": "Badger 2040",
        "title": "Badger 2040 (with Pimoroni libraries and Badger OS)",
        "_download_url_pattern": "https://github.com/pimoroni/badger2040/releases/download/v{version}/pimoroni-badger2040-v{version}-micropython-with-badger-os.uf2",
    },
    {
        "_id": "pimoroni-badger2040w",
        "model": "Badger 2040 W",
    },
    {
        "_id": "pimoroni-badger2040w-with-examples",
        "model": "Badger 2040 W",
        "title": "Badger 2040 W (with Pimoroni libraries and Badger OS)",
        "_download_url_pattern": "https://github.com/pimoroni/badger2040/releases/download/v{version}/pimoroni-badger2040w-v{version}-micropython-with-badger-os.uf2",
    },
]

print(f"Updating {len(badger_variants)} Badger variants")

add_defaults_and_downloads_to_variants(
    {
        "vendor": "Pimoroni",
        "family": "rp2",
        "info_url": "https://github.com/pimoroni/badger2040/releases",
        "_download_url_pattern": "https://github.com/pimoroni/badger2040/releases/download/v{version}/{id}-v{version}-micropython.uf2",
    },
    ["0.0.2"],
    badger_variants,
)

for variant in badger_variants:
    if "title" not in variant:
        variant["title"] = f"{variant['model']} (with Pimoroni libraries)"


all_variants += badger_variants

########################################################
pimoroni_variants = [
    {
        "_id": "pimoroni-pico",
        "vendor": "Raspberry Pi",
        "model": "Pico",
    },
    {
        "_id": "pimoroni-picolipo_16mb",
        "model": "Pimoroni Pico LiPo (16MB)",
    },
    {
        "_id": "pimoroni-picolipo_4mb",
        "model": "Pimoroni Pico LiPo (4MB)",
    },
    {
        "_id": "pimoroni-picow",
        "vendor": "Raspberry Pi",
        "model": "Pico W",
    },
    {
        "_id": "pimoroni-picow_cosmic_unicorn",
        "model": "Cosmic Unicorn",
    },
    {
        "_id": "pimoroni-picow_enviro",
        "model": "Enviro",
    },
    {
        "_id": "pimoroni-picow_galactic_unicorn",
        "model": "Galactic Unicorn",
    },
    {
        "_id": "pimoroni-picow_inky_frame",
        "model": "Inky Frame",
    },
    {
        "_id": "pimoroni-tiny2040",
        "model": "Tiny 2040",
    },
    {
        "_id": "pimoroni-tufty2040",
        "model": "Tufty 2040",
    },
]

print(f"Updating {len(pimoroni_variants)} Pimoroni variants")

add_defaults_and_downloads_to_variants(
    {
        "vendor": "Pimoroni",
        "family": "rp2",
        "info_url": "https://github.com/pimoroni/pimoroni-pico/releases",
        "_download_url_pattern": "https://github.com/pimoroni/pimoroni-pico/releases/download/v{version}/{id}-v{version}-micropython.uf2",
    },
    ["1.19.18", "1.18.7"],
    pimoroni_variants,
)

for variant in pimoroni_variants:
    if "title" not in variant:
        variant["title"] = f"{variant['model']} (with Pimoroni libraries)"


all_variants += pimoroni_variants

########################################################
pololu_variants = [
    {
        "_id": "pololu-3pi-2040-robot",
        "model": "3pi+ 2040 Robot",
    },
]

print(f"Updating {len(pololu_variants)} Pololu variants")
add_defaults_and_downloads_to_variants(
    {
        "vendor": "Pololu",
        "family": "rp2",
        "info_url": "https://github.com/pololu/micropython-build/releases/",
        "_download_url_pattern": "https://github.com/pololu/micropython-build/releases/download/{version}/micropython-{id}-v1.19.1-{version}.uf2",
    },
    ["230405", "230303"],
    pololu_variants,
)

all_variants += pololu_variants

#####################################################
simplified_microbits = [
    {
        "vendor": "BBC",
        "model": "micro:bit v1",
        "family": "nrf51",
        "title": "micro:bit v1 (original simplified API)",
        "info_url": "https://github.com/bbcmicrobit/micropython/releases/",
        "downloads": [
            {
                "version": "1.1.1",
                "url": "https://github.com/bbcmicrobit/micropython/releases/download/v1.1.1/micropython-microbit-v1.1.1.hex",
            },
            {
                "version": "1.0.1",
                "url": "https://github.com/bbcmicrobit/micropython/releases/download/v1.0.1/microbit-micropython-v1.0.1.hex",
            },
        ],
        "popular": True,
    },
    {
        "vendor": "BBC",
        "model": "micro:bit v2",
        "title": "micro:bit v2 (original simplified API)",
        "family": "nrf52",
        "info_url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/",
        "downloads": [
            {
                "version": "2.1.1",
                "url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/download/v2.1.1/micropython-microbit-v2.1.1.hex",
            },
            {
                "version": "2.0.0",
                "url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/download/v2.0.0/micropython-microbit-v2.0.0.hex",
            },
        ],
        "popular": True,
    },
]
print(f"Adding {len(simplified_microbits)} simplified micro:bit-s")
all_variants += simplified_microbits

print(f"Got {len(all_variants)} boards")


save_variants(
    all_variants,
    ["uf2"],
    {"rp2", "samd21", "samd51", "nrf51", "nrf52", "esp32s2", "esp32s3"},
    "micropython-variants-uf2.json",
    latest_prerelease_regex=UNSTABLE_VERSION,
)


save_variants(
    all_variants,
    ["hex"],
    {"nrf51", "nrf52"},
    "micropython-variants-daplink.json",
    latest_prerelease_regex=UNSTABLE_VERSION,
)

save_variants(
    all_variants,
    ["bin"],
    {"esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3"},
    "micropython-variants-esptool.json",
    latest_prerelease_regex=UNSTABLE_VERSION,
)

print("Done")
