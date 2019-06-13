# SubScraper

SubScraper uses DNS brute force, Google & Bing scraping, and DNSdumpster to enumerate subdomains of a given host. Written in Python3, SubScraper performs HTTP(S) requests and DNS "A" record lookups during the enumeration process to validate discovered subdomains. This provides further information to help prioritize targets and aid in potential next steps. Post-Enumeration, "CNAME" lookups are displayed to identify subdomain takeover opportunities.

Users also have the option of adding their Censys.io API Key & Secret in the command line arguments. This will allow subdomain enumeration using the Censys.io SSL Cert database. Create an account to get a free API key here: https://censys.io/register.

![](https://user-images.githubusercontent.com/13889819/59461972-a287ff80-8df0-11e9-9971-fb1cdf39471f.png)

### Install
```bash
git clone https://github.com/m8r0wn/subscraper
cd subscraper
python3 setup.py install
```

### Usage
```bash
subscraper example.com
subscraper -csv -T 35 example.com
```

### Options
```
  -s                    Only use internet to find subdomains
  -b                    Only use DNS brute forcing to find subdomains
  -csv                  Create CSV output file
  -t MAX_THREADS        Max threads (Default: 10)
  -T TIMEOUT            Timeout [seconds] for search threads (Default: 25)
  -w SUBLIST            Custom subdomain wordlist
  --censys-api          Add CensysIO API Key
  --censys-secret       Add CensysIO Secret
```
