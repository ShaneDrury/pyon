import numpy as np
# Binning functions
from numpy.core.multiarray import ndarray


def bin_data(configs: list, bin_size: int) -> ndarray:
    """ Averages successive correlators into n_bins bins e.g. n=2 with 4
    samples would give 2 binned samples: Ave(1+2, 3+4)
    """
    num_configs = len(configs)
    # t_extent = len(configs[0])
    n_bins = num_configs / bin_size  # This is integer division e.g. 195 / 2 = 97 bins
    remainder = num_configs % bin_size
    bins = np.reshape(range(0, num_configs-remainder), (n_bins, bin_size))
    binned_configs = np.average(configs[bins], axis=1)
    binned_configs = list(binned_configs)
    # Append the ones we missed without averaging
    [binned_configs.append(configs[-(i+1)]) for i in range(remainder)]
    return np.array(binned_configs)
