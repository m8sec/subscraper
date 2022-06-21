import threading
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'bufferoverrun'
    description = "Bufferover.run passive enumeration."
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
        link = "https://dns.bufferover.run/dns?q=.{}".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                data = resp.json()
                for line in data['FDNS_A']:
                    try:
                        sub = line.split(",")[1]
                        self.handler.sub_handler({'Name': sub, 'Source': self.name})
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
