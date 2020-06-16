from urllib.parse import urlparse
from subscraper.helpers import get_request

class WaybackMachine():
    def __init__(self, args, target, handler):
        self.description = "Search wayback machine (archive.org) for subdomains"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target

    def execute(self):
        link = "http://web.archive.org/cdx/search/cdx?url=*.{}/*&output=json&collapse=urlkey".format(self.target)
        try:
            resp = get_request(link.format(self.target), self.timeout)
            if resp.text and resp.status_code == 200:
                for data in resp.json():
                    sub = urlparse(data[2]).netloc
                    if ":" in sub: # Parse out Port
                        sub = sub.split(":")[0]
                    self.handler.sub_handler({'Name': sub, 'Source': 'Archive.org'})
        except:
            pass