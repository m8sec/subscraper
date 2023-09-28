import re
import threading
from time import sleep
from queue import Queue

from taser.dns import DNSutils
from taser.logx import highlight, setup_file_logger
from taser.http import web_request, get_statuscode, extract_header, get_title


class SubReportQ(threading.Thread):
    # Report Queue executed in separate thread at runtime.
    # Offloads actual reporting task to SubReporter Class via
    # sub-threads to increase speed - esp. when using -http

    def __init__(self, args):
        threading.Thread.__init__(self)
        self.daemon = True
        self.running = True

        self.args = args
        self.sub_q = Queue()
        self.sub_cache = set(())

        self.ledger = setup_file_logger(self.args.report, logger_name='sub_report')
        self.csv_check()

        self.report_sub_threads = 10 if self.args.threads >= 25 else 2 if self.args.threads >= 10 else 1
        self.sub_regex = ".*[a-zA-Z0-9]([-a-zA-Z0-9]{0,61}[a-zA-Z0-9])?\.([a-zA-Z0-9]{1,2}([-a-zA-Z0-9]{0,252}[a-zA-Z0-9])?)\.([a-zA-Z]{2,63})"


    def run(self):
        th = []

        while self.running:
            if self.sub_q.empty():
                sleep(0.2)
            else:
                t = SubReporter(self.sub_q.get(), self.args, self.ledger)
                t.start()
                th.append(t)

                while len(th) > self.report_sub_threads:
                    for t in th:
                        if not t.is_alive():
                            th.remove(t)
                    sleep(0.05)

        while len(th) > 0:
            for t in th:
                if not t.is_alive():
                    th.remove(t)
            sleep(0.05)

    def add(self, sub_entry):
        # Add sub dict to queue and cache set to prevent duplicates
        if sub_entry['Name'].lower() not in self.sub_cache:
            if re.match(self.sub_regex, sub_entry['Name']):
                self.sub_cache.add(sub_entry['Name'].lower())
                self.sub_q.put(sub_entry)

    def stop(self):
        while not self.sub_q.empty():
            sleep(0.03)
        self.running = False

        # Let subs finish printing
        sleep(0.3)

    def csv_check(self):
        # Setup CSV Outfile
        if self.args.csv:
            csv_headers = '"Source","Subdomain",'

            if self.args.resolve:
                csv_headers += '"DNS (A)",'

            if self.args.cname:
                csv_headers += '"DNS (CNAME)",'

            for port in self.args.http_port:
                proto = get_http_proto(port)
                csv_headers += f'"Status ({port}/{proto})",'
                csv_headers += f'"Size ({port}/{proto})",'
                csv_headers += f'"Title ({port}/{proto})",'
                csv_headers += f'"Server ({port}/{proto})",'
            self.ledger.info(csv_headers)


class SubReporter(threading.Thread):
    # Enumerates and reports identified subdomains

    def __init__(self, sub_dict, args, ledger):
        threading.Thread.__init__(self)
        self.args = args
        self.ledger = ledger
        self.sub_dict = sub_dict

    def run(self):
        dns_lookup = False
        report_data = '"{}","{}",'.format(self.sub_dict['Source'], self.sub_dict['Name']) if self.args.csv else self.sub_dict['Name']

        out_string = '[{}] '.format(highlight(self.sub_dict['Source'], 'blue', 'bold', windows=self.args.no_color))
        out_string += self.sub_dict['Name']

        if self.args.resolve or self.args.active:
            dns_lookup = self.sub_dict['DNS'] if 'DNS' in self.sub_dict.keys() else self.resolve_ip(self.sub_dict['Name'], self.args.timeout)

            # only output for -resolve
            if self.args.resolve:
                report_data += f'"{dns_lookup}",'
                tmp = ' [{}]'.format(', '.join(dns_lookup))
                out_string += highlight(tmp, fg='green', style='none', windows=self.args.no_color)

        if self.args.cname:
            cname = self.resolve_cname(self.sub_dict['Name'], self.args.timeout)
            report_data += f'"{cname}",' if self.args.cname else ''

            tmp = ' [{}]'.format(', '.join([x[:-1] if x.endswith('.') else x for x in cname]))
            out_string += highlight(tmp, fg='red', style='none', windows=self.args.no_color)

        if self.args.http:
            for port in self.args.http_port:
                resp = self.get_web_request(self.sub_dict['Name'], port, self.args.timeout)
                if resp['code'] > 0:
                    report_data += '"{}","{}","{}","{}",'.format(resp['code'], resp['size'], resp['title'], resp['server'])

                    tmp = " [{}/{} - {} ({})".format(port, resp['proto'].upper(), resp['title'][:25], resp['code'])
                    tmp += "..]" if len(resp['title']) > 20 else "]"

                    color = 'cyan' if (self.args.http_port.index(port) % 2) == 0 else 'purple'
                    out_string += highlight(tmp, color, 'none', windows=self.args.no_color)

        if self.filter_active(dns_lookup):
            print(self.sub_dict['Name'] if self.args.silent else out_string)
            self.ledger.info(report_data)

    ###############################
    # probe requests
    ###############################
    def resolve_ip(self, subdomain, timeout):
        return DNSutils.query(subdomain, qtype="A", ns=self.args.ns, timeout=timeout)

    def resolve_cname(self, subdomain, timeout):
        return DNSutils.query(subdomain, qtype="CNAME", ns=self.args.ns, timeout=timeout)

    def get_web_request(self, subdomain, port, timeout):
        proto = get_http_proto(port)
        resp = web_request(f'{proto}://{subdomain}:{port}', timeout=timeout)
        return {'proto': proto,
                'code': get_statuscode(resp),
                'size': len(resp.text) if resp else 0,
                'title': get_title(resp),
                'server': extract_header('Server', resp)}

    ###############################
    # Output filtering
    ###############################
    def filter_active(self, dns_query):
        return not self.args.active or bool(dns_query)

def get_http_proto(port):
    return 'http' if port in ['80', '8080'] else 'https'