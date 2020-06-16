import re
import threading
from sys import stdout
from time import sleep
from subscraper.helpers import dns_lookup, get_request, respcode


class SubHandler():
    def __init__(self, reporter, sub_enum):
        self.reporter = reporter
        self.sub_enum = sub_enum
        self.sub_regex = ".*[a-zA-Z0-9]([-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?\.([a-zA-Z0-9]{1,2}([-a-zA-Z0-9]{0,252}[a-zA-Z0-9])?)\.([a-zA-Z]{2,63})"

    def sub_handler(self, sub):
        threading.Thread(target=self.data_handler, args=(sub,), daemon=True).start()

    def data_handler(self, sub):
        if re.match(self.sub_regex, sub['Name']):
            if "*." in sub['Name']:
                sub['Name'] = sub['Name'].split('*.')[1]

            if self.sub_enum >= 2 and 'DNS' not in sub:
                sub['DNS'] = dns_lookup(sub['Name'], 'A')
            if self.sub_enum >= 3:
                sub['HTTP']  = respcode(sub['Name'], proto='http')
                sub['HTTPS'] = respcode(sub['Name'], proto='https')
            self.reporter.subq.append(sub)


class SubReporter(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.subq     = []
        self.complete = []
        self.running  = True
        self.report = False
        self.report = args.report
        self.sub_enum = args.sub_enum

    def run(self):
        self.outfile = open(self.report, 'w')
        while self.running:
            if self.subq:
                self.reporter(self.subq[0])
                self.subq.pop(0)
            else:
                sleep(0.001)
        self.close()

    def close(self):
        try:
            self.outfile.close()
        except:
            pass

    def stop(self):
        while self.subq:
            sleep(0.05)
        self.running = False

    def reporter(self, sub):
        if sub['Name'].lower() in self.complete:
            return

        if self.enum_check(sub):
            self.write_file(sub['Name'])
            self.complete.append(sub['Name'].lower())

    def enum_check(self, sub):
        if self.sub_enum == 3 and len(sub['DNS']) > 0:
            stdout.write("\033[1;34m{:<20}\033[1;m{:<40}\t({:<3}/{:<3})\t{}\n".format('[{}]'.format(sub['Source']),sub['Name'], sub['HTTP'], sub['HTTPS'], sub['DNS']))
            return True
        elif self.sub_enum == 2 and len(sub['DNS']) > 0:
            stdout.write("\033[1;34m{:<20}\033[1;m{:<40}\t{}\n".format('[{}]'.format(sub['Source']), sub['Name'], sub['DNS']))
            return True
        elif self.sub_enum == 1:
            stdout.write("\033[1;34m{:<20}\033[1;m{}\n".format('[{}]'.format(sub['Source']), sub['Name']))
            return True
        return False

    def write_file(self, data):
        self.outfile.write('{}\n'.format(data))