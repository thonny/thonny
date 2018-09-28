import time
from math import *

from mmm import momo

# from math import sqrt
# Algne: 130 sek, 480 mb
# Peale source'i eemaldamist: 11 sek, 434 mb
# Peale optimeerimise ettevalmistust: 12 sek, 497 mb
# Peale esialgset optimeerimist (before olekud jagasid): 5 sek, 214 mb
# Peale pure tippude optimeerimist: 3.2 sek, 114 mb
# Peale export_value optimeerimist: 3.1 sek, 81 mb
# --------------------
# from math import *
# Enne globaalide jagamist 4.9 sek, 245 mb
# Peale globaalide jagamist 4.2 sek, 183 mb
# Peale mooduli lokaalide eemaldamist 3.3 sek, 122 mb
# Peale ValueInfo sissetoomist 3.75 sek, 80 mb
# Peale FrameInfo namedtuple sissetoomist 3.45 sek, 76.5 mb
# Peale TextRange namedtuple sissetoomist 3.3 sek, 74.5 mb
# Peale skipframe'i optimeerimist 3.1 sek, 74.5 mb
# Peale probablypure'i 2 sek, 48 mb
# Peale system_frame'ide meeldejätmist: 2.2 se, 57 mb
True, None
t = time.time()


def arvuta(punktid):
    momo()

    def fafa(n):
        pass

    fafa(0)
    kokku = len(punktid)
    kaugused_ja_vastavad_punktid = {}
    m = 0
    n = 0
    for punkt in punktid:
        for i in range(len(punktid)):
            n += 1
            esim_punkti_nr = str(punktid.index(punkt) + 1)
            teise_punkti_nr = str(i + 1)
            # fafa(n)
            if punktid.index(punkt) == i:
                continue
            firstx = punkt[0]
            firsty = punkt[1]
            secondx = punktid[i][0]
            secondy = punktid[i][1]
            kaugus = sqrt((secondx - firstx) ** 2 + (secondy - firsty) ** 2)
            kaugused_ja_vastavad_punktid[kaugus] = esim_punkti_nr, "ja", teise_punkti_nr
    vähim = min(kaugused_ja_vastavad_punktid)
    vähima_paari_nimi = kaugused_ja_vastavad_punktid[vähim]
    return vähima_paari_nimi


points = [
    [55, 42],
    [538, 68],
    [99, 238],
    [549, 276],
    [44, 381],
    [554, 393],
    [17, 517],
    [481, 553],
    [213, 565],
    [223, 420],
    [251, 211],
    [255, 55],
    [469, 163],
    [456, 174],
]
print(arvuta(points))
print(time.time() - t)
