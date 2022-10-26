import threading
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'bevigil'
    description = "BeVigil OSINT API for scraping mobile application for subdomains"
    author = "@alt-glitch"
    groups = ['all', 'scrape']
    args = {
        'API_KEY': {
            'Description': 'BeVigil OSINT API Key',
            'Required': True,
            'Value': ''
        }
    }

    def __init__(self, args, target, print_handler):
        threading.Thread.__init__(self)
        self.daemon = True
        self.handler = print_handler
        self.target = target
        self.timeout = args.timeout
        self.args['API_KEY']['Value'] = args.bevigil_key
        # print("here")


    def run(self):
        if not self.args['API_KEY']['Value']:
            return False

        url = "https://osint.bevigil.com/api/{}/subdomains/".format(self.target)
        header = {"X-Access-Token": self.args['API_KEY']['Value']}
        try:
            resp = get_request(link=url, timeout=self.timeout, headers=header)
            if resp.text and resp.status_code == 200:
                for sub in resp.json()['subdomains']:
                    self.handler.sub_handler({'Name': sub, 'Source': self.name})
        except:
            pass