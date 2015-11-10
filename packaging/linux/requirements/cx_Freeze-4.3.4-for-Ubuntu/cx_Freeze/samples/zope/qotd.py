#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple Quote of the Day server
"""

from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor


class QOTD(Protocol):
    def connectionMade(self):
        self.transport.write('An apple a day keeps the doctor away\r\n')
        self.transport.loseConnection()

# Next lines are magic:
factory = Factory()
factory.protocol = QOTD

# 8007 is the port you want to run under. Choose something >1024
reactor.listenTCP(8007, factory)
reactor.run()
