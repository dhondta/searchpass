# -*- coding: UTF-8 -*-
from argparse import Action, SUPPRESS
from dictquery import match
from pybots.apis.security.default_credentials import *
from pybots.apis.security.default_credentials import __all__
from pybots.core.utils.api import APIError
from tinyscript import *


__author__    = "Alexandre D'Hondt"
__email__     = "alexandre.dhondt@gmail.com"
__version__   = "1.0.5"
__copyright__ = ("A. D'Hondt", 2021)
__license__   = "gpl-3.0"
__source__    = "https://github.com/dhondta/searchpass"
__doc__       = """
This tool aims to search for default passwords of common devices based on criteria like the vendor or the model.
It works by caching the whole lists of known default passwords downloaded from various sources (relying on pybots ;
 including CIRTnet, DataRecovery, PasswordDB, RouterPasswd or even SaynamWeb) to perform searches locally.
"""
__examples__  = [
    "--update",
    "--passwords",
    "--query \"username=='user'\" --passwords",
]


APIS = __all__[:]
KEYS = {
    'username': ["user", "username", "user-id"],
    'password': ["password", "pass", "pswd", "passwd"],
}
PATH = ts.Path("~/.searchpass", create=True, expand=True)


class _UpdateAction(Action):
    """ Custom action for updating the passwords databases. """
    def __init__(self, option_strings, dest=SUPPRESS, help=None):
        super(_UpdateAction, self).__init__(option_strings=option_strings, dest=SUPPRESS, default=SUPPRESS, nargs=0,
                                           help=help)
    
    def __call__(self, parser, namespace, values, option_string=None):
        update()
        parser.exit()


def load(warn=False):
    """ This loads and aggregates the records for every source of default passwords from the cached JSON files. """
    data = []
    for api_name in APIS:
        name = api_name[:-3]
        path = PATH.joinpath("%s.json" % name.lower())
        if path.exists():
            with path.open() as f:
                d = json.load(f)
            for vendor, lst in d.items():
                for item in (lst.get('data') if isinstance(lst, dict) else lst):
                    item['vendor'] = vendor
                    for k in ["username", "password"]:
                        for k2 in KEYS[k]:
                            try:
                                item[k] = item.pop(k2)
                            except KeyError:
                                pass
                    data.append(item)
        elif warn:
            logger.warning("'%s' does not exist" % path)
    return data


def update(warn=False):
    """ This downloads the records for each source of default passwords separately and caches them to JSON files. """
    data = {}
    for api_name in APIS:
        name = api_name[:-3]
        path = PATH.joinpath("%s.json" % name.lower())
        path.touch()
        logger.info("Downloading default credentials from %s..." % name)
        data = {}
        with globals()[api_name]() as api:
            for vendor in api.vendors:
                try:
                    data[vendor] = api.credentials(vendor)['data']
                except APIError as e:
                    if warn:
                        logger.warning(e)
        with path.open('w') as f:
            json.dump(data, f, indent=2)


def main():
    """ Tool's main function """
    parser.register('action', 'update', _UpdateAction)
    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("-e", "--empty", action="store_true", help="include empty username or password")
    fmt.add_argument("--passwords", action="store_true", help="get passwords only")
    parser.add_argument("-q", "--query", help="search query")
    fmt.add_argument("--usernames", action="store_true", help="get usernames only")
    extra = parser.add_argument_group("extra arguments")
    extra.add_argument("--update", action="update", help="update passwords databases")
    initialize()
    data, creds = load(), {}
    for item in data:
        if args.query is None or match(item, args.query):
            user, pswd = item.get('username'), item.get('password')
            if user is None or pswd is None:
                continue
            if not args.empty and (user == "" or pswd == ""):
                continue
            creds.setdefault(user, [])
            creds[user].append(pswd)
    if args.usernames:
        for u in sorted(set(creds.keys())):
            print(u)
    elif args.passwords:
        pswds = []
        for plst in creds.values():
            pswds.extend(plst)
        for p in sorted(set(pswds)):
            print(p)
    else:
        for user, pswds in sorted(creds.items(), key=lambda x: x[0].lower()):
            for pswd in set(pswds):
                print("%s:%s" % (user, pswd))
    return 0

