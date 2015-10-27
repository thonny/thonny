#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Implements a simple service using cx_Freeze.

See below for more information on what methods must be implemented and how they
are called.
"""

import threading

class Handler(object):

    # no parameters are permitted; all configuration should be placed in the
    # configuration file and handled in the Initialize() method
    def __init__(self):
        self.stopEvent = threading.Event()
        self.stopRequestedEvent = threading.Event()

    # called when the service is starting
    def Initialize(self, configFileName):
        pass

    # called when the service is starting immediately after Initialize()
    # use this to perform the work of the service; don't forget to set or check
    # for the stop event or the service GUI will not respond to requests to
    # stop the service
    def Run(self):
        self.stopRequestedEvent.wait()
        self.stopEvent.set()

    # called when the service is being stopped by the service manager GUI
    def Stop(self):
        self.stopRequestedEvent.set()
        self.stopEvent.wait()

