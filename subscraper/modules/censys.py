import threading
from sys import stdout
from censys.search import CensysCertificates
from subscraper.support.cli import highlight

class SubModule(threading.Thread):
    name = 'censys'
    description = "Gather subdomains through censys.io SSL cert Lookups."
    author = '@m8r0wn'
    groups = ['all', 'scrape']
    args = {
        'API_ID': {
            'Description': 'Censys.io API ID',
            'Required': True,
            'Value': ''
        },
        'API_SECRET': {
            'Description': 'Censys.io API Secret',
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
        self.args['API_ID']['Value'] = args.censys_id
        self.args['API_SECRET']['Value'] = args.censys_secret


    def run(self):
        if not self.args['API_ID']['Value'] or not self.args['API_SECRET']['Value']:
            return False

        try:
            certs = CensysCertificates(api_id=self.args['API_ID']['Value'], api_secret=self.args['API_SECRET']['Value'])
            resp = certs.search("parsed.names: {}".format(self.target), fields=['parsed.names'])
            for line in resp:
                for sub in line['parsed.names']:
                    if sub.endswith(self.target):
                        self.handler.sub_handler({'Name': sub, 'Source': self.name})

        except Exception as e:
            if str(e).startswith('403 (unauthorized):'):
                print(highlight('[!]', 'yellow'),
                      highlight('Censys Authentication Failed: Verify API ID & Secret.', 'gray'))
            elif '400 (max_results)' in str(e):
                pass
            else:
                print(highlight('[!]', 'yellow'), highlight('Censys.IO Error: {}.'.format(e), 'gray'))
