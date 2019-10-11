import sys
from subscraper.helpers import dns_lookup

class DNSBrute():
    def __init__(self, args, target, handler):
        self.description = "DNS Brute Forcer"
        self.author      = '@m8r0wn'
        self.method      = ['brute']

        self.handler    = handler
        self.target     = target
        self.sublist    = args.sublist

    def execute(self):
        for s in self.sublist:
            try:
                sub = s + '.' + self.target
                dns_query = dns_lookup(sub, 'A')
                if dns_query:
                    self.handler.sub_handler({'Name': sub, 'Source': 'DNS-Brute', 'DNS': dns_query})
            except Exception as e:
                sys.stdout.write("\033[1;30m{:<13}\t{:<25}\033[1;m\n".format('[Error-03]', str(e)))