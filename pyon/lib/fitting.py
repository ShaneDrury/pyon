from collections import defaultdict, namedtuple
import inspect
from scipy.optimize import minimize
from pyon.lib.register import Register
from pyon.lib.resampling import registered_resamplers
import numpy as np
from pyon.lib.statistics import get_inverse_cov_matrix


__author__ = 'srd1g10'

registered_fitters = {}

FitParams = namedtuple('FitParams', ['average_params', 'errs',
                                     'resampled_params'])
"""
:class:`FitParams` is a namedtuple that packages the things that \
:func:`Fitter.fit` returns.
"""


class Fitter:
    """
    :class:`Fitter` fits data.

    :param fit_func: The function we fit to. Used to calculate the chi squared
    :param resampler: The way we calculate the errors e.g. \
    :class:`Jackknife <resampling.Jackknife>`
    """
    def __init__(self, fit_func=None, resampler='jackknife',
                 resampler_args=None):
        self.fit_func = fit_func
        if resampler_args is None:
            resampler_args = {}
        self.resampler = registered_resamplers[resampler](**resampler_args)

    def fit(self, data=None, errors=None, initial_value=None, fit_range=None,
            covariant=False, correlated=False,
            **kwargs):
        """
        Performs the fit. A specific implementation will use a certain method \
        of minimizing the chi-squared of
        ``fit_func`` against the ``data``.

        :param data: Iterable set of independent measurements that the fit \
        function models.
        :param errors: Iterable set of errors of each measurement.
        :param initial_value: Initial guesses of the best fit of the \
        parameters in ``fit_func``.
        :type initial_value: iterable
        :param fit_range: Iterable set of numbers that determine the data \
        points used in the fit. Can be a list of
            iterables if the fit function requires more than one fit range \
            e.g. simultaneous fit.
        :type fit_range: iterable or list of iterables
        :param covariant: Set the fit as covariant.
        :type covariant: bool
        :param correlated: Set the fit as correlated.
        :type correlated: bool
        """
        resampled_params = defaultdict(list)
        fit_range = np.array(fit_range)
        if covariant:
            pared_data = np.array([[d[t] for d in data] for t in fit_range])
            inv_covar = get_inverse_cov_matrix(pared_data, correlated)
        else:
            inv_covar = None
        for sample in self.resampler.generate_samples(data):
            fit_param = self.fit_one(sample, errors, initial_value, fit_range,
                                     inverse_covariance=inv_covar,
                                     **kwargs)
            for k, v in fit_param.items():
                resampled_params[k].append(v)
        average_params = self.fit_one(np.average(data, axis=0), errors,
                                      initial_value, fit_range,
                                      inverse_covariance=inv_covar, **kwargs)
        errs = self.resampler.calculate_fit_errors(average_params,
                                                   resampled_params)
        return FitParams(average_params, errs, resampled_params)

    def fit_chi_sq(self, **kwargs):
        """
        Implement this in a derived class e.g. :func:`ScipyFitter.fit_chi_sq`.
        """
        raise NotImplementedError("Implement this in a derived class.")

    def fit_one(self, data=None, errors=None, initial_value=None,
                fit_range=None, inverse_covariance=None,
                **kwargs):
        chi_sq = self.generate_chi_sq(data=data, errors=errors,
                                      fit_range=fit_range,
                                      inverse_covariance=inverse_covariance)
        # if hessian:
        #     hess = self._generate_chi_sq_hessian(errors=errors,
        #                                          fit_range=fit_range,
        #                                          hessian=hessian)
        # else:
        #     hess = None
        fit_param = self.fit_chi_sq(chi_sq, initial_value=initial_value,
                                    **kwargs)
        return fit_param

    def generate_chi_sq(self, data, errors=None, inverse_covariance=None,
                        fit_range=None):
        if errors is None:
            errors = [1. for _ in data]
        if inverse_covariance is not None:
            chi_sq = self._generate_chi_sq_covariant(data, inverse_covariance,
                                                     fit_range, self.fit_func)
        else:
            chi_sq = self._generate_chi_sq_uncovariant(data, errors, fit_range,
                                                       self.fit_func)
        return chi_sq

    @staticmethod
    def _generate_chi_sq_covariant(data, inverse_covariance, fit_range,
                                   fit_func):
        def chi_sq(args):
            pared_data = np.array([data[t] for t in fit_range])
            v = np.array(fit_func(fit_range, *args) - pared_data)
            m = np.array(inverse_covariance)
            r = np.dot(m, v)
            c2 = np.dot(v, r)
            return c2 / len(fit_range)
        return chi_sq

    @staticmethod
    def _generate_chi_sq_uncovariant(data, errors, fit_range, fit_func):
        #chi_sq = GenericChi2(fit_func, data, errors, fit_range)
        def chi_sq(args):
            return sum([(data[t] - fit_func(t, *args))**2 / (errors[t])**2
                        for t in fit_range]) / len(fit_range)
        return chi_sq

        # def _generate_chi_sq_hessian(self, errors, fit_range, hessian):
        #     def hess(args):
        #         h_11 = sum([hessian(t, *args)[0]**2 / errors[t]**2
        #                     for t in fit_range])
        #         h_12 = sum([hessian(t, *args)[0]*hessian(t, *args)[1] / \
        # errors[t]**2
        #                     for t in fit_range])
        #         h_21 = h_12
        #         h_22 = sum([hessian(t, *args)[1]**2 / errors[t]**2
        #                     for t in fit_range])
        #         return np.asmatrix([[h_11, h_12], [h_21, h_22]])
        #     return hess




@Register(registered_fitters, 'scipy')
class ScipyFitter(Fitter):
    """
    Inherits from :class:`Fitter`.
    """

    def fit_chi_sq(self, chi_sq, initial_value, method='L-BFGS-B',
                   **kwargs):
        """
        Uses scipy's :func:`minimize <scipy.optimize.minimize>` function to \
        minimize the ``chi_sq`` of the fit.

        :param initial_value: Initial guesses of the best fit of the \
        parameters in ``fit_func``
        :type initial_value: dict
        :param method: Method of fitting to pass through to \
        :func:`minimize <scipy.optimize.minimize>`
        :param \*\*kwargs: Extra parameters to pass in to \
        :func:`minimize <scipy.optimize.minimize>`
        :rtype: dict
        """
        out = minimize(chi_sq, initial_value, method=method,
                       **kwargs)
        fit_params = populate_dict_args(self.fit_func, out.x)
        return fit_params


def populate_dict_args(func, vals):
    """
    A minimization function may return unnamed estimates of the variables. \
    This function maps those values to the
    names of the function arguments. Assume that the first argument of \
    ``func`` the independent variable - we skip it.

    :param func: A function with at least two arguments. The first argument \
    is assumed to be an independent variable
        and is skipped.
    :param vals: Values that are associated with each argument.
    :rtype: dict
    """
    func_args = inspect.getargspec(func).args[1:]
    return {k: v for k, v in zip(func_args, vals)}


def fit_hadron(hadron, initial_value=None, fit_range=None, covariant=False,
               method=None,
               **kwargs):
    """
    Common use case, uses Scipy for fitting and Jackknife for errors.
    """
    if method is None:
        fitter = ScipyFitter(fit_func=hadron.fit_func,
                             resampler='jackknife')
    else:
        fitter = method(fit_func=hadron.fit_func,
                        resampler='jackknife')
    return fitter.fit(hadron.data, hadron.central_errs,
                      initial_value=initial_value, fit_range=fit_range,
                      covariant=covariant, **kwargs)
