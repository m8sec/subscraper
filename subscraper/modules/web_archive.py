import logging
import threading

from taser.http import web_request, get_statuscode
from taser.http.parser import URLParser


class SubModule(threading.Thread):
    name = 'archive'
    description = "Use archive.org to find subdomains."
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
        url = f"http://web.archive.org/cdx/search/cdx?url=*.{self.domain}/*&output=json&collapse=urlkey"

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code != 200:
                raise Exception(f'Web request failed to {url} ({status_code})')
            for data in resp.json():
                sub = URLParser.extract_subdomain(data[2])
                self.report_q.add({'Name': self.scrub_port(sub), 'Source': self.name})
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')

    def scrub_port(self, sub):
        return sub.split(":")[0] if ':' in sub else sub
