import logging
import threading

from taser.http import web_request, get_statuscode


class SubModule(threading.Thread):
    name = 'chaos'
    description = "Project Discovery's Chaos"
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
        if not self.config.chaos['access_token']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        url = f'https://dns.projectdiscovery.io/dns/{self.domain}/subdomains'
        headers = {"Content-Type": "application/json", "Authorization": self.config.chaos['access_token']}

        try:
            resp = web_request(url, headers=headers, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code != 200:
                raise Exception(f'Web request failed to {url} ({status_code})')
            for sub in resp.json()['subdomains']:
                self.report_q.add({'Name': f'{sub}.{self.domain}', 'Source': self.name})
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
