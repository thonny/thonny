from html.parser import HTMLParser
from typing import Dict

from update_variants_common import get_attr_value, urlopen_ua, add_mappings, save_variants

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
                    "board_vendor": get_attr_value(attrs, "data-manufacturer"),
                    "model_name": get_attr_value(attrs, "data-name"),
                    "board_family": get_attr_value(attrs, "data-mcufamily"),
                    "downloads_url": f"https://circuitpython.org/board/{data_id}/",
                }
            )


parser = IndexParser()

with urlopen_ua(base_url) as fp:
    parser.feed(fp.read().decode("utf-8"))

all_variants = parser.variants.copy()

for i, variant in enumerate(all_variants):
    print("Processing", i+1, variant)
    # TODO:
    if variant["downloads_url"] == "https://circuitpython.org/board/unexpectedmaker_feathers3/":
        variant["downloads_url"] = "https://circuitpython.org/board/unexpectedmaker_feather3/"
    add_mappings(variant, "circuitpython")

print(f"Got {len(all_variants)} variants")

save_variants(all_variants, "circuitpython-variants.json")

print("Done")
