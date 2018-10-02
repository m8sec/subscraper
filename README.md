# SubScraper v1.1.0

SubScraper uses DNS brute force, Google & Bing scraping, and Virus Total to enumerate subdomains without an API. Written in Python3, SubScraper performs HTTP(S) requests and DNS "A" record lookups during the enumeration process to validate discovered subdomains. This provides further information to help prioritize targets and aid in potential next steps. Post-Enumeration, "CNAME" lookups are displayed to identify subdomain takeover opportunities. 

![](https://user-images.githubusercontent.com/13889819/46205430-90ac0e00-c2ee-11e8-801c-626b066448ca.png)

### Install
```bash
pip3 install -r requirements.txt
```
### Usage
```bash
python3 subscraper.py example.com
python3 subscraper.py -t 5 -o csv example.com
```

### Options
```
  -s              Only use internet to find subdomains
  -b              Only use DNS brute forcing to find subdomains
  -o OUTFILE      Define output file type: csv/txt (Default: None)
  -t MAX_THREADS  Max threads (Default: 10)
  -w SUBLIST      Custom subdomain wordlist
```
