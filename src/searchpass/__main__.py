# -*- coding: UTF-8 -*-
from argparse import Action, SUPPRESS as _SUP
from tinyscript import *

from .__info__ import __author__, __copyright__, __email__, __license__, __version__
from .db import CredentialsDB


__source__    = "https://github.com/dhondta/searchpass"
__doc__       = """
This tool aims to search for default passwords of common devices based on criteria like the vendor or the model.
It works by caching the whole lists of known default passwords downloaded from various sources (relying on pybots ;
 including CIRTnet, DataRecovery, PasswordDB, RouterPasswd or even SaynamWeb) to perform searches locally.
"""
__examples__  = [
    "--update",
    "--passwords",
    "--stats",
    "--query \"username='user'",
    "--query \"username LIKE \\\"Admin%%\\\"\" --passwords",
]

DB_ACTIONS = {
    'reset':  "remove cached credentials databases",
    'show':   "show records of credentials databases",
    'stats':  "get statistics on credentials databases",
    'update': "update credentials databases",
}


def custom_action(method):
    class _Action(Action):
        """ Custom action for applying a method of searchpass.db.CredentialsDB. """
        def __init__(self, option_strings, dest=_SUP, help=None):
            super(_Action, self).__init__(option_strings=option_strings, dest=_SUP, default=_SUP, nargs=0, help=help)
        
        def __call__(self, parser, namespace, values, option_string=None):
            namespace._action = method
    return _Action


def main():
    """ Tool's main function """
    from shutil import which
    if not which("visidata"):
        del DB_ACTIONS['show']
    for a in DB_ACTIONS.keys():
        cls = globals()[f'_{a.capitalize()}Action'] = custom_action(a)
        parser.register('action', a, cls)
    so = parser.add_argument_group("search options")
    fmt = so.add_mutually_exclusive_group()
    fmt.add_argument("-e", "--empty", action="store_true", help="include empty username or password")
    fmt.add_argument("--passwords", action="store_true", help="get passwords only")
    so.add_argument("-q", "--query", help="search query")
    fmt.add_argument("--usernames", action="store_true", help="get usernames only")
    dba = parser.add_argument_group("action arguments")
    for a, h in DB_ACTIONS.items():
        dba.add_argument(f"--{a}", action=a, help=h)
    initialize()
    args.logger = logger
    credsdb = CredentialsDB(**vars(args))
    m = getattr(args, "_action", None)
    if m is not None:
        getattr(credsdb, m)(**vars(args))
    else:
        creds = credsdb.search(**vars(args))
        if len(creds) == 0:
            logger.warning("No credential found")
        elif args.usernames:
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

