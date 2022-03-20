from subscraper.helpers import get_request

class ThreatCrowd():
    def __init__(self, args, target, handler):
        self.description = "Use threatcrowd to find subdomains"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target

    def execute(self):
        link = "https://www.threatcrowd.org/searchApi/v2/domain/report/?domain={}".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                for sub in resp.json()['subdomains']:
                    self.handler.sub_handler({'Name': sub, 'Source': 'ThreatCrowd'})
        except:
            pass