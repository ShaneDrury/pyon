from collections import namedtuple
import inspect
from scipy.optimize import minimize
from pyon.lib.fitting.binning import bin_data
from pyon.lib.fitting.util import populate_dict_args
from pyon.lib.resampling import Jackknife
import numpy as np
from collections import defaultdict
from pyon.lib.statistics import get_inverse_cov_matrix

FitParams = namedtuple('FitParams', ['average_params', 'errs',
                                     'resampled_params'])
"""
:class:`FitParams` is a namedtuple that packages the things that \
:func:`Fitter.fit` returns.
"""

"""
The recipe for fitting goes:

1. Generate jackknife samples of the data
2. Generate errors from data for the fit
3. Prepare the object to be fit i.e. chi2 or whatever for each sample
4. Fit each sample and get the parameters in a nice form
5. Use the parameters to find the error on the quantity
6. Return central&error for each param in a nice form

Relevant classes/functions for each step
1. Resampler
2. generate_error(data)
3. FitObject create_fit_object?
4. FitMethod or fit(FitObject)
5. Resampler
6. FitParams
"""


class FitterBase(object):
    """
    Fits data.
    """
    def fit(self):
        raise NotImplementedError()


class FitMethod(object):
    """
    Fits a `FitObject`.
    """
    def fit(self, fit_obj, initial_value, bounds):
        raise NotImplementedError()


class ScipyFitMethod(FitMethod):
    def __init__(self, fit_func):
        self.fit_func = fit_func

    def _convert_initial_value(self, dic):
        """
        Convert the dict into a list. If we just do dic.values(), the order
        is not deterministic, so do it in the order of the fit function
        arguments.
        """
        func_args = inspect.getargspec(self.fit_func).args[1:]
        initial_value = [dic[k] for k in func_args]
        return initial_value

    def _convert_fit_output(self, out):
        return populate_dict_args(self.fit_func, out.x)

    def fit(self, fit_obj, initial_value, bounds):
        initial_value = self._convert_initial_value(initial_value)

        def to_fit(p):
            """
            Scipy expects the function to have one argument, so this is a
            wrapper to unpack those values and forward them to the fit_obj.
            """
            return fit_obj(*p)

        out = minimize(to_fit, initial_value, bounds=bounds)
        fit_params = self._convert_fit_output(out)
        return fit_params


class Fitter(FitterBase):
    def __init__(self, data=None, fit_range=None, fit_func=None,
                 initial_value=None, gen_err_func=None, gen_fit_obj=None,
                 fit_method=None, resampler=None, bounds=None, frozen=True,
                 bin_size=1):

        self.bin_size = bin_size
        self.data = self._gen_data(data)
        self.fit_range = fit_range
        self.fit_func = fit_func
        self.initial_value = initial_value
        self.gen_err_func = gen_err_func
        self.gen_fit_obj = gen_fit_obj
        self.fit_method = fit_method
        self.resampler = resampler
        self.frozen = frozen
        self.errors = self._gen_errs()
        self.bounds = bounds

    def _gen_data(self, data):
        data = np.array(data)
        if self.bin_size > 1:
            data = bin_data(data, self.bin_size)
        return data

    def _gen_errs(self):
        if self.frozen:
            errs = self.gen_err_func(self.data)
            errors = [errs for _ in self.data]
        else:
            errors = [self.gen_err_func(sample) for sample in
                      self.resampler.generate_samples(self.data)]
        return errors

    def _gen_resampled_fit_objs(self):
        fit_objs = [self.gen_fit_obj(sample, err, self.fit_range,
                                     self.fit_func)
                    for sample, err in
                    zip(self.resampler.generate_samples(self.data),
                        self.errors)]
        return fit_objs

    def _get_resampled_params(self):
        resampled_params = defaultdict(list)
        fit_objs = self._gen_resampled_fit_objs()
        for fit_obj in fit_objs:
            fit_param = self.fit_method.fit(fit_obj,
                                            self.initial_value, self.bounds)
            for k, v in fit_param.items():
                resampled_params[k].append(v)
        return resampled_params

    def _get_average_params(self):
        average_fit_obj = self.gen_fit_obj(np.average(self.data, axis=0),
                                           np.average(self.errors, axis=0),
                                           self.fit_range, self.fit_func)
        average_params = self.fit_method.fit(average_fit_obj,
                                             self.initial_value, self.bounds)
        return average_params

    def fit(self):
        resampled_params = self._get_resampled_params()
        average_params = self._get_average_params()
        errs = self.resampler.calculate_fit_errors(average_params,
                                                   resampled_params)
        return FitParams(average_params, errs, resampled_params)


def fit_hadron(hadron, initial_value=None, fit_range=None, covariant=False,
               method=None, correlated=False, **kwargs):
    """
    Common use case, uses Scipy for fitting and Jackknife for errors.
    """
    if method is None:
        fitter = fit_chi2_scipy(hadron.data, hadron.fit_func, fit_range,
                                initial_value, covariant=covariant,
                                correlated=correlated, **kwargs)
    else:
        fitter = create_generic_chi2_fitter(hadron.data, method,
                                            hadron.fit_func, fit_range,
                                            initial_value, covariant=covariant,
                                            correlated=correlated, **kwargs)
    return fitter.fit()


def fit_chi2_scipy(data, fit_func=None, fit_range=None, initial_value=None,
                   resampler=None, covariant=False, correlated=False,
                   bounds=None):
    fitter = create_generic_chi2_fitter(data, ScipyFitMethod, fit_func,
                                        fit_range, initial_value, resampler,
                                        covariant, correlated, bounds)
    return fitter


def create_generic_chi2_fitter(data, fit_method=None, fit_func=None,
                               fit_range=None, initial_value=None,
                               resampler=None, covariant=False,
                               correlated=False, bounds=None, frozen=True,
                               bin_size=1):
    resampler = resampler or Jackknife(n=1)
    if covariant:
        def gen_err_func(x):
            return get_inverse_cov_matrix(x[fit_range], correlated)
        gen_fit_obj = make_chi_sq_covar
    else:
        def gen_err_func(x):
            return np.std(x, axis=0) / len(x)
        gen_fit_obj = make_chi_sq
    fitter = Fitter(data, fit_range, fit_func, initial_value, gen_err_func,
                    gen_fit_obj, fit_method, resampler, bounds, frozen,
                    bin_size)
    return fitter


def make_chi_sq(data, errors, fit_range, fit_func):
    data = data[fit_range]
    errors = errors[fit_range]

    def chi_sq(m, c):
        ff = fit_func(fit_range, m, c)
        return sum((data - ff)**2 / errors**2) / len(fit_range)
    return chi_sq


def make_chi_sq_covar(data, inverse_covariance, fit_range, fit_func):
    data = data[fit_range]

    def chi_sq(m, c):
        ff = fit_func(fit_range, m, c)
        v = np.array(ff - data)
        m = np.array(inverse_covariance)
        r = np.dot(m, v)
        c2 = np.dot(v, r)
        return c2 / len(fit_range)
    return chi_sq
