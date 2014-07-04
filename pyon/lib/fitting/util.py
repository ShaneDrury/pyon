import inspect
from io import StringIO
import re

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


def arguments_from_docstring(doc):
    """Parse first line of docstring for argument name

    Docstring should be of the form ``min(iterable[, key=func])``.

    It can also parse cython docstring of the form
    ``Minuit.migrad(self[, int ncall_me =10000, resume=True, int nsplit=1])``
    """
    if doc is None:
        raise RuntimeError('__doc__ is None')
    sio = StringIO(doc.lstrip())
    #care only the firstline
    #docstring can be long
    line = sio.readline()
    if line.startswith("('...',)"):
        line = sio.readline()  # stupid cython
    p = re.compile(r'^[\w|\s.]+\(([^)]*)\).*')
    #'min(iterable[, key=func])\n' -> 'iterable[, key=func]'
    sig = p.search(line)
    if sig is None:
        return []
    # iterable[, key=func]' -> ['iterable[' ,' key=func]']
    sig = sig.groups()[0].split(',')
    ret = []
    for s in sig:
        #print s
        #get the last one after all space after =
        #ex: int x= True
        tmp = s.split('=')[0].split()[-1]
        #clean up non _+alphanum character
        ret.append(''.join(filter(lambda x: str.isalnum(x) or x == '_', tmp)))
        #re.compile(r'[\s|\[]*(\w+)(?:\s*=\s*.*)')
        #ret += self.docstring_kwd_re.findall(s)
    ret = filter(lambda x: x != '', ret)

    if len(ret) == 0:
        raise RuntimeError('Your doc is unparsable\n'+doc)

    return ret


def is_bound(f):
    getattr(f, 'im_self', None) is not None


def better_arg_spec(f, verbose=False):
    """extract function signature

    ..seealso::

        :ref:`function-sig-label`
    """
    # print(f.__call__.func_code)

    try:
        vnames = f.func_code.co_varnames
        #bound method and fake function will be None
        if is_bound(f):
            #bound method dock off self
            return list(vnames[1:f.func_code.co_argcount])
        else:
            #unbound and fakefunc
            return list(vnames[:f.func_code.co_argcount])
    except Exception as e:
        if verbose:
            print(e)  # this might not be such a good dea.
            print("f.func_code.co_varnames[:f.func_code.co_argcount] fails")
            #using __call__ funccode

    try:
        #vnames = f.__call__.func_code.co_varnames

        return list(f.__call__.func_code.co_varnames[1:
        f.__call__.func_code.co_argcount])
    except Exception as e:
        if verbose:
            print(e)  # this too
            print("f.__call__.func_code.co_varnames[1:f.__call__."
                  "func_code.co_argcount] fails")

    try:
        return list(inspect.getargspec(f.__call__)[0][1:])
    except Exception as e:
        if verbose:
            print(e)
            print("inspect.getargspec(f)[0] fails")

    try:
        # print(list(inspect.getargspec(f).args[1:]))
        return list(inspect.getargspec(f).args[1:])
    except Exception as e:
        if verbose:
            print(e)
            print("inspect.getargspec(f)[0] fails")

    #now we are parsing __call__.__doc__
    #we assume that __call__.__doc__ doesn't have self
    #this is what cython gives

    try:
        t = arguments_from_docstring(f.__call__.__doc__)
        if t[0] == 'self':
            t = t[1:]
        return t
    except Exception as e:
        if verbose:
            print(e)
            print("fail parsing __call__.__doc__")

    #how about just __doc__
    try:
        t = arguments_from_docstring(f.__doc__)
        if t[0] == 'self':
            t = t[1:]
        return t
    except Exception as e:
        if verbose:
            print(e)
            print("fail parsing __doc__")
    all_args = inspect.getargspec(f.func).args[1:]
    removed_args = list(f.keywords)
    return diff(all_args, removed_args)


def diff(a, b):
    """
    a - b where a and b are lists
    """
    return [aa for aa in a if aa not in b]


class Struct:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def __str__(self):
        return self.__dict__.__str__()

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, s):
        return self.__dict__[s]