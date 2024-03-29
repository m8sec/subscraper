import logging
import threading
from subscraper.utils import remove_wildcard
from taser.http import web_request, get_statuscode

class SubModule(threading.Thread):
    name = 'crt.sh'
    description = "Subdomains enumeration using cert.sh."
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
        url = "https://crt.sh/?q=%25.{}&output=json".format(self.domain)
        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for data in resp.json():
                    for sub in data['name_value'].split('\n'):
                        self.report_q.add({'Name': remove_wildcard(sub), 'Source': self.name})
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')

