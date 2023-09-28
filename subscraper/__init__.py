#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Author: @m8sec
import os
import logging
import threading
from time import sleep
from datetime import datetime
from ipparser import ipparser

from taser import logx
from taser.dns import DNSutils
from taser.utils import delimiter2list

from subscraper.utils import ConfigParser
from subscraper.reporter import SubReportQ
from subscraper.modules import ModuleLoader
from subscraper.cli import banner, cmd_parser
logging.getLogger("taser").setLevel(logging.WARNING)


def do_stuff(args, targets, config):
    reporter = SubReportQ(args)
    reporter.start()
    logging.debug('Started Subdomain Reporting Thread')

    try:
        for target in targets:
            for module in delimiter2list(args.modules):
                for mod_file in os.listdir(os.path.join(os.path.dirname(__file__), 'modules')):
                    if mod_file[-3:] == '.py' and mod_file[:-3] != '__init__':
                        mod_class = ModuleLoader.get_moduleClass(mod_file[:-3], args, target, reporter, config)
                        if module == mod_class.name or args.modules == '*':
                            mod_class.start()

                        while threading.activeCount() > args.threads:
                            sleep(0.003)

            sub_brute(target, args, reporter)

        while threading.activeCount() > 2:
            sleep(0.05)
        reporter.stop()

    except KeyboardInterrupt:
        reporter.stop()
        logx.color('\n[!] Key Event Detected, closing...', fg='yellow', windows=args.no_color)
        return len(reporter.sub_cache)

    except Exception as e:
        logging.debug('Subhandler Err::{}'.format(e))
    finally:
        return len(reporter.sub_cache)


def sub_brute(host, args, reporter):
    if args.module_only:
        return

    with open(args.wordlist) as f:
        for s in f:
            th = threading.Thread(target=sub_resolver, args=('{}.{}'.format(s.strip("\n"), host), args, reporter))
            th.daemon = True
            th.start()
            while threading.activeCount() > args.threads:
                sleep(0.03)


def sub_resolver(host, args, reporter):
    query = DNSutils.query(host, 'A', ns=args.ns, timeout=args.timeout)
    if query:
        reporter.add({'Name': host, 'Source': 'dns-brute', 'DNS': query})


def print_headers(args):
    title_headers = '{:<15} {:<35} '.format('Source', 'Subdomain')
    title_headers += '{:<10}   '.format('HTTP/HTTPS') if args.http else ''
    title_headers += '{:<35} '.format('Takeover (CNAME)') if args.takeover else ''
    title_headers += '{:<20} '.format('DNS (A)') if args.dns else ''
    logx.color(title_headers, fg='gray', windows=args.no_color)


def main():
    args = cmd_parser()
    banner(args) if not args.silent else False

    ModuleLoader.list_modules(args) if args.list_modules else False
    logx.setup_debug_logger() if args.debug else False
    config = ConfigParser(args)


    start_timer = datetime.now()
    count = do_stuff(args, ipparser(args.domain), config)
    stop_timer = datetime.now()

    if not args.silent:
        logx.color("[*] Identified {} subdomain(s) in {}.".format(count, stop_timer - start_timer), fg='gray', windows=args.no_color)
        logx.color("[*] Subdomains written to {}.".format(args.report), fg='gray', windows=args.no_color) if args.report else False


if __name__ == '__main__':
    main()
