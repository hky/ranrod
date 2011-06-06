from ranrod.config import Config
from ranrod.login import Login, Telnet, SSH

config = Config('etc/devices.cfg')
host = config['localhost']
host['device']  = None
for method in host['connect']:
    try:
        print 'Trying to connect using', method
        remote = Login.attempt(host, method)
    except Exception, e:
        print 'login failed', str(e)
    else:
        remote.login()
        print remote.command('uname -a')
        print remote.command('uptime')
        remote.logout()
        break
