import os
import dns.resolver
from requests import get
from random import choice
from bs4 import BeautifulSoup
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)

UA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources/user_agents.txt')
USER_AGENTS = [line.strip() for line in open(UA_FILE)]

def get_request(link, timeout):
    head = {
        'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'}
    return get(link, headers=head, verify=False, timeout=timeout)


def get_links(raw_response):
    # HTLM Parser to extract links
    links = []
    soup = BeautifulSoup(raw_response.content, 'html.parser')
    for link in soup.findAll('a'):
        try:
            links.append(str(link.get('href')))
        except:
            pass
    return links


def dns_lookup(target, lookup_type):
    results = []
    try:
        res = dns.resolver.Resolver()
        res.timeout = 2
        res.lifetime = 2
        dns_query = res.query(target, lookup_type)
        dns_query.nameservers = ['1.1.1.1', '8.8.8.8']
        for name in dns_query:
            results.append(str(name))
    except:
        pass
    return results

def respcode(sub, proto='http'):
    protocol = {
                 'http'  : 'http://',
                 'https' : 'https://'
               }
    try:
        return get_request(protocol[proto] + sub, 2).status_code
    except:
        return "Err"
