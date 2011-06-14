from distutils.core import setup
from datetime import datetime

today = datetime.now().strftime('%Y%m%d')

setup(
    name         = 'ranrod',
    version      = '0.1-%s' % (today,),
    author       = 'Wijnand Modderman-Lenstra',
    author_email = 'maze@pyth0n.org',
    description  = 'RANROD router config differ and collector',
    long_description = file('README.rst').read(),
    license      = 'MIT',
    keywords     = 'ranrod router network config diff collect',
    scripts      = [
        'bin/ranrod',
    ],
    packages     = [
        'ranrod',
        'ranrod.client',
        'ranrod.client.protocol',
        'ranrod.device',
        'ranrod.util',
    ],
)

