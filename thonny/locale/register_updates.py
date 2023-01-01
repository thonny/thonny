import json
import os.path

import polib
import pyperclip

locale_dir = os.path.dirname(__file__)


def register_locale(name: str) -> None:
    print(f"Processing {name}")
    po_path = os.path.join(locale_dir, name, "LC_MESSAGES", "thonny.po")
    po = polib.pofile(po_path)

    registered_path = os.path.join(locale_dir, name, "LC_MESSAGES", "registered.json")
    if not os.path.exists(registered_path):
        with open(registered_path, "w", encoding="utf-8") as fp:
            fp.write("{}")

    with open(registered_path, encoding="utf-8") as fp:
        registered = json.load(fp)

    new_registered = {}

    new_messages = []

    for entry in po:
        if entry.msgid not in registered or registered[entry.msgid] != entry.msgstr:
            msg = entry.msgstr.strip().replace("\n", " ")
            if not msg.endswith("."):
                msg = msg + "."
            new_messages.append(msg)

        if entry.msgstr:
            new_registered[entry.msgid] = entry.msgstr

    if new_messages:
        print("\n".join(new_messages))
        pyperclip.copy("\n".join(new_messages))

        input("... Press ENTER to confirm! ...")

    with open(registered_path, "w", encoding="utf-8") as fp:
        json.dump(new_registered, fp, sort_keys=True, indent=4, ensure_ascii=False)

    print("--------------------------------------")


for name in os.listdir(locale_dir):
    if os.path.isdir(name):
        register_locale(name)
