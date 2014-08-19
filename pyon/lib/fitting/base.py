from collections import namedtuple
import logging


log = logging.getLogger(__name__)

FitParams = namedtuple('FitParams', ['average_params',
                                     'errs',
                                     'resampled_params'])
"""
:class:`FitParams` is a namedtuple that packages the things that \
:func:`Fitter.fit` returns.
"""

"""
The recipe for fitting goes:

1. Prepare data i.e. self.data = Data(data)
2. Generate Resampled from data and apply fit range
3. Generate errors from data or resampled data
4. Generate fit objects from resampled data, errors, fit function and x_range
5. Using FitMethod, fit each fit object with initial value, bounds
6. The return value of this function is a FitResults instance
7. Use the Resampler to generate errors on the fit results
8. Package these in FitParams and return

---
The structure of the code:

def fit(data, x_range, fit_func, Resampler, ErrorGenerator,
        FitObjectGenerator, FitMethod):

    Data(data) -> data (np.array)
    Resampler(data) -> resampled_data (np.array)
    ErrorGenerator(resampled_data) -> errors (np.array)
    FitObjectGenerator(resampled_data, errors, x_range, fit_func)
        -> fit_objects (list of callables)
    FitMethod(fit_objects) -> fit_results (defaultdict(list))
    Resampler(fit_results) -> fit_errors (list of floats)
    return FitParams(average, errs, resampled)

"""


class FitterBase(object):
    """
    Brings together the other fitting classes.
    """
    def fit(self):
        raise NotImplementedError()


class FitObjectGeneratorBase(object):
    """
    Generates `FitObject`s.
    """
    def generate(self, data, errors, fit_func, x_range):
        raise NotImplementedError()


class FitObjectBase(object):
    """
    The thing to be fitted.

    Takes `Data`, `Errors` and `FitFunction` as parameters. Acts as a callable.
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class FitFunction(object):
    """
    The function to be combined with `Data` and `Errors` to make e.g. chi-sq
    """
    def __call__(self, *args, **kwargs):
        raise NotImplementedError()


class FitMethodBase(object):
    """
    Fits a list of `FitObject`s.
    """
    def fit(self, fit_objs, initial_value, bounds):
        raise NotImplementedError()

    def fit_one(self, fit_obj, initial_value, bounds):
        return {k: v[0]
                for k, v in self.fit([fit_obj], initial_value, bounds).items()}
