<h1 align="center">SearchPass</h1>
<h3 align="center">Get default passwords for network devices by vendor.</h3>

[![PyPi](https://img.shields.io/pypi/v/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)
[![Python Versions](https://img.shields.io/pypi/pyversions/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)
[![Build Status](https://github.com/dhondta/searchpass/actions/workflows/python-package.yml/badge.svg)](https://github.com/dhondta/searchpass/actions/workflows/python-package.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/searchpass/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/searchpass?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)

This tool is similar to the Ruby implementation [SearchPass](https://github.com/michenriksen/searchpass) *for offline searching of default credentials for network devices, web applications and more*. The present tool expands its capabilities to **more databases of credentials** and allows to **update the local database**, a bit like [SearchSploit](https://www.exploit-db.com/searchsploit) allows to update references to exploits on your local machine.

It relies on [`pybots`](https://github.com/dhondta/pybots) for abstracting robots that download from the sources of default credentials and on [`dictquery`](https://github.com/cyberlis/dictquery) for querying the underlying data using the `--query` option.

```session
$ pip install searchpass
[...]

$ searchpass --help
[...]
This tool aims to search for default passwords of common devices based on criteria like the vendor or the model.
It works by caching the whole lists of known default passwords downloaded from various sources (relying on pybots ;
 including CIRTnet, DataRecovery, PasswordDB, RouterPasswd or even SaynamWeb) to perform searches locally.

usage: searchpass [-e] [--passwords] [-q QUERY] [--usernames] [--update] [-h] [--help] [-v]

optional arguments:
  -e, --empty           include empty username or password (default: False)
  --passwords           get passwords only (default: False)
  -q QUERY, --query QUERY
                        search query (default: None)
  --usernames           get usernames only (default: False)

extra arguments:
  --update       update passwords databases
  -h             show usage message and exit
  --help         show this help message and exit
  -v, --verbose  verbose mode (default: False)

Usage examples:
  searchpass --update
  searchpass --passwords
  searchpass --query "username=='user'" --passwords
```


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/searchpass](https://reporoster.com/stars/dark/dhondta/searchpass)](https://github.com/dhondta/searchpass/stargazers)

[![Forkers repo roster for @dhondta/searchpass](https://reporoster.com/forks/dark/dhondta/searchpass)](https://github.com/dhondta/searchpass/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
