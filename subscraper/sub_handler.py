import threading
from sys import stdout
from time import sleep
from subscraper.helpers import dns_lookup, get_request, respcode

class SubHandler():
    def __init__(self, subq):
        self.subq = subq

    def sub_handler(self, sub):
        threading.Thread(target=self.data_handler, args=(sub,), daemon=True).start()

    def data_handler(self, sub):
        try:
            dns = sub['DNS']
        except:
            dns = dns_lookup(sub['Name'], 'A')

        sub['HTTP']  = respcode(sub['Name'], proto='http')
        sub['HTTPS'] = respcode(sub['Name'], proto='https')
        sub['DNS']   = dns
        self.subq.append(sub)


class SubReporter(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.subq     = []
        self.complete = []
        self.running  = True
        self.report   = args.report
        self.rtype    = args.report_type


    def run(self):
        if self.report:
            self.outfile = open(self.report, 'a')
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
        except:pass


    def stop(self):
        while self.subq:
            sleep(0.05)
        self.running = False


    def reporter(self, sub):
        if sub['Name'].lower() in self.complete:
            return

        stdout.write("\033[1;34m{:<13}\033[1;m\t{:<45}\t({:<3}/{:<3})\t{}\n".format('[{}]'.format(sub['Source']), sub['Name'], sub['HTTP'], sub['HTTPS'], sub['DNS']))

        if self.report and self.rtype == 'txt':
            self.write_file(sub['Name'])
        elif self.report and self.rtype == 'csv':
            self.write_file("{},{},{},{}".format(sub['Name'], sub['HTTP'], sub['HTTPS'], sub['DNS']))

        self.complete.append(sub['Name'].lower())


    def write_file(self, data):
        self.outfile.write('{}\n'.format(data))