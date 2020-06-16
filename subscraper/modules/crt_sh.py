from subscraper.helpers import get_request

class CrtSh():
    def __init__(self, args, target, handler):
        self.description = "Use crt.sh to find subdomains"
        self.author      = '@m8r0wn'
        self.method      = ['scrape']

        self.timeout = args.timeout
        self.handler = handler
        self.target  = target

    def execute(self):
        link = "https://crt.sh/?q=%25.{}&output=json".format(self.target)
        try:
            resp = get_request(link, self.timeout)
            if resp.text and resp.status_code == 200:
                for data in resp.json():
                    sub = data['name_value']
                    for xsub in sub.split('\n'):
                        self.handler.sub_handler({'Name': xsub, 'Source': 'CRT.SH'})
        except:
            pass