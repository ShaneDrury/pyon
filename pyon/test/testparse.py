from random import shuffle
from pyon.lib.fitting import fit_hadron

__author__ = 'srd1g10'
import os
from pyon.lib.io.folder import get_list_of_files
from pyon.lib.io.formats import parse_iwasaki_32c_charged_meson_file, \
    filter_correlators
from pyon.lib.meson import PseudoscalarChargedMeson
import unittest


class TestParsing(unittest.TestCase):
    def setUp(self):
        self.iwasaki_file = os.path.join('testfiles', 'parse', 'f1',
                                         'meson_BOX_RELOADED.src0.ch1-0.3333333333.'
                                         'ch2-0.3333333333.m10.03.m20.03.dat.510')
        self.iwasaki_folder = os.path.join('testfiles', 'parse', 'f1')

    def test_parse_iwasaki(self):
        with open(self.iwasaki_file, 'r') as f:
            raw_data = parse_iwasaki_32c_charged_meson_file(f)
        filtered_data = filter_correlators(raw_data, source='GAM_5', sink='GAM_5', masses=(0.03, 0.03))
        self.failUnlessEqual(filtered_data['data'][0], 4.984743e+06)
        self.failUnlessEqual(filtered_data['masses'], (0.03, 0.03))
        self.failUnlessEqual(filtered_data['source'], 'GAM_5')
        self.failUnlessEqual(filtered_data['config_number'], 510)

    def test_fail_parse_iwasaki(self):
        with open(self.iwasaki_file, 'r') as f:
            raw_data = parse_iwasaki_32c_charged_meson_file(f)
        self.assertRaises(ValueError, filter_correlators, raw_data, source='GAM_5', sink='dfjkdfjk',
                          masses=(0.03, 0.03))

    def test_parse_multiple_iwasaki(self):
        raw_data = []
        for ff in get_list_of_files(self.iwasaki_folder):
            with open(ff, 'r') as f:
                raw_data.append(parse_iwasaki_32c_charged_meson_file(f))
        filtered_data = [filter_correlators(rd, source='GAM_5', sink='GAM_5', masses=(0.03, 0.03)) for rd in raw_data]
        filtered_data.sort(key=lambda k: k['config_number'])
        self.assertEqual(filtered_data[0]['data'][0], 4.984743e+06)
        self.assertEqual(filtered_data[0]['masses'], (0.03, 0.03))
        self.assertEqual(filtered_data[0]['source'], 'GAM_5')
        self.assertEqual(filtered_data[0]['config_number'], 510)
        self.assertNotEqual(filtered_data[1]['config_number'], 510)

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


    @unittest.skip('slow')
    def test_fit_parsed_data(self):
        fit_params = self.fit_test_hadron().average_params
        self.assertTrue(fit_params is not None)  # fail if the fit fails or fit_params don't exist
        mass = fit_params['m']
        c = fit_params['c']
        self.failUnlessAlmostEqual(mass, 0.3212, delta=1e-2)
        self.failUnlessAlmostEqual(c, 1.53, delta=1e-2)

    @unittest.skip('slow')
    def test_fit_parsed_error(self):
        fit_errors = self.fit_test_hadron().errs
        self.assertTrue(fit_errors is not None)  # fail if the fit fails or fit_params don't exist
        m_err = fit_errors['m']
        c_err = fit_errors['c']
        self.failUnlessAlmostEqual(m_err, 0.00044, delta=1e-4)
        self.failUnlessAlmostEqual(c_err, 0.0053, delta=1e-4)
