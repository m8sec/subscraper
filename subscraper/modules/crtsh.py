import threading
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'certsh'
    description = "Subdomains enumeration using cert.sh."
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
        link = "https://crt.sh/?q=%25.{}&output=json".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                for data in resp.json():
                    sub = data['name_value']
                    for xsub in sub.split('\n'):
                        self.handler.sub_handler({'Name': xsub, 'Source': self.name})
        except:
            pass
