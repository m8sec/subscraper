import logging
import threading

from taser.http import web_request, get_statuscode, extract_links


class SubModule(threading.Thread):
    name = 'dnsrepo'
    description = "Parse dnsrepo.noc.org without an API key - 150 result limit"
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
        url = f"https://dnsrepo.noc.org/?search={self.domain}"

        try:
            resp = web_request(url, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code != 200:
                raise Exception(f'Web request failed to {url} ({status_code})')
            for link in extract_links(resp, mailto=False, source={'a': 'href'}):
                if "?domain=" in link and link.endswith(f'{self.domain}.'):
                    sub = link.split('/?domain=')[1]
                    sub = sub[:-1] if sub.endswith('.') else sub
                    self.report_q.add({'Name': sub, 'Source': self.name})
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
