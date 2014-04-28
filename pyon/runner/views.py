registered_views = {}


class View(object):
    queryset = None
    data_source = None
    filter = None

    def get_queryset(self):
        if self.queryset is None:
            if self.filter is not None:
                return self.data_source.filter(**self.filter)
            else:
                return self.data_source.all()
        else:
            return self.queryset

    @property
    def data(self):
        return self.get_queryset().all()

