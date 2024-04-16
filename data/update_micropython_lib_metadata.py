import json
import os.path
import glob

import requests

from bs4 import BeautifulSoup
from markdown import markdown

def markdown_to_text(markdown_string):
    html = markdown(markdown_string)
    return BeautifulSoup(html, "lxml").text

URL_PREFIX = "https://github.com/micropython/micropython-lib/tree/master"

os.chdir("../../micropython-lib")
mp_lib_path = os.getcwd()
os.system("git pull")

fallback_descriptions = {
    "aioble-central": "A subset of the modules in 'aioble'",
    "aioble-client": "A subset of the modules in 'aioble'",
    "aioble-core": "A subset of the modules in 'aioble'",
    "aioble-l2cap": "A subset of the modules in 'aioble'",
    "aioble-security": "A subset of the modules in 'aioble'",
    "aioble-server": "A subset of the modules in 'aioble'",
    "cbor2": "Encoding and decoding for the Concise Binary Object Representation (CBOR, RFC 8949) serialization format",
    "iperf3": "Pure Python, iperf3-compatible network performance test tool",
    "lora": "MicroPython LoRa module",
    "lora-async": "MicroPython LoRa async modem driver",
    "lora-stm32wl5": "MicroPython LoRa STM32WL55 embedded sub-ghz radio driver",
    "lora-sx126x": "MicroPython LoRa SX126x (SX1261, SX1262) driver",
    "lora-sx127x": "MicroPython LoRa SX127x driver",
    "lora-sync": "MicroPython LoRa synchronous modem driver",
    "pyjwt" : "MicroPython compatible implementation of RFC 7519 (JSON Web Token)"

}

data = {}

# https://github.com/micropython/micropython-lib/blob/master/tools/build.py
lib_dirs = ["micropython", "python-stdlib", "python-ecosys"]
for lib_dir in lib_dirs:
    for manifest_path in glob.glob(os.path.join(lib_dir, "**", "manifest.py"), recursive=True):
        dirname = os.path.dirname(manifest_path)
        dist_name = os.path.basename(dirname)
        print("Processing", dist_name)

        description = ""
        readme_url = f"https://raw.githubusercontent.com/micropython/micropython-lib/master/{dirname}/README.md"
        response = requests.get(readme_url, headers={'Accept-Encoding': 'gzip'})

        if response.status_code != 404:
            in_first_para = False
            for line in response.text.splitlines():
                line = line.strip()
                if not in_first_para:
                    if not line or line == dist_name or line.startswith("=") or line.startswith("#"):
                        # probably the title
                        continue
                    else:
                        in_first_para = True

                assert in_first_para
                if line:
                    description += " " + line
                else:
                    break

        data[dist_name] = {"project_url": URL_PREFIX + "/" + dirname}

        if description:
            print("Found desc:", description)
            description = markdown_to_text(description.replace("`", "'")).strip()
            print("After cleaning:", description)
        elif dist_name in fallback_descriptions:
            description = fallback_descriptions[dist_name]
        elif dirname.startswith("python-stdlib"):
            description = f"MicroPython port of Python standard library module '{dist_name}'"

        if description:
            data[dist_name]["description"] = description

os.chdir(os.path.dirname(__file__))

data = dict(sorted(data.items()))
with open("micropython-lib-metadata.json", "wt", encoding="utf-8") as fp:
    json.dump(data, fp=fp, indent=4)

