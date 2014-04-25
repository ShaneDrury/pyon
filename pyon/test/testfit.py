from numpy import random
import os
from pyon.lib.fitfunction import pp_flat
from pyon.lib.fitting import ScipyFitter, fit_hadron
from pyon.lib.io.folder import get_list_of_files
from pyon.lib.io.formats import parse_iwasaki_32c_charged_meson_file, \
    filter_correlators
from pyon.lib.meson import PseudoscalarChargedMeson
from pyon.lib.resampling import Jackknife

__author__ = 'srd1g10'
import unittest


class TestFitting(unittest.TestCase):
    def setUp(self):
        """
        Using (0.03, 0.03), (-1, -1) from 0.004 32c
        """
        self.time_extent = 64
        self.corr = [pp_flat(t, 1.0, 1.0, self.time_extent) for t in range(self.time_extent)]
        self.corrs = [[pp_flat(t, 1.0, 1.0, self.time_extent) + random.normal(scale=1e-6)
                       for t in range(self.time_extent)] for _ in range(200)]
        self.iwasaki_folder = os.path.join('testfiles', 'parse', 'f1')
        self.fit_func = lambda t, m, c: pp_flat(t, m, c, self.time_extent)

    def test_make_correlator(self):
        corr = [pp_flat(t, 1.0, 1.0, self.time_extent) for t in range(self.time_extent)]
        self.failUnlessEqual(corr[0], 1.)
        self.failIfEqual(corr[0], 2.)

    def test_fit_one_correlator(self):
        fitter = ScipyFitter(fit_func=self.fit_func)
        fit_params = fitter.fit_one(self.corr,
                                    fit_range=range(1, 32+1),
                                    initial_value=[1.3, 1.0])
        self.failUnless(fit_params is not None)  # fail if the fit fails or fit_params don't exist
        mass = fit_params['m']
        self.failUnlessAlmostEqual(mass, 1.0, delta=1e-3)
        self.failIfAlmostEqual(mass, 2.0, delta=1e-3)

    def test_fail_fit(self):
        fitter = ScipyFitter()
        self.assertRaises(TypeError, fitter.fit_one, self.corr,
                          fit_range=range(1, 32+1),
                          initial_value=[0.8, 1.5])

    def make_hadron(self):
        raw_data = []
        for ff in get_list_of_files(self.iwasaki_folder):
            with open(ff, 'r') as f:
                raw_data.append(parse_iwasaki_32c_charged_meson_file(f))
        filtered_data = [filter_correlators(rd, source='GAM_5', sink='GAM_5', masses=(0.03, 0.03))
                         for rd in raw_data]
        had = PseudoscalarChargedMeson.from_parsed_data(filtered_data)
        had.sort()
        had.fold()
        had.scale()
        return had

    def test_fit_covar(self):
        had = self.make_hadron()
        bnds = ((0., 1.), (0, None))
        fp = fit_hadron(had, fit_range=range(9, 32+1), initial_value=[0.3212, 1.654], covariant=True, bounds=bnds)
        fit_params = fp.average_params
        self.assertTrue(fit_params is not None)  # fail if the fit fails or fit_params don't exist
        mass = fit_params['m']
        c = fit_params['c']
        self.failUnlessAlmostEqual(mass, 0.32120951002753384, delta=1e-6)
        self.failUnlessAlmostEqual(c, 1.6542423508883226, delta=1e-6)

    def test_fit_covar_err(self):
        had = self.make_hadron()
        bnds = ((0., 1.), (0., None))
        fp = fit_hadron(had, fit_range=range(9, 32+1), initial_value=[0.3212, 1.654], covariant=True, bounds=bnds)
        errs = fp.errs
        self.assertTrue(errs is not None)  # fail if the fit fails or fit_params don't exist
        mass = errs['m']
        c = errs['c']
        self.failUnlessAlmostEqual(mass, 0.0003960453177452647, delta=1e-2)
        self.failUnlessAlmostEqual(c, 0.014091062055500116, delta=1e-2)

    def test_fit(self):
        fitter = ScipyFitter(fit_func=self.fit_func)
        f = fitter.fit(self.corrs,
                       fit_range=range(1, 32+1),
                       initial_value=[1.4, 1.5], covariant=False)
        fit_params = f.average_params
        self.assertTrue(fit_params is not None)  # fail if the fit fails or fit_params don't exist
        mass = fit_params['m']
        self.failUnlessAlmostEqual(mass, 1.0, delta=1e-2)
        self.failIfAlmostEqual(mass, 2.0, delta=1e-3)