import logging
import threading
from taser.http import web_request, get_statuscode

class SubModule(threading.Thread):
    name = 'redhuntlabs'
    description = "RedHunt Labs' recon API"
    author = ['@redhuntlabs']
    api_key = True

    def __init__(self, args, domain, report_q, config):
        threading.Thread.__init__(self)
        self.daemon = True

        self.args = args
        self.config = config
        self.domain = domain
        self.report_q = report_q

    def run(self):
        # API key check
        if not self.config.redhuntlabs['X-BLOBR-KEY']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        page = 1
        url = f'https://reconapi.redhuntlabs.com/community/v1/domains/subdomains?domain={self.domain}&page_size=10&page={}'
        headers = {"X-BLOBR-KEY": self.config.redhuntlabs['X-BLOBR-KEY']}

        while 1:
            try:
                resp = web_request(url.format(self.domain, page), headers=headers, timeout=self.args.timeout)
                status_code = get_statuscode(resp)

                if status_code == 200:
                    if resp.json()['subdomains']:
                        for sub in resp.json()['subdomains']: self.report_q.add({'Name': f'{sub}.{self.domain}', 'Source': self.name})
                        page+=1
                    else:
                        logging.debug(f'{self.name}: No results found (Pg. {page}) closing thread')
                        page = False
                elif status_code == 403: raise Exception(f'API Limit reached ({status_code})')
                else: raise Exception(f'Web request failed to {url} ({status_code})')
                
            except Exception as e:
                logging.debug(f'{self.name.upper()} ERR: {e}')
                page = False
