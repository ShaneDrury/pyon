__author__ = 'srd1g10'


class MeasurementBase(object):
    def run(self):
        raise NotImplementedError


class Measurement(MeasurementBase):
    def __init__(self, simulation, views=None, simulation_kwargs=None):
        self.simulation = simulation
        self.views = views
        self.sim_kwargs = simulation_kwargs

    def run(self):
        return self.simulation(*self.views, **self.sim_kwargs)