import logging
import os
import re

# Matches scientific notation e.g. 1.2345e+06
RE_SCIENTIFIC = "[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?"

IWASAKI_REGEX = {
    'filename': ("\w+\.src\d+\."
                 "ch1(?P<charge1>{res})\.ch2(?P<charge2>{res})\.".format(res=RE_SCIENTIFIC) +
                 "m1(?P<mass1>{res})\.m2(?P<mass2>{res})\.".format(res=RE_SCIENTIFIC) +
                 "dat\.(?P<config_number>\d+)"),
    'data': ("^STARTPROP\n"
             "^MASSES:\s\s(?P<m1>{res})\s{{3}}(?P<m2>{res})".format(res=RE_SCIENTIFIC) + "\n"
             "^SOURCE:\s(?P<source>\w+)\n"
             "^SINKS:\s(?P<sink>\w+)\n"
             "(?P<data>" + "(^\d+\s\s{res}\s\s{res}".format(res=RE_SCIENTIFIC)
             + "\n)+)"
             "^ENDPROP"),
}
IWASAKI_COMPILED_REGEX = re.compile(IWASAKI_REGEX['data'], re.MULTILINE)


def parse_iwasaki_32c_charged_meson_file(f):
    """
    Parse all the data from an Iwasaki Charged Meson file e.g. \
    meson_BOX_RELOADED.src0.ch1-0.3333333333.ch2-0.3333333333.m10.03.m20.03.dat.510
    """
    data = []
    raw_data = f.read()
    fname = os.path.basename(f.name)
    m = re.match(IWASAKI_REGEX['filename'], fname)
    if m:
        charge_1 = int(round(3 * float(m.group('charge1')), 1))
        charge_2 = int(round(3 * float(m.group('charge2')), 1))
        mass_1 = float(m.group('mass1'))
        mass_2 = float(m.group('mass2'))
        config_number = int(m.group('config_number'))
    else:
        raise re.error("Cannot match filename")
    r = IWASAKI_COMPILED_REGEX
    matched = [m.groupdict() for m in r.finditer(raw_data)]
    for match in matched:
        re_data = []
        im_data = []
        time_slices = []
        for line in match['data'].split('\n'):
            try:
                n, re_c, im_c = line.split()
                re_c = float(re_c)
                im_c = float(im_c)
                n = int(n)
                re_data.append(re_c)
                im_data.append(im_c)
                time_slices.append(n)
            except ValueError:
                pass
        dic = {'source': match['source'],
               'sink': match['sink'],
               'data': re_data,
               'im_data': im_data,
               'time_slices': time_slices,
               'masses': (mass_1, mass_2),
               'charges': (charge_1, charge_2),
               'config_number': config_number}
        data.append(dic)
    return data


def filter_correlators(corrs, **kwargs):
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
