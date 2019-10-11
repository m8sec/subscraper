#!/usr/bin/env python3
# Author: @m8r0wn

import argparse
from os import path
from time import sleep
from datetime import datetime
from sys import exit, stdout
from threading import Thread, activeCount
from subscraper.modules import MODULES, get_module_class
from subscraper.sub_handler import SubHandler, SubReporter
from subscraper.helpers import dns_lookup, respcode

def takeover_check(sub, target):
    for cname in dns_lookup(sub, 'CNAME'):
            if target not in cname:
                http = respcode(sub, proto='http')
                https = respcode(sub, proto='https')
                stdout.write("{:<45}\t({:<3}/{:<3})\t{}\n".format(sub, http, https, cname))

def takeover(args, sublist, target):
    try:
        stdout.write("\n\033[1;30m[*] Subdomain Takeover Check\033[1;m\n")
        stdout.write("\033[1;30m{:<45}\t({:<9})\t{}\033[1;m\n".format('Subdomain', 'http/https', 'CNAME Record'))
        for sub in sublist:
            Thread(target=takeover_check, args=(sub, target,), daemon=True).start()
            while activeCount() > 15:
                sleep(0.001)
        while activeCount() > 1:
            sleep(0.005)

    except KeyboardInterrupt:
        stdout.write("\n[!] Key Event Detected...\n\n")
        return

def subenum(args, target):
    try:
        stdout.write("\n\033[1;30m{:<13}\t{:<45}\t({:<9})\t{}\033[1;m\n".format('[Source]', 'Subdomain', 'http/https', 'DNS Resolution'))

        reporter = SubReporter(args)
        reporter.daemon = True
        reporter.start()
        handler = SubHandler(reporter.subq)

        for module in MODULES:
            module_class = get_module_class(module)
            class_obj    = module_class(args, target, handler)

            # Brute force methods
            if args.scrape and 'brute' in class_obj.method:
                Thread(target=class_obj.execute, args=(), daemon=True).start()

            # Scraping methods
            elif args.brute and 'scrape' in class_obj.method:
                Thread(target=class_obj.execute, args=(), daemon=True).start()

            while activeCount() > args.max_threads:
                sleep(0.001)

        while activeCount() > 2:
            sleep(0.005)
        reporter.stop()

        takeover(args, reporter.complete, target)
        return len(reporter.complete)

    except KeyboardInterrupt:
        try:
            reporter.close()
        except:
            pass

        stdout.write("\n[!] Key Event Detected...\n\n")
        return len(reporter.complete)

    except Exception as e:
        stdout.write("\033[1;30m{:<13}\t{:<25}\033[1;m\n".format('[Error-01]', str(e)))

def file_exists(parser, filename):
    if not filename:
        return
    if not path.exists(filename):
        parser.error("Input file not found: {}".format(filename))
    return [x.strip() for x in open(filename)]

def main():
    VERSION = "2.1.0"
    print("""\033[1;30m
      ____        _    ____                                 
     / ___| _   _| |__/ ___|  ___ _ __ __ _ _ __   ___ _ __ 
     \___ \| | | | '_ \___ \ / __| '__/ _` | '_ \ / _ \ '__|
      ___) | |_| | |_) |__) | (__| | | (_| | |_) |  __/ |   
     |____/ \__,_|_.__/____/ \___|_|  \__,_| .__/ \___|_|   
                                           |_|            v{} \033[1;m""".format(VERSION))
    args = argparse.ArgumentParser(description="""
---------------------------------------------------------------
Subdomain enumeration through various techniques. In addition, SubScraper will provide DNS 'A' record 
lookups and http/https response codes to verify active subdomains. Lastly, CNAME lookups are performed 
to identify potential subdomain takeover opportunities.

usage:
    subscraper -s example.com
    subscraper m8r0wn.com""", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    options = args.add_argument_group("SubScraper Options")
    options.add_argument('-T', dest='max_threads', type=int, default=75, help='Max threads')
    options.add_argument('-t', dest='timeout', type=int, default=25, help='Timeout [seconds] for search threads (Default: 25)')
    options.add_argument(dest='target', nargs='+', help='Target domain (Positional)')

    sub = args.add_argument_group("Subdomain Enumeration Options")
    sub.add_argument('-s', dest="scrape", action='store_false', help="Only use internet to find subdomains")
    sub.add_argument('-b', dest="brute", action='store_false', help="Only use DNS brute forcing to find subdomains")
    sub.add_argument('-w', dest="sublist",default=path.join(path.dirname(path.realpath(__file__)), 'resources/subdomains.txt'), type=lambda x: file_exists(args, x), help='Custom subdomain wordlist')
    sub.add_argument('--censys-api', dest='censys_api', type=str, default='', help='Add Censys.io API Key')
    sub.add_argument('--censys-secret', dest='censys_secret', type=str, default='', help='Add Censys.io Secret')

    report = args.add_argument_group("Subdomain Enumeration: Reporting")
    report.add_argument('-r', '--report', dest='report', type=str, default='', help="Write subdomains to txt file")
    report.add_argument('--report-type', dest='report_type', type=str, choices=['txt', 'csv'], default='txt', help="Output file types: txt, csv")

    to = args.add_argument_group("Subdomain TakeOver")
    to.add_argument('--takeover', dest="takeover", default='', type=lambda x: file_exists(args, x), help='Perform takeover check on list of subs')
    args = args.parse_args()

    if args.takeover:
        takeover(args, args.takeover, args.target[0])
    else:
        start_timer = datetime.now()
        count = subenum(args, args.target[0])
        stop_timer = datetime.now()
        stdout.write("\n\033[1;30m[*] Identified {} subdomain(s) in {}\n\033[1;m\n".format(count, stop_timer - start_timer))

if __name__ == '__main__':
    main()