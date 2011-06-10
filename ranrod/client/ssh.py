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
import paramiko
import socket
from ranrod.client.base import Client
from ranrod.client.base import ClientError, ClientTimeout, ClientConnectionError
from ranrod.client.constants import *
from ranrod.util.hexdump import HexDump


class SSH(Client):
    '''
    SSH client.
    '''

    name = 'ssh'
    port = 22
    defaults = {
        # Tell the server not to echo our input
        'timeout':  30,
        # Possible newline combinations
        'newlines': [CR + LF, LF + CR, LF],
    }

    def __init__(self, address, config={}):
        super(SSH, self).__init__(address, config)

        # Receive buffer
        self.buffer = ''

    def connect(self):
        self.transport = paramiko.SSHClient()
        # Automatically accept fresh host keys
        self.transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # RANROD supports SSH key authentication
        ssh_keyfile = self.config.get('ssh_keyfile', None)
        # Establish connection
        try:
            self.transport.connect(self.address[0], self.address[1],
                username = self.config.username,
                password = self.config.password,
                key_filename = ssh_keyfile and [ssh_keyfile] or None,
                timeout = self.config.timeout,
            )
            # Request a shell SSH channel
            self.remote = self.transport.invoke_shell()
        except socket.error, e:
            raise ClientConnectionError(e)
        
    def close(self):
        self.remote.close()
        self.transport.close()

    def send(self, *args, **kwargs):
        data = ''.join(args)
        timeout = kwargs.get('timeout', self.config['timeout'])
        print '>>>'
        self.debug(data)
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
        print '<<<'
        self.debug(data)
        return data

    def debug(self, data):
        HexDump(step=32).dump(data)


if __name__ == '__main__':
    import sys
    address = (sys.argv[1], int(sys.argv[2]))
    client = SSH(address)
    client.connect()
    client.sendline('')
    while True:
        print repr(client.readsome(timeout=5))
