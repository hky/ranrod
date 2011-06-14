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
import sys


# Named levels
LEVELS = dict(
    debug    = 0,
    info     = 1,
    notice   = 1,
    warn     = 2,
    warning  = 2,
    critical = 3,
    severe   = 3,
)


def Logger(*args, **kwargs):
    class LoggerBase(object):
        defaults = {
            'level':  LEVELS['info'],
            'output': '-',
        }
        instance = None

        def __init__(self, config={}):
            self.config = self.defaults.copy()
            self.config.update(config)

            if type(self.config['level']) != int:
                self.config['level'] = LEVELS[self.config['level']]

            if self.config['output'] == '-':
                self.output = sys.stdout
            else:
                self.output = open(self.config['output'], 'a')

            self('Log starting', level='info')

        def __call__(self, message, level='info'):
            return self.write(message, level)

        def close(self):
            self('Log closing', level='info')

        def write(self, message, level='info'):
            if type(level) != int:
                level = LEVELS.get(level, self.config['level'])
            
            if level >= self.config['level']:
                self.output.write('%s %s\n' % (datetime.datetime.now(), message))

    if not LoggerBase.instance:
        LoggerBase.instance = LoggerBase(*args, **kwargs)

    return LoggerBase.instance
        