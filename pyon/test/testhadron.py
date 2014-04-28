import os
from random import shuffle
from numpy import random
from pyon.lib.fitfunction import pp_flat
from pyon.lib.fitting import registered_fitters, fit_hadron
from pyon.lib.io.folder import get_list_of_files
from pyon.lib.io.formats import parse_iwasaki_32c_charged_meson_file, \
    filter_correlators
from pyon.lib.meson import PseudoscalarMeson, PseudoscalarChargedMeson

__author__ = 'srd1g10'
import unittest


class TestHadron(unittest.TestCase):
    def setUp(self):
        self.time_extent = 64
        self.fit_func = lambda t, m, c: pp_flat(t, m, c, self.time_extent)
        self.iwasaki_folder = os.path.join('testfiles', 'parse', 'f1')

    def test_make_hadron(self):
        data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-4)
                 for t in range(self.time_extent)] for _ in range(10)]
        had = PseudoscalarMeson(data, masses=(0.01, 0.01))
        self.failUnlessEqual(had.data[0][0], data[0][0])
        self.failUnlessEqual(had.masses, (0.01, 0.01))

    #@unittest.skip('slow')
    def test_fit_hadron(self):
        data = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-4)
                 for t in range(self.time_extent)] for _ in range(50)]
        had = PseudoscalarMeson(data, masses=(0.01, 0.01))
        fp = fit_hadron(had, fit_range=range(1, 32+1),
                        initial_value=[0.8, 1.5], covariant=False)
        self.assertAlmostEqual(fp.average_params['m'], 1.0, 2)

    def make_filtered_data(self):
        raw_data = []
        for ff in get_list_of_files(self.iwasaki_folder):
            with open(ff, 'r') as f:
                raw_data.append(parse_iwasaki_32c_charged_meson_file(f))
        filtered_data = [filter_correlators(rd, source='GAM_5', sink='GAM_5', masses=(0.03, 0.03))
                         for rd in raw_data]
        return filtered_data

    def fit_test_hadron(self):
        filtered_data = self.make_filtered_data()
        had = PseudoscalarChargedMeson.from_parsed_data(filtered_data)
        had.sort()
        had.scale()
        fp = fit_hadron(had, fit_range=range(1, 32+1), initial_value=[0.3212, 1.65], covariant=False)
        return fp

    def test_sort(self):
        filtered_data = self.make_filtered_data()
        shuffle(filtered_data)  # shuffle to test sort
        shuffled_config_numbers = [fd['config_number'] for fd in filtered_data]
        had = PseudoscalarChargedMeson.from_parsed_data(filtered_data)
        had.sort()
        had.scale()
        self.assertEqual(had.config_numbers[0], 510)
        self.assertNotEqual(had.config_numbers, shuffled_config_numbers)

    def test_scale(self):
        filtered_data = self.make_filtered_data()
        had = PseudoscalarChargedMeson.from_parsed_data(filtered_data)
        had.sort()
        had.scale()
        self.assertAlmostEqual(had.central_data[0], 1.0, 5)

    def test_fold(self):
        filtered_data = self.make_filtered_data()
        had = PseudoscalarChargedMeson.from_parsed_data(filtered_data)
        had.sort()
        had.scale()
        had.fold()
        self.assertEqual(had.data[0][1], had.data[0][-1])