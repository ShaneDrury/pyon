from pyon import registered_simulations, registered_views
from pyon import registered_models
from pyon import registered_sources

__author__ = 'srd1g10'


def create_register(registry):
    class Register(object):
        def __init__(self, name):
            self.register_to = registry
            self.name = name

        def __call__(self, cls):
            a = self.register_to  # alias
            if self.name not in a:  # Avoid duplicates
                a.update({self.name: cls})
            return cls
    return Register


view = create_register(registered_views)

source = create_register(registered_sources)

model = create_register(registered_models)

simulation = create_register(registered_simulations)