import logging
import threading
from taser.http.parser import URLParser
from taser.http import web_request, get_statuscode


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
        url = "http://web.archive.org/cdx/search/cdx?url=*.{}/*&output=json&collapse=urlkey".format(self.domain)

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for data in resp.json():
                    sub = URLParser.extract_subdomain(data[2])
                    self.report_q.add({'Name': self.scrub_port(sub), 'Source': self.name})
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')

    def scrub_port(self, sub):
        return sub.split(":")[0] if ':' in sub else sub
