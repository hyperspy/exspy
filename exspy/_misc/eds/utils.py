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
from functools import reduce

from hyperspy.misc.utils import display, stack, DictionaryTreeBrowser
import numpy as np
from prettytable import PrettyTable
from scipy import constants

from exspy._docstrings.eds import (
    FLOAT_FORMAT_PARAMETER,
    ENERGY_RANGE_PARAMETER,
    ONLY_LINES_PARAMETER,
    SORTING_PARAMETER,
    WEIGHT_THRESHOLD_PARAMETER,
    WIDTH_PARAMETER,
)
from exspy._misc.elements import elements as elements_db


eV2keV = 1000.0
sigma2fwhm = 2 * math.sqrt(2 * math.log(2))


_ABSORPTION_CORRECTION_DOCSTRING = """absorption_correction : numpy.ndarray or None
        If None (default), absorption correction is ignored, otherwise, the
        array must contain values between 0 and 1 to correct the intensities
        based on estimated absorption.
"""


def _get_element_and_line(xray_line):
    """
    Returns the element name and line character for a particular X-ray line as
    a tuple.

    By example, if xray_line = 'Mn_Ka' this function returns ('Mn', 'Ka')
    """
    lim = xray_line.find("_")
    if lim == -1:
        raise ValueError(f"Invalid xray-line: {xray_line}")
    return xray_line[:lim], xray_line[lim + 1 :]


def _get_energy_xray_line(xray_line):
    """
    Returns the energy (in keV) associated with a given X-ray line.

    By example, if xray_line = 'Mn_Ka' this function returns 5.8987
    """
    element, line = _get_element_and_line(xray_line)
    return elements_db[element]["Atomic_properties"]["Xray_lines"][line]["energy (keV)"]


def _get_xray_lines_family(xray_line):
    """
    Returns the family to which a particular X-ray line belongs.

    By example, if xray_line = 'Mn_Ka' this function returns 'Mn_K'
    """
    return xray_line[: xray_line.find("_") + 2]


def _parse_only_lines(only_lines):
    if isinstance(only_lines, str):
        pass
    elif hasattr(only_lines, "__iter__"):
        if any(isinstance(line, str) is False for line in only_lines):
            return only_lines
    else:
        return only_lines
    only_lines = list(only_lines)
    for only_line in only_lines:
        if only_line == "a":
            only_lines.extend(["Ka", "La", "Ma"])
        elif only_line == "b":
            only_lines.extend(["Kb", "Lb1", "Mb"])
    return only_lines


def get_xray_lines_near_energy(energy, width=0.2, only_lines=None):
    """
    Find xray lines near a specific energy, more specifically all xray lines
    that satisfy ``only_lines`` and are within the given energy window width
    around the passed energy.

    Parameters
    ----------
    energy : float
        Energy to search near in keV
    %s
    %s

    Returns
    -------
    xray_lines : list
        List of xray-lines sorted by energy difference to the given energy.

    See also
    --------
    get_xray_lines, print_lines, print_lines_near_energy
    """
    only_lines = _parse_only_lines(only_lines)
    valid_lines = []
    E_min, E_max = energy - width / 2.0, energy + width / 2.0
    for element, el_props in elements_db.items():
        # Not all elements in the DB have the keys, so catch KeyErrors
        try:
            lines = el_props["Atomic_properties"]["Xray_lines"]
        except KeyError:
            continue
        for line, l_props in lines.items():
            if only_lines and line not in only_lines:
                continue
            line_energy = l_props["energy (keV)"]
            if E_min <= line_energy <= E_max:
                # Store line in Element_Line format, and energy difference
                valid_lines.append((element + "_" + line, abs(line_energy - energy)))

    # Sort by energy difference, but return only the line names
    return [line for line, _ in sorted(valid_lines, key=lambda x: x[1])]


get_xray_lines_near_energy.__doc__ %= (WIDTH_PARAMETER, ONLY_LINES_PARAMETER)


def get_FWHM_at_Energy(energy_resolution_MnKa, E):
    """
    Calculates an approximate FWHM, accounting for peak broadening due to the
    detector, for a peak at energy E given a known width at a reference energy.

    The factor 2.5 is a constant derived by Fiori & Newbury as references
    below.

    Parameters
    ----------
    energy_resolution_MnKa : float
        Energy resolution of Mn Ka in eV
    E : float
        Energy of the peak in keV

    Returns
    -------
    FWHM : float
        FWHM of the peak in keV

    Notes
    -----
    This method implements the equation derived by Fiori and Newbury as is
    documented in the following:

        Fiori, C. E., and Newbury, D. E. (1978). In SEM/1978/I, SEM, Inc.,
        AMF O'Hare, Illinois, p. 401.

        Goldstein et al. (2003). "Scanning Electron Microscopy & X-ray
        Microanalysis", Plenum, third edition, p 315.

    """
    FWHM_ref = energy_resolution_MnKa
    E_ref = _get_energy_xray_line("Mn_Ka")

    FWHM_e = 2.5 * (E - E_ref) * eV2keV + FWHM_ref * FWHM_ref

    return math.sqrt(FWHM_e) / 1000.0  # In mrad


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
        density = elements_db[element]["Physical_properties"]["density (g/cm^3)"]
    Xray_energy = _get_energy_xray_line(xray_line)
    # Note: magic numbers here are from Andersen-Hasler parameterization. See
    # docstring for associated references.
    return 0.064 / density * (np.power(beam_energy, 1.68) - np.power(Xray_energy, 1.68))


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
    >>> hs.eds.electron_range('Cu', 30.)
    2.8766744984001607

    Notes
    -----
    From Kanaya, K. and S. Okayama (1972). J. Phys. D. Appl. Phys. 5, p43

    See also the textbook of Goldstein et al., Plenum publisher,
    third edition p 72.

    """

    if density == "auto":
        density = elements_db[element]["Physical_properties"]["density (g/cm^3)"]
    Z = elements_db[element]["General_properties"]["Z"]
    A = elements_db[element]["General_properties"]["atomic_weight"]
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


def take_off_angle(tilt_stage, azimuth_angle, elevation_angle, beta_tilt=0.0):
    """Calculate the take-off-angle (TOA).

    TOA is the angle with which the X-rays leave the surface towards
    the detector.

    Parameters
    ----------
    alpha_tilt : float
        The alpha-tilt of the stage in degrees. The sample is facing the detector
        when positively tilted.
    azimuth_angle : float
        The azimuth of the detector in degrees. 0 is perpendicular to the alpha
        tilt axis.
    elevation_angle : float
        The elevation of the detector in degrees.
    beta_tilt : float
        The beta-tilt of the stage in degrees. The sample is facing positive 90
        in the azimuthal direction when positively tilted.

    Returns
    -------
    take_off_angle : float
        The take off angle in degrees.

    Examples
    --------
    >>> hs.eds.take_off_angle(alpha_tilt=10., beta_tilt=0.
    >>>                          azimuth_angle=45., elevation_angle=22.)
    28.865971201155283
    """

    if tilt_stage is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Stage.tilt_alpha` is not set."
        )

    if azimuth_angle is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Detector.EDS.azimuth_angle` is not set."
        )

    if elevation_angle is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Detector.EDS.elevation_angle` is not set."
        )

    alpha = math.radians(tilt_stage)
    beta = -math.radians(beta_tilt)
    phi = math.radians(azimuth_angle)
    theta = -math.radians(elevation_angle)

    return 90 - math.degrees(
        np.arccos(
            math.sin(alpha) * math.cos(beta) * math.cos(phi) * math.cos(theta)
            - math.sin(beta) * math.sin(phi) * math.cos(theta)
            - math.cos(alpha) * math.cos(beta) * math.sin(theta)
        )
    )


def xray_lines_model(
    elements,
    beam_energy=200,
    weight_percents=None,
    energy_resolution_MnKa=130,
    energy_axis=None,
):
    """
    Generate a model of X-ray lines using a Gaussian distribution for each
    peak.

    The area under a main peak (alpha) is equal to 1 and weighted by the
    composition.

    Parameters
    ----------
    elements : list of strings
        A list of chemical element symbols.
    beam_energy: float
        The energy of the beam in keV.
    weight_percents: list of float
        The composition in weight percent.
    energy_resolution_MnKa: float
        The energy resolution of the detector in eV
    energy_axis: dic
        The dictionary for the energy axis. It must contains 'size' and the
        units must be 'eV' of 'keV'.

    Example
    -------
    >>> s = xray_lines_model(['Cu', 'Fe'], beam_energy=30)
    >>> s.plot()
    """
    from exspy.signals.eds_tem import EDSTEMSpectrum

    if energy_axis is None:
        energy_axis = {
            "name": "E",
            "scale": 0.01,
            "units": "keV",
            "offset": -0.1,
            "size": 1024,
        }
    s = EDSTEMSpectrum(np.zeros(energy_axis["size"]), axes=[energy_axis])
    s.set_microscope_parameters(
        beam_energy=beam_energy, energy_resolution_MnKa=energy_resolution_MnKa
    )
    s.add_elements(elements)
    counts_rate = 1.0
    live_time = 1.0
    if weight_percents is None:
        weight_percents = [100.0 / len(elements)] * len(elements)
    m = s.create_model(auto_background=False)
    weight_percent_dict = {
        element_: weight_ for element_, weight_ in zip(elements, weight_percents)
    }
    if len(elements) == len(weight_percents):
        for component in m.xray_lines:
            element = component.name.split("_")[0]
            component.A.value = (
                live_time * counts_rate * weight_percent_dict[element] / 100
            )
    else:
        raise ValueError(
            "The number of elements specified is not the same "
            "as the number of weight_percents"
        )

    # make sure all values are set
    m.assign_current_values_to_all()

    s.data = m.as_signal().data
    return s


def quantification_cliff_lorimer(
    intensities, kfactors, absorption_correction=None, mask=None
):
    """
    Quantification using Cliff-Lorimer

    Parameters
    ----------
    intensities: numpy.array
        the intensities for each X-ray lines. The first axis should be the
        elements axis.
    kfactors: list of float
        The list of kfactor in same order as intensities eg. kfactors =
        [1, 1.47, 1.72] for ['Al_Ka','Cr_Ka', 'Ni_Ka']
    %s
    mask: array of bool, signal of bool or None
        The mask with the dimension of intensities[0]. If a pixel is True,
        the composition is set to zero.

    Return
    ------
    numpy.array containing the weight fraction with the same
    shape as intensities.
    """
    # Value used as an threshold to prevent using zeros as denominator
    min_intensity = 0.1
    dim = intensities.shape
    dim2 = reduce(lambda x, y: x * y, dim[1:])
    intens = intensities.reshape(dim[0], dim2).astype(float)

    if absorption_correction is None:
        # default to ones
        absorption_correction = np.ones_like(intens, dtype=float)
    else:
        absorption_correction = absorption_correction.reshape(dim[0], dim2)

    for i in range(dim2):
        index = np.where(intens[:, i] > min_intensity)[0]
        if len(index) > 1:
            ref_index, ref_index2 = index[:2]
            intens[:, i] = _quantification_cliff_lorimer(
                intens[:, i],
                kfactors,
                absorption_correction[:, i],
                ref_index,
                ref_index2,
            )
        else:
            intens[:, i] = np.zeros_like(intens[:, i])
            if len(index) == 1:
                intens[index[0], i] = 1.0

    intens = intens.reshape(dim)
    if mask is not None:
        from hyperspy.signals import BaseSignal

        if isinstance(mask, BaseSignal):
            mask = mask.data
        if mask.dtype != bool:
            mask = mask.astype(bool)
        for i in range(dim[0]):
            intens[i][mask] = 0

    return intens


quantification_cliff_lorimer.__doc__ %= _ABSORPTION_CORRECTION_DOCSTRING


def _quantification_cliff_lorimer(
    intensities, kfactors, absorption_correction, ref_index=0, ref_index2=1
):
    """
    Quantification using Cliff-Lorimer

    Parameters
    ----------
    intensities: numpy.array
        the intensities for each X-ray lines. The first axis should be the
        elements axis.
    absorption_correction: numpy.ndarray
        value between 0 and 1 in order to correct the intensities based on
        estimated absorption.
    kfactors: list of float
        The list of kfactor in same order as  intensities eg. kfactors =
        [1, 1.47, 1.72] for ['Al_Ka','Cr_Ka', 'Ni_Ka']
    ref_index, ref_index2: int
        index of the elements that will be in the denominator. Should be non
        zeros if possible.

    Return
    ------
    numpy.array containing the weight fraction with the same
    shape as intensities.
    """
    if len(intensities) != len(kfactors):
        raise ValueError(
            "The number of kfactors must match the size of the "
            "first axis of intensities."
        )

    ab = np.zeros_like(intensities, dtype="float")
    composition = np.ones_like(intensities, dtype="float")
    # ab = Ia/Ib / kab
    other_index = list(range(len(kfactors)))
    other_index.pop(ref_index)
    for i in other_index:
        ab[i] = (
            (intensities[ref_index] * absorption_correction[ref_index])
            / (intensities[i] * absorption_correction[i])
            * (kfactors[ref_index] / kfactors[i])
        )
    # Ca = ab /(1 + ab + ab/ac + ab/ad + ...)
    for i in other_index:
        if i == ref_index2:
            composition[ref_index] += ab[ref_index2]
        else:
            composition[ref_index] += ab[ref_index2] / ab[i]
    composition[ref_index] = ab[ref_index2] / composition[ref_index]
    # Cb = Ca / ab
    for i in other_index:
        composition[i] = composition[ref_index] / ab[i]
    return composition


def quantification_zeta_factor(intensities, zfactors, dose, absorption_correction=None):
    """
    Quantification using the zeta-factor method

    Parameters
    ----------
    intensities: numpy.array
        The intensities for each X-ray line. The first axis should be the
        elements axis.
    zfactors: list of float
        The list of zeta-factors in the same order as intensities
        e.g. zfactors = [628.10, 539.89] for ['As_Ka', 'Ga_Ka'].
    dose: float
        The total electron dose given by i*t*N, i the current,
        t the acquisition time and
        N the number of electrons per unit electric charge (1/e).
    %s

    Returns
    ------
    A numpy.array containing the weight fraction with the same
    shape as intensities and mass thickness in kg/m^2.
    """
    if absorption_correction is None:
        # default to ones
        absorption_correction = np.ones_like(intensities, dtype="float")

    sumzi = np.zeros_like(intensities[0], dtype="float")
    composition = np.zeros_like(intensities, dtype="float")
    for intensity, zfactor, acf in zip(intensities, zfactors, absorption_correction):
        sumzi = sumzi + (intensity * zfactor * acf)
    for i, (intensity, zfactor, acf) in enumerate(
        zip(intensities, zfactors, absorption_correction)
    ):
        composition[i] = intensity * zfactor * acf / sumzi
    mass_thickness = sumzi / dose
    return composition, mass_thickness


quantification_zeta_factor.__doc__ %= _ABSORPTION_CORRECTION_DOCSTRING


def get_abs_corr_zeta(weight_percent, mass_thickness, take_off_angle):
    """
    Calculate absorption correction terms.

    Parameters
    ----------
    weight_percent: list of signal
        Composition in weight percent.
    mass_thickness: signal
        Density-thickness map in kg/m^2
    take_off_angle: float
        X-ray take-off angle in degrees.
    """
    from exspy._misc import material

    toa_rad = np.radians(take_off_angle)
    csc_toa = 1.0 / np.sin(toa_rad)
    # convert from cm^2/g to m^2/kg
    mac = (
        stack(
            material.mass_absorption_mixture(weight_percent=weight_percent),
            show_progressbar=False,
        )
        * 0.1
    )
    expo = mac.data * mass_thickness.data * csc_toa
    acf = expo / (1.0 - np.exp(-(expo)))
    return acf


def quantification_cross_section(
    intensities, cross_sections, dose, absorption_correction=None
):
    """
    Quantification using EDX cross sections
    Calculate the atomic compostion and the number of atoms per pixel
    from the raw X-ray intensity

    Parameters
    ----------
    intensity : numpy.ndarray
        The integrated intensity for each X-ray line, where the first axis
        is the element axis.
    cross_sections : list of floats
        List of X-ray scattering cross-sections in the same order as the
        intensities.
    dose: float
        the dose per unit area given by i*t*N/A, i the current,
        t the acquisition time, and
        N the number of electron by unit electric charge.
    %s

    Returns
    -------
    numpy.array containing the atomic fraction of each element, with
    the same shape as the intensity input.
    numpy.array of the number of atoms counts for each element, with the same
    shape as the intensity input.
    """

    if absorption_correction is None:
        # default to ones
        absorption_correction = np.ones_like(intensities, dtype=float)

    shp = len(intensities.shape) - 1
    slices = (slice(None),) + (None,) * shp
    x_sections = np.array(cross_sections, dtype=float)[slices]
    number_of_atoms = intensities / (x_sections * dose * 1e-10) * absorption_correction
    total_atoms = np.cumsum(number_of_atoms, axis=0)[-1]
    composition = number_of_atoms / total_atoms

    return composition, number_of_atoms


quantification_cross_section.__doc__ %= _ABSORPTION_CORRECTION_DOCSTRING


def get_abs_corr_cross_section(
    composition, number_of_atoms, take_off_angle, probe_area
):
    """
    Calculate absorption correction terms.

    Parameters
    ----------
    number_of_atoms: list of signal
        Stack of maps with number of atoms per pixel.
    take_off_angle: float
        X-ray take-off angle in degrees.
    """
    from exspy._misc import material

    toa_rad = np.radians(take_off_angle)
    Av = constants.Avogadro
    elements = [intensity.metadata.Sample.elements[0] for intensity in number_of_atoms]
    atomic_weights = np.array(
        [
            elements_db[element]["General_properties"]["atomic_weight"]
            for element in elements
        ]
    )

    number_of_atoms = stack(number_of_atoms, show_progressbar=False).data

    # calculate the total_mass in kg/m^2, or mass thickness.
    total_mass = np.zeros_like(number_of_atoms[0], dtype="float")
    for i, (weight) in enumerate(atomic_weights):
        total_mass += number_of_atoms[i] * weight / Av / 1e3 / probe_area / 1e-18
    # determine mass absorption coefficients and convert from cm^2/g to m^2/kg.
    to_stack = material.mass_absorption_mixture(
        weight_percent=material.atomic_to_weight(composition)
    )
    mac = stack(to_stack, show_progressbar=False) * 0.1
    acf = np.zeros_like(number_of_atoms)
    csc_toa = 1 / math.sin(toa_rad)
    # determine an absorption coeficient per element per pixel.
    for i, (weight) in enumerate(atomic_weights):
        expo = mac.data[i] * total_mass * csc_toa
        acf[i] = expo / (1 - np.exp(-expo))
    return acf


def cross_section_to_zeta(cross_sections, elements):
    """Convert a list of cross_sections in barns (b) to zeta-factors (kg/m^2).

    Parameters
    ----------
    cross_section : list of float
        A list of cross sections in barns.
    elements : list of str
        A list of element chemical symbols in the same order as the
        cross sections e.g. ['Al','Zn']

    Returns
    -------
    zeta_factors : list of float
        The zeta factors with units kg/m^2.

    See Also
    --------
    zeta_to_cross_section

    """
    if len(elements) != len(cross_sections):
        raise ValueError(
            "The number of elements must match the number of cross sections."
        )
    zeta_factors = []
    for i, element in enumerate(elements):
        atomic_weight = elements_db[element]["General_properties"]["atomic_weight"]
        zeta = atomic_weight / (cross_sections[i] * constants.Avogadro * 1e-25)
        zeta_factors.append(zeta)
    return zeta_factors


def zeta_to_cross_section(zfactors, elements):
    """Convert a list of zeta-factors (kg/m^2) to cross_sections in barns (b).

    Parameters
    ----------
    zfactors : list of float
        A list of zeta-factors.
    elements : list of str
        A list of element chemical symbols in the same order as the
        cross sections e.g. ['Al','Zn']

    Returns
    -------
    cross_sections : list of float
        The cross sections with units in barns.

    See Also
    --------
    cross_section_to_zeta

    """
    if len(elements) != len(zfactors):
        raise ValueError(
            "The number of elements must match the number of cross sections."
        )
    cross_sections = []
    for i, element in enumerate(elements):
        atomic_weight = elements_db[element]["General_properties"]["atomic_weight"]
        xsec = atomic_weight / (zfactors[i] * constants.Avogadro * 1e-25)
        cross_sections.append(xsec)
    return cross_sections


def get_xray_lines(elements, weight_threshold=0.1, energy_range=None, only_lines=None):
    """
    Get all x-ray lines for the given elements.

    Parameters
    ----------
    elements : tuple or list
        The list of elements.
    %s
    %s
    %s

    Returns
    -------
    :class:`hyperspy.misc.utils.DictionaryTreeBrowser`

    Examples
    --------
    Get the x-ray lines of a single element:

    >>> from exspy.utils.eds import get_xray_lines
    >>> get_xray_lines(["O"])
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    Get the x-ray lines of multiple elements:

    >>> get_xray_lines(["O", "Fe"])
    ├── Fe
    │   ├── Ka
    │   │   ├── energy (keV) = 6.4039
    │   │   └── weight = 1.0
    │   ├── Kb
    │   │   ├── energy (keV) = 7.058
    │   │   └── weight = 0.1272
    │   ├── La
    │   │   ├── energy (keV) = 0.7045
    │   │   └── weight = 1.0
    │   ├── Ll
    │   │   ├── energy (keV) = 0.6152
    │   │   └── weight = 0.3086
    │   └── Ln
    │       ├── energy (keV) = 0.6282
    │       └── weight = 0.12525
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    Restrict to a specific energy range:

    >>> exspy.utils.eds.get_xray_lines(["O", "Fe"], energy_range=[0.5, 1.0])
    ├── Fe
    │   ├── La
    │   │   ├── energy (keV) = 0.7045
    │   │   └── weight = 1.0
    │   ├── Ll
    │   │   ├── energy (keV) = 0.6152
    │   │   └── weight = 0.3086
    │   └── Ln
    │       ├── energy (keV) = 0.6282
    │       └── weight = 0.12525
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    Restrict to specific lines:

    >>> exspy.utils.eds.get_xray_lines(["O", "Fe"], energy_range=[0.5, 1.0], only_lines=["a"])
    ├── Fe
    │   └── La
    │       ├── energy (keV) = 0.7045
    │       └── weight = 1.0
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    Specify only high intensity x-ray lines:

    >>> exspy.utils.eds.get_xray_lines(["O", "Fe"], weight_threshold=0.5)
    ├── Fe
    │   ├── Ka
    │   │   ├── energy (keV) = 6.4039
    │   │   └── weight = 1.0
    │   └── La
    │       ├── energy (keV) = 0.7045
    │       └── weight = 1.0
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    See also
    --------
    get_xray_lines_near_energy, print_lines, print_lines_near_energy
    """
    only_lines = _parse_only_lines(only_lines)

    out = DictionaryTreeBrowser()
    if energy_range is None:
        energy_range = [0.0, 400.0]
    energy_min, energy_max = energy_range
    for element in elements:
        if element not in ["Am", "Np", "Pu"]:
            # no xray lines for these elements in the database
            d = {
                k: v
                for k, v in elements_db[element]["Atomic_properties"][
                    "Xray_lines"
                ].items()
                if (
                    float(v["weight"]) >= weight_threshold
                    and energy_min <= float(v["energy (keV)"])
                    and float(v["energy (keV)"]) <= energy_max
                    and not (only_lines and k not in only_lines)
                )
            }
            if d:
                out[element] = d

    return out


get_xray_lines.__doc__ %= (
    WEIGHT_THRESHOLD_PARAMETER,
    ENERGY_RANGE_PARAMETER,
    ONLY_LINES_PARAMETER,
)


def _as_xray_lines_table(dtb, sorting, float_format):
    table = PrettyTable()
    table.field_names = ["Element", "Line", "Energy (keV)", "Weight", "Intensity"]

    def get_weight_scale(weight):
        # weight is a number in range [0, 1]
        return "".join(["#"] * int(weight * 10))

    for element, element_d in dtb:
        element_ = element
        for i, (line, line_d) in enumerate(element_d):
            w = line_d["weight"]
            table.add_row(
                [element_, line, line_d["energy (keV)"], w, get_weight_scale(w)],
                divider=(i == len(element_d) - 1),
            )

            if sorting == "elements":
                # Only display in the first line
                element_ = ""

    # this ensures the html version try its best to mimick the ASCII one
    table.format = True
    table.float_format = float_format
    table.align["Intensity"] = "l"
    if sorting == "energy":
        table.sortby = "Energy (keV)"

    return table


def print_lines_near_energy(
    energy,
    width=0.1,
    weight_threshold=0.1,
    only_lines=None,
    sorting="energy",
    float_format=".2",
):
    """
    Display a table of X-ray lines close to a given energy.

    Parameters
    ----------
    energy : float
        The energy to search around, in keV.
    %s
    %s
    %s
    %s
    %s

    Examples
    --------
    >>> import exspy
    >>> exspy.utils.eds.print_lines_near_energy(energy=6.4)
    +---------+------+--------------+--------+------------+
    | Element | Line | Energy (keV) | Weight | Intensity  |
    +---------+------+--------------+--------+------------+
    |    Sm   | Lb3  |     6.32     |  0.13  | #          |
    |    Pm   | Lb2  |     6.34     |  0.20  | #          |
    |    Fe   |  Ka  |     6.40     |  1.00  | ########## |
    |    Eu   | Lb1  |     6.46     |  0.44  | ####       |
    |    Mn   |  Kb  |     6.49     |  0.13  | #          |
    |    Dy   |  La  |     6.50     |  1.00  | ########## |
    +---------+------+--------------+--------+------------+

    See also
    --------
    get_xray_lines, get_xray_lines_near_energy, print_lines
    """
    energy_range = [energy - width, energy + width]
    dict_tree = get_xray_lines(
        elements_db.keys(), weight_threshold, energy_range, only_lines
    )
    # Convert to a table
    table = _as_xray_lines_table(dict_tree, sorting, float_format)

    display(table)


print_lines_near_energy.__doc__ %= (
    WIDTH_PARAMETER,
    WEIGHT_THRESHOLD_PARAMETER,
    ONLY_LINES_PARAMETER,
    SORTING_PARAMETER,
    FLOAT_FORMAT_PARAMETER,
)


def print_lines(
    elements,
    weight_threshold=0.1,
    energy_range=None,
    only_lines=None,
    sorting="elements",
    float_format=".2",
):
    """
    Display a table of X-ray lines for given elements.

    Parameters
    ----------
    elements : list, tuple or None
        The list of elements.
    %s
    %s
    %s
    %s
    %s

    Examples
    --------
    >>> import exspy
    >>> exspy.utils.eds.print_lines(elements=["Fe", "Pt"])
    +---------+------+--------------+--------+------------+
    | Element | Line | Energy (keV) | Weight | Intensity  |
    +---------+------+--------------+--------+------------+
    |    Fe   |  Ka  |     6.40     |  1.00  | ########## |
    |         |  Kb  |     7.06     |  0.13  | #          |
    |         |  La  |     0.70     |  1.00  | ########## |
    |         |  Ll  |     0.62     |  0.31  | ###        |
    |         |  Ln  |     0.63     |  0.13  | #          |
    +---------+------+--------------+--------+------------+
    |    Pt   |  Ka  |    66.83     |  1.00  | ########## |
    |         |  Kb  |    75.75     |  0.15  | #          |
    |         |  La  |     9.44     |  1.00  | ########## |
    |         | Lb1  |    11.07     |  0.41  | ####       |
    |         | Lb2  |    11.25     |  0.22  | ##         |
    |         |  Ma  |     2.05     |  1.00  | ########## |
    |         |  Mb  |     2.13     |  0.59  | #####      |
    +---------+------+--------------+--------+------------+

    See also
    --------
    get_xray_lines, get_xray_lines_near_energy, print_lines_near_energy
    """
    # Get the xray lines data as dictionary
    dict_tree = get_xray_lines(elements, weight_threshold, energy_range, only_lines)
    # Convert to a table
    table = _as_xray_lines_table(dict_tree, sorting, float_format)
    display(table)


print_lines.__doc__ %= (
    WEIGHT_THRESHOLD_PARAMETER,
    ENERGY_RANGE_PARAMETER,
    ONLY_LINES_PARAMETER,
    SORTING_PARAMETER,
    FLOAT_FORMAT_PARAMETER,
)
