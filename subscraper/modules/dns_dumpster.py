import logging
import threading
from taser.http import web_request, get_statuscode


class SubModule(threading.Thread):
    name = 'dnsdumpster'
    description = "Use DNS dumpster to enumerate subdomains."
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
        url = f"https://api.hackertarget.com/hostsearch/?q={self.domain}"
        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)
            if status_code == 200:
                for line in resp.text.splitlines():
                    if line.count('.') > 1:
                        if sub := self.sub_extractor(line):
                            self.report_q.add({'Name': sub, 'Source': self.name})

            elif status_code == 429:
                raise Exception(f'Too many requests ({status_code})')
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')

    def sub_extractor(self, line):
        try:
            return line.split(",")[0]
        except Exception:
            return False
