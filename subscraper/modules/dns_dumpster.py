from subscraper.helpers import get_request

class DNSDumpster():
    def __init__(self, args, target, handler):
        self.description = "DNS Dumpster lookup"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target
        self.sublist = args.sublist

    def execute(self):
        link = "https://api.hackertarget.com/hostsearch/?q={}"
        try:
            resp = get_request(link.format(self.target), self.timeout)
            if resp.text:
                for line in resp.text.splitlines():
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