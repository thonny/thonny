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

    review_messages = []

    for entry in po:
        if entry.msgstr and (
            entry.msgid not in registered or registered[entry.msgid] != entry.msgstr
        ):
            msg = entry.msgstr.strip().replace("\n", " ")
            if not msg.endswith("."):
                msg = msg + "."

            review_messages.append(msg)

        if entry.msgstr:
            new_registered[entry.msgid] = entry.msgstr

    if review_messages:
        print("\n".join(review_messages))
        pyperclip.copy("\n".join(review_messages))

        input(f"... Press ENTER to confirm {name}! ...")

    with open(registered_path, "w", encoding="utf-8") as fp:
        json.dump(new_registered, fp, sort_keys=True, indent=4, ensure_ascii=False)

    print("--------------------------------------")


for name in os.listdir(locale_dir):
    path = os.path.join(locale_dir, name)
    if os.path.isdir(path):
        register_locale(name)
