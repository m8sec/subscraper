import logging
import threading
from taser.http import web_request, get_statuscode

class SubModule(threading.Thread):
    name = 'shodan'
    description = "Get subdomains with Shodan"
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
        if not self.config.shodan['api_key']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        url = "https://api.shodan.io/dns/domain/{}?key={}".format(self.domain, self.config.shodan['api_key'])

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for line in resp.json()["data"]:
                    if line["subdomain"]:
                        # Dup checks, cname lookups, & dns resolution handled by report_q
                        self.report_q.add({'Name': '.'.join([line["subdomain"], self.domain]), 'Source': self.name})
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
