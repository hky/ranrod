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


import io
import select
import socket
from ranrod.client.base import Client
from ranrod.client.base import ClientError, ClientTimeout
from ranrod.client.constants import *
from ranrod.util.hexdump import HexDump


class Telnet(Client):
    '''
    Telnet client implementing (partially):

        * RFC854, Telnet protocol specification
        * RFC855, Telnet option specification
        * RFC857, Telnet echo option
        * RFC858, Telnet supress-go-ahead option
        * RFC1079, Telnet terminal speed option
        * RFC1091, Telnet terminal-type option

    '''

    name = 'telnet'
    port = 23
    defaults = {
        # Tell the server not to echo our input
        'echo':     False,
        'timeout':  30,
        # Possible newline combinations
        'newlines': [CR + LF, LF + CR, LF],
    }

    def __init__(self, address, config={}):
        super(Telnet, self).__init__(address, config)

        # Receive buffer
        self.buffer = ''

        # IAC sequences
        self.IAC = False
        self.IACByte = None

    def connect(self):
        print 'Connecting to', self.address
        self.remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote.connect(self.address)
        self.send(IAC, DONT, ECHO)
        self.send(IAC, WILL, ECHO)

    def echo(self, enabled):
        if enabled:
            self.send(IAC, DO, ECHO)
        else:
            self.send(IAC, DONT, ECHO)

    def send(self, *args, **kwargs):
        data = ''.join(args)
        timeout = kwargs.get('timeout', self.config['timeout'])
        #print '>>>'; self.debug(data)
        oldtimeout = self.remote.gettimeout()
        self.remote.settimeout(timeout)
        try:
            return self.remote.send(data)
        finally:
            self.remote.settimeout(oldtimeout)

    def sendline(self, line, timeout=None):
        self.send(line, CR, LF, timeout=timeout)

    def read(self, size=1024, timeout=None):
        oldtimeout = self.remote.gettimeout()
        self.remote.settimeout(timeout or self.config['timeout'])
        try:
            data = self.remote.recv(size)
        finally:
            self.remote.settimeout(oldtimeout)
        #print '<<<'; self.debug(data)
        return data

    def readloop(self, callback, timeout=None):
        timeout = timeout or self.config['timeout']
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

    def process(self, data):
        '''
        Process a chunk of data. Here we will perform a byte-by-byte
        investigation of what crosses the wire, the telnet protocol can
        send all sorts of control-sequences anywhere in the session.

        All non-sequence items are stored in the internal buffer.
        '''
        chunk = io.BytesIO()
        for char in data:
            # If we are working on an IAC sequence
            if self.IAC:
                # and are working on a request state
                if self.IACByte:
                    # Check if the next byte is a sub-request
                    if self.IACByte == SB:
                        if char == SE:
                            self.handle_IAC_SB(chunk.getvalue())
                            chunk = io.BytesIO()
                            self.IAC = False
                            self.IACByte = None
                        else:
                            chunk.write(char)

                    # Otherwise, this is part of a W/W/D/D sequence
                    else:
                        try:
                            getattr(self, 'handle_IAC_%s' % \
                                (NAME[self.IACByte]),)(char)
                        except KeyError:
                            pass
                        self.IAC = False
                        self.IACByte = None
                else:
                    # Got IAC, read next byte in W/W/D/D sequence
                    self.IACByte = char

            elif char == IAC:
                self.IAC = True
            else:
                chunk.write(char)

        return chunk.getvalue()

    def handle_IAC_SB(self, chunk):
        '''
        Handle subnegotiation.
        '''
        #print 'IAC SB:'
        #self.debug(chunk)
        if chunk == TERM_TYPE + ECHO + IAC:
            # TODO: make configurable
            self.send(IAC, SB, TERM_TYPE, IS, "VT100", IAC, SE)
        elif chunk == TERM_SPEED + ECHO + IAC:
            # TODO: make configurable
            self.send(IAC, SB, TERM_SPEED, IS, "9600,9600", IAC, SE)

    def handle_IAC_DO(self, feature):
        if feature in [TERM_TYPE, TERM_SPEED]:
            self.send(IAC, WILL, feature)
        else:
            self.send(IAC, WONT, feature)

    def handle_IAC_DONT(self, feature):
        pass # What ever

    def handle_IAC_WILL(self, feature):
        # Tell the server not to echo if echoing is enabled
        if feature == ECHO and not self.config['echo']:
            self.send(IAC, DONT, ECHO)
            self.send(IAC, WONT, ECHO)

    def handle_IAC_WONT(self, feature):
        # Tell the server to echo if echoing is disnabled
        if feature == ECHO and self.config['echo']:
            self.send(IAC, DO, ECHO)
            self.send(IAC, WILL, ECHO)

    def debug(self, data):
        HexDump(step=32).dump(data)


if __name__ == '__main__':
    import sys
    address = (sys.argv[1], int(sys.argv[2]))
    telnet = Telnet(address)
    telnet.connect()
    telnet.sendline('')
    while True:
        print repr(telnet.readsome(timeout=5))
