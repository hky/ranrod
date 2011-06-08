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


class RepositoryError(Exception):
    pass


class Repository(object):
    def __init__(self, path, **extra):
        self.path = os.path.abspath(path)
        if type(self.path) is unicode:
            self.path = self.path.encode('utf-8')
        self.extra = extra

        if not self.check():
            self.init()
    
    def open(self, name, mode='r'):
        path = os.path.abspath(os.path.join(self.path, name))
        base = os.path.dirname(path)
        if not path.startswith(self.path):
            raise RepositoryError('Path outside repository')
        if not os.path.isdir(base):
            os.makedirs(base)
        return open(path, mode)

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
        print 'execute', repr(command), isinstance(command[0], basestring)
        if len(command) == 1 and isinstance(command[0], basestring):
            if type(command[0]) == unicode:
                command = shlex.split(str(command[0]))
            else:
                command = shlex.split(command[0])

        print command, shlex.split(command[0])
        pipe = subprocess.Popen(command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        data = pipe.communicate()
        if pipe.returncode > 0:
            raise RepositoryError(data[1])
        else:
            return data[0]
    
    def add(self, filename):
        command = self.extra.get('add') % {
            'root': self.path, 
            'path': filename,
        }
        print self.execute(command)
    
    def commit(self, message, user='ranrod', path=''):
        command = self.extra.get('commit') % {
            'root': self.path,
            'message': message,
            'user': user,
            'path': path,
        }
        print self.execute(command)

    def init(self):
        print 'Initializing repository in', self.path
        command = self.extra.get('create') % {
            'path': self.path,
        }
        print 'Executing:', repr(command)
        print self.execute(command)
