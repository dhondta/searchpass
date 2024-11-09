# -*- coding: UTF-8 -*-
from .lexer import WhereStatementLexer
from .table import BASE, FIELDS, FIELDS_MAP


class CredsSQLiteDB:
    def __init__(self, path, logger=None, **kwargs):
        from tinyscript import logging
        self.path = path
        self.__logger = logger or logging.nullLogger
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    
    def _exec(self, cursor, statement, *args, **kwargs):
        self.__logger.debug(f"{statement} - {args[0]}" if len(args) > 0 and isinstance(args[0], tuple) else statement)
        cursor.execute(statement, *args, **kwargs)
    
    def close(self):
        try:
            self.__conn.close()
        except AttributeError:
            pass
    
    def connect(self):
        from sqlite3 import connect
        self.__conn = connect(str(self.path))
    
    def count(self, *fields):
        cursor = self.__conn.cursor()
        self._exec(cursor, f"SELECT {', '.join(fields)}, COUNT(*) AS count FROM {BASE} GROUP BY {', '.join(fields)}")
        for row in cursor.fetchall():
            yield row
    
    def create(self):
        fields = ", ".join(f"{f} {d['type']}" for f, d in FIELDS.items())
        primary_keys = ", ".join(f for f, d in FIELDS.items() if d.get('primary', False))
        cursor = self.__conn.cursor()
        self._exec(cursor, f"DROP TABLE IF EXISTS {BASE}")
        self._exec(cursor, f"CREATE TABLE {BASE} ({fields}, PRIMARY KEY ({primary_keys}))")
        self.__conn.commit()
    
    def distinct(self, *fields):
        multi = len(fields) > 1
        fields = ", ".join(fields)
        cursor = self.__conn.cursor()
        self._exec(cursor, f"SELECT COUNT(*) AS count FROM (SELECT {fields} FROM {BASE} GROUP BY {fields})" if multi \
                      else f"SELECT COUNT(DISTINCT {fields}) AS {fields}_count FROM {BASE}")
        for row in cursor.fetchall():
            yield row
    
    def ingest(self, **record):
        data, primary_keys = [{}], [f for f, d in FIELDS.items() if d.get('primary', False)]
        # create data from the input record, handling data expansion where relevant
        for k, v in record.items():
            k = FIELDS_MAP.get(k, k)
            f = FIELDS[k].get('format', lambda x: x)
            v = FIELDS[k].get('expand', lambda x: x)(v)
            if isinstance(v, list):
                if k in primary_keys:
                    from itertools import product
                    old, data = tuple(data), []
                    for d, v2 in product(old, v):
                        d2 = {k: v for k, v in d.items()}
                        d2[k] = f(v2)
                        data.append(d2)
                else:
                    v2 = ",".join(map(f, v))
                    for d in data:
                        d[k] = v2
            else:
                for d in data:
                    d[k] = str(f(v))
        # populate values for primary keys
        for f in primary_keys:
            for d in data:
                if f in d:
                    continue
                d[f] = ""
        # now save to the database
        for d in data:
            fields, marks = ", ".join(d.keys()), ", ".join(len(d) * ['?'])
            update = ", ".join(f"{f} = excluded.{f}" for f in d.keys() if f not in primary_keys)
            update = "DO NOTHING" if update == "" else f"DO UPDATE SET {update}"
            self.__conn.cursor().execute(f"INSERT INTO {BASE} ({fields}) VALUES ({marks}) ON CONFLICT" \
                                         f"({', '.join(primary_keys)}) {update}", tuple(d.values()))
        self.__conn.commit()
    
    def select(self, where_statement, fields=None):
        where, values = WhereStatementLexer.prepare(where_statement)
        cursor = self.__conn.cursor()
        self._exec(cursor, f"SELECT {'*' if fields is None else ', '.join(fields)} FROM {BASE} WHERE {where}", values)
        for row in cursor.fetchall():
            yield row

