import logging
from pyon.runner.query import QuerySet
from pyon import registered_parsers
registered_sources = {}


class Source:
    data_format = None
    folder = None
    files = None
    data_format_kwargs = {}
    _data = None

    def get_data(self):
        parser = self.get_parser()
        if self.files:
            return parser.get_from_files(self.files)
        elif self.folder:
            return parser.get_from_folder(self.folder)

    def get_parser(self):
        return registered_parsers[self.data_format](**self.data_format_kwargs)

    def all(self):
        return self.get_queryset()

    def get_queryset(self):
        if self._data is None:
            logging.debug("Getting data from {}".format(self.folder))
            self._data = self.get_data()
        return QuerySet(self._data)

