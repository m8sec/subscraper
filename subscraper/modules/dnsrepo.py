import logging
import threading
import random
from taser.http import web_request, get_statuscode, extract_links

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G985F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 10; en-us; SM-N975U Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 9; en-US; Redmi Note 7 Pro Build/PKQ1.181203.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.111 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; CrOS x86_64 12871.102.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.141 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; ARM; Lumia 950) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edge/40.15254.603",
]

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
        user_agent = random.choice(USER_AGENTS)
        url = "https://dnsrepo.noc.org/?search={}".format(self.domain)

        try:
            resp = web_request(url, user_agent=user_agent, timeout=self.args.timeout)
            status_code = get_statuscode(resp)

            if status_code == 200:
                for link in extract_links(resp, mailto=False, source={'a':'href'}):
                    if "?domain=" in link and link.endswith(f'{self.domain}.'):
                        sub = link.split('/?domain=')[1]
                        sub = sub[:-1] if sub.endswith('.') else sub
                        self.report_q.add({'Name': sub, 'Source': self.name})
            else:
                raise Exception(f'Web request failed to {url} ({status_code})')
        except Exception as e:
            logging.debug(f'{self.name.upper()} ERR: {e}')
