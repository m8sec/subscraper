from subscraper.helpers import get_request

class DNSDumpster():
    def __init__(self, args, target, handler):
        self.description = "DNS Dumpster lookup"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target

    def execute(self):
        link = "https://api.hackertarget.com/hostsearch/?q={}".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                for line in resp.text.splitlines():
                    if line.count('.') > 1:
                        sub = self.sub_extractor(line)
                        if sub:
                            self.handler.sub_handler({'Name': sub, 'Source': 'DNS-Dumpster'})
        except:
            pass

    def sub_extractor(self, line):
        try:
            return line.split(",")[0]
        except:
            return False