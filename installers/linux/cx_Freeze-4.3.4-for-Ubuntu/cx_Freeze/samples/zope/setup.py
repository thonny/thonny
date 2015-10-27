# -*- coding: utf-8 -*-

# A simple setup script to create an executable using Zope which demonstrates
# the use of namespace packages.
#
# qotd.py is a very simple type of Zope application
#
# Run the build process by running the command 'python setup.py build'
#
# If everything works well you should find a subdirectory in the build
# subdirectory that contains the files needed to run the application

import sys
from cx_Freeze import setup, Executable

options = {
    'build_exe': {
        'namespace_packages': ['zope']
    }
}

executables = [
    Executable('qotd.py')
]

setup(name='QOTD sample',
      version='1.0',
      description='QOTD sample for demonstrating use of namespace packages',
      options=options,
      executables=executables
      )
