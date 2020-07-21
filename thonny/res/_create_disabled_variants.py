import os.path

from PIL import Image

d = os.path.dirname(__file__)

"""
for name in os.listdir(d):
    full_path = os.path.join(d, name)
    if full_path.endswith(".gif") and os.path.isfile(full_path.replace(".gif", ".png")):
        os.remove(full_path)
"""

os.chdir(d)
for name in os.listdir(d):
    if (name.endswith(".gif") or name.endswith(".png")) and "_disabled_" not in name:
        im = Image.open(name)
        trans_brightness = 160
        trans = Image.new(
            "RGBA", im.size, (trans_brightness, trans_brightness, trans_brightness, 0)
        )
        im = im.convert("RGBA")
        im = Image.blend(trans, im, 0.4)
        im.save("_disabled_" + name)
