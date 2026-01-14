# -*- coding: utf-8 -*-
# Copyright 2007-2025 The eXSpy developers
#
# This file is part of eXSpy.
#
# eXSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# eXSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with eXSpy. If not, see <https://www.gnu.org/licenses/#GPL>.

import math

import numpy as np

from exspy._misc import elements as elements_module
from exspy.utils.eds import _get_element_and_line, _get_energy_xray_line


def electron_range(element, beam_energy, density="auto", tilt=0):
    """Returns the maximum electron range for a pure bulk material according to
    the Kanaya-Okayama parameterziation.

    Parameters
    ----------
    element : str
        The element symbol, e.g. 'Al'.
    beam_energy : float
        The energy of the beam in keV.
    density : float or str (``'auto'``)
        The density of the material in g/cm3. If 'auto', the density of
        the pure element is used.
    tilt : float
        The tilt of the sample in degrees.

    Returns
    -------
    electron_range : float
        Electron range in micrometers.

    See Also
    --------
    exspy.utils.eds.xray_range

    Examples
    --------
    >>> # Electron range in pure Copper at 30 kV in micron
    >>> exspy.utils.eds.electron_range('Cu', 30.)
    2.8766744984001607

    Notes
    -----
    From Kanaya, K. and S. Okayama (1972). J. Phys. D. Appl. Phys. 5, p43

    See also the textbook of Goldstein et al., Plenum publisher,
    third edition p 72.

    """

    if density == "auto":
        density = elements_module.elements[element]["Physical_properties"][
            "density (g/cm^3)"
        ]
    Z = elements_module.elements[element]["General_properties"]["Z"]
    A = elements_module.elements[element]["General_properties"]["atomic_weight"]
    # Note: magic numbers here are from Kanaya-Okayama parameterization. See
    # docstring for associated references.
    return (
        0.0276
        * A
        / np.power(Z, 0.89)
        / density
        * np.power(beam_energy, 1.67)
        * math.cos(math.radians(tilt))
    )


def xray_range(xray_line, beam_energy, density="auto"):
    """
    Return the maximum range of X-ray generation according to the
    Anderson-Hasler parameterization.

    Parameters
    ----------
    xray_line : str
        The X-ray line, e.g. 'Al_Ka'
    beam_energy : float
        The energy of the beam in kV.
    density : {float, 'auto'}
        The density of the material in g/cm3. If 'auto', the density
        of the pure element is used.

    Returns
    -------
    xray_range : float
        The X-ray range in micrometer.

    See Also
    --------
    exspy.utils.eds.electron_range

    Examples
    --------
    >>> # X-ray range of Cu Ka in pure Copper at 30 kV in micron
    >>> hs.eds.xray_range('Cu_Ka', 30.)
    1.9361716759499248

    >>> # X-ray range of Cu Ka in pure Carbon at 30kV in micron
    >>> hs.eds.xray_range('Cu_Ka', 30., hs.material.elements.C.
    >>>                      Physical_properties.density_gcm3)
    7.6418811280855454

    Notes
    -----
    From Anderson, C.A. and M.F. Hasler (1966). In proceedings of the
    4th international conference on X-ray optics and microanalysis.

    See also the textbook of Goldstein et al., Plenum publisher,
    third edition p 286

    """

    element, line = _get_element_and_line(xray_line)
    if density == "auto":
        density = elements_module.elements[element]["Physical_properties"][
            "density (g/cm^3)"
        ]
    Xray_energy = _get_energy_xray_line(xray_line)
    # Note: magic numbers here are from Andersen-Hasler parameterization. See
    # docstring for associated references.
    return 0.064 / density * (np.power(beam_energy, 1.68) - np.power(Xray_energy, 1.68))
