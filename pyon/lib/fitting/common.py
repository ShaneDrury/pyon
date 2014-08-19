"""
Common use cases for fitting constructed from base classes in base.py
"""
from collections import defaultdict
from functools import partial
import inspect
from numpy.core.multiarray import ndarray
from scipy.optimize import minimize, OptimizeResult
from pyon.lib.fitting.base import FitterBase, FitObjectGeneratorBase, \
    FitObjectBase, FitParams, FitMethodBase
import numpy as np
from pyon.lib.fitting.util import populate_dict_args, better_arg_spec
from pyon.lib.hadron import Hadron
from pyon.lib.resampling import Jackknife, ResamplerBase
from pyon.lib.statistics import get_inverse_cov_matrix
from pyon.lib.structs.errors import ErrorGeneratorBase, OneErrorGeneratorBase


def fit_hadron(hadron: Hadron, initial_value: dict=None, x_range: ndarray=None,
               covariant: bool=False,
               correlated: bool=False, bounds: dict=None, method=None,
               frozen: bool=True) -> FitParams:
    resampler = Jackknife(n=1)
    fit_method = method(hadron.fit_func)
    fitter = create_chi_sq_fitter(hadron.data, x_range, hadron.fit_func,
                                  initial_value, bounds, resampler, fit_method,
                                  frozen, covariant, correlated)
    return fitter.fit()


def fit_data(data, x_range, fit_func, initial_value, bounds, frozen=True,
             covariant=False, correlated=False) -> FitParams:
    """
    Common use case. Jackknife(n=1) resampler, scipy chi-sq fitting.
    """
    resampler = Jackknife(n=1)
    fit_method = ScipyFitMethod(fit_func)
    fitter = create_chi_sq_fitter(data, x_range, fit_func, initial_value,
                                  bounds, resampler, fit_method, frozen,
                                  covariant, correlated)
    return fitter.fit()


def create_chi_sq_fitter(data: ndarray,
                         x_range: ndarray,
                         fit_func: 'callable',
                         initial_value: dict,
                         bounds: dict,
                         resampler: ResamplerBase,
                         fit_method: FitMethodBase,
                         frozen: bool=True,
                         covariant: bool=False,
                         correlated: bool=False) -> FitParams:
    if covariant:
        one_error_generator = CovariantOneErrorGenerator(correlated)
        fit_object_generator = ChiSqCovariantFitObjectGenerator()
    else:
        one_error_generator = UncovariantOneErrorGenerator()
        fit_object_generator = ChiSqFitObjectGenerator()
    fitter = create_fitter(data, x_range, fit_func, initial_value, bounds,
                           resampler, one_error_generator,
                           fit_object_generator, fit_method, frozen)
    return fitter


def create_fitter(data: ndarray,
                  x_range: ndarray,
                  fit_func: 'callable',
                  initial_value: dict,
                  bounds: dict,
                  resampler: ResamplerBase,
                  one_error_generator: OneErrorGeneratorBase,
                  fit_object_generator: FitObjectGeneratorBase,
                  fit_method: FitMethodBase,
                  frozen: bool=True) -> FitParams:
    error_generator = ErrorGenerator(one_error_generator, frozen)
    fitter = Fitter(data, x_range, fit_func, initial_value, bounds, resampler,
                    error_generator, fit_object_generator, fit_method)
    return fitter


class Fitter(FitterBase):
    """
    """
    def __init__(self, data: ndarray,
                 x_range: ndarray,
                 fit_func: 'callable',
                 initial_value: dict,
                 bounds: dict,
                 resampler: ResamplerBase,
                 error_generator: ErrorGeneratorBase,
                 fit_object_generator: FitObjectGeneratorBase,
                 fit_method: FitMethodBase):
        self._data = data
        self._x_range = x_range
        self._fit_func_base = fit_func
        self._initial_value = initial_value
        self._bounds = bounds
        self._resampler = resampler
        self._err_gen = error_generator
        self._fit_obj_gen = fit_object_generator
        self._fit_method = fit_method
        self._central_fit_obj = None  # Set by _prepare()
        self._fit_objects = None  # Set by _prepare()
        self._fit_funcs = None  # Set by _prepare()
        self._resampled_data = np.asarray([])  # Set by _prepare_samples()
        self._ave_resampled = np.asarray([])  # Set by _prepare_ave_resampled()
        self._errors = np.asarray([])  # Set by _prepare_errors()
        self._prepare()

    def _prepare(self):
        self._prepare_data()
        self._prepare_samples()
        self._prepare_ave_resampled()
        self._prepare_fit_funcs()
        self._prepare_central_fit_obj()
        self._prepare_errors()
        self._prepare_fit_objs()

    def _prepare_samples(self):
        self._resampled_data = self._resampler.generate_samples(self._data)

    def _prepare_ave_resampled(self):
        self._ave_resampled = np.average(self._resampled_data, axis=0)

    def _prepare_data(self):
        self._data = self._data[:, self._x_range]

    def _prepare_errors(self):
        self._errors = self._err_gen.generate_errors(self._resampled_data,
                                                     self._data)

    def _prepare_central_fit_obj(self):
        self._central_fit_obj = self._fit_obj_gen.generate(
            np.average(self._data, axis=0),
            self._err_gen.generate_central_error(self._data),
            self._central_fit_func, self._x_range)

    def _prepare_fit_objs(self):
        self._fit_objects = [self._fit_obj_gen.generate(sample, err,
                                                        ff,
                                                        self._x_range)
                             for sample, err, ff in zip(self._ave_resampled,
                                                        self._errors,
                                                        self._fit_funcs)]

    def _prepare_fit_funcs(self):
        self._fit_funcs = [self._fit_func_base for _ in self._data]
        self._central_fit_func = self._fit_func_base

    def fit(self) -> FitParams:
        average_params = self._fit_method.fit_one(self._central_fit_obj,
                                                  self._initial_value,
                                                  self._bounds)
        resampled_params = self._fit_method.fit(self._fit_objects,
                                                self._initial_value,
                                                self._bounds)
        fit_errors = self._resampler.calculate_fit_errors(average_params,
                                                          resampled_params)
        return FitParams(average_params, fit_errors, resampled_params)



class CovariantOneErrorGenerator(OneErrorGeneratorBase):
    def __init__(self, correlated: bool=False):
        self._correlated = correlated
        self._func = partial(get_inverse_cov_matrix,
                             correlated=self._correlated)

    def generate(self, data: ndarray) -> ndarray:
        return self._func(data.T)


class UncovariantOneErrorGenerator(OneErrorGeneratorBase):
    def generate(self, data: ndarray):
        return np.std(data) / len(data)


class ErrorGenerator(ErrorGeneratorBase):
    def __init__(self, one_error_generator: OneErrorGeneratorBase,
                 frozen: bool=True):
        self._frozen = frozen
        self._one_error_gen = one_error_generator.generate

    def generate_errors(self, data: ndarray, central_data: bool=None):
        if self._frozen:
            if central_data is not None:
                err = self._one_error_gen(central_data)
                return np.array([err for _ in central_data])
            else:
                raise NotImplementedError("MEH")
        else:
            return np.array([self._one_error_gen(dat) for dat in data])

    def generate_central_error(self, data: ndarray):
        return np.array(self._one_error_gen(data))


class ChiSqFitObjectGenerator(FitObjectGeneratorBase):
    """
    TODO: Make this into a function
    """
    def generate(self, data: ndarray, errors: ndarray, fit_func: 'callable',
                 x_range: ndarray):
        return GenericChi2(data, errors, x_range, fit_func)


class ChiSqCovariantFitObjectGenerator(FitObjectGeneratorBase):
    """
    TODO: Make this into a function
    """
    def generate(self, data, errors, fit_func, x_range):
        return GenericChi2Covariant(data, errors, x_range, fit_func)


class GenericChi2(FitObjectBase):
    def __init__(self, data: ndarray,
                 errors: ndarray,
                 x_range: ndarray,
                 fit_func: 'callable'):
        self.fit_func = fit_func
        # TODO: probably put the eval stuff in a wrapper or function?

        self.args = better_arg_spec(fit_func)  # extract function signature
        self.data = data
        self.errors = errors
        self.x_range = x_range

    def __call__(self, *args, **kwargs):
        ff = self.fit_func(self.x_range, *args, **kwargs)
        return sum(((self.data - ff) / self.errors)**2)  # / len(self.x_range)


class GenericChi2Covariant(FitObjectBase):
    def __init__(self, data: ndarray, inverse_covariance: ndarray,
                 x_range: ndarray,
                 fit_func: 'callable'):
        self.fit_func = fit_func
        self.args = better_arg_spec(fit_func)
        self.data = data
        self.inverse_cov = inverse_covariance
        self.x_range = x_range

    def __call__(self, *args, **kwargs):
        ff = self.fit_func(self.x_range, *args, **kwargs)
        v = np.array(ff - self.data)
        m = np.array(self.inverse_cov)
        r = np.dot(m, v)
        c2 = np.dot(v, r)
        return c2  # / len(self.x_range)


class ScipyFitMethod(FitMethodBase):
    def __init__(self, fit_func: 'callable'):
        self._fit_func = fit_func

    def _convert_initial_value(self, dic: dict) -> list:
        """
        Convert the dict into a list. If we just do dic.values(), the order
        is not deterministic, so do it in the order of the fit function
        arguments.
        """
        func_args = inspect.getargspec(self._fit_func).args[1:]
        initial_value = [dic[k] for k in func_args]
        return initial_value

    def _convert_fit_output(self, out: OptimizeResult) -> dict:
        return populate_dict_args(self._fit_func, out.x)

    def fit(self, fit_objs: list, initial_value: dict, bounds: tuple) -> dict:
        initial_value = self._convert_initial_value(initial_value)
        fit_params = defaultdict(list)
        for fit_obj in fit_objs:
            # Scipy expects the function to have one argument, so this is a
            # wrapper to unpack those values and forward them to the fit_obj.
            to_fit = lambda p: fit_obj(*p)

            out = minimize(to_fit, initial_value, bounds=bounds)
            for k, v in self._convert_fit_output(out).items():
                fit_params[k].append(v)
            c2 = out.fun / (len(fit_obj.x_range) - len(fit_obj.args) + 1)
            fit_params['chi_sq_dof'].append(c2)
        return fit_params


def map_fit_params_to_dict(fit_params: FitParams) -> dict:
    to_return = {k: FitParams(fit_params.average_params[k],
                              fit_params.errs[k],
                              fit_params.resampled_params[k])
                 for k in fit_params.average_params.keys()}
    return to_return