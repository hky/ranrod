import re
import select
import socket
try:
    import paramiko
except ImportError:
    import warnings
    warnings.warn('SSH support is not available, paramiko module is missing')
    paramiko = None


class Login(object):
    re_method = re.compile(r'(?P<protocol>udp|tcp)/(?P<name>\w+):?(?P<port>\d*)')
    ports = dict(
        ftp     = 21,
        ssh     = 22,
        telnet  = 23,
    )
    klass = dict()

    def __init__(self, device, address, username, password, prompt_user, prompt_admin, **extra):
        self.device = device
        self.address = address
        self.username = username
        self.password = password
        self.prompt_user = prompt_user
        self.prompt_admin = prompt_admin
        self.extra = extra.copy()

    @staticmethod
    def attempt(config, method):
        test = Login.re_method.search(method)
        if test:
            info = test.groupdict()
            port = int(info.get('port', Login.ports[info['name']]))
            config['address'] = (config['hostname'], port)
            remote = Login.klass.get(info['name'])(**config)
            remote.connect()
            return remote
        else:
            raise ValueError('Unknown method "%s".' % (method,))

    def connect(self):
        pass

    def login(self):
        self.wait_for_prompt()

    def logout(self):
        self.remote.close()

    def wait_for(self, test, timeout=5.0):
        buffer = ''
        while True:
            chunk = self.remote.recv(1024)
            buffer += chunk
            if test(buffer):
                return buffer

    def wait_for_prompt(self, timeout=5.0):
        test = lambda buffer: self.prompt_user.search(buffer) or self.prompt_admin.search(buffer)
        return self.wait_for(test, timeout)

    def command(self, command):
        self.remote.send('%s\n' % (command.strip(),))
        return '\r\n'.join(self.wait_for_prompt().splitlines()[1:-1])

class Telnet(Login):
    def connect(self):
        family, socktype, proto, canonname, sockaddr = \
            socket.getaddrinfo(self.address[0], self.address[1],
                socket.AF_INET, socket.SOCK_STREAM)[0]
        self.remote = socket.socket(family, socktype, proto)
        if 'bind' in self.extra:
            self.remote.bind(self.extra['bind'])
        self.remote.connect()


class SSH(Login):
    def connect(self):
        ssh_keyfile = self.extra.get('ssh_keyfile', None)
        self.transport = paramiko.SSHClient()
        # Automatically add host key
        self.transport.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.transport.connect(self.address[0], self.address[1],
            username = self.username,
            password = self.password,
            key_filename = ssh_keyfile and [ssh_keyfile] or [],
        )
        self.remote = self.transport.invoke_shell()
        self.remote.write = lambda self, data: self.send(data)

# Export classes to Login class
Login.klass['telnet'] = Telnet
Login.klass['ssh']    = SSH
