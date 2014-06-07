from pyon.lib.statistics import get_inverse_cov_matrix


class UncovariantError(object):
    def __init__(self, errors=None):
        self.errors = errors


class CovariantError(object):
    def __init__(self, data=None, inv_covar=None, correlated=False):
        self.correlated = correlated
        self.inv_covar = inv_covar or get_inverse_cov_matrix(data,
                                                             self.correlated)