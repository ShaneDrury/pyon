import json
from numpy import random
from pyon.lib.fitfunction import pp_flat
#from pyon.lib.fitting import fit_hadron
from pyon.lib.fitting import registered_fitters
#from pyon.lib.hadron import Hadron
from pyon.lib.meson import PseudoscalarMeson

__author__ = 'srd1g10'
import unittest


class TestSerialize(unittest.TestCase):
    def setUp(self):
        self.time_extent = 64
        self.fit_func = lambda t, m, c: pp_flat(t, m, c, self.time_extent)

    # def test_serialize_stdout(self):
    #     data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-4)
    #              for t in range(self.time_extent)] for _ in range(10)]
    #     had = PseudoscalarMeson(data, masses=(0.01, 0.01))
    #     s = had.dumps(method='string')
    #     print(s)
    #     self.assertTrue(True)

    def test_serialize_json(self):
        data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-4)
                 for t in range(self.time_extent)] for _ in range(50)]
        had = PseudoscalarMeson(data, masses=(0.01, 0.01))
        j = had.json()
        had2 = PseudoscalarMeson.from_json(j)
        self.assertEqual(had2.masses, [0.01, 0.01])
