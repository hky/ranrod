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
import re

class Config(object):
    re_regexp = re.compile(r'^/(?P<regexp>.*)/(?P<flags>[igm]*)')

    def __init__(self, filename, parse=True, multi=False):
        self.filename = filename
        self.sections = {}
        self.multi = multi
        if parse:
            self.parse()

    def __getitem__(self, item):
        return self.sections[item]

    @property
    def is_multi(self):
        '''
        Property that indicates if multiple values are allowed or not, this can
        be set from the global configuration directive ``config_multi``.
        '''
        return self.multi or self.get('global', 'config_multi', False)

    def get(self, section, key, default=None):
        '''
        Get the ``value`` for a ``key`` in the specified ``section``.

        Optionally you may pass a ``default`` value if the given ``key`` does
        not exist in the section.
        '''
        if not section in self.sections:
            raise ValueError('Section "%s" does not exist.' % (section,))
        else:
            if default is None:
                return self.sections[section].get(key)
            else:
                return self.sections[section].get(key, default)

    def set(self, section, key, value):
        '''
        Set the ``value`` for a ``key`` in the specified ``section``.
        '''
        if not section in self.sections:
            raise ValueError('Section "%s" does not exist.' % (section,))
        else:
            exists = self.sections[section].get(key, None)
            if exists is None:
                self.sections[section][key] = value
            elif self.is_multi:
                if type(exists) == list:
                    self.sections[section][key].append(value)
                else:
                    self.sections[section][key] = [exists, value]
            else:
                raise ValueError('Key "%s" in section "%s" already exists.' % (section, key))
        
    def add_section(self, section, defaults=None):
        '''
        Add a ``section`` if it does not exist already.
        '''
        if not section in self.sections:
            self.set_section(section, defaults)

    def set_section(self, section, defaults=None):
        '''
        Set a ``section`` to its ``defaults``, defaults to an empty ``dict``
        if the ``defaults`` parameter is omitted.
        '''
        if defaults is None:
            self.sections[section] = {}
        else:
            self.sections[section] = defaults

    def parse(self):
        '''
        Parse the configuration file.
        '''
        self.set_section('global', {})
        with open(self.filename) as config:

            lineno = 0
            section = 'global'
            self.set_section(section)

            for line in config.xreadlines():
                lineno += 1
                line = line.strip()
                if not line:
                    continue

                # Comment
                if line[0] in ';#':
                    continue

                # Section
                if line[0] == '[' and line[-1] == ']':
                    section = line[1:-1]
                    if section in self.sections:
                         raise ValueError('%s[%d]: section "%s" already exists' % (self.filename,
                            lineno, section))
                    else:
                        self.add_section(section)
                    continue

                # Key-value pair
                if '=' in line:
                    key, value = map(lambda s: s.strip(), line.split('=', 1))
                    self.set(section, key, self.parse_value(value))
                    continue

                # Include
                if line.startswith('<'):
                    filename = os.path.join(os.path.dirname(self.filename), line[1:].strip())
                    config = Config(filename)
                    if section == 'global':
                        for s in config.sections:
                            self.add_section(s)
                            self.sections[s].update(config.sections[s])
                    else:
                        self.sections['global'].update(config.sections['global'])
                    continue

                # Inherit
                if line.startswith('@'):
                    inherit = line[1:].strip()
                    if inherit in self.sections:
                        self.sections[section].update(self.sections[inherit])
                    else:
                        raise ValueError('%s[%d]: inherited section "%s" not found' % \
                            (self.filename, lineno, inherit))
                    continue

                raise ValueError('%s[%d]: syntax error "%s"' % \
                    (self.filename, lineno, line))

    def parse_value(self, value):
        value = value.strip()

        # Booleans
        if value.lower() in ['yes', 'true', 'enabled']:
            return True
        if value.lower() in ['no', 'false', 'disabled']:
            return False
        if value.lower() in ['none', 'null']:
            return None

        # Numbers (always long, because we can)
        try:
            return long(value)
        except ValueError:
            pass

        # Float
        try:
            return float(value)
        except ValueError:
            pass

        # Regular expressions
        if value.startswith('/'):
            test = self.re_regexp.match(value)
            if test:
                regexp = test.groupdict()['regexp']
                flags = 0
                for flag in test.groupdict()['flags']:
                    flags = flags | getattr(re, flag.upper())
                return re.compile(regexp, flags)
            else:
                ValueError('Invalid regular expression: "%s"' % (value,))

        # Configuration includes
        if value.startswith('<'):
            filename = os.path.join(os.path.dirname(self.filename), value[1:])
            config = Config(filename)
            return config

        # Lists
        if ',' in value:
            return list(map(self.parse_value, value.split(',')))

        # Default, return string value
        return value.decode('utf-8')


if __name__ == '__main__':
    import sys
    import pprint
    c = Config(sys.argv[1])
    p = pprint.PrettyPrinter()
    p.pprint(c.sections)

