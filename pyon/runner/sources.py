import logging
import sqlite3
from pyon.lib.manager import DBManager, FileManager
from pyon.runner.query import QuerySet
from pyon import registered_parsers


class Source(object):
    def __init__(self, manager=None):
        self.manager = manager
        self._data = None
        self.manager_args = {}

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()
        return self._data

    def filter(self, **kwargs):
        qs = self._qs_from_data()
        return qs.filter(**kwargs)

    def exclude(self, **kwargs):
        qs = self._qs_from_data()
        return qs.exclude(**kwargs)

    def all(self):
        return self._qs_from_data().all()

    def unique(self, field_name):
        qs = self._qs_from_data()
        return qs.unique(field_name)

    def _qs_from_data(self):
        return QuerySet(self.data, self.manager, self.manager_args)

    def _get_data(self):
        pass


class FileSource(Source):
    data_format = None
    folder = None
    files = None

    def __init__(self):
        super(FileSource, self).__init__(FileManager)

    def _get_data(self):
        logging.debug("Getting files")
        parser = self._get_parser()
        if self.files:
            return parser.get_from_files(self.files)
        elif self.folder:
            return parser.get_from_folder(self.folder)

    def _get_parser(self):
        return registered_parsers[self.data_format]()


class DBSource(Source):
    db_path = None
    table_name = None

    def __init__(self):
        super(DBSource, self).__init__(DBManager)
        self.con = None
        self.manager_class = DBManager
        self.manager_args['table_name'] = self.table_name

    def __enter__(self):
        self._get_data()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.con.close()

    def _get_data(self):
        logging.debug("Loading DB")
        self.con = sqlite3.connect(self.db_path,
                                   detect_types=sqlite3.PARSE_DECLTYPES)
        return self.con

