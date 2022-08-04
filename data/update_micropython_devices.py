from typing import Dict
from urllib.request import urlopen
from html.parser import HTMLParser

base_url = "https://micropython.org/download/"


def get_attr_value(attrs, name):
    for key, value in attrs:
        if key == name:
            return value

    return None


class IndexParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.boards = []
        self._current_board = None
        self._current_attribute = None

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "a" and get_attr_value(attrs, "class") == "board-card":
            self._current_board = {"id": get_attr_value(attrs, "href")}
            self.boards.append(self._current_board)

        elif (
            tag == "div"
            and get_attr_value(attrs, "class") in ["board-product", "board-vendor"]
            and self._current_board
        ):
            self._current_attribute = get_attr_value(attrs, "class")

    def handle_endtag(self, tag):
        if tag == "a":
            self._current_board = None
        elif tag == "div":
            self._current_attribute = None

    def handle_data(self, data):
        if self._current_attribute:
            assert self._current_board
            self._current_board[self._current_attribute] = data.strip()


out = []

mcu_list = "RA4M1, RA4W1, RA6M1, RA6M2, RP2040, STM32H747, cc3200, esp32, esp32c3, esp32s2, esp32s3, esp8266, mimxrt, nRF52840, nrf51, nrf52, nrf91, rp2040, samd21, samd51, stm32, stm32f0, stm32f4, stm32f7, stm32g0, stm32g4, stm32h7, stm32l0, stm32l4, stm32wb, stm32wl"

for mcu in map(str.strip, mcu_list.split(",")):
    print("Fetching mcu", mcu, end="... ")
    parser = IndexParser()
    with urlopen(base_url + "?mcu=" + mcu) as fp:
        parser.feed(fp.read().decode("utf-8"))

    print(f"Adding {len(parser.boards)} boards")
    for board in parser.boards:
        out.append(
            {
                "vendor": board["board-vendor"],
                "product": board["board-product"],
                "family": mcu,
                "url": base_url + board["id"],
            }
        )

pimoroni_boards = [
    {
        "id": "pimoroni-badger2040",
        "vendor": "Pimoroni",
        "product": "Badger 2040 (with Pimoroni libraries)",
    },
    {"id": "pimoroni-pico", "vendor": "Raspberry Pi", "product": "Pico (with Pimoroni libraries)"},
    {
        "id": "pimoroni-picolipo_16mb",
        "vendor": "Pimoroni",
        "product": "Pimoroni Pico LiPo (16MB) (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-picolipo_4mb",
        "vendor": "Pimoroni",
        "product": "Pimoroni Pico LiPo (4MB) (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-picow",
        "vendor": "Raspberry Pi",
        "product": "Pico W (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-tiny2040",
        "vendor": "Pimoroni",
        "product": "Tiny 2040 (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-tufty2040",
        "vendor": "Pimoroni",
        "product": "Tufty 2040 (with Pimoroni libraries)",
    },
]

print(f"Adding {len(pimoroni_boards)} Pimoroni variants")
for board in pimoroni_boards:
    out.append(
        {
            "vendor": board["vendor"],
            "product": board["product"],
            "family": "RP2040",
            "url": "https://github.com/pimoroni/pimoroni-pico/releases",
            "filename_prefix": board["id"] + "-v",
        }
    )
print(out)
