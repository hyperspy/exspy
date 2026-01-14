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
from prettytable import PrettyTable

from hyperspy.misc import utils as hs_utils

from exspy import signals
from exspy._docstrings.eds import (
    FLOAT_FORMAT_PARAMETER,
    ENERGY_RANGE_PARAMETER,
    ONLY_LINES_PARAMETER,
    SORTING_PARAMETER,
    WEIGHT_THRESHOLD_PARAMETER,
    WIDTH_PARAMETER,
)
from exspy._misc import elements as elements_module


eV2keV = 1000.0
sigma2fwhm = 2 * math.sqrt(2 * math.log(2))


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
    return elements_module.elements[element]["Atomic_properties"]["Xray_lines"][line][
        "energy (keV)"
    ]


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
    Find X-ray lines near a specific energy, more specifically all X-ray lines
    that satisfy ``only_lines`` and are within the given energy window width
    around the passed energy.

    Parameters
    ----------
    energy : float
        Energy in keV around which to search.
    %s
    %s

    Returns
    -------
    xray_lines : list
        List of X-ray-lines sorted by energy difference to the given energy.

    See also
    --------
    get_xray_lines, print_lines, print_lines_near_energy
    """
    only_lines = _parse_only_lines(only_lines)
    valid_lines = []
    E_min, E_max = energy - width / 2.0, energy + width / 2.0
    for element, el_props in elements_module.elements.items():
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

    if energy_axis is None:
        energy_axis = {
            "name": "E",
            "scale": 0.01,
            "units": "keV",
            "offset": -0.1,
            "size": 1024,
        }
    s = signals.EDSTEMSpectrum(np.zeros(energy_axis["size"]), axes=[energy_axis])
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


def get_xray_lines(elements, weight_threshold=0.1, energy_range=None, only_lines=None):
    """
    Get all X-ray lines for the given elements.

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
    Get the X-ray lines of a single element:

    >>> from exspy.utils.eds import get_xray_lines
    >>> get_xray_lines(["O"])
    └── O
        └── Ka
            ├── energy (keV) = 0.5249
            └── weight = 1.0

    Get the X-ray lines of multiple elements:

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

    Specify a threshold to only return high intensity X-ray lines

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

    out = hs_utils.DictionaryTreeBrowser()
    if energy_range is None:
        energy_range = [0.0, 400.0]
    energy_min, energy_max = energy_range
    for element in elements:
        if element not in ["Am", "Np", "Pu"]:
            # no xray lines for these elements in the database
            d = {
                k: v
                for k, v in elements_module.elements[element]["Atomic_properties"][
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
        elements_module.elements.keys(), weight_threshold, energy_range, only_lines
    )
    # Convert to a table
    table = _as_xray_lines_table(dict_tree, sorting, float_format)

    hs_utils.display(table)


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
    hs_utils.display(table)


print_lines.__doc__ %= (
    WEIGHT_THRESHOLD_PARAMETER,
    ENERGY_RANGE_PARAMETER,
    ONLY_LINES_PARAMETER,
    SORTING_PARAMETER,
    FLOAT_FORMAT_PARAMETER,
)
