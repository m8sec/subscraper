#!/usr/bin/env python3
import argparse
from sys import argv
from time import sleep
from os import path, listdir
from datetime import datetime
from threading import activeCount
from subscraper.modules import ModuleLoader
from subscraper.support import target_parser
from subscraper.support.cli import highlight
from subscraper.support.sub_handler import SubHandler, SubReporter

def banner():
    version = '3.0.2'
    banner = """                 
     ___      _    ___                            
    / __|_  _| |__/ __| __ _ _ __ _ _ __  ___ _ _ 
    \__ \ || | '_ \__ \/ _| '_/ _` | '_ \/ -_) '_|
    |___/\_,_|_.__/___/\__|_| \__,_| .__/\___|_| v{}
                                   |_|           @m8r0wn
    """.format(version)
    print(highlight(banner, 'gray'))

def print_headers(args):
    title_headers = '{:<15} {:<35} '.format('Source', 'Subdomain')
    title_headers += '{:<10}   '.format('HTTP/HTTPS') if args.http else ''
    title_headers += '{:<35} '.format('Takeover (CNAME)') if args.takeover else ''
    title_headers += '{:<20} '.format('DNS (A)') if args.dns else ''
    print(highlight(title_headers, 'gray'))

def subenum(args, targets):
    reporter = SubReporter(args)
    reporter.start()
    report_handler = SubHandler(reporter, args)
    print_headers(args)

    try:
        for target in targets:
            for module in args.modules.split(','):
                for mod_file in listdir(path.join(path.dirname(__file__), 'modules')):
                    if mod_file[-3:] == '.py' and mod_file[:-3] != '__init__':
                        mod_class = ModuleLoader.get_moduleClass(mod_file[:-3], args, target, report_handler)
                        if module == mod_class.name or module in mod_class.groups:
                            mod_class.start()
                while activeCount() > args.max_threads:
                    sleep(0.003)
        while activeCount() > 2:
            sleep(0.03)
        reporter.stop()
        return len(reporter.complete)

    except KeyboardInterrupt:
        reporter.stop()
        print("\n[!] Key Event Detected...\n")
        return len(reporter.complete)

    except Exception as e:
        print('SubScraper:main::{}'.format(e))
    finally:
        reporter.close()

def file_exists(parser, filename):
    if not filename:
        return
    if not path.exists(filename):
        parser.error("Input file not found: {}".format(filename))
    return [x.strip() for x in open(filename)]

def adjust_all(args):
    setattr(args, 'dns', True if args.all else args.dns)
    setattr(args, 'http', True if args.all or args.takeover else args.http)
    setattr(args, 'takeover', True if args.all else args.takeover)

def main():
    banner()
    args = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    options = args.add_argument_group("SubScraper Options")
    options.add_argument('-T',
                         dest='max_threads',
                         type=int, default=55,
                         help='Max threads for enumeration (Default: 55).'
    )
    options.add_argument('-t',
                         dest='timeout',
                         type=int,
                         default=25,
                         help='Timeout [seconds] for search threads (Default: 25).'
    )
    options.add_argument('-r',
                         dest='report',
                         type=str,
                         default='./subscraper_report.txt',
                         help="Output to specific file {txt*, csv}."
    )
    options.add_argument(dest='target',
                         nargs='+',
                         help='Target domain.'
    )
    mod = args.add_argument_group("Module Options")
    mod.add_argument('-L',
                     dest="list_modules",
                     action='store_true',
                     help='List SubScraper enumeration modules.'
    )
    mod.add_argument('-M',
                     dest="modules",
                     type=str,
                     default='all',
                     help="Execute module(s) by name or group (Default: all)."
    )
    mod.add_argument('-w',
                     dest='wordlist',
                     default=path.join(path.dirname(path.realpath(__file__)), 'resources', 'subdomains.txt'),
                     type=lambda x: file_exists(args, x), help='Custom wordlist for DNS brute force.'
    )

    mod.add_argument('--censys-id',
                      dest="censys_id",
                      type=str,
                      default=False,
                      help='Censys.io API ID.'
    )

    mod.add_argument('--censys-secret',
                      dest="censys_secret",
                      type=str,
                      default=False,
                      help='Censys.io API Secret.'
    )

    enum = args.add_argument_group("Enumeration Options")
    enum.add_argument('--dns',
                      dest="dns",
                      action='store_true',
                      help='Resolve DNS address for each subdomain identified.'
    )
    enum.add_argument('--http',
                      dest="http",
                      action='store_true',
                      help='Probe for active HTTP:80 & HTTPS:443 services.'
    )
    enum.add_argument('--takeover',
                      dest="takeover",
                      action='store_true',
                      help='Perform CNAME lookup & probe for HTTP(s) response.'
    )
    enum.add_argument('--all',
                      dest="all",
                      action='store_true',
                      help='Perform all checks on enumerated subdomains.'
    )

    if len(argv) < 2: args.print_help(); exit(0)
    if "-L" in argv: ModuleLoader.list_modules(); exit(0)
    args = args.parse_args()
    adjust_all(args)

    start_timer = datetime.now()
    count = subenum(args, target_parser(args.target))
    stop_timer = datetime.now()

    print(highlight("[*] Identified {} subdomain(s) in {}.".format(count, stop_timer - start_timer), 'gray'))
    print(highlight("[*] Subdomains written to {}.".format(args.report), 'gray'))


if __name__ == '__main__':
    main()
