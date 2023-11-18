import logging
import threading
from taser.http import web_request, get_statuscode, extract_links


class SubModule(threading.Thread):
    name = 'alienvault'
    description = "Find subdomains using AlienVault OTX"
    author = ['@m8sec']
    api_key = False

    def __init__(self, args, domain, report_q, config):
        threading.Thread.__init__(self)
        self.daemon = True

        self.args = args
        self.config = config
        self.domain = domain
        self.report_q = report_q

    def run(self):
        url = f"https://otx.alienvault.com/api/v1/indicators/domain/{self.domain}/passive_dns"

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code != 200:
                raise Exception(f'Web request failed to {url} ({status_code})')
            for data in resp.json()['passive_dns']:
                self.report_q.add({'Name': data['hostname'], 'Source': self.name})
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
