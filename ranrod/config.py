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


class ConfigMap(object):
    '''
    Configuration map, makes a ``dict`` act like an object.
    '''

    def __init__(self, config={}):
        if isinstance(config, ConfigMap):
            self.config = config.config
        else:
            self.config = config

    def __contains__(self, item):
        if hasattr(super(ConfigMap, self), 'config'):
            return item in self.config
        else:
            return False

    def __iter__(self):
        return iter(self.config)

    def __repr__(self):
        return repr(self.config)

    def __getitem__(self, item):
        return self.config.get(item)

    def __setitem__(self, item, value):
        self.config[item] = value

    def __getattr__(self, attr):
        try:
            return self.config[attr]
        except KeyError:
            if hasattr(super(ConfigMap, self), 'config'):
                raise AttributeError('Configuration option "%s" is missing' % \
                    attr)
            else:
                return getattr(super(ConfigMap, self), attr)

    def __setattr__(self, attr, value):
        try:
            self.config[attr] = value
        except AttributeError:
            object.__setattr__(self, attr, value)

    def keys(self):
        return self.config.keys()

    def get(self, item, default=None):
        return self.config.get(item, default)

    def update(self, items):
        self.config.update(items)

    def values(self):
        return self.config.values()


class Config(object):
    '''
    Configuration file parser.
    
    :param filename: path to configuration file
    :param parse: boolean indicating if the file should be parsed immediately
    :param multi: boolean indicating if multi-value items are allowed
    '''
    
    re_regexp = re.compile(r'^/(?P<regexp>.*)/(?P<flags>[igm]*)')

    def __init__(self, filename, parse=True, multi=False):
        self.filename = filename
        self.sections = {}
        self.multi = multi
        if parse:
            self.parse()

    def __dict__(self):
        return self.sections

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
                raise ValueError('Key "%s" in section "%s" already exists.' % \
                    (section, key))

    def add_section(self, section, defaults=None):
        '''
        Add a ``section`` if it does not exist already.
        
        :param section: name of the section
        :param defaults: default value
        '''
        if not section in self.sections:
            self.set_section(section, defaults)

    def get_section(self, section):
        '''
        Get all key-value pairs for a section.
        
        :param section: name of the section
        '''
        return self[section]

    def get_sections(self):
        '''
        Get all section names.
        '''
        return [s for s in self.sections if s != 'global']

    def set_section(self, section, defaults=None):
        '''
        Set a ``section`` to its ``defaults``, defaults to an empty ``dict``
        if the ``defaults`` parameter is omitted.
        
        :param section: name of the section
        :param defaults: default values for the section
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
                        raise ValueError('%s[%d]: duplicate section "%s"' % \
                            (self.filename, lineno, section))
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
                    filename = os.path.join(os.path.dirname(self.filename),
                        line[1:].strip())
                    config = Config(filename)
                    if section == 'global':
                        for s in config.sections:
                            self.add_section(s)
                            self.sections[s].update(config.sections[s])
                    else:
                        self.sections['global'].update(
                            config.sections['global'])
                    continue

                # Inherit
                if line.startswith('@'):
                    inherit = line[1:].strip()
                    if inherit in self.sections:
                        self.sections[section].update(self.sections[inherit])
                    else:
                        error = '%s[%d]: inherited section "%s" not found'
                        raise ValueError(error % \
                            (self.filename, lineno, inherit))
                    continue

                raise ValueError('%s[%d]: syntax error "%s"' % \
                    (self.filename, lineno, line))

    def parse_value(self, value):
        '''
        Parse a single section value.
        
        :param value: string value that need to be parsed
        '''
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
