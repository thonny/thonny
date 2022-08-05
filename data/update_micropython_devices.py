import json
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


all_boards = []

mcu_list = "RA4M1, RA4W1, RA6M1, RA6M2, RP2040, STM32H747, cc3200, esp32, esp32c3, esp32s2, esp32s3, esp8266, mimxrt, nRF52840, nrf51, nrf52, nrf91, rp2040, samd21, samd51, stm32, stm32f0, stm32f4, stm32f7, stm32g0, stm32g4, stm32h7, stm32l0, stm32l4, stm32wb, stm32wl"

for mcu in map(str.strip, mcu_list.split(",")):
    print("Fetching mcu", mcu, end="... ")
    parser = IndexParser()
    with urlopen(base_url + "?mcu=" + mcu) as fp:
        parser.feed(fp.read().decode("utf-8"))

    print(f"Adding {len(parser.boards)} boards")
    for board in parser.boards:

        all_boards.append(
            {
                "board_vendor": board["board-vendor"],
                "build_name": board["board-product"],
                "board_family": mcu,
                "url": base_url + board["id"],
            }
        )

pimoroni_boards = [
    {
        "id": "pimoroni-badger2040",
        "board_vendor": "Pimoroni",
        "board_name": "Badger 2040",
        "build_name": "Badger 2040 (with Pimoroni libraries)",
    },
    {"id": "pimoroni-pico", "board_vendor": "Raspberry Pi", "build_name": "Pico (with Pimoroni libraries)"},
    {
        "id": "pimoroni-picolipo_16mb",
        "board_vendor": "Pimoroni",
        "board_name": "Pimoroni Pico LiPo (16MB)",
        "build_name": "Pimoroni Pico LiPo (16MB) (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-picolipo_4mb",
        "board_vendor": "Pimoroni",
        "board_name": "Pimoroni Pico LiPo (4MB)",
        "build_name": "Pimoroni Pico LiPo (4MB) (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-picow",
        "board_vendor": "Raspberry Pi",
        "board_name": "Pico W",
        "build_name": "Pico W (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-tiny2040",
        "board_vendor": "Pimoroni",
        "board_name": "Tiny 2040",
        "build_name": "Tiny 2040 (with Pimoroni libraries)",
    },
    {
        "id": "pimoroni-tufty2040",
        "board_vendor": "Pimoroni",
        "board_name": "Tufty 2040",
        "build_name": "Tufty 2040 (with Pimoroni libraries)",
    },
]

print(f"Adding {len(pimoroni_boards)} Pimoroni variants")
for board in pimoroni_boards:
    all_boards.append(
        {
            "board_vendor": board["board_vendor"],
            "board_name": board["board_name"],
            "build_name": board["build_name"],
            "board_family": "RP2040",
            "url": "https://github.com/pimoroni/pimoroni-pico/releases",
            "download_filename_patterns": [f"^{board['id']}-v.+.uf2$"],
        }
    )
# print(all_boards)

simplified_microbits = [
    {
        "board_vendor": "BBC",
        "board_name": "micro:bit v1",
        "build_name": "micro:bit v1 (original simplified API)",
        "mcu": "nrf51",
        "url": "https://github.com/bbcmicrobit/micropython/releases",
        "download_filename_patterns": [rf"^.+\.hex$"],
    },
    {
        "board_vendor": "BBC",
        "board_name": "micro:bit v2",
        "build_name": "micro:bit v2 (original simplified API)",
        "mcu": "nrf52",
        "url": "https://github.com/microbit-foundation/micropython-microbit-v2/releases",
        "download_filename_patterns": [rf"^.+\.hex$"],
    },
]
print(f"Adding {len(simplified_microbits)} simplified micro:bit-s")
for board in simplified_microbits:
    all_boards.append(
        {
            "board_vendor": board["board_vendor"],
            "build_name": board["build_name"],
            "board_family": board["mcu"],
            "url": board["url"],
            "download_filename_patterns": board["download_filename_patterns"],
        }
    )
# print(all_boards)

print(f"Got {len(all_boards)} boards")

print("Applying tweaks")
for board in all_boards:
    if board["build_name"] == "micro:bit v1":
        board["build_name"] += " (standard API)"
        board["board_name"] = "micro:bit v1"

    if board["build_name"].startswith("micro:bit v1"):
        board["target_volume_patterns"] = [
            {"file_name" : "DETAILS.TXT", "line_pattern" : "^Unique ID: 990[0-3].+$"}
        ]
    elif board["build_name"].startswith("micro:bit v2"):
        board["target_volume_patterns"] = [
            {"file_name" : "DETAILS.TXT", "line_pattern" : "^Unique ID: 990[4-6].+$"}
        ]
    elif board["board_family"].upper() == "RP2040":
        board["target_volume_patterns"] = [
            {"file_name" : "INFO_UF2.TXT", "line_pattern" : "^Board-ID: RPI-RP2.+$"}
        ]



with open("micropython-builds.json", mode="w", encoding="utf-8") as fp:
    json.dump(all_boards, fp, indent=4)

print("Done")
