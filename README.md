# SubScraper

<p align="center">
  <a href="https://github.com/m8r0wn/subscraper/tree/master/subscraper/modules">
    <img src="https://img.shields.io/badge/Call%20for%20Modules-OPEN-green?style=plastic"/>
  </a>&nbsp;
  <a href="https://www.twitter.com/m8r0wn">
      <img src="https://img.shields.io/badge/Twitter-@m8r0wn-blue?style=plastic&logo=twitter"/>
  </a>&nbsp;
  <a href="https://github.com/sponsors/m8r0wn">
      <img src="https://img.shields.io/badge/Sponsor-GitHub-red?style=plastic&logo=github"/>
  </a>
  <br>
    <a href="https://github.com/m8r0wn/subscraper#subscraper">Overview</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8r0wn/subscraper#usage">Usage</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8r0wn/subscraper#contribute">Contribute</a>
  <br>
</p>

:boom: **v3.0 now available!** :boom:

SubScraper is a fast subdomain enumeration tool that uses a variety of techniques to find subdomains of a given target. Subdomain enumeration is especially helpful during penetration testing and bug bounty hunting to uncover an organization's attack surface.

Depending on the CMD arguments applied, SubScraper can resolve DNS names, request HTTP(S) information, and perform CNAME lookups for takeover opportunities during the enumeration process. This can help identify next steps and discover patterns for exploitation.  

#### Key Features

- Modular design makes it easy to add new techniques/sources.
- Various levels of enumeration for additional data gathering.
- Allows for multiple target inputs or read targets from txt file.
- Windows CLI compatibility. 
- Generate output files in `.txt` or `.csv` format.

<p align="center">
<img width="942" alt="demo" src="https://user-images.githubusercontent.com/13889819/174695175-78ded7ff-6d27-4bda-8ebd-0c51ef1def0f.png">
</p>

## Install
The following can be used to install SubScraper on Windows, Linux, & MacOs:

```bash
git clone https://github.com/m8r0wn/subscraper
cd subscraper
python3 setup.py install
```

## Usage
#### Command Line Args
```
SubScraper Options:
  -T MAX_THREADS  Max threads for enumeration (Default: 55).
  -t TIMEOUT      Timeout [seconds] for search threads (Default: 25).
  -r REPORT       Output to specific file {txt*, csv}.
  target          Target domain.

Module Options:
  -L              List SubScraper enumeration modules.
  -M MODULES      Execute module(s) by name or group (Default: all).
  -w WORDLIST     Custom wordlist for DNS brute force.

Enumeration Options:
  --dns           Resolve DNS address for each subdomain identified.
  --http          Probe for active HTTP:80 & HTTPS:443 services.
  --takeover      Perform CNAME lookup & probe for HTTP(s) response.
  --all           Perform all checks on enumerated subdomains.
```

#### Modules
Modules can be executed by name or by module groups:
```
  Module Name       Description

  archiveorg           - Use archive.org to find subdomains.
  certsh               - Subdomains enumeration using cert.sh.
  dnsbrute             - DNS bruteforce.
  threatcrowd          - Threadcrowd.org subdomain enumeration.
  dnsdumpster          - Use DNS dumpster to enumerate subdomains.
  bufferoverrun        - Bufferover.run passive enumeration.
  search               - Subdomain enumeration via search engine scraping.
  censysio             - Gather subdomains through Censys SSL cert Lookups.
    |_APIKEY                   Censys.io API Key              (Required:True)
    |_SECRET                   Censys.io API Secret           (Required:True)
```
**Module Groups**
  * *all* - Execute all modules (Default).
  * *brute* - Only execute DNS brute force techniques.
  * *scrape* - Only execute web scraping techniques. 

#### Example Usage
```
subscraper example.com
subscraper targets.txt
cat targets.txt | subscraper pipe
subscraper -all -r enumeration.csv example.com
subscraper -M brute -w mywords.txt example.com
subscraper -M censys_io -o 'APIKEY=abc123,SECRET=xyz456' example.com
```

#### Execution Notes
* SubScraper only uses **PASSIVE** enumeration techniques unless the `--http` or `--all` arguments are applied. 
* API keys are required for the `censys_io` module, register for free at [censys.io/register](https://search.censys.io/register).
* When output data to `.csv` report AND `--http` or `-all` args applied, additional data such as page size, title and Server headers are reported. 

## Contribute
Contribute to the project by:
* Downloading and sharing the tool!
* Create an issue to report new enumeration techniques or, better yet, develop a module and initiate a PR.
