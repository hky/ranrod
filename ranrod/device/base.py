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
import parser
import re
import traceback
from ranrod.device.constants import *
from ranrod.device.logger import DeviceLogger


class DeviceError(Exception):
    '''
    Error indicating that the device generated an error.
    '''
    pass


class DeviceConfigError(DeviceError):
    pass


class DeviceDumper(object):
    def __init__(self, device, config={}):
        self.device = device
        self.config = config

    def __enter__(self):
        self.device.cmd_log('Device log starting')
        self.log = self.device.repository.open(self.device.name, 'w')
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            self.device.cmd_log('Fatal error: %s %s' % \
                (exc_type.__name__, exc_value))
            for line in traceback.format_list(traceback.extract_tb(tb)):
                self.device.cmd_log(line)
        self.close()

    def close(self):
        self.log.close()
        self.device.repository.add(self.log.name)
        self.device.repository.commit('update')
        self.device.cmd_log('Device log closing')

    def write(self, data):
        self.log.write(data)


def record(device):
    class DeviceRecord(object):
        def __init__(self, log, func, wait=False):
            if isinstance(func, type(lambda: _)):
                log.write(self.filtered(func()))
            else:
                log.write(self.filtered(func))

            # Wait for prompt
            if wait:
                device.prompt()

        @staticmethod
        def filter(pattern, replace=None):
            if not isinstance(pattern, RE_TYPE):
                pattern = re.compile(pattern, re.M)
            device.filters.append((pattern, replace))
        
        @staticmethod
        def ignore(pattern):
            if not isinstance(pattern, RE_TYPE):
                pattern = re.compile(pattern)
            device.ignores.append(pattern)

        def filtered(self, data):
            for pattern in device.ignores:
                data = pattern.sub('', data)
            for pattern, replace in device.filters:
                for match in pattern.finditer(data):
                    for item in match.groups():
                        data = data.replace(item, replace or '*' * 8, 1)
            return data

    return DeviceRecord


def connect(device):
    class DeviceConnect(object):
        def __enter__(self):
            from ranrod.client import telnet
            device.remote = telnet.Telnet(device.config.address)
            device.remote.connect()
            device.cmd_log('Connected to %r' % (device.config.address,))

        def __exit__(self, exc_type, exc_value, tb):
            device.remote.close()

    return DeviceConnect()


class DeviceConfig(object):
    def __init__(self, config, allow_missing=False):
        self.allow_missing = allow_missing
        self.config = dict(config)

    def __contains__(self, item):
        return item in self.config

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        elif self.allow_missing:
            return None
        else:
            raise AttributeError(attr)

    def __getitem__(self, item):
        return self.config[item]


class Device(object):
    def __init__(self, config, name, repository):
        self.config = DeviceConfig(config, True)
        self.name = name
        self.repository = repository

        self.environ = {}
        self.capture = {}
        self.filters = []
        self.ignores = []
        self.expects = {}
        self.prompt = ''
        self.logger = DeviceLogger(self)
        self.record = record(self)
        self.remote = None

    def __str__(self):
        if self.remote:
            return '[%s] %s' % (self.name, self.remote)
        else:
            return '[%s] %s (disconnected)' % (self.name, self.config.hostname,)

    def parse(self, filename):
        '''
        This reads the RANROD device description file and evaluates the
        script within. Some day this should be refactored to an AST-type
        of parser, but for now this give us the flexibility we need.
        '''
        data = []
        # Make sure we have the with-statement available
        data.append('from __future__ import with_statement')
        # Append the file data
        data.append(file(filename).read())
        # Compile!
        code = compile('\n'.join(data), filename, 'exec')
        # Reset environment
        self.reset()
        try:
            eval(code, self.environ, self.capture)
        except Exception, e:
            # TODO: Handle exception in script
            raise

    def reset(self):
        '''
        Resets the environment in which device description files will be
        evaluated.
        '''
        self.environ.update({
            # Variables
            'device':  self,
            'dumper':  DeviceDumper,
            'log':     self.cmd_log,

            # Functions
            'header':  self.cmd_header,
            'capture': self.cmd_capture,
            'command': self.cmd_command,
            'connect': self.cmd_connect,
            'record':  self.cmd_record,
            'filter':  self.cmd_filter,
            'ignore':  self.cmd_ignore,
            'expect':  self.cmd_expect,
            'pattern': self.cmd_pattern,
            'prompt':  self.cmd_prompt,
        })
    
    def cmd_capture(self, pattern, *names):
        '''
        Allows to capture pattern matches to variables available in the 
        script.
        
        TODO: Also exclude builtins etc.
        '''

        reserved = []
        reserved.extend(self.environ.keys())
        reserved.extend(dir(__builtins__))
        
        def capture(line, match):
            info = match.groupdict()
            if not info:
                info = dict(zip(names, match.groups()))
            for item in info:
                if not item in reserved:
                    self.capture[item] = info[item]
            print self.capture
        
        # Register hook
        self.cmd_expect(pattern, capture)

    def cmd_command(self, line):
        '''
        Execute a command and wait for the device to return to the prompt.
        Will return the output of the command, so one can re-use it in a
        recording session::

            >>> record(output, command('uptime'))

        '''
        if self.remote:
            self.sendline(line)
            output = self.remote.wait_for(self.prompt)
            if output.startswith(line):
                # Device did not respect our echo off request
                output = '\n'.join(output.splitlines()[1:-1])

            output = ''.join(['%%\r\n%% command: %s\r\n%%\r\n' % (line, ), output])
            return output
        else:
            raise DeviceError('Remote not connected.')

    def cmd_connect(self, device):
        return connect(device)

    def cmd_expect(self, pattern, func):
        '''
        Adds a string that we can expect. If the provided ``pattern`` is not
        a compiled regular expression we will compile it for the user. If the
        provided ``func`` is a string, we will wrap the string in a function
        that sends the line to the peer.

        It is important to note that the lines fed to the matching loop are
        being stripped, so patterns like ``"\s+$"`` won't work.

        Some examples::

            >>> expect('login:', 'maze')

        Using regular expression objects::

            >>> expect(pattern('^[Ll]ogin:$'), 'maze')

        Using a function:

            >>> def handle_error(line):
            ...     device.close()
            ...
            >>> expect(pattern('error', 'i'), handle_error)

        '''
        if not isinstance(pattern, RE_TYPE):
            pattern = re.compile(pattern)

        if not isinstance(func, FUNC_TYPE):
            data = func

            def send(*args, **kwargs):
                self.sendline(data)

            func = send

        self.expects[pattern] = func

    def cmd_filter(self, pattern, replace=None):
        '''
        Filter out the given ``pattern`` from :py:func:`command` output. If
        ``replace`` is ommitted, the matched groups will be replaced by eight
        asterisks (``********``).

        Only matches in regular expression groups will be replaced, not the
        entire pattern!
        '''
        #lambda *a, **kw: self.record.filter(*a, **kw),
        return self.record.filter(pattern, replace)

    def cmd_ignore(self, pattern, flags='m'):
        '''
        Filter out lines that match the given ``pattern``.
        '''
        return self.record.ignore(self.cmd_pattern(pattern, flags))

    def cmd_header(self, remark, comment='%'):
        return '%s\r\n%s RANROD - Device configuration for %s\r\n%s\r\n' % \
            (comment, comment, remark, comment)

    def cmd_log(self, message):
        self.logger.write(message)

    def cmd_pattern(self, pattern, flags=''):
        '''
        Compile a string into a regular expression::

            >>> pattern(r'm[4a]z[3e]', 'i')

        '''
        if type(pattern) == RE_TYPE:
            return pattern

        re_flags = 0
        for flag in flags:
            re_flags |= getattr(re, flag.upper())
        try:
            return re.compile(pattern, re_flags)
        except TypeError, e:
            raise DeviceConfigError('Invalid pattern "%s": %s' % \
                (pattern, str(e)))

    def cmd_prompt(self, pattern=None):
        '''
        This function has a double purpose:

            * If given no arguments, wait until the device gives a prompt
            * Otherwise, set the prompt that we can expect to the given
              ``pattern``

        While waiting for the prompt, all possible expected strings that
        were previously defined with the ``expect`` command will be
        evaluated.
        '''
        # Set prompt pattern
        if pattern:
            if isinstance(pattern, RE_TYPE):
                self.prompt = pattern
            else:
                self.prompt = re.compile(pattern)

        # Wait for prompt
        else:
            if self.remote:
                self.remote.wait_for(self.prompt, callbacks=self.expects)
            else:
                raise DeviceError('Remote not connected.')

    def cmd_record(self, *args, **kwargs):
        return self.record(*args, **kwargs)

    def sendline(self, data, timeout=None):
        self.remote.sendline(data, timeout)
