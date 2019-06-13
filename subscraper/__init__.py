#!/usr/bin/env python3

# Author: @m8r0wn
# License: GPL-3.0

import argparse
from os import path
import dns.resolver
from re import compile
from time import sleep
from requests import get
from random import choice
from bs4 import BeautifulSoup
from datetime import datetime
from sys import exit, argv, stdout
from threading import Thread, activeCount
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)

################################################
# Global Vars
################################################
# List of user-agents to evade detection during HTTP requests
UA_FILE = path.join(path.dirname(path.realpath(__file__)), 'resources/user_agents.txt')
USER_AGENTS = [line.strip() for line in open(UA_FILE)]
# Global Dict for Subdomain Collection
FOUND = {}


################################################
# Method 5: DNS Dumpster
################################################
def dns_dumpster(target, timeout):
    link = "https://api.hackertarget.com/hostsearch/?q={}"
    try:
        resp = get_request(link.format(target), timeout)
        if resp.text:
            for line in resp.text.splitlines():
                sub = dd_extract_sub(line)
                if sub:
                    subdomain_output(sub, "DNSdumpster")
    except:
        pass

def dd_extract_sub(line):
    try:
        return line.split(",")[0]
    except:
        return False


################################################
# Method 4: Censys.io Cert Lookup (API Required)
################################################
class CensysIO():
    def __init__(self, api, secret):
        self.api = api
        self.secret = secret
        self.thread_count = 0
        self.running = True

    def timer(self, time):
        # Exit on timeout
        sleep(time)
        self.running = False

    def search(self, target, timeout):
        try:
            # Don't import until required
            import censys.certificates
            # Start timeout thread
            Thread(target=self.timer, args=(timeout,), daemon=True).start()
            # Start Search
            certs = censys.certificates.CensysCertificates(api_id=self.api, api_secret=self.secret)
            resp = certs.search("parsed.names: {}".format(target), fields=['parsed.names'])
            for line in resp:
                # Return on timeout
                if not self.running:
                    return
                # Threading to parse results
                self.thread_count += 1
                Thread(target=self.parser, args=(target, line,)).start()
                # Sleep while max threads reached
                while self.thread_count >= 2:
                    sleep(0.001)
            while self.thread_count > 0:
                sleep(0.001)
        except:
            stdout.write("\033[1;33m[!]\033[1;m \033[1;30mCensys.IO Error, verify API Key/Secret\033[1;m\n")

    def parser(self, target, line):
        #for line in resp:
        try:
            for sub in line['parsed.names']:
                if target in sub and "*" not in sub:
                    subdomain_output(sub, 'Censys.io')
        except:
            pass
        self.thread_count -= 1

################################################
# Method 3: Scrape Search Engine Results
################################################
def search_thread(source, target, timeout):
    # Scrape search engine results for subdomains
    for link in SiteSearch().search(source, target, timeout):
        try:
            sub = link.split("/")[2].strip().lower()
            if ".{}".format(target) in sub:
                subdomain_output(sub, "Search-" + source.title())
        except:
            pass

class SiteSearch():
    # Use search engine(s) to search for links associated with a single site
    URL = {'google': 'https://www.google.com/search?q=site:{}&num=100&start={}',
           'bing': 'http://www.bing.com/search?q=site:{}&first={}'}

    def __init__(self):
        self.links = []     # List of all links found during search
        self.running = True

    def timer(self, time):
        # Exit search on timeout
        sleep(time)
        self.running = False

    def search(self, search_engine, site, timeout):
        self.running = True     # Define search as "running" after init(), not used in DNS_Enum
        Thread(target=self.timer, args=(timeout,), daemon=True).start() # Start timeout thread
        self.search_links = 0   # Total Links found by search engine
        self.site_links = 0     # Total links found by search engine w/ our domain in URL
        found_links = 0         # Local count to detect when no new links are found

        while self.running:
            # End on timeout OR when no more links are found with site in URL
            if self.search_links > 0 and found_links == self.site_links:
                return self.links
            found_links = self.site_links
            # Catch failed connection attempts
            try:
                self.site_search(search_engine, self.search_links, site)
            except Exception as e:
                pass
        return self.links

    def site_search(self, search_engine, count, site):
        # Regex to extract link
        HTTP = compile("http([^\)]+){}([^\)]+)".format(site))
        HTTPS = compile("https([^\)]+){}([^\)]+)".format(site))
        # Search
        for link in get_links(get_request(self.URL[search_engine].format(site, count), 3)):
            if search_engine not in link.lower():
                self.search_links += 1
                if HTTP.match(link) or HTTPS.match(link):
                    self.site_links += 1
                    if link not in self.links:
                        self.links.append(link)

def get_links(raw_response):
    # Returns a list of links from raw requests input
    links = []
    soup = BeautifulSoup(raw_response.content, 'html.parser')
    for link in soup.findAll('a'):
        try:
            links.append(str(link.get('href')))
        except:
            pass
    return links

################################################
# Method 2: VirusTotal Lookup
################################################
# [Work in Progress] site changed: no longer working :(
"""
def virustotal_thread(target):
    # Get subdomains using VirusTotal (No API)
    count = 0
    try:
        resp = get_request("https://www.virustotal.com/gui/domain/{}/relations".format(target), 5)
        print(resp.text)
        data = resp.content.decode('utf-8').splitlines()
        for line in data:
            count += 1
            # Div is before identified subdomain in HTML
            if '<div class="enum ">' in line:
                sub = vt_extract_sub(target, data[count])
                subdomain_output(sub, "VirusTotal")
    except:
        pass

def vt_extract_sub(target, html):
    # Extract subdomain from VirusTotal lookup HTML
    try:
        if target in html:
            return html.split("/en/domain/")[1].split("/information")[0]
    except:
        return False
"""

################################################
# Method 1: DNS Brute Force
################################################
def brute_thread(s, target):
    # Subdomain Enumeration through DNS brute force
    try:
        sub = s + '.' + target
        dns_query = dns_lookup(sub, 'A')
        if dns_query and sub not in FOUND:
            subdomain_output(sub, 'DNS-Brute')
    except KeyboardInterrupt:
        print("\n[!] Key Event Detected...\n\n")
        exit(0)
    except Exception as e:
        stdout.write("\033[1;30m{:<13}\t{:<25}\033[1;m\n".format('[Error-03]', str(e)))

################################################
# HTTP(S) Requests & DNS Queries
################################################
def dns_lookup(target, lookup_type):
    # User defined DNS record lookup
    results = []
    try:
        res = dns.resolver.Resolver()
        res.timeout = 2
        res.lifetime = 2
        dns_query = res.query(target, lookup_type)
        dns_query.nameservers = ['8.8.8.8', '8.8.4.4']
        # Display Data
        for name in dns_query:
            results.append(str(name))
    except:
        pass
    return results

def get_request(link, timeout):
    # HTTP(S) GET request w/ user defined timeout
    head = {
        'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'}
    return get(link, headers=head, verify=False, timeout=timeout)

################################################
# Terminal Output
################################################
def subdomain_output(sub, source):
    if sub not in FOUND and sub.count('.') > 1:
        FOUND[sub] = '' # Placeholder
        http = sub_respcode(sub)
        dns = dns_lookup(sub, 'A')
        FOUND[sub] = dns, http
        stdout.write("\033[1;34m{:<13}\033[1;m\t{:<25}\t({:<3}/{:<3})\t{}\n".format('[{}]'.format(source), sub, http[0], http[1], dns))

def display_results(outfile, target):
    # Cycle through final results & print/report
    dedup = []
    if outfile:
        openFile = open('{}_subs.csv'.format(target), 'a')
        openFile.write("\"Subdomain\",\"IP\",\"HTTP Code\",\"HTTPS Code\",\n")

    stdout.write("\n\033[1;30m[*] Results\033[1;m\n")
    for k, v in FOUND.items():
        # Check for duplicates
        if k not in dedup:
            dedup.append(k)
            print(k)

        if outfile:
            # Print hosts with multiple IP addresses (one per line)
            if v[0]:
                for x in v[0]:
                    openFile.write("\"{}\",\"{}\",\"{}\",\"{}\",\n".format(k, x, v[1][0], v[1][1]))
            else:
                openFile.write("\"{}\",\"{}\",\"Err\",\"Err\",\n".format(k, x))
    if outfile:
        openFile.close()

def takeover_check(target):
    stdout.write("\n\033[1;30m[*] Subdomain Takeover Check\033[1;m\n")
    stdout.write("\033[1;30m{:<25}\t({:<9})\t{}\033[1;m\n".format('Subdomain', 'http/https', 'CNAME Record'))
    for k, v in FOUND.items():
        # For each subdomain found perform cname lookup
        for x in dns_lookup(k, 'CNAME'):
            # Check target domain not in output (aka redirects)
            if target not in x:
                stdout.write("{:<25}\t({:<3}/{:<3})\t{}\n".format(k, v[1][0], v[1][1], x))

################################################
# Logging / Support Functions
################################################
def file_exists(parser, filename):
    # Used with argparse to check input file exists
    if not path.exists(filename):
        parser.error("Input file not found: {}".format(filename))
    return [x.strip() for x in open(filename)]

def sub_respcode(sub):
    # Return list of HTTP/HTTPS response code for subdomain
    results = []
    try:
        results.append(get_request("http://"+sub, 2).status_code)
    except:
        results.append("Err")

    try:
        results.append(get_request("https://"+sub, 2).status_code)
    except:
        results.append("Err")
    return results

################################################
# Main
################################################
def start(args):
    try:
        stdout.write("\n\033[1;30m{:<13}\t{:<25}\t({:<9})\t{}\033[1;m\n".format('[Source]', 'Subdomain', 'http/https', 'DNS Resolution'))

        # Launch Subdomain Enumeration Threads
        if args.brute:
            if args.censys_api and args.censys_secret:
                Thread(target=CensysIO(args.censys_api, args.censys_secret).search, args=(args.target, args.timeout,), daemon=True).start()
            Thread(target=dns_dumpster, args=(args.target, args.timeout,), daemon=True).start()
            #Thread(target=virustotal_thread, args=(args.target,), daemon=True).start()
            Thread(target=search_thread, args=('bing', args.target, args.timeout,), daemon=True).start()
            Thread(target=search_thread, args=('google', args.target, args.timeout,), daemon=True).start()

        if args.scrape:
            for s in args.sublist:
                Thread(target=brute_thread, args=(s, args.target,), daemon=True).start()
                # Sleep while max threads reached
                while activeCount() > args.max_threads:
                    sleep(0.001)

        # Sleep while threads still active
        while activeCount() > 1:
            sleep(0.001)

        # Return on no results
        if not FOUND:
            return

        # Print/Log Results
        display_results(args.outfile, args.target)

        # Subdomain Takeover Check
        takeover_check(args.target)
    except KeyboardInterrupt:
        print("\n[!] Key Event Detected...\n\n")
        exit(0)

    except Exception as e:
        stdout.write("\033[1;30m{:<13}\t{:<25}\033[1;m\n".format('[Error-01]', str(e)))

def main():
    VERSION = "2.0.1"
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

    args.add_argument('-s', dest="scrape", action='store_false', help="Only use internet to find subdomains")
    args.add_argument('-b', dest="brute", action='store_false', help="Only use DNS brute forcing to find subdomains")
    args.add_argument('-csv', dest='outfile', action='store_true', help='Create CSV output file')
    args.add_argument('-t', dest='max_threads', type=int, default=10, help='Max threads (Default: 10)')
    args.add_argument('-T', dest='timeout', type=int, default=25, help='Timeout [seconds] for search threads (Default: 25)')
    args.add_argument('-w', dest="sublist", default=path.join(path.dirname(path.realpath(__file__)), 'resources/subdomains.txt'),type=lambda x: file_exists(args, x), help='Custom subdomain wordlist')
    args.add_argument('--censys-api', dest='censys_api', type=str, default='', help='Add Censys.io API Key')
    args.add_argument('--censys-secret', dest='censys_secret', type=str, default='', help='Add Censys.io Secret')
    args.add_argument(dest='target', nargs='+', help='Target domain')

    args = args.parse_args()

    # Setup output file and target
    args.target = args.target[0]

    # Start Enumeration
    start_timer = datetime.now()
    start(args)

    # End
    stop_timer = datetime.now()
    stdout.write("\n\033[1;30m[*] Identified {} subdomain(s) in {}\n\033[1;m\n".format(len(FOUND), stop_timer - start_timer))

if __name__ == '__main__':
    main()