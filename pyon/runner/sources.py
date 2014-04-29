import logging
from pyon.lib.manager import DBManager, FileManager
from pyon.runner.query import QuerySet
from pyon import registered_parsers
registered_sources = {}


# class Source2:
#     data_format = None
#     folder = None
#     files = None
#     data_format_kwargs = {}
#     _data = None
#
#     def __init__(self, manager=None):
#         self.manager = manager  # or DefaultManager()
#
#     def get_data(self):
#         parser = self.get_parser()
#         if self.files:
#             return parser.get_from_files(self.files)
#         elif self.folder:
#             return parser.get_from_folder(self.folder)
#
#     def get_parser(self):
#         return registered_parsers[self.data_format](**self.data_format_kwargs)
#
#     def all(self):
#         return self.get_queryset()
#
#     def get_queryset(self):
#         if self._data is None:
#             logging.debug("Getting data from {}".format(self.folder))
#             self._data = self.get_data()
#         return QuerySet(self._data)


class Source:
    def __init__(self, manager=None):
        self.manager = manager
        self._data = None

    @property
    def data(self):
        if self._data is None:
            self._data = self._get_data()
        return self._data

    def filter(self, **kwargs):
        qs = QuerySet(self.data, self.manager)
        return qs.filter(**kwargs)

    def exclude(self, **kwargs):
        qs = QuerySet(self.data, self.manager)
        return qs.exclude(**kwargs)

    def all(self):
        return QuerySet(self.data, self.manager).all()

    def _get_data(self):
        pass


class FileSource(Source):
    data_format = None
    folder = None
    files = None

    def __init__(self):
        super(FileSource, self).__init__(FileManager)

    def _get_data(self):
        parser = self._get_parser()
        if self.files:
            return parser.get_from_files(self.files)
        elif self.folder:
            return parser.get_from_folder(self.folder)

    def _get_parser(self):
        return registered_parsers[self.data_format]()


class DBSource(Source):
    def __init__(self):
        super(DBSource, self).__init__(DBManager)
