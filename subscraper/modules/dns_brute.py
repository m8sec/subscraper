import threading
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
        active_th = []
        for s in self.sublist:
            sub = s + '.' + self.target
            th = threading.Thread(target=self.resolver, args=(sub,),)
            th.daemon = True
            active_th.append(th)
            th.start()

            while len(active_th) > 15:
                for th in reversed(active_th):
                    if not th.isAlive():
                        active_th.remove(th)

        while len(active_th) > 0:
            for th in reversed(active_th):
                if not th.isAlive():
                    active_th.remove(th)

    def resolver(self, sub):
        try:
            dns_query = dns_lookup(sub, 'A')
            if dns_query:
                self.handler.sub_handler({'Name': sub, 'Source': 'DNS-Brute', 'DNS': dns_query})
        except:
            pass