import math
import numpy as np
from pyon.lib.register import Register

__author__ = 'srd1g10'


registered_resamplers = {}


@Register(registered_resamplers, 'jackknife')
class Jackknife:
    """
    Jackknife resampler.

    :param n: The ``n`` parameter in the jackknife method.
    :type n: int
    """
    def __init__(self, n=1):
        self.n = n

    def generate_samples(self, data):
        length = len(data)
        lists = []
        selectevery = int(length/self.n)
        for j in range(selectevery):
            this_list = []
            for i in range(length):
                if i % selectevery != j:
                    this_list.append(data[i])
            lists.append(this_list)
        return np.average(lists, axis=1)

    def calculate_fit_errors(self, central, samples):
        fit_errs = {}
        for k, central in central.items():
            fit_errs[k] = self._jackknife_error(central, samples[k])
        return fit_errs

    def calculate_errors(self, central, samples):
        return self._jackknife_error(central, samples)

    @staticmethod
    def _jackknife_error(c, samples):
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


@Register(registered_resamplers, 'none')
class NoResampler:
    """
    Doesn't do any resampling (for testing mainly)
    """
    @staticmethod
    def generate_samples(data):
        return data

    @staticmethod
    def calculate_errors(average_params, resampled_params):
        return np.std(resampled_params)

# def jackknife_reduce(data, n=1):
#     """Returns averaged jackknife lists"""
#     lists = [np.average(l, axis=0) for l in generate_jackknife_samples(data, n)]
#     return lists
