import re
import os
import threading
from sys import stdout
from time import sleep
from queue import Queue
from itertools import cycle
from subscraper.support.cli import highlight
from subscraper.support import dns_lookup, web_info

class SubHandler():
    '''
    Intermediary class passed to each module. After successful subdomain is
    found, a thread is launched to perform additional enumeration (dns, http, etc).
    Results are passed to reporting queue for cli and/or file output.
    '''
    def __init__(self, reporter, args):
        self.reporter = reporter
        self.args = args
        self.sub_regex = ".*[a-zA-Z0-9]([-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?\.([a-zA-Z0-9]{1,2}([-a-zA-Z0-9]{0,252}[a-zA-Z0-9])?)\.([a-zA-Z]{2,63})"

    def sub_handler(self, sub):
        threading.Thread(target=self.data_handler, args=(sub,), daemon=True).start()

    def data_handler(self, sub):
        if re.match(self.sub_regex, sub['Name']):
            if "*." in sub['Name']:
                sub['Name'] = sub['Name'].split('*.')[1]

            if self.args.dns and 'DNS' not in sub:
                sub['DNS'] = dns_lookup(sub['Name'], 'A')

            if self.args.http:
                sub['HTTP'] = web_info(sub['Name'], proto='http', csv_report=self.args.report.endswith('.csv'))
                sub['HTTPS'] = web_info(sub['Name'], proto='https', csv_report=self.args.report.endswith('.csv'))

            if self.args.takeover:
                sub['Takeover'] = ','.join([x.rstrip('.') for x in dns_lookup(sub['Name'], 'CNAME')])

            self.reporter.subq.put(sub)


class SubReporter(threading.Thread):
    def __init__(self, args):
        threading.Thread.__init__(self)
        self.daemon = True
        self.subq = Queue()
        self.complete = []
        self.running = True
        self.report = False
        self.windows = True if os.name == 'nt' else False
        self.args = args
        self.status = cycle(['-', '/', '|', '\\'])

    def run(self):
        with open(self.args.report, 'w') as self.outfile:
            self.init_csv() if self.args.report.endswith('.csv') else False
            while self.running:
                if not self.subq.empty():
                    self.reporter(self.subq.get())
                else:
                    if self.windows is False: self.spinner()
                    sleep(0.2)

    def spinner(self):
        stdout.write(
            highlight("{} {} Subdomains Found.\n".format(
                next(self.status),
                len(self.complete)),
                'gray'
            )
        )
        stdout.write('\033[F' + '\033[K')

    def close(self):
        try:
            self.outfile.close()
        except:
            pass

    def stop(self):
        while not self.subq.empty():
            sleep(0.03)
        self.running = False

    def reporter(self, sub):
        # Remove duplicates
        if sub['Name'].lower() in self.complete:
            return

        self.cli_handler(sub)
        self.file_handler(sub)
        self.complete.append(sub['Name'].lower())

    def cli_handler(self, sub):
        src = '[{}]'.format(highlight(sub['Source'], 'blue'))
        pad_src = 15 if self.windows else (15+12)

        output = '{:<{}} {:<35} '.format(src, pad_src, sub['Name'])
        output += '({:<3}/{:<3})  '.format(sub['HTTP']['code'], sub['HTTPS']['code']) if self.args.http else ''
        output += '{:<35} '.format(sub['Takeover']) if self.args.takeover else ''
        output += '{} '.format(sub['DNS']) if self.args.dns else ''
        print(output)

    def file_handler(self, data):
        if self.args.report.endswith('.csv'):
            self.write_csv(data)
        elif self.args.report:
            self.write_txt(data['Name'])

    def write_txt(self, data):
        # Only write subdomains to file
        self.outfile.write('{}\n'.format(data))

    def init_csv(self):
        self.outfile.write('Source,Subdomain,')
        self.outfile.write('HTTP-code,HTTP-size,HTTP-title,HTTP-server,' if self.args.http else '')
        self.outfile.write('HTTPS-code,HTTPS-size,HTTPS-title,HTTPS-server,' if self.args.http else '')
        self.outfile.write('CNAME,' if self.args.takeover else '')
        self.outfile.write('DNS,' if self.args.dns else '')
        self.outfile.write('\n')

    def write_csv(self, data):
        # Write all data to file
        self.outfile.write('"{}","{}",'.format(data['Source'], data['Name']))
        if self.args.http:
            self.outfile.write('"{}","{}","{}","{}",'.format(data['HTTP']['code'],
                                                        data['HTTP']['size'],
                                                        data['HTTP']['title'],
                                                        data['HTTP']['server'])
                               )
            self.outfile.write('"{}","{}","{}","{}",'.format(data['HTTPS']['code'],
                                                        data['HTTPS']['size'],
                                                        data['HTTPS']['title'],
                                                        data['HTTPS']['server'])
                               )
            self.outfile.write('"{}",'.format(data['Takeover']) if self.args.takeover else '')
            self.outfile.write('"{}",'.format(data['DNS']) if self.args.dns else '')
        self.outfile.write('\n')

    def close(self):
        try:
            self.outfile.close()
        except:
            pass

    def stop(self):
        while not self.subq.empty():
            sleep(0.03)
        self.running = False

    def reporter(self, sub):
        # Remove duplicates
        if sub['Name'].lower() in self.complete:
            return

        self.cli_handler(sub)
        self.file_handler(sub)
        self.complete.append(sub['Name'].lower())

    def cli_handler(self, sub):
        src = '[{}]'.format(highlight(sub['Source'], 'blue'))
        pad_src = 15 if self.windows else (15+12)

        output = '{:<{}} {:<35} '.format(src, pad_src, sub['Name'])
        output += '({:<3}/{:<3})    '.format(sub['HTTP']['code'], sub['HTTPS']['code']) if self.args.http else ''
        output += '{:<35} '.format(sub['Takeover']) if self.args.takeover else ''
        output += '{} '.format(sub['DNS']) if self.args.dns else ''
        print(output)

    def file_handler(self, data):
        if self.args.report.endswith('.csv'):
            self.write_csv(data)
        elif self.args.report:
            self.write_txt(data['Name'])

    def write_txt(self, data):
        # Only write subdomains to file
        self.outfile.write('{}\n'.format(data))

    def init_csv(self):
        self.outfile.write('Source,Subdomain,')
        self.outfile.write('HTTP-code,HTTP-size,HTTP-title,HTTP-server,' if self.args.http else '')
        self.outfile.write('HTTPS-code,HTTPS-size,HTTPS-title,HTTPS-server,' if self.args.http else '')
        self.outfile.write('CNAME,' if self.args.takeover else '')
        self.outfile.write('DNS,' if self.args.dns else '')
        self.outfile.write('\n')

    def write_csv(self, data):
        # Write all data to file
        self.outfile.write('"{}","{}",'.format(data['Source'], data['Name']))
        if self.args.http:
            self.outfile.write('"{}","{}","{}","{}",'.format(data['HTTP']['code'],
                                                        data['HTTP']['size'],
                                                        data['HTTP']['title'],
                                                        data['HTTP']['server'])
                               )
            self.outfile.write('"{}","{}","{}","{}",'.format(data['HTTPS']['code'],
                                                        data['HTTPS']['size'],
                                                        data['HTTPS']['title'],
                                                        data['HTTPS']['server'])
                               )
            self.outfile.write('"{}",'.format(data['Takeover']) if self.args.takeover else '')
            self.outfile.write('"{}",'.format(data['DNS']) if self.args.dns else '')
        self.outfile.write('\n')
