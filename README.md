# SubScraper

<p align="center">
  <a href="https://github.com/m8sec/subscraper/tree/master/subscraper/modules">
    <img src="https://img.shields.io/badge/Call%20for%20Modules-OPEN-green?style=plastic"/>
  </a>&nbsp;
  <a href="https://www.twitter.com/m8sec">
      <img src="https://img.shields.io/badge/Twitter-@m8sec-blue?style=plastic&logo=twitter"/>
  </a>&nbsp;
  <a href="https://github.com/sponsors/m8sec">
      <img src="https://img.shields.io/badge/Sponsor-GitHub-red?style=plastic&logo=github"/>
  </a>
  <br>
    <a href="https://github.com/m8sec/subscraper#subscraper">Overview</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8sec/subscraper#usage">Usage</a>
    &nbsp;&nbsp;:small_blue_diamond:&nbsp;&nbsp;
    <a href="https://github.com/m8sec/subscraper#contribute">Contribute</a>
  <br>
</p>

:boom: **v3.0 now available!** :boom:

SubScraper is a fast subdomain enumeration tool that uses a variety of techniques to find subdomains of a given target. Subdomain enumeration is especially helpful during penetration testing and bug bounty hunting to uncover an organization's attack surface.

Depending on the CMD arguments applied, SubScraper can resolve DNS names, request HTTP(S) information, and perform CNAME lookups for takeover opportunities during the enumeration process. This can help identify next steps and discover patterns for exploitation.  

#### Key Features

- Modular design makes it easy to add new techniques/sources.
- Various levels of enumeration for additional data gathering.
- Allows for multiple target inputs or read targets from `.txt` file.
- Windows CLI compatibility. 
- Generate output files in `.txt` or `.csv` format.

<p align="center">
<img width="942" alt="demo" src="https://user-images.githubusercontent.com/13889819/174695175-78ded7ff-6d27-4bda-8ebd-0c51ef1def0f.png">
</p>

## Install
The following can be used to install SubScraper on Windows, Linux, & MacOs:

```bash
git clone https://github.com/m8sec/subscraper
cd subscraper
python3 setup.py install
```

## Usage
#### Command Line Args
```
SubScraper Options:
  -T MAX_THREADS        Max threads for enumeration (Default: 55).
  -t TIMEOUT            Timeout [seconds] for search threads (Default: 25).
  -r REPORT             Output to specific file {txt*, csv}.
  target                Target domain.

Module Options:
  -L                    List SubScraper enumeration modules.
  -M MODULES            Execute module(s) by name or group (Default: all).
  -w WORDLIST           Custom wordlist for DNS brute force.
  --censys-id CENSYS_ID             Censys.io API ID.
  --censys-secret CENSYS_SECRET     Censys.io API Secret.

Enumeration Options:
  --dns                 Resolve DNS address for each subdomain identified.
  --http                Probe for active HTTP:80 & HTTPS:443 services.
  --takeover            Perform CNAME lookup & probe for HTTP(s) response.
  --all                 Perform all checks on enumerated subdomains.
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
  censys               - Gather subdomains through censys.io SSL cert Lookups.
    |_API_ID                   Censys.io API ID               (Required:True)
    |_API_SECRET               Censys.io API Secret           (Required:True)
  bevigil              - Gather subdomains through bevigil.com mobile app scan data
    |_API_Key                  BeVigil API Key                (Required:True)
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
subscraper -M censys --censys-id abc123 --censys-secret xyz456 example.com
```

#### Execution Notes
* SubScraper only uses **PASSIVE** enumeration techniques unless `all, http, takeover` arguments are applied. 
* API keys are required for the `censys` module, register for free at [censys.io/register](https://search.censys.io/register).
* `.txt` reports will only include subdomains. 
* `.csv` reports, when paired with cmd args `all, http, takeover`, will provide additional HTTP data such as page size, title, and Server headers. 

## Contribute
Contribute to the project by:
* Like and share the tool!
* Create an issue to report new enumeration techniques or, better yet, develop a module and initiate a PR.
