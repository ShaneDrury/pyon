__author__ = 'srd1g10'


class Simulation(object):
    """
    A simulation combines a view (aspect of data) and a model to perform some
    calculation with the data and the formulae of the model. The methods
    :func:`get_results` and :func:`get_plots` implement the way the results
    of the simulation are returned and visualised.
    """
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.simulation_params = None
        self.simulation_results = None

    def set_simulation_params(self, **kwargs):
        self.simulation_params = kwargs

    def do_simulation(self):
        raise NotImplementedError("Implement this in a derived class.")

    def get_results(self):
        if self.simulation_results is None:
            self.simulation_results = self.do_simulation()
        return self.simulation_results

    def get_plots(self):
        raise NotImplementedError("Implement this in a derived class.")
