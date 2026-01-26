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

import numpy as np

from exspy._misc import elements as elements_module


def get_edges_near_energy(energy, width=10, only_major=False, order="closest"):
    """Find edges near a given energy that are within the given energy
    window.

    Parameters
    ----------
    energy : float
        Energy to search, in eV
    width : float
        Width of window, in eV, around energy in which to find nearby
        energies, i.e. a value of 10 eV (the default) means to
        search +/- 5 eV. The default is 10.
    only_major : bool
        Whether to show only the major edges. The default is False.
    order : str
        Sort the edges, if 'closest', return in the order of energy difference,
        if 'ascending', return in ascending order, similarly for 'descending'

    Returns
    -------
    edges : list
        All edges that are within the given energy window, sorted by
        energy difference to the given energy.

    See Also
    --------
    exspy.utils.eels.get_info_from_edges
    """

    if width < 0:
        raise ValueError("Provided width needs to be >= 0.")
    if order not in ("closest", "ascending", "descending"):
        raise ValueError("order needs to be 'closest', 'ascending' or 'descending'")

    Emin, Emax = energy - width / 2, energy + width / 2

    # find all subshells that have its energy within range
    valid_edges = []
    for element, element_info in elements_module.elements.items():
        try:
            for shell, shell_info in element_info["Atomic_properties"][
                "Binding_energies"
            ].items():
                if only_major:
                    if shell_info["relevance"] != "Major":
                        continue
                if shell[-1] != "a" and Emin <= shell_info["onset_energy (eV)"] <= Emax:
                    subshell = "{}_{}".format(element, shell)
                    Ediff = abs(shell_info["onset_energy (eV)"] - energy)
                    valid_edges.append(
                        (subshell, shell_info["onset_energy (eV)"], Ediff)
                    )
        except KeyError:
            continue

    # Sort according to 'order' and return only the edges
    if order == "closest":
        edges = [edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[2])]
    elif order == "ascending":
        edges = [edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[1])]
    elif order == "descending":
        edges = [
            edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[1], reverse=True)
        ]

    return edges


def get_info_from_edges(edges):
    """Return the information of a sequence of edges as a list of dictionaries

    Parameters
    ----------
    edges : str or iterable
        the sequence of edges, each entry in the format of 'element_subshell'.

    Returns
    -------
    info : list
        A list of dictionaries with information corresponding to the provided
        edges.

    See Also
    --------
    exspy.utils.eels.get_edges_near_energy
    """

    edges = np.atleast_1d(edges)
    info = []
    for edge in edges:
        element, subshell = edge.split("_")
        d = elements_module.elements[element]["Atomic_properties"]["Binding_energies"][
            subshell
        ]
        info.append(d)

    return info
