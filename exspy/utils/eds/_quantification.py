from functools import reduce
import math

import numpy as np
import scipy

import hyperspy.api as hs


_ABSORPTION_CORRECTION_DOCSTRING = """absorption_correction : numpy.ndarray or None
        If None (default), absorption correction is ignored, otherwise, the
        array must contain values between 0 and 1 to correct the intensities
        based on estimated absorption.
"""


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
        if isinstance(mask, hs.signals.BaseSignal):
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
        hs.stack(
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
    from exspy._misc import elements as elements_module

    toa_rad = np.radians(take_off_angle)
    Av = scipy.constants.Avogadro
    elements = [intensity.metadata.Sample.elements[0] for intensity in number_of_atoms]
    atomic_weights = np.array(
        [
            elements_module.elements[element]["General_properties"]["atomic_weight"]
            for element in elements
        ]
    )

    number_of_atoms = hs.stack(number_of_atoms, show_progressbar=False).data

    # calculate the total_mass in kg/m^2, or mass thickness.
    total_mass = np.zeros_like(number_of_atoms[0], dtype="float")
    for i, (weight) in enumerate(atomic_weights):
        total_mass += number_of_atoms[i] * weight / Av / 1e3 / probe_area / 1e-18
    # determine mass absorption coefficients and convert from cm^2/g to m^2/kg.
    to_stack = material.mass_absorption_mixture(
        weight_percent=material.atomic_to_weight(composition)
    )
    mac = hs.stack(to_stack, show_progressbar=False) * 0.1
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
    from exspy._misc import elements as elements_module

    if len(elements) != len(cross_sections):
        raise ValueError(
            "The number of elements must match the number of cross sections."
        )
    zeta_factors = []
    for i, element in enumerate(elements):
        atomic_weight = elements_module.elements[element]["General_properties"][
            "atomic_weight"
        ]
        zeta = atomic_weight / (cross_sections[i] * scipy.constants.Avogadro * 1e-25)
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
    from exspy._misc import elements as elements_module

    if len(elements) != len(zfactors):
        raise ValueError(
            "The number of elements must match the number of cross sections."
        )
    cross_sections = []
    for i, element in enumerate(elements):
        atomic_weight = elements_module.elements[element]["General_properties"][
            "atomic_weight"
        ]
        xsec = atomic_weight / (zfactors[i] * scipy.constants.Avogadro * 1e-25)
        cross_sections.append(xsec)

    return cross_sections
