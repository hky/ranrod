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


import os
import shlex
import subprocess


class Repository(object):
    def __init__(self, path, **extra):
        self.path = os.path.abspath(path)
        if type(self.path) is unicode:
            self.path = self.path.encode('utf-8')
        self.extra = extra

        if not self.check():
            self.init()

    def check(self):
        '''
        Check if the repository ``check``-file/directory exists.
        '''
        path = os.path.join(self.path, self.extra.get('check'))
        return os.path.exists(path)

    def execute(self, *command):
        '''
        Execute a shell command.
        '''
        if len(command) == 1 and isinstance(command[0], basestring):
            if type(command[0]) is unicode:
                command = shlex.split(command[0].encode('utf-8'))
            else:
                command = shlex.split(command[0])

        print command
        pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return pipe.communicate()[0]

    def init(self):
        print 'Initializing repository in', self.path
        command = self.extra.get('create') % {'path': self.path}
        print 'Executing:', repr(command)
        print self.execute(command)

