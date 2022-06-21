import threading
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'dnsdumpster'
    description = "Use DNS dumpster to enumerate subdomains."
    author = '@m8r0wn'
    groups = ['all', 'scrape']
    args = {}

    def __init__(self, args, target, print_handler):
        threading.Thread.__init__(self)
        self.daemon = True
        self.handler = print_handler
        self.target = target
        self.timeout = args.timeout

    def run(self):
        link = "https://api.hackertarget.com/hostsearch/?q={}".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.count('.') > 1:
                        sub = self.sub_extractor(line)
                        if sub:
                            self.handler.sub_handler({'Name': sub, 'Source': self.name})
        except:
            pass

    def sub_extractor(self, line):
        try:
            return line.split(",")[0]
        except:
            return False