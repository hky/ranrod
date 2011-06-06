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
    defaults = dict(
        prompt_user     = re.compile(r'>\s*'),
        prompt_admin    = re.compile(r'#\s*'),
        prompt_password = re.compile(r'password\s*:', re.I),
    )

    def __init__(self, device, address, username, password, prompt_user, prompt_admin, **extra):
        self.device = device
        self.address = address
        self.username = username
        self.password = password
        self.prompt_user = prompt_user
        self.prompt_admin = prompt_admin
        self.extra = extra.copy()

    @property
    def is_admin(self):
        return False

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

    def wait_for(self, timeout=5.0, *tests):
        assert tests
        output = ''
        while True:
            chunk = self.remote.recv(1024)
            print 'chunk =', repr(chunk)
            output += chunk
            for test in tests:
                filtered = test(output)
                if filtered is not None:
                    output = filtered
                    return output

    def wait_for_prompt(self, timeout=5.0):
        def prompt(output):
            if self.prompt_user.search(output) or \
                self.prompt_admin.search(output):
                return output

        return self.wait_for(timeout, prompt)

    def command(self, command, timeout=5.0, echo=False, prompt=False):
        self.remote.send('%s\r\n' % (command.strip(),))
        s = int(not echo)
        e = int(not prompt) * -1
        return '\r\n'.join(self.wait_for_prompt(timeout=timeout).strip().splitlines()[s:e])

    def enable(self, timeout=5.0):
        enable = self.extra['commands'].get('generic', 'enable')
        self.remote.send('%s\r\n' % (enable,))

        prompt_password = self.extra.get('prompt_password', self.defaults['prompt_password'])

        def response(output):
            output = output.replace(self.extra['password_admin'], '********')
            last = output.strip().splitlines()[-1]

            # Respond to password prompt
            if prompt_password.search(last):
                self.remote.send('%s\r\n' % (self.extra['password_admin'],))
                return None

            # If we're back at the user/admin prompt we are done
            if self.prompt_user.search(last) or \
                self.prompt_admin.search(last):
                return output

        return self.wait_for(timeout, response)
        

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

    @property
    def is_admin(self):
        test = self.command('', prompt=True)
        print test
        return self.prompt_admin.search(test)


# Export classes to Login class
Login.klass['telnet'] = Telnet
Login.klass['ssh']    = SSH
