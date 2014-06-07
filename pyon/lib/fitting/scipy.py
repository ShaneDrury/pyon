import numpy as np

from pyon.lib.fitting.util import convert_initial_value
from pyon.lib.resampling import Jackknife
from pyon.lib.statistics import get_inverse_cov_matrix





# class Fitter(FitterBase):
#     """
#     Uncovariant
#     """
#     def __init__(self, data=None, errors=None, fit_range=None,
#                  fit_func=None, resampler=None,
#                  initial_value=None):
#         self.fit_range = np.array(fit_range)
#         self.data = np.array([data[t] for t in self.fit_range])
#         if errors is None:
#             self.errors = np.array([1. for _ in fit_range])
#         else:
#             self.errors = np.array([errors[t] for t in fit_range])
#         self.initial_value = self._convert_initial_value(initial_value)
#         self.resampler = resampler or Jackknife(n=1)
#         self.fit_func = fit_func
#
#     def fit(self):
#         resampled_params = defaultdict(list)
#         for sample in self.resampler.generate_samples(self.data):
#             fit_param = self.fit_one(sample, self.errors,
#                                      self.initial_value,
#                                      self.fit_range)
#             for k, v in fit_param.items():
#                 resampled_params[k].append(v)
#
#         average_params = self.fit_one(np.average(self.data, axis=0),
#                                       self.errors,
#                                       self.initial_value, self.fit_range)
#         errs = self.resampler.calculate_fit_errors(average_params,
#                                                    resampled_params)
#         return FitParams(average_params, errs, resampled_params)
#
#     def fit_one(self, data=None, errors=None, initial_value=None,
#                 fit_range=None):
#         chi_sq = self.generate_chi_sq(data, errors, fit_range, self.fit_func)
#         fit_param = self.fit_chi_sq(chi_sq, initial_value=initial_value)
#         return fit_param
#
#     def _convert_initial_value(self, dikt):
#         """
#         Convert the dict into a list. If we just do dic.values(), the order
#         is not deterministic, so do it in the order of the fit function
#         arguments.
#         """
#         func_args = inspect.getargspec(self.fit_func).args[1:]
#         initial_value = [dikt[k] for k in func_args]
#         return initial_value
#
#     def generate_chi_sq(self, data, errors, fit_range, fit_func):
#         def chi_sq(args):
#             ff = fit_func(fit_range, *args)
#             return sum((data - ff)**2 / errors**2) / len(fit_range)
#         return chi_sq
#
#     def fit_chi_sq(self, chi_sq, initial_value):
#         """
#         Uses scipy's :func:`minimize <scipy.optimize.minimize>` function to \
#         minimize the ``chi_sq`` of the fit.
#
#         :param initial_value: Initial guesses of the best fit of the \
#         parameters in ``fit_func``
#         :type initial_value: dict
#         :param method: Method of fitting to pass through to \
#         :func:`minimize <scipy.optimize.minimize>`
#         :param \*\*kwargs: Extra parameters to pass in to \
#         :func:`minimize <scipy.optimize.minimize>`
#         :rtype: dict
#         """
#         method = 'L-BFGS-B'
#         out = minimize(chi_sq, initial_value, method=method)
#         fit_params = populate_dict_args(self.fit_func, out.x)
#         return fit_params

# THINK ABOUT THIS CAREFULLY:
# Don't want to inherit as it doesn't satify LSP
# Want to compose but don't want to copy/paste __init__.
# Can do this without copy/pasting.
# class CovariantFitter(FitterBase):
#     def __init__(self, data=None, errors=None, fit_range=None,
#                  fit_func=None, resampler=None,
#                  initial_value=None,
#                  correlated=False):
#         Fitter.__init__(self, data, errors, fit_range, fit_func, resampler,
#                         initial_value)
#         self.correlated = correlated
#         self.inv_covar = get_inverse_cov_matrix(self.data, self.correlated)
#
#     def generate_chi_sq(self, data, errors, fit_range, fit_func):
#         def chi_sq(args):
#             v = np.array(fit_func(fit_range, *args) - data)
#             m = np.array(self.inv_covar)
#             r = np.dot(m, v)
#             c2 = np.dot(v, r)
#             return c2 / len(fit_range)
#         return chi_sq
#


