# -*- coding: UTF-8 -*-
from pybots.apis.security.default_credentials import *
from pybots.apis.security.default_credentials import __all__ as _apis
from pybots.core.utils.api import APIError
from tinyscript import *
from tinyscript.report import *

from .sql import CredsSQLiteDB


__all__ = ["CredentialsDB"]

_DEPRECATED = ["SaynamWebAPI"]
APIS = [a for a in _apis if a not in _DEPRECATED]
DB = ts.Path("~/.searchpass.db", expand=True)


def _render(*elements):
    from rich.box import SIMPLE_HEAD
    from rich.console import Console
    from rich.markdown import Heading, Markdown
    from rich.style import Style
    from rich.table import Table as RichTable
    from rich.text import Text as RichText
    code.replace(Heading.__rich_console__, "text.justify = \"center\"", "")
    for e in elements:
        if hasattr(e, "md"):
            if isinstance(e, Table):
                opt = {'show_header': True, 'header_style': "bold", 'highlight': True}
                if e.title is not None:
                    opt['title'] = e.title
                    opt['title_justify'] = "left"
                    opt['title_style'] = Style(bold=True, color="bright_yellow", italic=False)
                if getattr(e, "borderless", True):
                    opt['box'] = SIMPLE_HEAD
                table = RichTable(**opt)
                for col in e.column_headers:
                    table.add_column(col, justify="center")
                for row in e.data:
                    if not all(set(str(cell).strip()) == {"-"} for cell in row):
                        table.add_row(*[RichText(str(cell), justify="left") for cell in row])
                Console(markup=False).print(table)
            elif isinstance(e, Section):
                Console().print(Markdown(e.md()), style=Style(bold=True, color="bright_cyan", italic=False))
            else:
                Console().print(Markdown(e.md()))
        elif e is not None:
            Console().print(Markdown(e))


class CredentialsDB:
    path = DB if DB.exists() else ts.Path(__file__).dirname.joinpath("searchpass.db")
    
    def __init__(self, logger=None, verbose=False, **kw):
        """ Loads and aggregates the records for every source of default credentials from the JSON files. """
        self.__logger, self.__verbose = logger or logging.nullLogger, verbose
    
    def reset(self, **kw):
        """ Resets cached JSON files. """
        DB.remove(False)
    
    def search(self, query=None, empty=False, **kw):
        """ Searches based on the given query in the given password dictionaries. """
        creds = {}
        with CredsSQLiteDB(self.path, logger=self.__logger) as db:
            try:
                for row in db.select(query, ("username", "password")):
                    user, pswd = row[0], row[1]
                    if user is None or pswd is None:
                        continue
                    if not empty and (user == "" or pswd == ""):
                        continue
                    m = re.match(r"^<<(.*?)>>$", pswd)
                    if m:
                        self.__logger.warning(f"Dynamic password found for username '{user}': {m.group(1)}")
                    creds.setdefault(user, [])
                    if pswd not in creds[user]:
                        creds[user].append(pswd)
            except SyntaxError as e:
                self.__logger.error(f"Bad query ({e})")
        return creds
    
    def show(self, **kw):
        """ Shows available credentials per source. """
        ts.execute(["visidata", str(self.path)])
    
    def stats(self, **kw):
        """ Computes statistics of the currently available passwords databases. """
        with CredsSQLiteDB(self.path, logger=self.__logger) as db:
            counts = [row for row in db.count("source")]
        _render(Section("Counts by source"), Table(counts, column_headers=["Source", "Count"]))
        stats = []
        with CredsSQLiteDB(self.path, logger=self.__logger) as db:
            stats.append([f"#unique credentials", next(db.distinct("username", "password"))[0]])
            for field in ["password", "username", "vendor"]:
                stats.append([f"#unique {field}s", next(db.distinct(field))[0]])
        _render(Section("Statistics"), Table(stats, column_headers=["Name", "Metric"]))
    
    def update(self, **kw):
        """ Downloads the records for each source of default passwords separately and caches them to JSON files. """
        self.__logger.debug("Recreating DB at {self.path}...")
        with CredsSQLiteDB(DB, logger=self.__logger) as db:
            db.create()
        for api_name in APIS:
            name = api_name[:-3]
            self.__logger.info(f"Downloading default credentials from {name}...")
            with globals()[api_name](verbose=self.__verbose) as api, CredsSQLiteDB(DB, logger=self.__logger) as db:
                for vendor in api.vendors:
                    try:
                        for record in api.credentials(vendor)['data']:
                            db.ingest(source=name, vendor=vendor, **record)
                    except APIError as e:
                        self.__logger.warning(e)
                self.__logger.debug("Saving to DB...")
        CredentialsDB.path = DB

