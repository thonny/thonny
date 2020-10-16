#!/usr/bin/env python3
# Assumes https://github.com/microsoft/uf2-samdx1 to be next to thonny dev directory

import json
import os.path

relevant_vars = [
    "VENDOR_NAME",
    "PRODUCT_NAME",
    "VOLUME_LABEL",
    "INDEX_URL",
    "BOARD_ID",
    "USB_VID",
    "USB_PID",
]


def update_info(existing_map, name, info_path):
    info = {}
    with open(info_path, encoding="utf-8") as fp:
        for line in fp:
            if " //" in line:
                line = line[: line.find(" //")]
            parts = list(map(str.strip, line.strip().split(maxsplit=2)))
            if len(parts) == 3 and parts[0] == "#define" and parts[1] in relevant_vars:
                value = parts[2]
                if value.startswith('"'):
                    value = value[1:-1]
                info[parts[1]] = value

    if "BOARD_ID" in info:
        combined_record = existing_map.get(info["BOARD_ID"], {})
        combined_record.update(info)
        if "FIRMWARE_DOWNLOAD" not in combined_record:
            combined_record["FIRMWARE_DOWNLOAD"] = ""
        existing_map[info["BOARD_ID"]] = combined_record


if __name__ == "__main__":
    file_path = "firmware_mapping.json"
    with open(file_path, encoding="utf-8") as fp:
        existing_map = json.load(fp)

    samd_info_dir = os.path.abspath("../../../../uf2-samdx1/boards")

    for name in os.listdir(samd_info_dir):
        info_path = samd_info_dir + "/" + name + "/board_config.h"
        if os.path.exists(info_path):
            update_info(existing_map, name, info_path)

    with open(file_path, "w", encoding="utf-8") as fp:
        json.dump(existing_map, fp, indent=4)
