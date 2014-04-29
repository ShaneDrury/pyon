from pyon.lib.io.formats import filter_one_correlator


class Manager(object):
    """
    A manager defines how to access and filter a :class:`Source`.
    """

    def __init__(self, query_set):
        self.qs = query_set

    def filter(self, **kwargs):
        pass

    def exclude(self, **kwargs):
        pass

    def sort(self, sort_by):
        pass

    def unique(self, field_name):
        pass


class DBManager(Manager):
    def filter(self, **kwargs):
        pass

    def exclude(self, **kwargs):
        pass

    def filter_to_query(self, filter):
        qry = filter
        return qry

    def _do_query(self, query):
        pass


class FileManager(Manager):
    def filter(self, **kwargs):
        my_filter = lambda x: filter_one_correlator(x, **kwargs)
        filtered = self._do_filter(my_filter, self.qs.all())
        if len(filtered) == 0:
            raise ValueError("Cannot match {}".format(kwargs))
        return filtered

    def exclude(self, **kwargs):
        my_filter = lambda x: not filter_one_correlator(x, **kwargs)
        filtered = self._do_filter(my_filter, self.qs.all())
        if len(filtered) == 0:
            raise ValueError("Cannot match {}".format(kwargs))
        return filtered

    @staticmethod
    def _do_filter(filt, data):
        filtered = list(filter(filt, data))
        return filtered

    def sort(self, sort_by):
        return sorted(list(self.qs.all()), key=lambda item: item[sort_by])

    def unique(self, field_name):
        values = []
        for f in self.qs.all():
            try:
                v = f[field_name]
                if v not in values:
                    values.append(v)
            except KeyError:
                pass
        return values
