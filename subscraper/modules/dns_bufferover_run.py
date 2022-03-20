from subscraper.helpers import get_request

class DNSBufferOverRun():
    def __init__(self, args, target, handler):
        self.description = "Use dns.bufferover.run to find subdomains"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target

    def execute(self):
        link = "https://dns.bufferover.run/dns?q=.{}".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                data = resp.json()
                for line in data['FDNS_A']:
                    try:
                        sub = line.split(",")[1]
                        self.handler.sub_handler({'Name': sub, 'Source': 'DNSBufferOverRun'})
                    except:
                        pass
                for line in data['RDNS']:
                    try:
                        sub = line.split(",")[1]
                        self.handler.sub_handler({'Name': sub, 'Source': 'DNSBufferOverRun'})
                    except:
                        pass
        except:
            pass
