# -*- coding: utf-8 -*-

import sys

sys.stdout.write('importing pkg1.pkg2.sub3\n')

from . import sub5
from .. import sub6
