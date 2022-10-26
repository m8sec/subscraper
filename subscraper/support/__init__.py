import os
import sys
import dns.resolver
from requests import get
from random import choice
from bs4 import BeautifulSoup
from ipparser import ipparser
from warnings import filterwarnings
from urllib3 import disable_warnings, exceptions
disable_warnings(exceptions.InsecureRequestWarning)
filterwarnings("ignore", category=UserWarning, module='bs4')

UA_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'resources', 'user_agents.txt')
USER_AGENTS = [line.strip() for line in open(UA_FILE)]

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

def get_request(link, timeout, headers=None):
    head = {
        'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Upgrade-Insecure-Requests': '1'}
    
    if headers:
        head.update(headers)
        
    try:
        return get(link, headers=head, verify=False, timeout=timeout)
    except:
        return False

def get_statuscode(resp):
    try:
        return resp.status_code
    except:
        return "Err"

def get_pagetitle(resp):
    try:
        soup = BeautifulSoup(resp.content, 'lxml')
        return(str(soup.title.string.split(",")[0]).strip().strip('\n'))
    except:
        return "Err"

def extract_header(header_field, resp):
    try:
        return resp.headers[header_field].strip()
    except:
        return "Err"

def web_info(sub, proto='http', csv_report=False):
    data = {}
    proto_schema = {'http': 'http://', 'https': 'https://'}
    resp = get_request(proto_schema[proto] + sub, 2)
    data['code'] = get_statuscode(resp)
    data['size'] = len(resp.text) if resp else 0
    data['title'] = get_pagetitle(resp) if csv_report else False
    data['server'] = extract_header('Server', resp) if csv_report else False
    return data

def target_parser(targets):
    hosts = []
    for x in targets:
        if x.lower() == "pipe":
            for y in sys.stdin:
                hosts = (hosts + ipparser(y.strip(), open_ports=True, exit_on_error=False, debug=False)) if y else hosts
        else:
            hosts = (hosts + ipparser(x.strip(), open_ports=True, exit_on_error=False, debug=False)) if x else hosts
    return hosts
