# -*- coding: utf-8 -*-
"""
Digital Cinema Distribution Master (DCDM)
=========================================

Defines the *DCDM* opto-electrical transfer function (OETF / OECF) and
electro-optical transfer function (EOTF / EOCF):

-   :func:`colour.models.oetf_DCDM`
-   :func:`colour.models.eotf_DCDM`

See Also
--------
`RGB Colourspaces Jupyter Notebook
<http://nbviewer.jupyter.org/github/colour-science/colour-notebooks/\
blob/master/notebooks/models/rgb.ipynb>`_

References
----------
-   :cite:`DigitalCinemaInitiatives2007b` : Digital Cinema Initiatives. (2007).
    Digital Cinema System Specification - Version 1.1. Retrieved from
    http://www.dcimovies.com/archives/spec_v1_1/\
DCI_DCinema_System_Spec_v1_1.pdf
"""

from __future__ import division, unicode_literals

import numpy as np

__author__ = 'Colour Developers'
__copyright__ = 'Copyright (C) 2013-2018 - Colour Developers'
__license__ = 'New BSD License - http://opensource.org/licenses/BSD-3-Clause'
__maintainer__ = 'Colour Developers'
__email__ = 'colour-science@googlegroups.com'
__status__ = 'Production'

__all__ = ['oetf_DCDM', 'eotf_DCDM']


def oetf_DCDM(XYZ, out_int=False):
    """
    Defines the *DCDM* opto-electronic transfer function (OETF / OECF).

    Parameters
    ----------
    XYZ : numeric or array_like
        *CIE XYZ* tristimulus values.
    out_int : bool, optional
        Whether to return value as integer code value or float equivalent of a
        code value at a given bit depth.

    Returns
    -------
    numeric or ndarray
        Non-linear *CIE XYZ'* tristimulus values.

    References
    ----------
    -   :cite:`DigitalCinemaInitiatives2007b`

    Examples
    --------
    >>> oetf_DCDM(0.18)  # doctest: +ELLIPSIS
    0.1128186...
    >>> oetf_DCDM(0.18, out_int=True)  # doctest: +ELLIPSIS
    461.9922059...
    """

    XYZ = np.asarray(XYZ)

    XYZ_p = (XYZ / 52.37) ** (1 / 2.6)

    if out_int:
        XYZ_p *= 4095

    return XYZ_p


def eotf_DCDM(XYZ_p, in_int=False):
    """
    Defines the *DCDM* electro-optical transfer function (EOTF / EOCF).

    Parameters
    ----------
    XYZ_p : numeric or array_like
        Non-linear *CIE XYZ'* tristimulus values.
    in_int : bool, optional
        Whether to treat the input value as integer code value or float
        equivalent of a code value at a given bit depth.

    Returns
    -------
    numeric or ndarray
        *CIE XYZ* tristimulus values.

    References
    ----------
    -   :cite:`DigitalCinemaInitiatives2007b`

    Examples
    --------
    >>> eotf_DCDM(0.11281860951766724)
    ... # doctest: +ELLIPSIS
    0.18...
    >>> eotf_DCDM(461.99220597484737, in_int=True)
    ... # doctest: +ELLIPSIS
    0.18...
    """

    XYZ_p = np.asarray(XYZ_p)

    if in_int:
        XYZ_p = XYZ_p / 4095

    return 52.37 * XYZ_p ** 2.6
