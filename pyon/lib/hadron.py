import numpy as np
from pyon.lib.fitfunction import effective_mass_pp
from pyon.lib.fitting.binning import bin_data
from pyon.lib.resampling import Jackknife
import json


class Hadron(object):
    """
    :class:`Hadron` is a representation of a QCD hadron. A particular class
    that inherits from this will specify the ``fit_func`` and how to plot the
    data that represents a certain correlation function.
    """
    def __init__(self, data=None, config_numbers=None, sort=True, source=None,
                 sink=None, im_data=None,
                 time_slices=None):
        self.data = np.array(data)
        if sort and config_numbers:
            self.config_numbers = config_numbers
            self.sort()
        else:
            self.config_numbers = [-1 for _ in self.data]
        self.time_extent = len(data[0])  # Assume it's the same for samples
        self.fit_func = None  # define this in the derived class
        self.source = source
        self.sink = sink
        self.im_data = im_data
        self.time_slices = time_slices

    @classmethod
    def from_parsed_data(cls, parsed_data):
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_data):
        """
        Create :class:`Hadron` from JSON data. Defaults to passing arguments to
        the default constructor.
        """
        return cls(**json.loads(json_data))

    @classmethod
    def from_queryset(cls, qs):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def _name(self):
        raise NotImplementedError

    def dump(self, **kwargs):
        """
        Can override this to call some other serializer to dump e.g. Pickle/raw
         string
        """
        return self.json(**kwargs)

    def json(self, **kwargs):
        """
        Returns the JSON encoded representation of the hadron.

        :param \*\*kwargs: Optional arguments that :func:`json.dumps` takes.
        """
        to_dump = self._to_dump()
        return json.dumps(to_dump, **kwargs)

    def _to_dump(self):
        """
        Specify the fields that will be dumped by :func:`json`.
        See :func:`ScipyFitter._to_dump` for an example of how to inherit and
        adapt this function.
        """
        return {'data': self.data, 'config_numbers': self.config_numbers, 'source': self.source, 'sink': self.sink,
                'im_data': self.im_data, 'time_slices': self.time_slices}

    def sort(self):
        """
        Sorts the data using ``config_numbers`` as a key.
        """
        self.data = np.array([x for (y, x) in sorted(zip(self.config_numbers,
                                                self.data))])
        self.config_numbers.sort()

    def scale(self):
        """
        Scales the data using ``self.central_data[0]`` as a scale factor.
        Scaling can improve the convergence of fitting since we aren't dealing
        with huge numbers.
        """
        scale_factor = self.central_data[0]
        self.data = self.data / scale_factor

    def bin(self, bin_size=1):
        """
        Bin the data to reduce autocorrelation
        """
        self.data = bin_data(self.data, bin_size)

    def fold(self):
        """
        Fold the data to improve statistics. Defaults to PP folding i.e. fold
        down the middle time slice.
        """
        t_ext = self.time_extent
        self.data = np.array([self._fold_one(c, t_ext) for c in self.data])

    @staticmethod
    def _fold_one(corr, t_ext):
        raise NotImplementedError

    @property
    def central_data(self):
        return np.average(self.data, axis=0)

    @property
    def central_errs(self):
        return np.std(self.data, axis=0) / len(self.config_numbers)

    @property
    def effective_mass(self):
        return self._effective_mass_fn(self.central_data)

    @property
    def effective_mass_errs(self):
        """
        Return the central errors on the effective mass. By default this will
        calculate them via jackknife.
        """
        resampler = Jackknife(n=1)
        samples = [self._effective_mass_fn(j) for j in resampler.generate_samples(self.data)]
        errs = [resampler.calculate_errors(cent, col) for col, cent in zip(columns(samples), self.effective_mass)]
        return errs

    @staticmethod
    def _effective_mass_fn(data):
        return effective_mass_pp(data)


def columns(mat):
    for n in range(len(mat[0])):
        yield np.array(mat)[:, n]
