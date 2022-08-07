from html.parser import HTMLParser
from typing import Dict

from update_variants_common import get_attr_value, urlopen_ua, add_mappings, save_variants

base_url = "https://micropython.org/download/"


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

mcu_list = "RA4M1, RA4W1, RA6M1, RA6M2, RP2040, STM32H747, cc3200, esp32, esp32c3, esp32s2, esp32s3, esp8266, mimxrt, nRF52840, nrf51, nrf52, nrf91, rp2040, samd21, samd51, stm32, stm32f0, stm32f4, stm32f7, stm32g0, stm32g4, stm32h7, stm32l0, stm32l4, stm32wb, stm32wl"

for mcu in map(str.strip, mcu_list.split(",")):
    print("Fetching mcu", mcu, end="... ")
    parser = IndexParser()
    with urlopen_ua(base_url + "?mcu=" + mcu) as fp:
        parser.feed(fp.read().decode("utf-8"))

    print(f"Adding {len(parser.variants)} boards ..........................................")
    for pvariant in parser.variants:
        variant = {
            "board_vendor": pvariant["board-vendor"],
            "model_name": pvariant["board-product"],
            "board_family": mcu,
            "downloads_url": base_url + pvariant["id"],
        }
        all_variants.append(variant)

pimoroni_variants = [
    {
        "_id": "pimoroni-badger2040",
        "board_vendor": "Pimoroni",
        "model_name": "Badger 2040",
        "variant_name": "Badger 2040 (with Pimoroni libraries)",
        "_download_url_pattern":
            rf"pimoroni-badger2040-v.+-micropython-without-badger-os\.uf2$"
    },
    {
        "_id": "pimoroni-badger2040-with-badger-os",
        "board_vendor": "Pimoroni",
        "model_name": "Badger 2040",
        "variant_name": "Badger 2040 (with Pimoroni libraries and BadgerOS)",
        "_download_url_pattern": rf"pimoroni-badger2040-v.+\-micropython\.uf2$",
    },
    {
        "_id": "pimoroni-pico",
        "board_vendor": "Raspberry Pi",
        "model_name": "Pico",
        "variant_name": "Pico (with Pimoroni libraries)",
    },
    {
        "_id": "pimoroni-picolipo_16mb",
        "board_vendor": "Pimoroni",
        "model_name": "Pimoroni Pico LiPo (16MB)",
        "variant_name": "Pimoroni Pico LiPo (16MB) (with Pimoroni libraries)",
    },
    {
        "_id": "pimoroni-picolipo_4mb",
        "board_vendor": "Pimoroni",
        "model_name": "Pimoroni Pico LiPo (4MB)",
        "variant_name": "Pimoroni Pico LiPo (4MB) (with Pimoroni libraries)",
    },
    {
        "_id": "pimoroni-picow",
        "board_vendor": "Raspberry Pi",
        "model_name": "Pico W",
        "variant_name": "Pico W (with Pimoroni libraries)",
    },
    {
        "_id": "pimoroni-tiny2040",
        "board_vendor": "Pimoroni",
        "model_name": "Tiny 2040",
        "variant_name": "Tiny 2040 (with Pimoroni libraries)",
    },
    {
        "_id": "pimoroni-tufty2040",
        "board_vendor": "Pimoroni",
        "model_name": "Tufty 2040",
        "variant_name": "Tufty 2040 (with Pimoroni libraries)",
    },
]

for variant in pimoroni_variants:
    if "_download_url_pattern" not in variant:
        variant["_download_url_pattern"] = rf"/{variant['_id']}-v.+-micropython.uf2$"

    variant["board_family"] = "RP2040"
    variant["downloads_url"] = "https://github.com/pimoroni/pimoroni-pico/releases"

print(f"Adding {len(pimoroni_variants)} Pimoroni variants")
all_variants += pimoroni_variants

simplified_microbits = [
    {
        "board_vendor": "BBC",
        "model_name": "micro:bit v1",
        "variant_name": "micro:bit v1 (original simplified API)",
        "board_family": "nrf51",
        "downloads_url": "https://github.com/bbcmicrobit/micropython/releases",
    },
    {
        "board_vendor": "BBC",
        "model_name": "micro:bit v2",
        "variant_name": "micro:bit v2 (original simplified API)",
        "board_family": "nrf52",
        "downloads_url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases",
    },
]
print(f"Adding {len(simplified_microbits)} simplified micro:bit-s")
all_variants += simplified_microbits

print(f"Got {len(all_variants)} boards")

print("Adding mappings")
for i, variant in enumerate(all_variants):
    print("Adding mapping for", i+1, variant)
    add_mappings(variant, "micropython")

save_variants(all_variants, "micropython-variants.json")

print("Done")
