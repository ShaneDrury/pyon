__author__ = 'srd1g10'
import numpy as np


def get_cov(X, Y):
    """
    Returns covariance of the two vectors ``X`` and ``Y``.
    Formula is: :math:`Cov(X, Y) = 1/(n - 1) \sum_{i = 1}^{n} (x_i - \hat x) (y_i - \hat y)`

    :param X: Vector of floats
    :param Y: Vector of floats
    :rtype: float
    """
    N = len(X)
    mean_x = np.average(X)
    mean_y = np.average(Y)
    total = np.sum([(x - mean_x)*(y - mean_y) for x,y in zip(X,Y)])
    cov = 1.0 / (N - 1.0) * total
    return cov


def get_inverse_cov_matrix(M, correlated=False):
    """
    Returns the inverse covariance matrix of ``M``.

    :param M: The matrix of floats
    :param correlated: Whether the calculation uses the correlated form or not.
    :type correlated: bool
    :rtype: :class:`numpy.matrix`
    """
    Ndata = len(M)
    Nconf = len(M[0])
    cov_matrix = np.zeros((Ndata, Ndata))
    for i in range(Ndata):
        row_i = M[i,:]
        for j in range(Ndata):
            row_j = M[j,:]
            if i != j and not correlated:
                continue
            temp = get_cov(row_i, row_j) / Nconf
            cov_matrix[i][j] = temp
    cov_matrix = np.matrix(cov_matrix)
    invcov = cov_matrix.I
    return invcov