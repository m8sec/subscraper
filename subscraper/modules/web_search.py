import threading
from re import compile
from time import sleep
from threading import Thread
from bs4 import BeautifulSoup
from subscraper.support import get_request

class SubModule(threading.Thread):
    name = 'search'
    description = "Subdomain enumeration via search engine scraping."
    author = '@m8r0wn'
    groups = ['all', 'scrape']
    args = {}

    def __init__(self, args, target, print_handler):
        threading.Thread.__init__(self)
        self.daemon = True

        self.search_sites = ['google', 'bing']
        self.handler = print_handler
        self.target = target
        self.timeout = args.timeout

    def run(self):
        # Launch subthreads per search site:
        for search_engine in self.search_sites:
            Thread(target=self.launcher, args=(search_engine,)).start()

    def launcher(self, search_engine):
            for link in SearchScraper().search(search_engine, self.target, self.timeout):
                try:
                    sub = link.split("/")[2].strip().lower()
                    if ".{}".format(self.target) in sub:
                        self.handler.sub_handler({'Name': sub, 'Source': '{}-search'.format(search_engine)})
                except:
                    pass

class SearchScraper():
    URL = {'google': 'https://www.google.com/search?q=site:{}&num=100&start={}',
           'bing': 'http://www.bing.com/search?q=site:{}&first={}'}

    def __init__(self):
        self.links   = []
        self.running = True

    def timer(self, time):
        # Exit search on timeout
        sleep(time)
        self.running = False

    def search(self, search_engine, site, timeout):
        Thread(target=self.timer, args=(timeout,), daemon=True).start() # Start timeout thread
        self.running        = True  # Define search as "running" after init(), not used in DNS_Enum
        self.search_links   = 0     # Total Links found by search engine
        self.site_links     = 0     # Total links found by search engine w/ our domain in URL
        found_links         = 0     # Local count to detect when no new links are found

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
    # HTLM Parser to extract links for search engine scraping
    links = []
    soup = BeautifulSoup(raw_response.content, 'html.parser')
    for link in soup.findAll('a'):
        try:
            links.append(str(link.get('href')))
        except:
            pass
    return links
