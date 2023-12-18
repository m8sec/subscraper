import logging
import threading
from taser.http import web_request, get_statuscode


class SubModule(threading.Thread):
    name = 'virustotal'
    description = "Lookup subdomain on VirusTotal"
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
        if not self.config.virustotal['api_key']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        url = "https://www.virustotal.com/vtapi/v2/domain/report?apikey={}&domain={}".format(self.config.virustotal['api_key'], self.domain)

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for sub in resp.json()['subdomains']:
                    self.report_q.add({'Name': sub, 'Source': self.name})
            elif status_code == 204:
                raise Exception(f'Exceeded API key quota ({status_code})')
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
