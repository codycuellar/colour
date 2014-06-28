# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
**tristimulus.py**

**Platform:**
    Windows, Linux, Mac Os X.

**Description:**
    Defines **Colour** package colour *transformations* objects.

**Others:**

"""

from __future__ import unicode_literals

import math
import numpy

import colour.algebra.matrix
import colour.computation.chromatic_adaptation
import colour.computation.lightness
import colour.dataset.illuminants.chromaticity_coordinates
import colour.utilities.exceptions
import colour.utilities.verbose

__author__ = "Thomas Mansencal"
__copyright__ = "Copyright (C) 2013 - 2014 - Thomas Mansencal"
__license__ = "GPL V3.0 - http://www.gnu.org/licenses/"
__maintainer__ = "Thomas Mansencal"
__email__ = "thomas.mansencal@gmail.com"
__status__ = "Production"

__all__ = ["XYZ_to_xyY",
           "xyY_to_XYZ",
           "xy_to_XYZ",
           "XYZ_to_xy",
           "XYZ_to_RGB",
           "RGB_to_XYZ",
           "xyY_to_RGB",
           "RGB_to_xyY",
           "XYZ_to_UCS",
           "UCS_to_XYZ",
           "UCS_to_uv",
           "UCS_uv_to_xy",
           "XYZ_to_UVW",
           "XYZ_to_Luv",
           "Luv_to_XYZ",
           "Luv_to_uv",
           "Luv_uv_to_xy",
           "Luv_to_LCHuv",
           "LCHuv_to_Luv",
           "XYZ_to_Lab",
           "Lab_to_XYZ",
           "Lab_to_LCHab",
           "LCHab_to_Lab"]

LOGGER = colour.utilities.verbose.install_logger()


def XYZ_to_xyY(XYZ,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE XYZ* colourspace to *CIE xyY* colourspace and reference *illuminant*.

    Reference: http://www.brucelindbloom.com/Eqn_XYZ_to_xyY.html

    Usage::

        >>> XYZ_to_xyY(numpy.matrix([11.80583421, 10.34, 5.15089229]).reshape((3, 1)))
        matrix([[  0.4325],
                [  0.3788],
                [ 10.34  ]])

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE xyY* matrix.
    :rtype: matrix (3x1)
    """

    X, Y, Z = numpy.ravel(XYZ)

    if X == 0 and Y == 0 and Z == 0:
        return numpy.matrix([illuminant[0], illuminant[1], Y]).reshape((3, 1))
    else:
        return numpy.matrix([X / (X + Y + Z), Y / (X + Y + Z), Y]).reshape((3, 1))


def xyY_to_XYZ(xyY):
    """
    Converts from *CIE xyY* colourspace to *CIE XYZ* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_xyY_to_XYZ.html

    Usage::

        >>> xyY_to_XYZ(numpy.matrix([0.4325, 0.3788, 10.34]).reshape((3, 1)))
        matrix([[ 11.80583421],
                [ 10.34      ],
                [  5.15089229]])

    :param xyY: *CIE xyY* matrix.
    :type xyY: matrix (3x1)
    :return: *CIE XYZ* matrix.
    :rtype: matrix (3x1)
    """

    x, y, Y = numpy.ravel(xyY)

    if y == 0:
        return numpy.matrix([0., 0., 0.]).reshape((3, 1))
    else:
        return numpy.matrix([x * Y / y, Y, (1. - x - y) * Y / y]).reshape((3, 1))


def xy_to_XYZ(xy):
    """
    Returns the *CIE XYZ* matrix from given *xy* chromaticity coordinates.

    Usage::

        >>> xy_to_XYZ((0.25, 0.25))
        matrix([[ 1.],
                [ 1.],
                [ 2.]])

    :param xy: *xy* chromaticity coordinate.
    :type xy: tuple
    :return: *CIE XYZ* matrix.
    :rtype: matrix (3x1)
    """

    return xyY_to_XYZ(numpy.matrix([xy[0], xy[1], 1.]).reshape((3, 1)))


def XYZ_to_xy(XYZ,
              illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                  "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Returns the *xy* chromaticity coordinates from given *CIE XYZ* matrix.

    Usage::

        >>> XYZ_to_xy(numpy.matrix([0.97137399, 1., 1.04462134]).reshape((3, 1)))
        (0.32207410281368043, 0.33156550013623531)
        >>> XYZ_to_xy((0.97137399, 1., 1.04462134))
        (0.32207410281368043, 0.33156550013623531)

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *xy* chromaticity coordinates.
    :rtype: tuple
    """

    xyY = numpy.ravel(XYZ_to_xyY(XYZ, illuminant))
    return xyY[0], xyY[1]


def XYZ_to_RGB(XYZ,
               illuminant_XYZ,
               illuminant_RGB,
               chromatic_adaptation_method,
               from_XYZ,
               transfer_function=None):
    """
    Converts from *CIE XYZ* colourspace to *RGB* colourspace using given *CIE XYZ* matrix, *illuminants*,
    *chromatic adaptation* method, *normalised primary matrix* and *transfer function*.

    Usage::

        >>> XYZ = numpy.matrix([11.51847498, 10.08, 5.08937252]).reshape((3, 1))
        >>> illuminant_XYZ =  (0.34567, 0.35850)
        >>> illuminant_RGB =  (0.31271, 0.32902)
        >>> chromatic_adaptation_method =  "Bradford"
        >>> from_XYZ =  numpy.matrix([3.24100326, -1.53739899, -0.49861587, -0.96922426,  1.87592999,  0.04155422, 0.05563942, -0.2040112 ,  1.05714897]).reshape((3, 3))
        >>> XYZ_to_RGB(XYZ, illuminant_XYZ, illuminant_RGB, chromatic_adaptation_method, from_XYZ)
        matrix([[ 17.303501],
                [ 8.8211033],
                [ 5.5672498]])

    :param XYZ: *CIE XYZ* colourspace matrix.
    :type XYZ: matrix (3x1)
    :param illuminant_XYZ: *CIE XYZ* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_XYZ: tuple
    :param illuminant_RGB: *RGB* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_RGB: tuple
    :param chromatic_adaptation_method: *Chromatic adaptation* method.
    :type chromatic_adaptation_method: unicode
    :param from_XYZ: *Normalised primary matrix*.
    :type from_XYZ: matrix (3x3)
    :param transfer_function: *Transfer function*.
    :type transfer_function: object
    :return: *RGB* colourspace matrix.
    :rtype: matrix (3x1)
    """

    cat = colour.computation.chromatic_adaptation.get_chromatic_adaptation_matrix(
        xy_to_XYZ(illuminant_XYZ),
        xy_to_XYZ(illuminant_RGB),
        method=chromatic_adaptation_method)

    adaptedXYZ = cat * XYZ

    RGB = from_XYZ * adaptedXYZ

    if transfer_function is not None:
        RGB = numpy.matrix(map(lambda x: transfer_function(x), numpy.ravel(RGB))).reshape((3, 1))

    LOGGER.debug("> 'Chromatic adaptation' matrix:\n{0}".format(repr(cat)))
    LOGGER.debug("> Adapted 'CIE XYZ' matrix:\n{0}".format(repr(adaptedXYZ)))
    LOGGER.debug("> 'RGB' matrix:\n{0}".format(repr(RGB)))

    return RGB


def RGB_to_XYZ(RGB,
               illuminant_RGB,
               illuminant_XYZ,
               chromatic_adaptation_method,
               to_XYZ,
               inverse_transfer_function=None):
    """
    Converts from *RGB* colourspace to *CIE XYZ* colourspace using given *RGB* matrix, *illuminants*,
    *chromatic adaptation* method, *normalised primary matrix* and *transfer function*.

    Usage::

        >>> RGB = numpy.matrix([17.303501, 8.211033, 5.672498]).reshape((3, 1))
        >>> illuminant_RGB = (0.31271, 0.32902)
        >>> illuminant_XYZ = (0.34567, 0.35850)
        >>> chromatic_adaptation_method =  "Bradford"
        >>> to_XYZ = numpy.matrix([0.41238656, 0.35759149, 0.18045049, 0.21263682, 0.71518298, 0.0721802, 0.01933062, 0.11919716, 0.95037259]).reshape((3, 3)))
        >>> RGB_to_XYZ(RGB, illuminant_RGB, illuminant_XYZ, chromatic_adaptation_method, to_XYZ)
        matrix([[ 11.51847498],
                [ 10.0799999 ],
                [  5.08937278]])

    :param RGB: *RGB* colourspace matrix.
    :type RGB: matrix (3x1)
    :param illuminant_RGB: *RGB* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_RGB: tuple
    :param illuminant_XYZ: *CIE XYZ* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_XYZ: tuple
    :param chromatic_adaptation_method: *Chromatic adaptation* method.
    :type chromatic_adaptation_method: unicode
    :param to_XYZ: *Normalised primary matrix*.
    :type to_XYZ: matrix (3x3)
    :param inverse_transfer_function: *Inverse transfer function*.
    :type inverse_transfer_function: object
    :return: *CIE XYZ* colourspace matrix.
    :rtype: matrix (3x1)
    """

    if inverse_transfer_function is not None:
        RGB = numpy.matrix(map(lambda x: inverse_transfer_function(x), numpy.ravel(RGB))).reshape((3, 1))

    XYZ = to_XYZ * RGB

    cat = colour.computation.chromatic_adaptation.get_chromatic_adaptation_matrix(
        xy_to_XYZ(illuminant_RGB),
        xy_to_XYZ(illuminant_XYZ),
        method=chromatic_adaptation_method)

    adaptedXYZ = cat * XYZ

    LOGGER.debug("> 'CIE XYZ' matrix:\n{0}".format(repr(XYZ)))
    LOGGER.debug("> 'Chromatic adaptation' matrix:\n{0}".format(repr(cat)))
    LOGGER.debug("> Adapted 'CIE XYZ' matrix:\n{0}".format(repr(adaptedXYZ)))

    return adaptedXYZ


def xyY_to_RGB(xyY,
               illuminant_xyY,
               illuminant_RGB,
               chromatic_adaptation_method,
               from_XYZ,
               transfer_function=None):
    """
    Converts from *CIE xyY* colourspace to *RGB* colourspace using given *CIE xyY* matrix, *illuminants*,
    *chromatic adaptation* method, *normalised primary matrix* and *transfer function*.

    Usage::

        >>> xyY = numpy.matrix([0.4316, 0.3777, 10.08]).reshape((3, 1))
        >>> illuminant_xyY = (0.34567, 0.35850)
        >>> illuminant_RGB = (0.31271, 0.32902)
        >>> chromatic_adaptation_method =  "Bradford"
        >>> from_XYZ = numpy.matrix([ 3.24100326, -1.53739899, -0.49861587, -0.96922426,  1.87592999,  0.04155422, 0.05563942, -0.2040112 ,  1.05714897]).reshape((3, 3)))
        >>> xyY_to_RGB(xyY, illuminant_xyY, illuminant_RGB, chromatic_adaptation_method, from_XYZ)
        matrix([[ 17.30350095],
                [  8.21103314],
                [  5.67249761]])

    :param xyY: *CIE xyY* matrix.
    :type xyY: matrix (3x1)
    :param illuminant_xyY: *CIE xyY* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_xyY: tuple
    :param illuminant_RGB: *RGB* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_RGB: tuple
    :param chromatic_adaptation_method: *Chromatic adaptation* method.
    :type chromatic_adaptation_method: unicode
    :param from_XYZ: *Normalised primary matrix*.
    :type from_XYZ: matrix (3x3)
    :param transfer_function: *Transfer function*.
    :type transfer_function: object
    :return: *RGB* colourspace matrix.
    :rtype: matrix (3x1)
    """

    return XYZ_to_RGB(xyY_to_XYZ(xyY),
                      illuminant_xyY,
                      illuminant_RGB,
                      chromatic_adaptation_method,
                      from_XYZ,
                      transfer_function)


def RGB_to_xyY(RGB,
               illuminant_RGB,
               illuminant_xyY,
               chromatic_adaptation_method,
               to_XYZ,
               inverse_transfer_function=None):
    """
    Converts from *RGB* colourspace to *CIE xyY* colourspace using given *RGB* matrix, *illuminants*,
    *chromatic adaptation* method, *normalised primary matrix* and *transfer function*.

    Usage::

        >>> RGB = numpy.matrix([17.303501, 8.211033, 5.672498]).reshape((3, 1))
        >>> illuminant_RGB = (0.31271, 0.32902)
        >>> illuminant_xyY = (0.34567, 0.35850)
        >>> chromatic_adaptation_method = "Bradford"
        >>> to_XYZ = numpy.matrix([0.41238656, 0.35759149, 0.18045049, 0.21263682, 0.71518298, 0.0721802, 0.01933062, 0.11919716, 0.95037259]).reshape((3, 3)))
        >>> RGB_to_xyY(RGB, illuminant_RGB, illuminant_xyY, chromatic_adaptation_method, to_XYZ)
        matrix([[  0.4316    ],
                [  0.37769999],
                [ 10.0799999 ]])

    :param RGB: *RGB* colourspace matrix.
    :type RGB: matrix (3x1)
    :param illuminant_RGB: *RGB* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_RGB: tuple
    :param illuminant_xyY: *CIE xyY* colourspace *illuminant* chromaticity coordinates.
    :type illuminant_xyY: tuple
    :param chromatic_adaptation_method: *Chromatic adaptation* method.
    :type chromatic_adaptation_method: unicode
    :param to_XYZ: *Normalised primary* matrix.
    :type to_XYZ: matrix (3x3)
    :param inverse_transfer_function: *Inverse transfer* function.
    :type inverse_transfer_function: object
    :return: *CIE XYZ* matrix.
    :rtype: matrix (3x1)
    """

    return XYZ_to_xyY(RGB_to_XYZ(RGB,
                                 illuminant_RGB,
                                 illuminant_xyY,
                                 chromatic_adaptation_method,
                                 to_XYZ,
                                 inverse_transfer_function))


def XYZ_to_UCS(XYZ):
    """
    Converts from *CIE XYZ* colourspace to *CIE UCS* colourspace.

    Reference: http://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIEXYZ

    Usage::

        >>> XYZ_to_UCS(numpy.matrix([11.80583421, 10.34, 5.15089229]).reshape((3, 1)))
        matrix([[  7.87055614]
                [ 10.34      ]
                [ 12.18252904]])

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :return: *CIE UCS* matrix.
    :rtype: matrix (3x1)
    """

    X, Y, Z = numpy.ravel(XYZ)

    return numpy.matrix([2. / 3. * X, Y, 1. / 2. * (-X + 3. * Y + Z)]).reshape((3, 1))


def UCS_to_XYZ(UVW):
    """
    Converts from *CIE UCS* colourspace to *CIE XYZ* colourspace.

    Reference: http://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIEXYZ

    Usage::

        >>> UCS_to_XYZ(numpy.matrix([11.80583421, 10.34, 5.15089229]).reshape((3, 1)))
        matrix([[  7.87055614]
                [ 10.34      ]
                [ 12.18252904]])

    :param UVW: *CIE UCS* matrix.
    :type UVW: matrix (3x1)
    :return: *CIE XYZ* matrix.
    :rtype: matrix (3x1)
    """

    U, V, W = numpy.ravel(UVW)

    return numpy.matrix([3. / 2. * U, V, 3. / 2. * U - (3. * V) + (2. * W)]).reshape((3, 1))


def UCS_to_uv(UVW):
    """
    Returns the *uv* chromaticity coordinates from given *CIE UCS* matrix.

    Reference: http://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIEXYZ

    Usage::

        >>> UCS_to_uv(numpy.matrix([11.80583421, 10.34, 5.15089229]).reshape((3, 1)))
        (0.43249999995420702, 0.378800000065942)

    :param UVW: *CIE UCS* matrix.
    :type UVW: matrix (3x1)
    :return: *uv* chromaticity coordinates.
    :rtype: tuple
    """

    U, V, W = numpy.ravel(UVW)

    return U / (U + V + W), V / (U + V + W)


def UCS_uv_to_xy(uv):
    """
    Returns the *xy* chromaticity coordinates from given *CIE UCS* colourspace *uv* chromaticity coordinates.

    Reference: http://en.wikipedia.org/wiki/CIE_1960_color_space#Relation_to_CIEXYZ

    Usage::

        >>> UCS_uv_to_xy((0.2033733344733139, 0.3140500001549052))
        (0.32207410281368043, 0.33156550013623537)

    :param uv: *CIE UCS uv* chromaticity coordinate.
    :type uv: tuple
    :return: *xy* chromaticity coordinates.
    :rtype: tuple
    """

    return 3. * uv[0] / (2. * uv[0] - 8. * uv[1] + 4.), 2. * uv[1] / (2. * uv[0] - 8. * uv[1] + 4.)


def XYZ_to_UVW(XYZ,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE XYZ* colourspace to *CIE 1964 U\*V*\W\** colourspace.

    Reference: http://en.wikipedia.org/wiki/CIE_1964_color_space

    Usage::

        >>> XYZ_to_UCS(numpy.matrix([11.80583421, 10.34, 5.15089229]).reshape((3, 1)))
        matrix([[  7.87055614]
                [ 10.34      ]
                [ 12.18252904]])

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE 1964 U\*V*\W\** matrix.
    :rtype: matrix (3x1)
    """

    x, y, Y = numpy.ravel(XYZ_to_xyY(XYZ, illuminant))
    u, v = numpy.ravel(UCS_to_uv(XYZ_to_UCS(XYZ)))
    u0, v0 = numpy.ravel(UCS_to_uv(XYZ_to_UCS(xy_to_XYZ(illuminant))))

    W = 25. * Y ** (1. / 3.) - 17.
    U = 13. * W * (u - u0)
    V = 13. * W * (v - v0)

    return numpy.matrix([U, V, W]).reshape((3, 1))


def XYZ_to_Luv(XYZ,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE XYZ* colourspace to *CIE Luv* colourspace.

    Reference: http://brucelindbloom.com/Eqn_XYZ_to_Luv.html

    Usage::

        >>> XYZ_to_Luv(numpy.matrix([0.92193107, 1., 1.03744246]).reshape((3, 1)))
        matrix([[ 100.        ]
                [ -20.04304247]
                [ -45.09684555]])

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE Luv* matrix.
    :rtype: matrix (3x1)
    """

    X, Y, Z = numpy.ravel(XYZ)
    Xr, Yr, Zr = numpy.ravel(xy_to_XYZ(illuminant))

    yr = Y / Yr

    L = 116. * yr ** (
        1. / 3.) - 16. if yr > colour.computation.lightness.CIE_E else colour.computation.lightness.CIE_K * yr
    u = 13. * L * ((4. * X / (X + 15. * Y + 3. * Z)) - (4. * Xr / (Xr + 15. * Yr + 3. * Zr)))
    v = 13. * L * ((9. * Y / (X + 15. * Y + 3. * Z)) - (9. * Yr / (Xr + 15. * Yr + 3. * Zr)))

    return numpy.matrix([L, u, v]).reshape((3, 1))


def Luv_to_XYZ(Luv,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE Luv* colourspace to *CIE XYZ* colourspace.

    Reference: http://brucelindbloom.com/Eqn_Luv_to_XYZ.html

    Usage::

        >>> Luv_to_XYZ(numpy.matrix([100., -20.04304247, -19.81676035]).reshape((3, 1)))
        matrix([[ 0.92193107]
                [ 1.        ]
                [ 1.03744246]])

    :param Luv: *CIE Luv* matrix.
    :type Luv: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE XYZ* matrix.
    :rtype: matrix (3x1)
    """

    L, u, v = numpy.ravel(Luv)
    Xr, Yr, Zr = numpy.ravel(xy_to_XYZ(illuminant))

    Y = ((
             L + 16.) / 116.) ** 3. if L > colour.computation.lightness.CIE_E * colour.computation.lightness.CIE_K else L / colour.computation.lightness.CIE_K

    a = 1. / 3. * ((52. * L / (u + 13. * L * (4. * Xr / (Xr + 15. * Yr + 3. * Zr)))) - 1.)
    b = -5. * Y
    c = -1. / 3.0
    d = Y * (39. * L / (v + 13. * L * (9. * Yr / (Xr + 15. * Yr + 3. * Zr))) - 5.)

    X = (d - b) / (a - c)
    Z = X * a + b

    return numpy.matrix([X, Y, Z]).reshape((3, 1))


def Luv_to_uv(Luv,
              illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                  "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Returns the *u'v'* chromaticity coordinates from given *CIE Luv* matrix.

    Reference: http://en.wikipedia.org/wiki/CIELUV#The_forward_transformation

    Usage::

        >>> Luv_to_uv(numpy.matrix([100., -20.04304247, -19.81676035]).reshape((3, 1)))
        (0.19374142100850045, 0.47283165896209456)

    :param Luv: *CIE Luv* matrix.
    :type Luv: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *u'v'* chromaticity coordinates.
    :rtype: tuple
    """

    X, Y, Z = numpy.ravel(Luv_to_XYZ(Luv, illuminant))

    return 4. * X / (X + 15. * Y + 3. * Z), 9. * Y / (X + 15. * Y + 3. * Z)


def Luv_uv_to_xy(uv):
    """
    Returns the *xy* chromaticity coordinates from given *CIE Luv* colourspace *u'v'* chromaticity coordinates.

    Reference: http://en.wikipedia.org/wiki/CIELUV#The_reverse_transformation'.

    Usage::

        >>> Luv_uv_to_xy((0.2033733344733139, 0.3140500001549052))
        (0.32207410281368043, 0.33156550013623537)

    :param uv: *CIE Luv u'v'* chromaticity coordinate.
    :type uv: tuple
    :return: *xy* chromaticity coordinates.
    :rtype: tuple
    """

    return 9. * uv[0] / (6. * uv[0] - 16. * uv[1] + 12.), 4. * uv[1] / (6. * uv[0] - 16. * uv[1] + 12.)


def Luv_to_LCHuv(Luv):
    """
    Converts from *CIE Luv* colourspace to *CIE LCHuv* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_Luv_to_LCH.html

    Usage::

        >>> Luv_to_LCHuv(numpy.matrix([100., -20.04304247, -19.81676035]).reshape((3, 1)))
        matrix([[ 100.        ]
                [  28.18559104]
                [ 224.6747382 ]])

    :param Luv: *CIE Luv* matrix.
    :type Luv: matrix (3x1)
    :return: *CIE LCHuv* matrix.
    :rtype: matrix (3x1)
    """

    L, u, v = numpy.ravel(Luv)

    H = 180. * math.atan2(v, u) / math.pi
    if H < 0.:
        H += 360.

    return numpy.matrix([L, math.sqrt(u ** 2 + v ** 2), H]).reshape((3, 1))


def LCHuv_to_Luv(LCHuv):
    """
    Converts from *CIE LCHuv* colourspace to *CIE Luv* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_LCH_to_Luv.html

    Usage::

        >>> LCHuv_to_Luv(numpy.matrix([100., 28.18559104, 224.6747382]).reshape((3, 1)))
        matrix([[ 100.        ]
                [ -20.04304247]
                [ -19.81676035]])

    :param LCHuv: *CIE LCHuv* matrix.
    :type LCHuv: matrix (3x1)
    :return: *CIE Luv* matrix.
    :rtype: matrix (3x1)
    """

    L, C, H = numpy.ravel(LCHuv)

    return numpy.matrix([L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))]).reshape((3, 1))


def XYZ_to_Lab(XYZ,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE XYZ* colourspace to *CIE Lab* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_XYZ_to_Lab.html

    Usage::

        >>> XYZ_to_Lab(numpy.matrix([0.92193107, 1., 1.03744246]).reshape((3, 1)))
        matrix([[ 100.        ]
                [  -7.41787844]
                [ -15.85742105]])

    :param XYZ: *CIE XYZ* matrix.
    :type XYZ: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE Lab* matrix.
    :rtype: matrix (3x1)
    """

    X, Y, Z = numpy.ravel(XYZ)
    Xr, Yr, Zr = numpy.ravel(xy_to_XYZ(illuminant))

    xr = X / Xr
    yr = Y / Yr
    zr = Z / Zr

    fx = xr ** (1. / 3.) if xr > colour.computation.lightness.CIE_E else (
                                                                             colour.computation.lightness.CIE_K * xr + 16.) / 116.
    fy = yr ** (1. / 3.) if yr > colour.computation.lightness.CIE_E else (
                                                                             colour.computation.lightness.CIE_K * yr + 16.) / 116.
    fz = zr ** (1. / 3.) if zr > colour.computation.lightness.CIE_E else (
                                                                             colour.computation.lightness.CIE_K * zr + 16.) / 116.

    L = 116. * fy - 16.
    a = 500. * (fx - fy)
    b = 200. * (fy - fz)

    return numpy.matrix([L, a, b]).reshape((3, 1))


def Lab_to_XYZ(Lab,
               illuminant=colour.dataset.illuminants.chromaticity_coordinates.ILLUMINANTS.get(
                   "CIE 1931 2 Degree Standard Observer").get("D50")):
    """
    Converts from *CIE Lab* colourspace to *CIE XYZ* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_Lab_to_XYZ.html'.

    Usage::

        >>> Lab_to_XYZ(numpy.matrix([100., -7.41787844, -15.85742105]).reshape((3, 1)))
        matrix([[ 0.92193107]
                [ 0.11070565]
                [ 1.03744246]])

    :param Lab: *CIE Lab* matrix.
    :type Lab: matrix (3x1)
    :param illuminant: Reference *illuminant* chromaticity coordinates.
    :type illuminant: tuple
    :return: *CIE Lab* matrix.
    :rtype: matrix (3x1)
    """

    L, a, b = numpy.ravel(Lab)
    Xr, Yr, Zr = numpy.ravel(xy_to_XYZ(illuminant))

    fy = (L + 16.) / 116.
    fx = a / 500. + fy
    fz = fy - b / 200.

    xr = fx ** 3. if fx ** 3. > colour.computation.lightness.CIE_E else (
                                                                            116. * fx - 16.) / colour.computation.lightness.CIE_K
    yr = ((
              L + 16.) / 116.) ** 3. if L > colour.computation.lightness.CIE_K * colour.computation.lightness.CIE_E else L / colour.computation.lightness.CIE_K
    zr = fz ** 3. if fz ** 3. > colour.computation.lightness.CIE_E else (
                                                                            116. * fz - 16.) / colour.computation.lightness.CIE_K

    X = xr * Xr
    Y = yr * Yr
    Z = zr * Zr

    return numpy.matrix([X, Y, Z]).reshape((3, 1))


def Lab_to_LCHab(Lab):
    """
    Converts from *CIE Lab* colourspace to *CIE LCHab* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_Lab_to_LCH.html

    Usage::

        >>> Lab_to_LCHab(numpy.matrix([100., -7.41787844, -15.85742105]).reshape((3, 1)))
        matrix([[ 100.        ]
                [  17.50664796]
                [ 244.93046842]])

    :param Lab: *CIE Lab* matrix.
    :type Lab: matrix (3x1)
    :return: *CIE LCHab* matrix.
    :rtype: matrix (3x1)
    """

    L, a, b = numpy.ravel(Lab)

    H = 180. * math.atan2(b, a) / math.pi
    if H < 0.:
        H += 360.

    return numpy.matrix([L, math.sqrt(a ** 2 + b ** 2), H]).reshape((3, 1))


def LCHab_to_Lab(LCHab):
    """
    Converts from *CIE LCHab* colourspace to *CIE Lab* colourspace.

    Reference: http://www.brucelindbloom.com/Eqn_LCH_to_Lab.html

    Usage::

        >>> LCHab_to_Lab(numpy.matrix([100., 17.50664796, 244.93046842]).reshape((3, 1)))
        matrix([[ 100.        ]
                [  -7.41787844]
                [ -15.85742105]])

    :param LCHab: *CIE LCHab* matrix.
    :type LCHab: matrix (3x1)
    :return: *CIE Lab* matrix.
    :rtype: matrix (3x1)
    """

    L, C, H = numpy.ravel(LCHab)

    return numpy.matrix([L, C * math.cos(math.radians(H)), C * math.sin(math.radians(H))]).reshape((3, 1))
