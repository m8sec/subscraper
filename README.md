# SubScraper

<p align="left">
  <a href="https://github.com/m8r0wn/subscraper/tree/master/subscraper/modules">
    <img src="https://img.shields.io/badge/Call%20for%20Modules-OPEN-green?style=plastic"/>
  </a>&nbsp;
  <a href="https://www.twitter.com/m8r0wn">
      <img src="https://img.shields.io/badge/Twitter-@m8r0wn-blue?style=plastic&logo=twitter"/>
  </a>&nbsp;
  <a href="https://github.com/sponsors/m8r0wn">
      <img src="https://img.shields.io/badge/Sponsor-GitHub-green?style=plastic&logo=github"/>
  </a>&nbsp;
  <a href="https://www.paypal.com/donate?hosted_button_id=68W8UCUF4SMTCn">
      <img src="https://img.shields.io/badge/Donate-PayPal-blue?style=plastic&logo=paypal"/>
  </a>&nbsp;
</p>

SubScraper is a subdomain enumeration tool that uses a variety of techniques to find potential subdomains of a given target. This is especially helpful during penetration testing or bug bounty hunting to uncover additional attack surfaces. Depending on the the CMD args used, SubScraper can perform DNS lookups and HTTP/S requests during the enumeration process to help prioritize targets and aid in potential next steps.

#### Key Features

- Modular design makes it easy to add new techniques/sources.
- Various levels of enumeration for additional data gathering.
- Allows for multiple target inputs, or read targets from txt file.
- Multi-threaded for additional speed.

![Screenshot](https://user-images.githubusercontent.com/13889819/59461972-a287ff80-8df0-11e9-9971-fb1cdf39471f.png)

#### Enumeration Techniques

- DNS brute-force with built-in or custom wordlist
- Censys.io _(API Key required [https://search.censys.io/register](https://search.censys.io/register))_
- Archive.org _(Wayback Machine)_
- Google & Bing web scraping
- DNS Dumpster
- DNSBufferOverRun
- ThreatCrowd
- CRT.SH

## Install

```bash
git clone https://github.com/m8r0wn/subscraper
cd subscraper
python3 setup.py install
```

## Usage

#### Subdomain Enumeration

- The most basic usage of SubScraper will use bruteforce and web scraping techniques to find all available subdomains of the given target(s). Once complete, a "subscraper_report.txt" file will be created in the current directory listing all subdomains discovered:

```bash
subscraper example.com
```

- By Changing the level of enumeration (1-3), users can increase the data displayed for each subdomain:
  - 1 - Show all enumerated subdomains _(Default & Fastest)_
  - 2 - Used DNS to determine if subdomain is active and only display live hosts
  - 3 - Perform live check and get HTTP/S response code for each subdomain

```bash
subscraper --enum 2 example.com
subscraper -e 3 example.com
```

#### Subdomain Takeover

Once the output report is complete, users can check for subdomain takeover opportunities using the following command. This will perform CNAME lookups on all potential targets and display the results:

```bash
subscraper --takeover subscraper_report.txt
```

## All Options

```
SubScraper Options:
  -T MAX_THREADS       Max threads
  -t TIMEOUT           Timeout [seconds] for search threads (Default: 25)
  -o REPORT            Output to specific file
  target               Target domain (Positional)

Enumeration Options:
  -s                   Only use scraping techniques
  -b                   Only use DNS brute force
  -w SUBLIST           Custom subdomain wordlist
  -e LVL, --enum LVL   Enumeration Level:
                       1: Subdomain Only (Default)
                       2: Live subdomains, verified by DNS
                       3: Live check & get HTTP/S response codes

Enumeration Advanced:
  --censys-api API     Censys.io API Key
  --censys-secret KEY  Censys.io Secret

Subdomain TakeOver:
  --takeover           Perform takeover check on list of subs
```
