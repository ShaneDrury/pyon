import math
import numpy as np
from numpy.core.multiarray import ndarray

__author__ = 'srd1g10'


class ResamplerBase(object):
    def generate_samples(self, data):
        raise NotImplementedError()

    def calculate_fit_errors(self, central, samples):
        raise NotImplementedError()


class Jackknife(ResamplerBase):
    """
    Jackknife resampler.

    :param n: The ``n`` parameter in the jackknife method.
    :type n: int
    """
    def __init__(self, n=1):
        self.n = n

    def generate_samples(self, data: ndarray):
        length = len(data)
        lists = []
        selectevery = int(length/self.n)
        for j in range(selectevery):
            this_list = []
            for i in range(length):
                if i % selectevery != j:
                    this_list.append(data[i])
            lists.append(this_list)
        return np.swapaxes(lists, 0, 1)
        # return np.array(lists)
        # return np.average(lists, axis=1)

    def calculate_fit_errors(self, central: dict, samples: dict) -> dict:
        fit_errs = {}
        for k, central in central.items():
            fit_errs[k] = self._jackknife_error(central, samples[k])
        return fit_errs

    def calculate_errors(self, central: float, samples: list):
        return self._jackknife_error(central, samples)

    @staticmethod
    def _jackknife_error(c: float, samples: list):
        if not isinstance(samples, np.ndarray):
            samples = np.array(samples)
        s = 0.0
        for l in samples:
            d = c-l
            if math.isnan(d):  # Ignore infinities
                d = 0.0
            s += d*d
        s *= (1.0 - 1.0 / len(samples))
        return np.sqrt(s)


class NoResampler(ResamplerBase):
    """
    Doesn't do any resampling (for testing mainly)
    """
    def generate_samples(self, data):
        return data

    @staticmethod
    def calculate_errors(average_params, resampled_params):
        return np.std(resampled_params)
