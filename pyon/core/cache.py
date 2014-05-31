import logging
from django.core.cache import cache


class CachedData(object):
    """
    Use Django's cache framework to store data to speed up execution.
    The CachedData object has its `__call__` method overridden so it acts as a
    function. The func should return a Pickleable object.

    To clear the cache:

        >>> from django.core.cache import cache
        >>> cache.clear()
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


class cache_data(object):
    """
    Decorator to simplify the use of the class. The cache_key should be unique
    as it is global to the Django cache framework. It defaults to the function
    name the decorator is applied to, but may be set as an argument in the case
    of name collisions.

    Usage:
        >>> @cache_data()
        >>> def foo():
        ...     return pickleable_data
    """
    def __init__(self, cache_key=None, timeout=None):
        self.cache_key = cache_key
        self.TIMEOUT = timeout

    def __call__(self, f):
        if not self.cache_key:
            self.cache_key = f.__name__

        def wrapped_f(*args, **kwargs):
            data = cache.get(self.cache_key)
            if not data:
                data = f(*args, **kwargs)
                cache.set(self.cache_key, data, self.TIMEOUT)
            else:
                logging.debug("Accessing cache for {}".format(self.cache_key))
            return data
        return wrapped_f
