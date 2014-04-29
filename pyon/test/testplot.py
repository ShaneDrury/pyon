from numpy import random
from pyon.lib.fitfunction import pp_flat
from pyon.lib.meson import PseudoscalarMeson
from pyon.lib.plotting import plot_hadron
import unittest


class TestPlot(unittest.TestCase):
    def setUp(self):
        self.time_extent = 64

    @unittest.skip('annoying')
    def test_plot_hadron(self):
        data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-9)
                 for t in range(self.time_extent)] for _ in range(10)]
        had = PseudoscalarMeson(data, masses=(0.01, 0.01))
        plt = plot_hadron(had)
        plt.show()

    @unittest.skip('annoying')
    def test_eff_mass_hadron(self):
        data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-9)
                 for t in range(self.time_extent)] for _ in range(10)]
        had = PseudoscalarMeson(data, masses=(0.01, 0.01))
        plt = plot_hadron(had, effective_mass=True)
        plt.show()
