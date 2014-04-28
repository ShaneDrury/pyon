import functools
from pyon.lib.fitfunction import pp_flat
from pyon.lib.hadron import Hadron


class Meson(Hadron):
    def __init__(self, data=None, config_numbers=None, masses=None, **kwargs):
        """
        Creates a meson.

        :param data: The measurements of the correlation functions.
        :type data: list of floats
        :param masses: The bare masses of the quarks of the meson.
        :type masses: tuple of floats e.g. (0.01, 0.005)
        """
        super(Meson, self).__init__(data, config_numbers, **kwargs)
        self.masses = masses

    def _to_dump(self):
        to_dump = super(Meson, self)._to_dump()
        to_dump.update({'masses': self.masses})
        return to_dump

    def __str__(self):
        return "{}, Masses: {}".format(self._name, self.masses)

    @property
    def _name(self):
        return "Meson"


class PseudoscalarMeson(Meson):
    """
    A :class:`PseudoscalarMeson` is a :class:`Hadron <hadron.Hadron>`
    consisting of two valence quarks.
    """

    def __init__(self, data=None, config_numbers=None, masses=None, **kwargs):
        """
        Creates an uncharged pseudoscalar meson.

        :param data: The measurements of the correlation functions.
        :type data: list of floats
        :param masses: The bare masses of the quarks of the meson.
        :type masses: tuple of floats e.g. (0.01, 0.005)
        """
        super(PseudoscalarMeson, self).__init__(data, config_numbers, masses,
                                                **kwargs)
        #self.fit_func = functools.partial(pp_flat, T=self.time_extent)
        self.fit_func = lambda t, m, c: pp_flat(t, m, c,
                                                      self.time_extent)
        #self.hess = lambda t, m, c: pp_flat_hess(t, m, c, self.time_extent)

    @property
    def _name(self):
        return "Pseudoscalar Meson"


class PseudoscalarChargedMeson(Meson):
    def __init__(self, data=None, config_numbers=None, masses=None,
                 charges=None, **kwargs):
        super(PseudoscalarChargedMeson, self).__init__(data, config_numbers,
                                                       masses, **kwargs)
        self.charges = charges
        self.fit_func = lambda t, m, c: pp_flat(t, m, c,
                                                      self.time_extent)
        #self.hess = lambda t, m, c: pp_flat_hess(t, m, c, self.time_extent)

    def _to_dump(self):
        to_dump = super(PseudoscalarChargedMeson, self)._to_dump()
        to_dump.update({'charges': self.charges})
        return to_dump

    def __str__(self):
        return super(PseudoscalarChargedMeson, self).__str__() + \
            ", Charges: {}".format(self.charges)

    @property
    def _name(self):
        return "Pseudoscalar Charged Meson"
