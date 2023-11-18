import logging
import threading

from taser.http import web_request, get_statuscode

from subscraper.utils import remove_wildcard


class SubModule(threading.Thread):
    name = 'certspotter'
    description = "Use Certspotter API to collect subdomains"
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
        url = f"https://api.certspotter.com/v1/issuances?domain={self.domain}&include_subdomains=true&expand=dns_names"
        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for data in resp.json():
                    for sub in data['dns_names']:
                        if self.domain in sub:
                            self.report_q.add({'Name': remove_wildcard(sub), 'Source': self.name})
            elif status_code == 429:
                raise Exception(f'Too many requests ({status_code})')
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
