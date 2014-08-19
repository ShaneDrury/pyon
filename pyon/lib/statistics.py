from numpy.core.multiarray import ndarray

__author__ = 'srd1g10'
import numpy as np


def get_cov(x: ndarray, y: ndarray):
    """
    Returns covariance of the two vectors ``X`` and ``Y``.
    Formula is: :math:`Cov(X, Y) = 1/(n - 1) \sum_{i = 1}^{n} (x_i - \hat x) (y_i - \hat y)`

    :param x: Vector of floats
    :param y: Vector of floats
    :rtype: float
    """
    len_vec = len(x)
    mean_x = np.average(x)
    mean_y = np.average(y)
    total = np.sum([(xx - mean_x)*(yy - mean_y) for xx, yy in zip(x, y)])
    cov = 1.0 / (len_vec - 1.0) * total
    return cov


def get_inverse_cov_matrix(mat: ndarray, correlated: bool=False) -> ndarray:
    """
    Returns the inverse covariance matrix of ``M``.

    :param mat: The matrix of floats
    :param correlated: Whether the calculation uses the correlated form or not.
    :type correlated: bool
    :rtype: :class:`numpy.matrix`
    """
    n_data = len(mat)
    n_conf = len(mat[0])
    cov_matrix = np.zeros((n_data, n_data))
    for i in range(n_data):
        row_i = mat[i, :]
        for j in range(n_data):
            row_j = mat[j, :]
            if i != j and not correlated:
                continue
            temp = get_cov(row_i, row_j) / n_conf
            cov_matrix[i][j] = temp
    cov_matrix = np.asmatrix(cov_matrix)
    invcov = cov_matrix.I
    return invcov.A
