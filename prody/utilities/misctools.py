"""This module defines miscellaneous utility functions."""

from numpy import unique, linalg, diag, sqrt, dot, chararray
from numpy import diff, where, insert, nan, loadtxt, array
from collections import Counter

__all__ = ['Everything', 'rangeString', 'alnum', 'importLA', 'dictElement',
           'intorfloat', 'startswith', 'showFigure', 'countBytes', 'sqrtm',
           'saxsWater', 'count', 'addBreaks', 'copy', 'dictElementLoop', 
           'getDataPath', 'openData', 'chr2', 'toChararray']


class Everything(object):

    """A place for everything."""

    def __contains__(self, what):

        return True


def rangeString(lint, sep=' ', rng=' to ', exc=False, pos=True):
    """Returns a structured string for a given list of integers.

    :arg lint: integer list or array
    :arg sep: range or number separator
    :arg rng: range symbol
    :arg exc: set **True** if range symbol is exclusive
    :arg pos: only consider zero and positive integers

    .. ipython:: python

       from prody.utilities import rangeString
       lint = [1, 2, 3, 4, 10, 15, 16, 17]
       rangeString(lint)
       rangeString(lint, sep=',', rng='-')
       rangeString(lint, ',', ':', exc=True)"""

    ints = unique(lint)
    if pos and ints[0] < 0:
        ints = ints[ints > -1]

    prev = ints[0]
    lint = [[prev]]
    for i in ints[1:]:
        if i - prev > 1:
            lint.append([i])
        else:
            lint[-1].append(i)
        prev = i
    exc = int(exc)
    return sep.join([str(l[0]) if len(l) == 1 else
                     str(l[0]) + rng + str(l[-1] + exc) for l in lint])


def alnum(string, alt='_', trim=False, single=False):
    """Replace non alpha numeric characters with *alt*.  If *trim* is **True**
    remove preceding and trailing *arg* characters.  If *single* is **True**,
    contain only a single joining *alt* character. """

    result = ''
    multi = not bool(single)
    prev = None
    for char in string:
        if char.isalnum():
            result += char
            prev = char
        else:
            if multi or prev != alt:
                result += alt
            prev = alt
    trim = int(bool(trim))
    result = result[trim * (result[0] == alt):
                    len(result) - trim * (result[-1] == alt)]
    return result


def importLA():
    """Returns one of :mod:`scipy.linalg` or :mod:`numpy.linalg`."""

    try:
        import scipy.linalg as linalg
    except ImportError:
        try:
            import numpy.linalg as linalg
        except:
            raise ImportError('scipy.linalg or numpy.linalg is required for '
                              'NMA and structure alignment calculations')
    return linalg


def dictElement(element, prefix=None, number_multiples=False):
    """Returns a dictionary built from the children of *element*, which must be
    a :class:`xml.etree.ElementTree.Element` instance.  Keys of the dictionary
    are *tag* of children without the *prefix*, or namespace.  Values depend on
    the content of the child.  If a child does not have any children, its text
    attribute is the value.  If a child has children, then the child is the
    value.
    """
    if type(element) in [str, list, int]:
        raise TypeError('element should be an Element not str, list or int')

    dict_ = {}
    length = False
    if isinstance(prefix, str):
        length = len(prefix)

    prev_tag = ''
    for child in element:
        tag = child.tag

        if length and tag.startswith(prefix):
            tag = tag[length:]

        if tag != prev_tag:
            prev_tag = tag
            i = 0
        else:
            i += 1

        if number_multiples:
            tag = tag + '{:>4}'.format(str(i))
            
        if len(child) == 0:
            if child.text is None:
                dict_[tag] = child.items()
            else:
                dict_[tag] = child.text
        else:
            dict_[tag] = child

    return dict_

def dictElementLoop(dict_, keys, prefix=None, number_multiples=False):
    if isinstance(keys, str):
        keys = [keys]

    if not isinstance(keys, list) or len(keys) is None:
        raise TypeError('keys should be a list of keys')

    for key in keys:
        if not key in dict_.keys():
            raise ValueError('all keys should be keys of dict_')

    for orig_key in keys:
        dict2 = dictElement(dict_[orig_key], prefix, number_multiples)
        finished = 0
        while not finished:
            dict3 = dict2.copy()
            try:
                key = dict2.keys()[0]
                dict2[key] = dictElement(dict2[key], prefix, number_multiples)
            except:
                finished = 1
            else:
                dict2 = dict3
                for key in dict2.keys():
                    dict2[key] = dictElement(dict2[key], prefix, number_multiples)

        dict_[orig_key] = dict2

    return dict_

def intorfloat(x):
    """Returns ``int(x)``, or ``float(x)`` upon :exc:`ValueError`."""

    try:
        return int(x)
    except ValueError:
        return float(x)


def startswith(this, that):
    """Returns **True** if *this* or *that* starts with the other."""

    if len(this) < len(that):
        return that.startswith(this)
    else:
        return this.startswith(that)


def showFigure():
    """Call :func:`~matplotlib.pyplot.show` function with ``block=False``
    argument to avoid blocking behavior in non-interactive sessions.  If
    *block* keyword argument is not recognized, try again without it."""

    from matplotlib.pyplot import show
    try:
        show(block=False)
    except TypeError:
        show()


def countBytes(arrays, base=False):
    """Returns total number of bytes consumed by elements of arrays.  If
    *base* is **True**, use number of bytes from the base array."""

    if base:
        getbase = lambda arr: arr if arr.base is None else getbase(arr.base)
        nbytes = lambda arr: getbase(arr).nbytes
    else:
        nbytes = lambda arr: arr.nbytes

    return sum(nbytes(arr) for arr in arrays)

def sqrtm(matrix):
    """Returns the square root of a matrix."""
    (U,S,VT)=linalg.svd(matrix)
    D = diag(sqrt(S))
    return dot(dot(U,D),VT)

def getMasses(elements):
    """Gets the mass atom. """
    
    import numpy as np
    mass_dict = {'C':12,'N':14,'S':32,'O':16,'H':1}

    if isinstance(elements, str):
        return mass_dict[elements]
    else:
        masses = np.zeros(len(elements))
        for i,element in enumerate(elements):
            if element in mass_dict:
                masses[i] = mass_dict[element]
            else:
                masses[i] = 0.
        return masses

def count(L, a=None):
    return len([b for b in L if b is a])

def addBreaks(x, y, axis=0):
    """Finds breaks in x, extends them by one position and adds NaN at the 
    corresponding position in y. x needs to be an 1-D array, y can be a 
    matrix of column (or row) vectors"""

    d = diff(x)
    counter = Counter(d)
    step = counter.most_common(1)[0][0]

    breaks = where(d != step)[0]
    for b in reversed(breaks):
        x = insert(x, b+1, x[b]+step)
        y = insert(y, b+1, nan, axis=axis)

    return x, y

def copy(x):
    if x is None:
        return None
    return x.copy()

def getDataPath(filename):
    import pkg_resources
    return pkg_resources.resource_filename('prody.utilities', 'datafiles/%s'%filename)

def openData(filename, mode='rb'):
    return open(getDataPath(filename), mode)

def saxsWater():
    filename = getDataPath('saxs_water.dat')
    return loadtxt(filename, delimiter=',')

def chr2(a):
    try:
        c = chr(a)
    except TypeError:
        c = str(a)
    return c

def toChararray(arr, aligned=False):
    arr = array(arr, dtype='|S')
    try:
        ndim, dtype_, shape = arr.ndim, arr.dtype, arr.shape
    except AttributeError:
        raise TypeError('arr is not a Numpy array')

    if ndim < 1:
        raise ValueError('arr.ndim should be at least 1')
    if dtype_.char != 'S':
        raise ValueError('arr must be a character array')

    if ndim != 2:
        n_seq = shape[0]
        l_seq = dtype_.itemsize
        new_arr = chararray((n_seq, l_seq))
        for i, s in enumerate(arr):
            for j in range(l_seq):
                if j < len(s):
                    new_arr[i, j] = chr2(s[j])
                else:
                    if aligned:
                        raise ValueError('arr does not the same lengths')
                    new_arr[i, j] = '.'
    else:
        new_arr = array(arr, dtype='|S1')
    return new_arr