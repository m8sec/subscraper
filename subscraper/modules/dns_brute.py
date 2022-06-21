import threading
from subscraper.support import dns_lookup

class SubModule(threading.Thread):
    name = 'dnsbrute'
    description = "DNS bruteforce."
    author = '@m8r0wn'
    groups = ['all', 'brute']
    args = {}

    def __init__(self, args, target, print_handler):
        threading.Thread.__init__(self)
        self.daemon = True
        self.handler = print_handler
        self.target = target
        self.timeout = args.timeout
        self.wordlist = args.wordlist

    def run(self):
        active_th = []
        for s in self.wordlist:
            th = threading.Thread(target=self.resolver, args=('{}.{}'.format(s, self.target),))
            th.daemon = True
            active_th.append(th)
            th.start()

            while len(active_th) > 15:
                for th in reversed(active_th):
                    if not th.is_alive():
                        active_th.remove(th)

        while len(active_th) > 0:
            for th in reversed(active_th):
                if not th.is_alive():
                    active_th.remove(th)

    def resolver(self, sub):
        try:
            dns_query = dns_lookup(sub, 'A')
            if dns_query:
                self.handler.sub_handler({'Name': sub, 'Source': self.name, 'DNS': dns_query})
        except:
            pass