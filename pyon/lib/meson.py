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

    @classmethod
    def from_parsed_data(cls, parsed_data):
        """
        Create a :class:`Hadron` from ``parsed_data``. This handles all the \
        duplicate information that the parsed data
        might have. The ``parsed_data`` will be the return value from e.g. \
        :func:`parse_iwasaki_32c_charged_meson_file \
        <.io.formats.parse_iwasaki_32c_charged_meson_file>`
        """
        data = [fd['data'] for fd in parsed_data]
        config_numbers = [fd['config_number'] for fd in parsed_data]
        kwargs = parsed_data[0]  # assume all parameters are the same as the first one
        kwargs.pop('data')
        kwargs.pop('config_number')
        mass_1 = kwargs.pop('mass_1')
        mass_2 = kwargs.pop('mass_2')
        kwargs['masses'] = (mass_1, mass_2)
        charge_1 = kwargs.pop('charge_1')
        charge_2 = kwargs.pop('charge_2')
        kwargs['charges'] = (charge_1, charge_2)
        kwargs['config_numbers'] = config_numbers
        return cls(data, **kwargs)


    @classmethod
    def from_queryset(cls, qs):
        data = []
        im_data = []
        for q in qs:
            corr = q.data.all()
            data.append([s.re for s in corr])
            im_data.append([s.im for s in corr])
        config_numbers = [q.config_number for q in qs]
        q = qs[0]
        time_slices = [s.t for s in q.data.all()]
        kwargs = {
            'source': q.source,
            'sink': q.sink,
            'time_slices': time_slices,
            'im_data': im_data,
            'masses': (q.mass_1, q.mass_2),
            'charges': (q.charge_1, q.charge_2),
            'config_numbers': config_numbers

        }
        return cls(data, **kwargs)

    @staticmethod
    def _fold_one(corr, t_ext):
        return [0.5*(corr[t] + corr[(t_ext-t) % t_ext]) for t in range(t_ext)]

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
