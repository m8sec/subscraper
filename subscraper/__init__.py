#!/usr/bin/env python3
# Author: @m8r0wn

import argparse
from os import path
from time import sleep
from datetime import datetime
from sys import stdout
from threading import Thread, activeCount
from subscraper.modules import MODULES, get_module_class
from subscraper.sub_handler import SubHandler, SubReporter
from subscraper.helpers import dns_lookup, respcode
from ipparser import ipparser

def takeover_check(target):
    for cname in dns_lookup(target, 'CNAME'):
        http = respcode(target, proto='http')
        https = respcode(target, proto='https')
        stdout.write("{:<45}\t({:<3}/{:<3})\t{}\n".format(target, http, https, cname))

def takeover(args, targets):
    stdout.write("\n\033[1;30m[*] Subdomain Takeover Check\033[1;m\n")
    stdout.write("\033[1;30m{:<45}\t({:<9})\t{}\033[1;m\n".format('Subdomain', 'http/https', 'CNAME Record'))
    try:
        for target in targets:
            Thread(target=takeover_check, args=(target,), daemon=True).start()
            while activeCount() > args.max_threads:
                sleep(0.001)
        while activeCount() > 1:
            sleep(0.005)
    except KeyboardInterrupt:
        stdout.write("\n[!] Key Event Detected...\n\n")
        return

def subenum(args, targets):
    reporter = SubReporter(args)
    reporter.daemon = True
    reporter.start()
    handler = SubHandler(reporter, args.sub_enum)

    # Header
    insrt = ''
    if args.sub_enum >= 3:
        insrt = '({:<9})\t{}'.format('http/https', 'DNS Resolution')
    elif args.sub_enum >= 2:
        insrt = 'DNS Resolution'
    stdout.write("\n\033[1;30m{:<20} {:<40}\t{}\033[1;m\n".format('[Source]', 'Subdomain', insrt))

    try:
        for target in targets:
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
            sleep(0.05)
        reporter.stop()
        return len(reporter.complete)

    except KeyboardInterrupt:
        stdout.write("\n[!] Key Event Detected...\n\n")
        reporter.stop()
        return len(reporter.complete)

    except Exception as e:
        stdout.write("\033[1;30m{:<13}\t{:<25}\033[1;m\n".format('[Error-01]', str(e)))
    finally:
        reporter.close()


def file_exists(parser, filename):
    if not filename:
        return
    if not path.exists(filename):
        parser.error("Input file not found: {}".format(filename))
    return [x.strip() for x in open(filename)]


def main():
    VERSION = "2.2.1"
    print("""\033[1;30m
      ____        _    ____                                 
     / ___| _   _| |__/ ___|  ___ _ __ __ _ _ __   ___ _ __ 
     \___ \| | | | '_ \___ \ / __| '__/ _` | '_ \ / _ \ '__|
      ___) | |_| | |_) |__) | (__| | | (_| | |_) |  __/ |   
     |____/ \__,_|_.__/____/ \___|_|  \__,_| .__/ \___|_|   
                                           |_|            v{} \033[1;m""".format(VERSION))
    args = argparse.ArgumentParser(description="""
---------------------------------------------------------------""", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    options = args.add_argument_group("SubScraper Options")
    options.add_argument('-T', dest='max_threads', type=int, default=55, help='Max threads')
    options.add_argument('-t', dest='timeout', type=int, default=25, help='Timeout [seconds] for search threads (Default: 25)')
    options.add_argument('-o', dest='report', type=str, default='./subscraper_report.txt', help="Output to specific file")
    options.add_argument(dest='target', nargs='+', help='Target domain (Positional)')

    sub = args.add_argument_group("Enumeration Options")
    sub.add_argument('-s', dest="scrape", action='store_false', help="Only use scraping techniques")
    sub.add_argument('-b', dest="brute", action='store_false', help="Only use DNS brute force")
    sub.add_argument('-w', dest="sublist",default=path.join(path.dirname(path.realpath(__file__)), 'resources/subdomains.txt'), type=lambda x: file_exists(args, x), help='Custom subdomain wordlist')
    sub.add_argument('-e','--enum', metavar='LVL', dest="sub_enum", type=int, default=1, help="Enumeration Level:\n"
                                                                                                "1: Subdomain Only (Default)\n"
                                                                                                "2: Live subdomains, verified by DNS\n"
                                                                                                "3: Live check & get HTTP/S response codes")

    adv = args.add_argument_group("Enumeration Advanced")
    adv.add_argument('--censys-api', metavar='API', dest='censys_api', type=str, default='', help='Censys.io API Key')
    adv.add_argument('--censys-secret', metavar='KEY', dest='censys_secret', type=str, default='', help='Censys.io Secret')

    to = args.add_argument_group("Subdomain TakeOver")
    to.add_argument('--takeover', dest="takeover", action='store_true', help='Perform takeover check on list of subs')
    args = args.parse_args()

    if args.takeover:
        takeover(args, ipparser(args.target[0]))
    else:
        start_timer = datetime.now()
        count = subenum(args, ipparser(args.target[0]))
        stop_timer = datetime.now()
        stdout.write("\n\033[1;30m[*] Identified {} subdomain(s) in {}\n\033[1;m".format(count, stop_timer - start_timer))
        stdout.write("\033[1;30m[*] Subdomains written to {}\n\033[1;m".format(args.report))

if __name__ == '__main__':
    main()