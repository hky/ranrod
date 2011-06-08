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


class ClientError(Exception):
    '''
    Error indicating that an error on the network has occurred.
    '''
    pass


class ClientTimeout(ClientError):
    '''
    Error indicating that a timeout on the network has occurred.
    '''
    pass


class Client(object):
    defaults = {
        'timeout':  30.0,
        'newlines': [CR + LF, LF + CR, LF],
    }

    def __init__(self, address, config={}):
        self.address = address
        self.config = self.defaults.copy()
        self.config.update(config)

    def connect(self):
        '''
        To be implemented in the sub class.
        '''
        raise NotImplementedError

    def close(self):
        '''
        To be implemented in the sub class.
        '''
        raise NotImplementedError

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
