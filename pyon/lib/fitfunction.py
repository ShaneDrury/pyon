__author__ = 'srd1g10'
from functools import partial
import numpy as np


def pp(t, m, z, T=64):
    return 0.5*z*z/m*(np.exp(-m*t) + np.exp(-m*(T-t)))


def aa(t, m, f, Z, T=64):
    return 0.5*f*f*m/(Z*Z)*(np.exp(-m*t) + np.exp(-m*(T-t)))


def ap(t, m, z, f, Z, T=64):
    return 0.5*z*f/Z*(np.exp(-m*t) - np.exp(-m*(T-t)))


def pp_flat(t=1, m=1.0, c=1.0, T=64):
    return c * (np.exp(-m*t) + np.exp(-m*(T-t)))


# def pp_flat_hess(t=1, m=1.0, c=1.0, T=64):
#     h_mm = c * (t * t * np.exp(-m*t) + (T-t)*(T-t) * np.exp(-m*(T-t)))
#     h_mc = -(t * np.exp(-m*t) + (T-t)*np.exp(-m*(T-t)))
#     h_cm = h_mc
#     h_cc = 0.
#     return [[h_mm, h_mc], [h_cm, h_cc]]


def pp_flat_hess(t=1, m=1.0, c=1.0, T=64):
    h_m = -c * (t * np.exp(-m*t) + (T-t)*np.exp(-m*(T-t)))
    h_c = (np.exp(-m*t) + np.exp(-m*(T-t)))
    return [h_m, h_c]


def effective_mass_pp(corr):
    np.seterr('ignore')
    t_ext = len(corr)
    eff = [np.arccosh((corr[(t-1) % t_ext] + corr[(t + 1) % t_ext])/(2. * corr[t % t_ext])) for t in range(t_ext)]
    np.seterr('warn')
    return eff
