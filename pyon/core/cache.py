import logging
from django.core.cache import cache


class CachedData(object):
    """
    Use Django's cache framework to store data to speed up execution.
    The CachedData object has its `__call__` method overridden so it acts as a
    function. The func should return a Pickleable object.
    """
    def __init__(self, func, cache_key, timeout=None):
        self.func = func
        self.cache_key = cache_key
        self.data = None
        self.TIMEOUT = timeout

    def __call__(self, *args, **kwargs):
        return self.get_cache(*args, **kwargs)

    def set_cache(self, data):
        cache.set(self.cache_key, data, self.TIMEOUT)

    def get_cache(self, *args, **kwargs):

        data = cache.get(self.cache_key)
        if not data:
            data = self.func(*args, **kwargs)
            self.set_cache(data)
        else:
            logging.debug("Accessing cache for {}".format(self.cache_key))
        return data