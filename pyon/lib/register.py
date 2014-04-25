__author__ = 'srd1g10'


class Register(object):
    """
    Decorator to register the class ``cls`` to the dict ``register_to_cls`` with key ``name``. Maintains a list of
    functions that can be used. ::

        >>> from pyon.lib.fitting import registered_fitters
        >>> @Register(registered_fitters, 'scipy')
        ... class ScipyFitter:
        ...     pass
        >>> registered_fitters['scipy']
        <class 'pyon.lib.fitting.ScipyFitter'>

    """
    def __init__(self, register_to, name):
        self.register_to = register_to
        self.name = name

    def __call__(self, cls):
        a = self.register_to  # alias
        if self.name not in a:  # Avoid duplicates
            a.update({self.name: cls})
        return cls

