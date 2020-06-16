from sys import stdout
from time import sleep
import censys.certificates
from threading import Thread

class CensysIO():
    def __init__(self, args, target, handler):
        self.description  = "Gather subdomains through Censys SSL cert Lookup"
        self.author       = '@m8r0wn'
        self.method       = ['scrape']

        self.handler      = handler
        self.target       = target
        self.timeout      = args.timeout

        self.api          = args.censys_api
        self.secret       = args.censys_secret
        self.thread_count = 0
        self.running      = True


    def execute(self):
        if not self.api or not self.secret:
            return

        try:
            certs = censys.certificates.CensysCertificates(api_id=self.api, api_secret=self.secret)
            resp = certs.search("parsed.names: {}".format(self.target), fields=['parsed.names'])
            for line in resp:
                for sub in line['parsed.names']:
                    if sub.endswith(self.target):
                        self.handler.sub_handler({'Name': sub, 'Source': 'Censys.io'})

        except Exception as e:
            if str(e).startswith('403 (unauthorized):'):
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Authentication Failed: verify API Key/Secret\033[1;m\n")
            elif '400 (max_results)' in str(e):
                pass
            else:
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Error: {}\033[1;m\n".format(str(e)))