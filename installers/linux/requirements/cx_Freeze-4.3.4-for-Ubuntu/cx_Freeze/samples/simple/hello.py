#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
import sys
from sys import stdout

stdout.write('Hello from cx_Freeze\n')
stdout.write('The current date is %s\n\n' %
             datetime.today().strftime('%B %d, %Y %H:%M:%S'))

stdout.write('Executable: %r\n' % sys.executable)
stdout.write('Prefix: %r\n' % sys.prefix)
stdout.write('File system encoding: %r\n\n' % sys.getfilesystemencoding())

stdout.write('ARGUMENTS:\n')
for a in sys.argv:
    stdout.write('%s\n' % a)
stdout.write('\n')

stdout.write('PATH:\n')
for p in sys.path:
    stdout.write('%s\n' % p)
stdout.write('\n')
