<h1 align="center">SearchPass</h1>
<h3 align="center">Get default passwords for network devices by vendor.</h3>

[![PyPi](https://img.shields.io/pypi/v/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)
[![Python Versions](https://img.shields.io/pypi/pyversions/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)
[![Build Status](https://github.com/dhondta/searchpass/actions/workflows/python-package.yml/badge.svg)](https://github.com/dhondta/searchpass/actions/workflows/python-package.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/searchpass/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/searchpass?targetFile=requirements.txt)
[![License](https://img.shields.io/pypi/l/searchpass.svg)](https://pypi.python.org/pypi/searchpass/)

This tool is similar to the Ruby implementation [SearchPass](https://github.com/michenriksen/searchpass) *for offline searching of default credentials for network devices, web applications and more*. The present tool expands its capabilities to **more databases of credentials** and allows to **update the local database**, a bit like [SearchSploit](https://www.exploit-db.com/searchsploit) allows to update references to exploits on your local machine.

It relies on :
- [`tinyscript`](https://github.com/dhondta/python-tinyscript), for the CLI tool mechanics
- [`pybots`](https://github.com/dhondta/python-pybots) for abstracting robots that download from the sources of default credentials
- [`sqlite3`](https://docs.python.org/3/library/sqlite3.html) for querying the underlying data using the `--query` option

Data from the different sources gets normalized into a SQLite DB when updating the tool. [`searchpass´](https://github.com/dhondta/searchpass) package embeds a database updated end 2024.

```session
$ pip install searchpass
[...]

$ searchpass --help
searchpass 2.0.0
Author   : Alexandre D'Hondt (alexandre.dhondt@gmail.com)
Copyright: © 2021-2024 A. D'Hondt
License  : GPLv3 (https://www.gnu.org/licenses/gpl-3.0.fr.html)
Source   : https://github.com/dhondta/searchpass

This tool aims to search for default passwords of common devices based on criteria like the vendor or the model.
It works by caching the whole lists of known default passwords downloaded from various sources (relying on pybots ;
 including CIRTnet, DataRecovery, PasswordDB, RouterPasswd or even SaynamWeb) to perform searches locally.

usage: searchpass [-e] [--passwords] [-q QUERY] [--usernames] [--reset] [--show] [--stats] [--update] [-h] [--help] [-v]

search options:
  -e, --empty           include empty username or password (default: False)
  --passwords           get passwords only (default: False)
  -q QUERY, --query QUERY
                        search query (default: None)
  --usernames           get usernames only (default: False)

action arguments:
  --reset     remove cached credentials databases
  --show      show records of credentials databases
  --stats     get statistics on credentials databases
  --update    update credentials databases

extra arguments:
  -h               show usage message and exit
  --help           show this help message and exit
  -v, --verbose    verbose mode (default: False)

Usage examples:
  searchpass --update
  searchpass --passwords
  searchpass --stats
  searchpass --query "username='user'
  searchpass --query "username LIKE \"Admin%%\"" --passwords
```


## :clap:  Supporters

[![Stargazers repo roster for @dhondta/searchpass](https://reporoster.com/stars/dark/dhondta/searchpass)](https://github.com/dhondta/searchpass/stargazers)

[![Forkers repo roster for @dhondta/searchpass](https://reporoster.com/forks/dark/dhondta/searchpass)](https://github.com/dhondta/searchpass/network/members)

<p align="center"><a href="#"><img src="https://img.shields.io/badge/Back%20to%20top--lightgrey?style=social" alt="Back to top" height="20"/></a></p>
