# -*- coding: utf-8 -*-

import sys

sys.stdout.write('importing pkg1.pkg2\n')

from . import sub3
from .. import sub4
