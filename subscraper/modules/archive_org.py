import threading
from urllib.parse import urlparse
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'archiveorg'
    description = "Use archive.org to find subdomains."
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
        link = "http://web.archive.org/cdx/search/cdx?url=*.{}/*&output=json&collapse=urlkey".format(self.target)
        try:
            resp = get_request(link.format(self.target), self.timeout)
            if resp.text and resp.status_code == 200:
                for data in resp.json():
                    sub = urlparse(data[2]).netloc
                    if ":" in sub: # Parse out Port
                        sub = sub.split(":")[0]
                    self.handler.sub_handler({'Name': sub, 'Source': self.name})
        except:
            pass