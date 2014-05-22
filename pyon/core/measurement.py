__author__ = 'srd1g10'


class MeasurementBase(object):
    def run(self):
        raise NotImplementedError


class Measurement(MeasurementBase):
    def __init__(self, simulation, args=[], kwargs={}):
        self.simulation = simulation
        self.args = args
        self.kwargs = kwargs

    def run(self):
        return self.simulation(*self.args, **self.kwargs)
