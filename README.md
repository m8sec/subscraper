# SubScraper

<p align="center">
  <a href="https://www.twitter.com/m8sec">
        <img src="https://img.shields.io/badge/Twitter-@m8sec-blue?style=plastic&logo=twitter"/>
    </a>&nbsp;
    <a href="/LICENSE">
        <img src="https://img.shields.io/badge/License-BSD_3--Clause-green?style=plastic&logo=github"/>
    </a>&nbsp;
    <a href="https://github.com/sponsors/m8sec">
        <img src="https://img.shields.io/badge/Sponsor-GitHub-red?style=plastic&logo=github"/>
    </a>&nbsp;
  <br>
    <a href="https://github.com/m8sec/subscraper#subscraper">Overview</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8sec/subscraper#usage">Usage</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8sec/subscraper#contribute">Contribute</a>
  <br>
</p>

SubScraper is a subdomain enumeration tool that uses a variety of techniques to find subdomains of a given target. Subdomain enumeration is especially helpful during penetration testing and bug bounty hunting to uncover an organization's attack surface.

Depending on the CMD arguments applied, SubScraper can resolve DNS names, request HTTP(S) information, and perform CNAME lookups for takeover opportunities during the enumeration process. This can help identify next steps and discover patterns for exploitation.  

#### Key Features

- Modular design makes it easy to add new techniques/sources.
- Various levels of enumeration for additional data gathering.
- Allows for multiple target inputs, reading from `.txt` or STDIN.
- Windows CLI compatibility. 
- Generate output files in `.txt` or `.csv` format.

<p align="center">
<img width="942" alt="demo" src="https://github.com/m8sec/subscraper/assets/13889819/c8503198-7759-4123-b921-28a74b773e7b">
</p>


## Installation
### Python
The following can be used to install SubScraper on Windows, Linux, & MacOS:

```bash
git clone https://github.com/m8sec/subscraper
cd subscraper
pip3 install -r requirements.txt
```

### Poetry
Install and run SubScraper using [Poetry](https://python-poetry.org/docs/#installing-with-the-official-installer):
```bash
git clone https://github.com/m8sec/subscraper
cd subscraper
poetry install
poetry run subscraper -h
```

### Docker
You can build a docker image and run subscraper from Docker:
```
git clone https://github.com/m8sec/subscraper
cd subscraper
docker build -t m8sec/subscraper .

# Display help
docker run --rm m8sec/subscraper

# Example scanning a site
docker run --rm m8sec/subscraper -d example.com
```

## Configuration File
Use the configuration file at `~/.config/subscraper/config.json` to store API keys for easy reuse. 

If updating to a newer version after v4.0.0, use the `-update` argument to pull a new copy of the config file to ensure compatability. Note, this will remove any existing entries.


### Modules
A full list of modules can be found using the `-ls` command line argument:
```
Module Name            Description

bevigil              - BeVigil OSINT API for scraping mobile application for subdomains (API Key Req)
crt.sh               - Subdomains enumeration using cert.sh.
dnsrepo              - Parse dnsrepo.noc.org without an API key - 150 result limit
certspotter          - Use Certspotter API to collect subdomains
chaos                - Project Discovery's Chaos (API Key Req)
bufferover           - Query Bufferover.run API (API Key Req)
alienvault           - Find subdomains using AlienVault OTX
archive              - Use archive.org to find subdomains.
dnsdumpster          - Use DNS dumpster to enumerate subdomains.
censys.io            - Gather subdomains through censys.io SSL cert Lookups. (API Key Req)
```

## Usage
### Command Line Args
```
SubScraper Options:
  -debug                Enable debug logging
  -update               Update config file (Will remove existing entries)
  -config CONFIG        Override default config location
  -silent               Show subdomains only in output
  -threads THREADS, -T THREADS    Max threads for enumeration (65*).
  -t TIMEOUT                      set connection timeouts (3*)
  -d DOMAIN, --domain DOMAIN      Target domain input (domain, .txt, STDIN, etc.

Module Options:
  -ls                   List SubScraper enumeration modules.
  -m MODULES            Execute module(s) by name or group (all*).
  -module-only          Execute modules only not brute force

Bruteforce Options:
  -w WORDLIST           Custom wordlist for DNS brute force.
  -ns NS                Comma separated nameservers to use

Enumeration Options:
  -r, -resolve          Resolve IP address for each subdomain identified.
  -c, -cname            Perform CNAME lookup for subdomain takeover checks
  -http                 Probe for active HTTP services.
  -http-port HTTP_PORT  HTTP ports to check, comma separated (80,443*)

Output Options:
  -nc, -no-color        Disable color output
  -active               Only report active subdomains with resolved IP
  -csv                  Create CSV output report
  -o REPORT             Output file
```

### Example Inputs
```
python3 subscraper.py -d example.com -resolve -http -module-only
python3 subscraper.py -d example.com -cname -m none -o sub_report.csv -csv
cat domains.txt | python3 subscraper.py -active -silent
```

## Contribute
Contribute to the project by:
* Like and share the tool!
* Create an issue to report new enumeration techniques
* OR, better yet, develop a module and initiate a PR.
