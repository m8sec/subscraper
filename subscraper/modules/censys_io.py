from sys import stdout
from time import sleep
import censys.certificates
from threading import Thread

class CensysIO():
    def __init__(self, args, target, handler):
        self.description  = "Sub enum through Censys SSL cert Lookup"
        self.author       = '@m8r0wn'
        self.method       = ['scrape']

        self.handler      = handler
        self.target       = target
        self.timeout      = args.timeout

        self.api          = args.censys_api
        self.secret       = args.censys_secret
        self.thread_count = 0
        self.running      = True

    def timer(self, time):
        sleep(time)
        self.running = False

    def execute(self):
        if not self.api or not self.secret:
            return
        try:
            # Start timeout thread
            Thread(target=self.timer, args=(self.timeout,), daemon=True).start()
            # Start Search
            certs = censys.certificates.CensysCertificates(api_id=self.api, api_secret=self.secret)
            resp = certs.search("parsed.names: {}".format(self.target), fields=['parsed.names'])
            for line in resp:
                # Return on timeout
                if not self.running:
                    return
                # Threading to parse results
                self.thread_count += 1
                Thread(target=self.parser, args=(self.target, line,)).start()
                # Sleep while max threads reached
                while self.thread_count >= 2:
                    sleep(0.001)
            while self.thread_count > 0:
                sleep(0.001)
        except Exception as e:
            if str(e).startswith('403 (unauthorized):'):
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Authentication Failed: verify API Key/Secret\033[1;m\n")
            elif '400 (max_results)' in str(e):
                pass
            else:
                stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Error: {}\033[1;m\n".format(str(e)))


    def parser(self, target, line):
        #for line in resp:
        try:
            for sub in line['parsed.names']:
                if sub.endswith(target) and "*" not in sub:
                    self.handler.sub_handler({'Name': sub, 'Source': 'Censys.io'})
        except:
            pass
        self.thread_count -= 1