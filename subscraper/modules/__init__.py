import importlib

MODULES = {
        # File Name      Class Name
        'dns_brute'    : 'DNSBrute',
        'web_scraper'  : 'WebScraper',
        'censys_io'    : 'CensysIO',
        'dns_dumpster' : 'DNSDumpster'
    }

def get_module_class(name):
    cname = MODULES[name]
    modname = '.'.join([__name__, name])
    module = importlib.import_module(modname)
    return getattr(module, cname)