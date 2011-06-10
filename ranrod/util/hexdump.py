#! /usr/bin/env python
#
#                         _______
#   ____________ _______ _\__   /_________       ___  _____
#  |    _   _   \   _   |   ____\   _    /      |   |/  _  \
#  |    /   /   /   /   |  |     |  /___/   _   |   |   /  /
#  |___/___/   /___/____|________|___   |  |_|  |___|_____/
#          \__/                     |___|
#
#
# (c) 2011 Wijnand 'maze' Modderman-Lenstra - https://maze.io/
#

__author__    = 'Wijnand Modderman-Lenstra <maze@pyth0n.org>'
__copyright__ = '(C) 2011 Wijnand Modderman-Lenstra'
__license__   = 'MIT'
__url__       = 'https://maze.io/'

import sys

class HexDump(object):
    def __init__(self, pad=1, step=16, buffer=sys.stdout):
        self.pad = pad
        self.step = step
        # Make sure we have even steps
        if self.step % 2 != 0:
            self.step += 1
        self.buffer = buffer

    def dump(self, data, encoding='utf8', offset=0):
        '''
        Dump the contents of a byte array, such as a string or an unicode
        object.
        '''
        if type(data) == unicode:
            data = bytearray(data, encoding)
        else:
            data = bytearray(data)
        for y in xrange(0, len(data), self.step):
            part = data[y:y+self.step]
            print '0x%04x ' % (y * self.step + offset,),
            hexc = []
            for x in xrange(0, len(part), 2):
                if len(part[x:x+2]) == 1:
                    hexc.append('%02x  ' % (part[x],))
                else:
                    hexc.append('%02x%02x' % tuple(part[x:x+2]))

            char = [(c >= 0x20 and c < 0x7f) and chr(c) or '.' for c in part]
            pads = ' ' * self.pad
            print pads.join(hexc).ljust((self.step / 2) * (4 + self.pad)), ''.join(char)

    def dump_stream(self, stream, encoding='utf8'):
        '''
        Consume a stream dumping its contents.
        '''
        size = 0
        while True:
            data = stream.read(self.step)
            if len(data) == 0:
                break
            else:
                self.dump(data, encoding=encoding, offset=size)
                size += len(data)