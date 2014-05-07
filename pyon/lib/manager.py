import logging
from pyon.lib.io.formats import filter_one_correlator
from pyon.runner.db import ListType


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

    def __init__(self, query_set):
        super(DBManager, self).__init__(query_set)
        self.con = query_set.all()
        self.table_name = query_set.manager_kwargs['table_name']
        self._col_names = None

    @property
    def col_names(self):
        if self._col_names is None:
            self._col_names = self.get_col_names()
        return self._col_names

    def get_col_names(self):
        logging.debug("Getting column names")
        cur = self.con.cursor()
        cur.execute('select * from {}'.format(self.table_name))
        description = cur.description
        cur.close()
        return description

    def filter(self, **kwargs):
        qry, vals = self.filter_to_query(**kwargs)
        qry = self.con.execute(qry, tuple(vals))
        filtered = self.convert_qry_to_list(qry)
        return filtered

    def convert_qry_to_list(self, qry):
        return [self.map_name_to_row(row) for row in qry]

    def exclude(self, **kwargs):
        qry, vals = self.filter_to_query(exclude=True, **kwargs)
        qry = self.con.execute(qry, tuple(vals))
        filtered = self.convert_qry_to_list(qry)
        return filtered

    def filter_to_query(self, exclude=False, **kwargs):
        if exclude:
            equality = '!='
        else:
            equality = '='
        qry = "select * from {} where ".format(self.table_name)
        query_num = 1
        vals = []
        for k, v in kwargs.items():
            if query_num < len(kwargs):
                qry += k + "{}? and ".format(equality)
            else:
                qry += k + "{}?".format(equality)
            if isinstance(v, list) or isinstance(v, tuple):
                v = ListType(v)
            vals.append(v)
            query_num += 1
        return qry, vals

    def unique(self, field_name):
        values = []
        qry = "select distinct {} from {}".format(field_name, self.table_name)
        for row in self.con.execute(qry):
            values.append(row[0])
        return values

    def map_name_to_row(self, row):
        vals = {}
        for i, col in enumerate(self.col_names):
            vals[col[0]] = row[i]
        return vals


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
