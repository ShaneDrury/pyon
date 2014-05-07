class QuerySet(object):
    def __init__(self, data, manager_class=None, manager_kwargs=None):
        self.data = data

        if manager_class is None:
            raise ValueError("Must provide a manager class for a QuerySet")
        self.manager_class = manager_class
        self.manager_kwargs = manager_kwargs
        self.manager = manager_class(self)  # must be after setting kwargs
        self._list_data = None
        self.results = None

    def make_query_set(self, data):
        return QuerySet(data, self.manager_class,
                        manager_kwargs=self.manager_kwargs)

    def filter(self, **kwargs):
        self.results = self.manager.filter(**kwargs)
        return self
        #return self.make_query_set(self.manager.filter(**kwargs))

    def exclude(self, **kwargs):
        self.results = self.manager.exclude(**kwargs)
        return self
        #return self.make_query_set(self.manager.exclude(**kwargs))

    def all(self):
        return self.data

    def get_manager_kwargs(self):
        return self.manager_kwargs

    def __getitem__(self, item):
        """
        Allow indexing of data e.g. qs[0]

        Converts into a list to allow indexing and stores this so that it isn't
        calculated twice.
        """
        if self._list_data is None:
            self._list_data = list(self.data)
        return self._list_data[item]

    def sort(self, sort_by):
        self.data = self.manager.sort(sort_by)

    def unique(self, field_name):
        """
        Return a list of the unique values of ``field_name`` in the data.
        """
        return self.manager.unique(field_name)
