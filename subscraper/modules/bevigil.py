import logging
import threading

from taser.http import web_request, get_statuscode


class SubModule(threading.Thread):
    name = 'bevigil'
    description = "BeVigil OSINT API for scraping mobile application for subdomains"
    author = ['@alt-glitch', '@m8sec']
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
        if not self.config.bevigil['api_key']:
            logging.debug(f'Skipping {self.name}, API key(s) not found')
            return False

        url = f"https://osint.bevigil.com/api/{self.domain}/subdomains/"
        header = {"X-Access-Token": self.config.bevigil['api_key']}

        try:
            resp = web_request(url, timeout=self.args.timeout, headers=header)
            status_code = get_statuscode(resp)

            if status_code != 200:
                raise Exception(f'Web request failed to {url} ({status_code})')
            for sub in resp.json()['subdomains']:
                self.report_q.add({'Name': sub, 'Source': self.name})
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
