import json
from typing import Optional, List, Dict, Any

import requests
import re
import os.path

def normalize(name):
    return re.sub(r"[-_.]+", "-", name).lower()


def update_packages_json(top_url: Optional[str], extra_regexes: List[str], target_path: str,
                         attributes: List[str]) -> None:
    print("UPDATING", target_path)
    packages = {}
    if top_url is not None:
        top = requests.get(top_url).json()
        for p in top:
            if p["name"] is None:
                continue
            packages[normalize(p["name"])] = filter_atts(p, attributes)
    else:
        packages = {}

    if extra_regexes:
        index_path = "pypi_simple.html"
        if not os.path.exists(index_path):
            index = requests.get("https://pypi.org/simple/")
            with open(index_path, "w", encoding="utf-8") as fp:
                fp.write(index.text)

        with open(index_path, encoding="utf-8") as fp:
            index_lines = fp.read().splitlines()

        for line in index_lines:
            line_suffix = "</a>"
            if not line.endswith(line_suffix):
                continue
            name = normalize(line[:-(len(line_suffix))].split(">")[-1])
            for regex in extra_regexes:
                if re.search(regex, name):
                    metadata = fetch_metadata(name, attributes)
                    if metadata is not None:
                        packages[name] = metadata
                    break

    sorted_packages = list(sorted(packages.values(), key=lambda s: s["name"]))

    with open(target_path, "w", encoding="utf-8") as fp:
        json.dump(sorted_packages, fp, indent=4, sort_keys=True)

    print("DONE\n\n")

def filter_atts(d: Dict[str, Any], attributes: List[str]) -> Dict[str, Any]:
    result = {}
    for att in attributes:
        if att in d:
            result[att] = d[att]

    return result

def fetch_metadata(name: str, attributes: List[str]) -> Optional[Dict[str, Any]]:
    print("Fetching metadata for", name)
    full_meta = requests.get(f"https://pypi.org/pypi/{name}/json").json()
    if "info" not in full_meta:
        print("WARNING", full_meta)
        return None
    return filter_atts(full_meta["info"], attributes)

attributes = ["name", "summary"]

update_packages_json("https://robert-96.github.io/top-pypi-packages/json/packages.json",
                     [], "pypi_summaries_cpython.json", attributes)

update_packages_json(None,
                     [r"micropython-", "-micropython"], "pypi_summaries_micropython.json", attributes)

update_packages_json(None,
                     [r"circuitpython-", "-circuitpython"], "pypi_summaries_circuitpython.json", attributes)

