# Matches scientific notation e.g. 1.2345e+06
RE_SCIENTIFIC = "[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"


def filter_correlators(corrs, **kwargs):
    """
    Only for files. Shouldn't be used in production code
    """
    for corr in corrs:
        matched = True
        for k, v in kwargs.items():
            if corr[k] != v:
                matched = False
                break
        if matched:
            return corr
    raise ValueError("Cannot match {}".format(kwargs))


def filter_one_correlator(corr, **kwargs):
    matched = True
    for k, v in kwargs.items():
        if corr[k] != v:
            matched = False
    return matched
