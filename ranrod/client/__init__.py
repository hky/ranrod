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


__all__ = ['get_service', 'try_connect']


import re
from ranrod.client.base import ClientError
from ranrod.client.telnet import Telnet
from ranrod.client.ssh import SSH
from ranrod.device.base import Device


PROTOCOL_RE = re.compile(r'^(?P<proto>tcp|udp)/(?P<name>\w+):?(?P<port>\d*)$')
SERVICE_MAP = dict(
    telnet = Telnet,
    ssh = SSH,
)


def get_service(desc):
    '''
    Get port info from a service description, handles either:
    
        * <proto>/<name>
        * tcp/ssh
        * <proto>/<name>:port
        * tcp/ssh:2200
    '''
    test = PROTOCOL_RE.match(desc)
    if not test:
        raise ValueError('Invalid service description "%s"' % (desc,))
    else:
        info = test.groupdict()
        if not info['name'] in SERVICE_MAP:
            raise ValueError('Unknown service "%s"' % (info['name'],))
        if info['port']:
            port = int(info['port'])
        else:
            port = SERVICE_MAP[info['name']].port

        return SERVICE_MAP[info['name']], port

def try_connect(config, name, repository):
    if type(config.connect) != list:
        config.connect = [config.connect]
    
    for method in config.connect:
        factory, port = get_service(method)
        config.address = (config.hostname, port)
        device = Device(config, name, factory, repository)
        try:
            try:
                device.parse(config.model)
            except ClientError, e:
                print 'Cient error using "%s": %s' % (method, str(e))
            except Exception, e:
                print 'Unhandled error: %s' % (str(e),)
                raise
            else:
                return device
        finally:
            pass # device.close()


if __name__ == '__main__':
    print get_service('tcp/telnet')
    print get_service('tcp/telnet:2300')
    print get_service('tcp/ssh')
    print get_service('tcp/ssh:2200')
