"""
The point of this module is to be able to easily plot lattice QCD things - most often this will be correlators.
We want to have the same syntax for common use plotting regardless of what program is used to plot it. So, the classes
here implement a common API that forwards stuff to e.g. Pyplot and Gnuplot
"""
import matplotlib.pyplot as plt
#from pyon.lib.fitfunction import pp_effective_mass
from pyon.lib.register import Register
import numpy as np
__author__ = 'srd1g10'

registered_plotters = {}


class Plotter(object):
    """
    A :class:`Plotter` plots hadrons like mesons, baryons. e.g. ::

        >>> from pyon.lib.meson import PseudoscalarMeson
        >>> from pyon.lib.fitfunction import pp_flat
        >>> data = [
        ...    [pp_flat(t, 1.0, 1.0, 64) for t in range(64)]
        ...    for _ in range(200) ]
        >>> had = PseudoscalarMeson(data, masses=(0.05, 0.05))
        >>> plot_hadron(had)

    """
    def __init__(self, *args, **kwargs):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def plot(self, *args, **kwargs):
        pass

    def show(self):
        pass


@Register(registered_plotters, 'pyplot')
class PyplotPlotter(Plotter):
    """
    Uses matplotlib.pyplot to do the plotting.
    """

    def __init__(self, *args, **kwargs):
        super(PyplotPlotter, self).__init__(*args, **kwargs)
        self.fig, self.ax = plt.subplots()

    def __exit__(self, exc_type, exc_val, exc_tb):
        plt.close('all')
        return False

    def plot(self, x, y, yerr=None, title=None, log_scale=True, *args, **kwargs):
        """
        Set up the fields of the object to the specifics of the plot.
        """
        if title is not None:
            self.ax.set_title(title)
        self.ax.grid(True)
        self.ax.errorbar(x, y, yerr=yerr, *args, **kwargs)

    def set_scale(self, x_scale=None, y_scale=None):
        if x_scale:
            self.ax.set_xscale(x_scale)
        if y_scale:
            self.ax.set_yscale(y_scale)

    def show(self):
        self.fig.show()


def plot_hadron(hadron, title=None, effective_mass=False, **kwargs):
    """
    Simple common use case. Defaults to PyplotPlotter.

    :param hadron: The :class:`Hadron <hadron.Hadron>` object to plot.
    :param \*\*kwargs: The keyword arguments to pass to :func:`matplotlib.pyplot.errorbar`.
    """
    plotter = PyplotPlotter()
    if effective_mass:
        data = hadron.effective_mass
        errs = hadron.effective_mass_errs
        y_scale = None
    else:
        data = hadron.central_data
        errs = hadron.central_errs
        y_scale = 'log'
    t_range = range(hadron.time_extent//2)
    data = [data[t] for t in t_range]
    errs = [errs[t] for t in t_range]
    if title is None:
        title = str(hadron)
    plotter.plot(t_range, data, yerr=errs, title=title, **kwargs)
    plotter.set_scale(y_scale=y_scale)
    return plotter


