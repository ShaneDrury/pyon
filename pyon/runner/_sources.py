# import logging
# import sqlite3
# from pyon.lib.manager import DBManager, FileManager
# from pyon.runner.query import QuerySet
#
#
# class Source(object):
#     def __init__(self, manager):
#         self.manager = manager
#         self._data = None
#
#     @property
#     def data(self):
#         if self._data is None:
#             self._data = self._get_data()
#         return self._data
#
#     def filter(self, **kwargs):
#         qs = self._view_from_data()
#         return qs.filter(**kwargs)
#
#     def exclude(self, **kwargs):
#         qs = self._view_from_data()
#         return qs.exclude(**kwargs)
#
#     def all(self):
#         return self._view_from_data().all()
#
#     def unique(self, field_name):
#         qs = self._view_from_data()
#         return qs.distinct(field_name)
#
#     def _view_from_data(self):
#         return QuerySet(self.data, self.manager)
#
#     def _get_data(self):
#         pass
#
#
# class FileSource(Source):
#     parser = None
#     folder = None
#     files = None
#
#     def __init__(self):
#         super(FileSource, self).__init__(FileManager())
#
#     def _get_data(self):
#         logging.debug("Getting files")
#         if self.files:
#             return self.parser.get_from_files(self.files)
#         elif self.folder:
#             return self.parser.get_from_folder(self.folder)
#
#
# class DBSource(Source):
#     db_path = None
#     table_name = None
#
#     def __init__(self):
#         super(DBSource, self).__init__(DBManager(self.db_path, self.table_name))
#         self.con = None
#
#     def _get_data(self):
#         # logging.debug("Loading DB")
#         # self.con = sqlite3.connect(self.db_path,
#         #                            detect_types=sqlite3.PARSE_DECLTYPES)
#         return self.con