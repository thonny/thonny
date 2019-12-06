import os.path
from PIL import Image, ImageFilter, ImageEnhance

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
        trans = Image.new('RGBA', im.size, (255, 0, 0, 0))
        im = im.convert('RGBA')
        im = Image.alpha_composite(trans, im, 0.5)
        #enhancer = ImageEnhance.Color(im)
        #im = enhancer.enhance(0.2)
        #im.putalpha(128)
        #im = im.filter(ImageFilter.GaussianBlur(radius=1))
        #im = im.convert("LA")
        im.save("_disabled_" + name)
        

