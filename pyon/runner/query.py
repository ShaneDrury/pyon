"""
Define a QuerySet
"""
from pyon.lib.io.formats import filter_one_correlator


class QuerySet(object):
    def __init__(self, data):
        self.data = list(data)

    def filter(self, **kwargs):
        my_filter = lambda x: filter_one_correlator(x, **kwargs)
        filtered = self._do_filter(my_filter, self.data)
        if len(filtered.all()) == 0:
            raise ValueError("Cannot match {}".format(kwargs))
        return filtered

    def exclude(self, **kwargs):
        my_filter = lambda x: not filter_one_correlator(x, **kwargs)
        filtered = self._do_filter(my_filter, self.data)
        if len(filtered.all()) == 0:
            raise ValueError("Cannot match {}".format(kwargs))
        return filtered

    @staticmethod
    def _do_filter(filt, data):
        filtered = list(filter(filt, data))
        return QuerySet(filtered)

    def all(self):
        return self.data

    def __len__(self):
        return len(self.data)

    def sort(self, sort_by):
        self.data = sorted(self.data, key=lambda item: item[sort_by])

    def unique(self, field_name):
        """
        Return a list of the unique values of ``field_name`` in the data.
        """
        values = []
        for f in self.data:
            try:
                v = f[field_name]
                if v not in values:
                    values.append(v)
            except KeyError:
                pass
        return values


class QuerySet2(object):
    """
    Rewritten to use a database backend.
    """
    def __init__(self):
        pass

