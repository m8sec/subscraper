import threading
from sys import stdout
from censys.search import CensysCertificates

class SubModule(threading.Thread):
    name = 'censys'
    description = "Gather subdomains through censys.io SSL cert Lookups."
    author = '@m8r0wn'
    groups = ['all', 'scrape']
    args = {
        'APIKEY': {
            'Description': 'Censys.io API Key',
            'Required': True,
            'Value': ''
        },
        'SECRET': {
            'Description': 'Censys.io API Secret',
            'Required': True,
            'Value': ''
        }
    }

    def __init__(self, args, target, print_handler):
        threading.Thread.__init__(self)
        self.daemon  = True
        self.handler = print_handler
        self.target  = target
        self.timeout = args.timeout

    def run(self):
        if not self.args['APIKEY']['Value'] or not self.args['APISECRET']['Value']:
            return False

        try:
            certs = CensysCertificates(api_id=self.api, api_secret=self.secret)
            resp = certs.search("parsed.names: {}".format(self.target), fields=['parsed.names'])
            for line in resp:
                for sub in line['parsed.names']:
                    if sub.endswith(self.target):
                        self.handler.sub_handler({'Name': sub, 'Source': self.name})

        except Exception as e:
            if str(e).startswith('403 (unauthorized):'):
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Authentication Failed: verify API Key/Secret\033[1;m\n")
            elif '400 (max_results)' in str(e):
                pass
            else:
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Error: {}\033[1;m\n".format(str(e)))
