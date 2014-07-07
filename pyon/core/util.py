from collections import OrderedDict


def dict_to_ordered_dict(d, by_key=True):
    """
    Sort by key (or value if by_key=False).
    :param d: A `dict`
    :return: `OrderedDict`
    """
    idx = 0 if by_key else 1
    od = OrderedDict(sorted(d.items(), key=lambda t: t[idx]))
    return od