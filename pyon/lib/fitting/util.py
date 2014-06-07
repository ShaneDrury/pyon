import inspect

__author__ = 'srd1g10'


def convert_initial_value(fit_func, dikt):
    """
    Convert the dict into a list. If we just do dic.values(), the order
    is not deterministic, so do it in the order of the fit function
    arguments.
    """
    func_args = inspect.getargspec(fit_func).args[1:]
    initial_value = [dikt[k] for k in func_args]
    return initial_value


def populate_dict_args(func, vals):
    """
    A minimization function may return unnamed estimates of the variables. \
    This function maps those values to the
    names of the function arguments. Assume that the first argument of \
    ``func`` the independent variable - we skip it.

    :param func: A function with at least two arguments. The first argument \
    is assumed to be an independent variable
        and is skipped.
    :param vals: Values that are associated with each argument.
    :rtype: dict
    """
    func_args = inspect.getargspec(func).args[1:]
    return {k: v for k, v in zip(func_args, vals)}