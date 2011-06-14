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


from ranrod.client.constants import CR, LF
from ranrod.client.error import *
from ranrod.config import ConfigMap


class Client(object):
    '''
    Client base class, used to dirive other client implementations from.
    '''

    name = 'unknown'
    port = 0
    defaults = {
        'timeout':  30.0,
        'newlines': [CR + LF, LF + CR, LF],
    }

    def __init__(self, address, config={}):
        self.address = address
        self.config = ConfigMap(self.defaults.copy())
        self.config.update(config)

    def __str__(self):
        if self.address[1] == self.port:
            return '%s://%s' % (self.name, self.address[0])
        else:
            return '%s://%s:%d' % (self.name, self.address[0],
                self.address[1])

    def connect(self):
        '''
        To be implemented in the sub class.
        '''
        raise NotImplementedError

    def close(self):
        '''
        To be implemented in the sub class.
        '''
        self.remote.close()

    def nextline(self):
        '''
        Check if we have a new line in the buffer, we do this by checking
        all possible line endings.
        '''
        for feed in self.config['newlines']:
            newline = self.buffer.index(feed) + len(feed)
            output = self.buffer[:newline]
            self.buffer = self.buffer[newline:]
        return output

    def nextpart(self):
        '''
        Check if we still have (some) buffer remaining, if so, return that.
        '''
        if self.buffer:
            chunk = self.buffer
            self.buffer = ''
            return chunk
        else:
            raise ValueError('Empty buffer')

    def process(self, chunk):
        '''
        Process (partial) chunk of data (for in the readloop).
        '''
        return chunk

        def readloop(self, callback, timeout=None):
            timeout = timeout or self.config['timeout']
            print 'timeout =', timeout
            chunk = ''

            try:
                return callback()
            except ValueError:
                pass

            # Read socket until there is no data available
            while True:
                r, w, e = select.select([self.remote], [], [], timeout)
                if r:
                    chunk = self.read(timeout=timeout)
                    if chunk:
                        self.buffer += self.process(chunk)
                        try:
                            return callback()
                        except ValueError:
                            pass
                    else:
                        # Socket was readable, but it returned no data so peer
                        # must have gone away
                        raise ClientError('Connection closed by peer')
                else:
                    raise ClientTimeout('Read timeout')

    def readline(self, timeout=None):
        return self.readloop(self.nextline, timeout)

    def readpart(self, timeout=None):
        return self.readloop(self.nextpart, timeout)

    def readsome(self, timeout=None):
        try:
            return self.nextline()
        except ValueError:
            pass
        try:
            return self.nextpart()
        except ValueError:
            pass
        return self.readpart(timeout)

    def wait_for(self, pattern, timeout=None, callbacks={}):
        '''
        This loop will block until ``pattern`` is matched in the data received
        by the client. Furthermore, you can provide a dictionary with regular
        experession objects as keys, and a callback as value that will be
        called if matched on the current line being processed.
        '''
        seen = []
        while True:
            part = self.readsome(timeout=timeout)
            seen.append(part)

            # Now investigate the bits read line-for-line
            for line in part.splitlines():
                # Cleanup
                line = line.strip()
                if not line:
                    continue

                # Return if the expected pattern matches
                if pattern.search(line):
                    return ''.join(seen)

                # Iterate over possible callbacks
                for cpattern, callback in callbacks.iteritems():
                    match = cpattern.search(line)
                    if match:
                        callback(line, match)
