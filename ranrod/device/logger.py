#! /usr/bin/env python
#                         _______
#   ____________ _______ _\__   /_________       ___  _____
#  |    _   _   \   _   |   ____\   _    /      |   |/  _  \
#  |    /   /   /   /   |  |     |  /___/   _   |   |   /  /
#  |___/___/   /___/____|________|___   |  |_|  |___|_____/
#          \__/                     |___|
#

__author__    = 'Wijnand Modderman-Lenstra'
__email__     = 'maze@pyth0n.org'
__copyright__ = 'Copyright 2011, maze.io labs'
__license__   = 'MIT'


import datetime


class DeviceLogger(object):
    defaults = {
        'timestamp': 'blaat',
    }

    def __init__(self, device, config={}):
        self.config = self.defaults.copy()
        self.config.update(config)
        self.write('Log starting')

    def close(self):
        self.write('Log closing')

    def write(self, message):
        print '%s %s' % (datetime.datetime.now(), message)
