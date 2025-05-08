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

UNSTABLE_VERSION = r"\d{8}-v1.26.0-preview\.\d+\.[a-z0-9]{10}"
PREV_RELEVANT_VERSION = "1.24.1"
PREV_RELEVANT_VERSION_IN_URL = "20241129-v1.24.1"


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

mcu_list = "esp8266, esp32, esp32s2, esp32s3, esp32c3, esp32c6, rp2040, rp2350, samd21, samd51, nrf51, nrf52"

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
        elif mcu.lower() in ["rp2040", "rp2350"]:
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
    ["0.0.5", "0.0.4"],
    badger_variants,
)

for variant in badger_variants:
    if "title" not in variant:
        variant["title"] = f"{variant['model']} (with Pimoroni libraries)"


all_variants += badger_variants

########################################################
pimo2350_variants = [
    {
        "_id": "pico2",
        "vendor": "Raspberry Pi",
        "model": "Pico 2",
    },
    {
        "_id": "pico2b_rp2350",
        "vendor": "Raspberry Pi",
        "model": "Pico 2 (b)",
    },
    {
        "_id": "pico2_w",
        "vendor": "Raspberry Pi",
        "model": "Pico 2 W",
    },
    {
        "_id": "pico_plus2_rp2350",
        "model": "Pico Plus 2",
    },
    {
        "_id": "plasma2350",
        "model": "Plasma 2350",
    },
    {
        "_id": "tiny2350",
        "model": "Tiny 2350",
    },
]

print(f"Updating {len(pimo2350_variants)} Pimoroni 2350")

add_defaults_and_downloads_to_variants(
    {
        "vendor": "Pimoroni",
        "family": "rp2",
        "info_url": "https://github.com/pimoroni/pimoroni-pico-rp2350/releases",
        "_download_url_pattern": "https://github.com/pimoroni/pimoroni-pico-rp2350/releases/download/v{version}/{id}-v{version}-pimoroni-micropython.uf2",
    },
    ["0.0.12", "0.0.11"],
    pimo2350_variants,
)

for variant in pimo2350_variants:
    if "title" not in variant:
        variant["title"] = f"{variant['model']} (with Pimoroni libraries)"


all_variants += pimo2350_variants

########################################################
pimoroni_variants = [
    {
        "_id": "pico",
        "vendor": "Raspberry Pi",
        "model": "Pico",
    },
    {
        "_id": "picolipo_16mb",
        "model": "Pimoroni Pico LiPo (16MB)",
    },
    {
        "_id": "picolipo_4mb",
        "model": "Pimoroni Pico LiPo (4MB)",
    },
    {
        "_id": "picow",
        "vendor": "Raspberry Pi",
        "model": "Pico W",
    },
    {
        "_id": "cosmic_unicorn",
        "model": "Cosmic Unicorn",
    },
    {
        "_id": "enviro",
        "model": "Enviro",
    },
    {
        "_id": "galactic_unicorn",
        "model": "Galactic Unicorn",
    },
    {
        "_id": "inky_frame",
        "model": "Inky Frame",
    },
    {
        "_id": "stellar_unicorn",
        "model": "Stellar Unicorn",
    },
    {
        "_id": "tiny2040_8mb",
        "model": "Tiny 2040",
    },
    {
        "_id": "tufty2040",
        "model": "Tufty 2040",
    },
]

print(f"Updating {len(pimoroni_variants)} Pimoroni variants")

add_defaults_and_downloads_to_variants(
    {
        "vendor": "Pimoroni",
        "family": "rp2",
        "info_url": "https://github.com/pimoroni/pimoroni-pico/releases",
        "_download_url_pattern": "https://github.com/pimoroni/pimoroni-pico/releases/download/v{version}/{id}-v{version}-pimoroni-micropython.uf2",
    },
    ["1.23.0-1"],
    pimoroni_variants,
)

for variant in pimoroni_variants:
    if "title" not in variant:
        variant["title"] = f"{variant['model']} (with Pimoroni libraries)"


all_variants += pimoroni_variants

########################################################
pololu_variants = [
    {
        "vendor": "Pololu",
        "model": "3pi+ 2040 Robot",
        "family": "rp2",
        "info_url": "https://github.com/pololu/micropython-build/releases/",
        "downloads": [
            {
                "version": "240117",
                "url": "https://github.com/pololu/micropython-build/releases/download/240117/micropython-pololu-3pi-2040-robot-v1.22.1-240117.uf2"
            },
            {
                "version": "231113",
                "url": "https://github.com/pololu/micropython-build/releases/download/231113/micropython-pololu-3pi-2040-robot-v1.22.0-preview-231113.uf2"
            },
            {
                "version": "230510",
                "url": "https://github.com/pololu/micropython-build/releases/download/230510/micropython-pololu-3pi-2040-robot-v1.20.0-230510.uf2"
            },
            {
                "version": "230405",
                "url": "https://github.com/pololu/micropython-build/releases/download/230405/micropython-pololu-3pi-2040-robot-v1.19.1-230405.uf2"
            },
            {
                "version": "230303",
                "url": "https://github.com/pololu/micropython-build/releases/download/230303/micropython-pololu-3pi-2040-robot-v1.19.1-230303.uf2"
            },
        ]
    },
    {
        "vendor": "Pololu",
        "model": "Zumo 2040 Robot",
        "family": "rp2",
        "info_url": "https://github.com/pololu/micropython-build/releases/",
        "downloads": [
            {
                "version": "240117",
                "url": "https://github.com/pololu/micropython-build/releases/download/240117/micropython-pololu-zumo-2040-robot-v1.22.1-240117.uf2"
            },
            {
                "version": "231113",
                "url": "https://github.com/pololu/micropython-build/releases/download/231113/micropython-pololu-zumo-2040-robot-v1.22.0-preview-231113.uf2"
            },
        ]
    },
]

all_variants += pololu_variants

#####################################################
simplified_microbits_and_calliopes = [
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
                "version": "2.1.2",
                "url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases/download/v2.1.2/micropython-microbit-v2.1.2.hex",
            },
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
    {
        "vendor": "Calliope",
        "model": "Calliope mini 3",
        "family": "nrf52",
        "info_url": "https://github.com/calliope-mini/calliope-mini-micropython",
        "downloads": [],
        "popular": True,
    },
]
print(f"Adding {len(simplified_microbits_and_calliopes)} simplified micro:bit-s")
all_variants += simplified_microbits_and_calliopes

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
    {"esp8266", "esp32", "esp32s2", "esp32s3", "esp32c3", "esp32c6"},
    "micropython-variants-esptool.json",
    latest_prerelease_regex=UNSTABLE_VERSION,
)

print("Done")
