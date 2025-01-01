import json
import re

def format_log(in_path: str, out_path: str) -> None:
    with open(in_path, encoding="utf-8") as fp:
        in_txt = fp.read()

    out_fp = open(out_path, mode="wt", encoding="utf-8")

    current_block_sender = None
    current_block = ""
    for part in in_txt.split("!!!!!"):
        sender = part[-6:]
        payload = part[:-6]
        if sender == current_block_sender:
            current_block += payload
        else:
            if current_block:
                format_block(current_block, current_block_sender, out_fp)
            current_block = payload
            current_block_sender = sender

    format_block(current_block, current_block_sender, out_fp)

def format_block(block: str, sender: str, fp) -> None:
    for msg_str in re.split(r"Content-Length: \d+\n\n", block):
        if msg_str:
            format_message(msg_str, sender, fp)

def format_message(msg_str: str, sender: str, fp) -> None:
    print("formatting", repr(msg_str))
    fp.write(f"[[[ FROM {sender} ]]]\n")
    msg = json.loads(msg_str)
    fp.write(json.dumps(msg, indent=4, sort_keys=True))
    fp.write("\n")


format_log("helix-basedpyright.log", "helix-basedpyright-formatted.log")
