import logging
import threading
from subscraper.utils import remove_wildcard
from taser.http import web_request, get_statuscode

class SubModule(threading.Thread):
    name = 'bufferover'
    description = "Query Bufferover.run API"
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
        # API key check
        if not self.config.bufferover['api_key']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        url = "https://tls.bufferover.run/dns?q=.{}".format(self.domain)
        headers = {'x-api-key': self.config.bufferover['api_key']}

        try:
            resp = web_request(url, timeout=self.args.timeout, headers=headers)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for line in resp.json()['Results']:
                    for sub in line.split(','):
                        if self.domain in sub:
                            self.report_q.add({'Name': remove_wildcard(sub), 'Source': self.name})
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
