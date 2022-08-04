import json
from typing import Dict
import urllib.request
from html.parser import HTMLParser

FAKE_USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
base_url = "https://circuitpython.org/downloads"


def get_attr_value(attrs, name):
    for key, value in attrs:
        if key == name:
            return value

    return None


class IndexParser(HTMLParser):
    def __init__(self, *, convert_charrefs=True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.boards = []

    def handle_starttag(self, tag: str, attrs: Dict[str, str]):
        if tag == "div" and get_attr_value(attrs, "class") == "download":
            id = get_attr_value(attrs, "data-id")
            self.boards.append(
                {
                    "board_vendor": get_attr_value(attrs, "data-manufacturer"),
                    "build_name": get_attr_value(attrs, "data-name"),
                    "board_family": get_attr_value(attrs, "data-mcufamily"),
                    "url": f"https://circuitpython.org/board/{id}/",
                    "downloads_url": f"https://adafruit-circuit-python.s3.amazonaws.com/index.html?prefix=bin/{id}/en_US/",
                }
            )


parser = IndexParser()

req = urllib.request.Request(
    base_url,
    data=None,
    headers={
        "User-Agent": FAKE_USER_AGENT,
        "Cache-Control": "no-cache",
    },
)

with urllib.request.urlopen(req) as fp:
    parser.feed(fp.read().decode("utf-8"))

all_boards = parser.boards

print("Applying tweaks")
for board in all_boards:
    if board["build_name"].startswith("micro:bit v2"):
        board["target_volume_patterns"] = [
            {"file_name" : "DETAILS.TXT", "line_pattern" : "^Unique ID: 990[4-6].+$"}
        ]
    elif board["board_family"].upper() in ["RP2040", "raspberrypi"]:
        board["target_volume_patterns"] = [
            {"file_name" : "INFO_UF2.TXT", "line_pattern" : "^Board-ID: RPI-RP2.+$"}
        ]


# print(parser.boards)
print(f"Got {len(all_boards)} boards")

with open("circuitpython-devices.json", mode="w", encoding="utf-8") as fp:
    json.dump(all_boards, fp, indent=4)

print("Done")
