# -*- coding: UTF-8 -*-
BASE = "credentials"
FIELDS = {
    'source':       {'type': "TEXT NOT NULL", 'primary': True},
    'vendor':       {'type': "TEXT NOT NULL", 'primary': True},
    'model':        {'type': "TEXT NOT NULL", 'primary': True},
    'version':      {'type': "TEXT", 'primary': True},
    'access_type':  {'type': "TEXT", 'format': lambda x: x.lower().replace("/", ",")},
    'access_level': {'type': "TEXT"},
    'notes':        {'type': "TEXT"},
    'username':     {'type': "TEXT", 'primary': True},
    'password':     {'type': "TEXT", 'primary': True, 'format': lambda p: _pswd_formatter(p),
                                                      'expand': lambda p: _pswd_splitter(p)},
}
FIELDS_MAP = {
    'manufacturer': "vendor",
    'name':         "model",
    'revision':     "version",
    'access-type':  "access_type",
    'method':       "access_type",
    'protocol':     "access_type",
    'access-level': "access_level",
    'level':        "access_level",
    'privileges':   "access_level",
    'doc':          "notes",
    'user':         "username",
    'user-id':      "username",
    'pass':         "password",
    'passwd':       "password",
    'pswd':         "password",
}


def _pswd_formatter(password):
    if any(pattern in password for pattern in \
       ["just hit ENTER", "leave blank", "no password", "(blank)", "(no pw)", "(none by default)"]):
        return ""
    if any(pattern in password.lower() for pattern in \
       ["ip address", "serial number", "model#", "mac address", "unknown", "digits of "]):
        from re import sub
        password = sub(r"^The\s", "", password.strip(" ."))
        return f"<<{password}>>"
    return password


def _pswd_splitter(password, separators=(" / ", " or ", "/")):
    from itertools import chain
    from re import sub
    password = sub(r"\s\(or\sblank\)", " (blank)", password)
    for sep in separators:
        if sep in password:
            tokens = password.split(sep)
            return list(chain.from_iterable((x if isinstance(x, list) else [x] for x in \
                        [_pswd_splitter(p, ("/", )) for p in password.split(sep)])))
    return password

