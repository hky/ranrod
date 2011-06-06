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
        print remote.command('uname -a', echo=True)
        print remote.command('uptime', echo=True)
        if not remote.is_admin:
            remote.enable()
        print remote.command('id', echo=True)
        print remote.command('sysctl -a 2>/dev/null | grep "^kernel\\."', echo=True)
        remote.logout()
        break
