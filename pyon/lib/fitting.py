from collections import namedtuple
import inspect

#from pyon.lib.fitting.scipy import ScipyChi2Fitter
from pyon.lib.resampling import Jackknife





# class Fitter:
#     """
#     :class:`Fitter` fits data.
#
#     :param fit_func: The function we fit to. Used to calculate the chi squared
#     :param resampler: The way we calculate the errors e.g. \
#     :class:`Jackknife <resampling.Jackknife>`
#     """
#     def __init__(self, fit_func=None, resampler=Jackknife(n=1)):
#         self.fit_func = fit_func
#         self.resampler = resampler
#
#     def fit(self, data=None, errors=None, initial_value=None, fit_range=None,
#             covariant=False, correlated=False, **kwargs):
#         """
#         Performs the fit. A specific implementation will use a certain method \
#         of minimizing the chi-squared of
#         ``fit_func`` against the ``data``.
#
#         :param data: Iterable set of independent measurements that the fit \
#         function models.
#         :param errors: Iterable set of errors of each measurement.
#         :param initial_value: Initial guesses of the best fit of the \
#         parameters in ``fit_func``.
#         :type initial_value: dict
#         :param fit_range: Iterable set of numbers that determine the data \
#         points used in the fit. Can be a list of
#             iterables if the fit function requires more than one fit range \
#             e.g. simultaneous fit.
#         :type fit_range: iterable or list of iterables
#         :param covariant: Set the fit as covariant.
#         :type covariant: bool
#         :param correlated: Set the fit as correlated.
#         :type correlated: bool
#         """
#         resampled_params = defaultdict(list)
#         fit_range = np.array(fit_range)
#         initial_value = self._convert_initial_value(initial_value)
#         if covariant:
#             pared_data = np.array([[d[t] for d in data] for t in fit_range])
#             inv_covar = get_inverse_cov_matrix(pared_data, correlated)
#         else:
#             inv_covar = None
#         for sample in self.resampler.generate_samples(data):
#             fit_param = self.fit_one(sample, errors, initial_value, fit_range,
#                                      inverse_covariance=inv_covar,
#                                      **kwargs)
#             for k, v in fit_param.items():
#                 resampled_params[k].append(v)
#
#         average_params = self.fit_one(np.average(data, axis=0),
#                                       errors,
#                                       initial_value, fit_range,
#                                       inverse_covariance=inv_covar, **kwargs)
#         errs = self.resampler.calculate_fit_errors(average_params,
#                                                    resampled_params)
#         return FitParams(average_params, errs, resampled_params)
#
#     def _convert_initial_value(self, dic):
#         """
#         Some fitting functions need a list instead of a dict as an initial
#         guess, so override this function depending on what the function needs.
#         :param dic: A dict of the initial guesses for the fit.
#         :return:
#         """
#         return dic
#
#     def fit_chi_sq(self, **kwargs):
#         """
#         Implement this in a derived class e.g. :func:`ScipyFitter.fit_chi_sq`.
#         """
#         raise NotImplementedError("Implement this in a derived class.")
#
#     def fit_one(self, data=None, errors=None, initial_value=None,
#                 fit_range=None, inverse_covariance=None,
#                 **kwargs):
#
#         chi_sq = self.generate_chi_sq(data=data, errors=errors,
#                                       fit_range=fit_range,
#                                       inverse_covariance=inverse_covariance)
#         # if hessian:
#         #     hess = self._generate_chi_sq_hessian(errors=errors,
#         #                                          fit_range=fit_range,
#         #                                          hessian=hessian)
#         # else:
#         #     hess = None
#         fit_param = self.fit_chi_sq(chi_sq, initial_value=initial_value,
#                                     **kwargs)
#         return fit_param
#
#     def generate_chi_sq(self, data, errors=None, inverse_covariance=None,
#                         fit_range=None):
#         fit_range = np.array(fit_range)
#         d = np.array([data[t] for t in fit_range])
#         if errors is None:
#             e = np.array([1. for _ in fit_range])
#         else:
#             e = np.array([errors[t] for t in fit_range])
#
#         if inverse_covariance is not None:
#             chi_sq = self._generate_chi_sq_covariant(d, inverse_covariance,
#                                                      fit_range, self.fit_func)
#         else:
#             chi_sq = self._generate_chi_sq_uncovariant(d, e, fit_range,
#                                                        self.fit_func)
#         return chi_sq
#
#     @staticmethod
#     def _generate_chi_sq_covariant(data, inverse_covariance, fit_range,
#                                    fit_func):
#         def chi_sq(args):
#             #pared_data = np.array([data[t] for t in fit_range])
#             v = np.array(fit_func(fit_range, *args) - data)
#             m = np.array(inverse_covariance)
#             r = np.dot(m, v)
#             c2 = np.dot(v, r)
#             return c2 / len(fit_range)
#         return chi_sq
#
#     @staticmethod
#     def _generate_chi_sq_uncovariant(data, errors, fit_range, fit_func):
#         #chi_sq = GenericChi2(fit_func, data, errors, fit_range)
#         def chi_sq(args):
#             ff = fit_func(fit_range, *args)
#             return sum((data - ff)**2 / errors**2) / len(fit_range)
#             # return sum([(data[t] - ff[t])**2 / (errors[t])**2
#             #             for t in fit_range]) / len(fit_range)
#             # return sum([(data[t] - fit_func(t, *args))**2 / (errors[t])**2
#             #             for t in fit_range]) / len(fit_range)
#         return chi_sq
#
#         # def _generate_chi_sq_hessian(self, errors, fit_range, hessian):
#         #     def hess(args):
#         #         h_11 = sum([hessian(t, *args)[0]**2 / errors[t]**2
#         #                     for t in fit_range])
#         #         h_12 = sum([hessian(t, *args)[0]*hessian(t, *args)[1] / \
#         # errors[t]**2
#         #                     for t in fit_range])
#         #         h_21 = h_12
#         #         h_22 = sum([hessian(t, *args)[1]**2 / errors[t]**2
#         #                     for t in fit_range])
#         #         return np.asmatrix([[h_11, h_12], [h_21, h_22]])
#         #     return hess
#
#
# class ScipyFitter(Fitter):
#     """
#     Inherits from :class:`Fitter`.
#     """
#
#     def fit_chi_sq(self, chi_sq, initial_value, method='L-BFGS-B',
#                    **kwargs):
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
#         out = minimize(chi_sq, initial_value, method=method,
#                        **kwargs)
#         fit_params = populate_dict_args(self.fit_func, out.x)
#         return fit_params
#
#     def _convert_initial_value(self, dic):
#         """
#         Convert the dict into a list. If we just do dic.values(), the order
#         is not deterministic, so do it in the order of the fit function
#         arguments.
#         """
#         func_args = inspect.getargspec(self.fit_func).args[1:]
#         initial_value = [dic[k] for k in func_args]
#         return initial_value
#
#
