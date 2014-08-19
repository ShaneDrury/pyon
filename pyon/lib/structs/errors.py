import numpy as np


# class Errors(np.array):  # Probably not needed
#     """
#     Encapsulates errors on data.
#
#     Inherits from numpy array.
#     """
from numpy.core.multiarray import ndarray


class ErrorGeneratorBase(object):
    """
    Generates `Error`s from `Data`.
    """
    def generate_errors(self, data: ndarray, central_data: ndarray=None):
        raise NotImplementedError()

    def generate_central_error(self, data):
        raise NotImplementedError()


class OneErrorGeneratorBase(object):
    """
    Generate one error from one data.
    """
    def generate(self, data):
        raise NotImplementedError()