import logging
import threading

from censys.search import CensysCerts
from taser import logx


class SubModule(threading.Thread):
    name = 'censys.io'
    description = "Gather subdomains through censys.io SSL cert Lookups."
    author = ['@m8sec']
    api_key = True

    def __init__(self, args, domain, report_q, config):
        threading.Thread.__init__(self)
        self.daemon = True

        self.args = args
        self.config = config
        self.domain = domain
        self.report_q = report_q

    def run(self):
        if not self.config.censys['api_id'] or not self.config.censys['api_secret']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        try:
            certs = CensysCerts(api_id=self.config.censys['api_id'], api_secret=self.config.censys['api_secret'])
            resp = certs.search(f'names: {self.domain}', per_page=100, pages=-1)
            for page in resp:
                for line in page:
                    for sub in line['names']:
                        if sub.endswith(self.domain):
                            self.report_q.add({'Name': sub, 'Source': self.name})

        except Exception as e:
            if str(e).startswith('403 (unauthorized):'):
                logx.color(f'[{self.name}] Censys Authentication Failed: Verify API ID & Secret', fg='yellow')
            elif '400 (max_results)' in str(e):
                logx.color(f'[{self.name}] Max results hit (400)', fg='gray')
            else:
                logging.debug(f'{self.name.upper()} ERR: {e}')
