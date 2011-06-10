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


class Status(object):
    def __init__(self, repository):
        self.repository = repository
        self.status     = []
    
    def log(self, *args):
        self.status.append(args)
    
    def device_up(self, device):
        '''
        Mark a device as up in the status log.
        '''
        self.log(device.name, device.hostname, 'up')
        
    def device_down(self, device, reason=''):
        '''
        Mark a device as down in the status log, optionally pass a ``reason``.
        '''
        if reason:
            reason = reason.splitlines()[0]
        self.log(device.name, device.hostname, 'down', reason)

    def save(self):
        '''
        Save devices to the status log and commit the file.
        '''
        self.status.sort()
        log = self.repository.open('status', 'w')
        log.write('\t'.join(['name', 'hostname', 'status', 'reason']))
        log.write('\n')
        for line in self.status:
            log.write('\t'.join(line))
            log.write('\n')
        log.close()
        self.repository.file_add(log.name, message='status update')
        self.repository.file_commit(log.name)
