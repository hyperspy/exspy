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

import pytest

from exspy._misc.eels.tools import get_edges_near_energy, get_info_from_edges


def test_single_edge():
    edges = get_edges_near_energy(532, width=0)
    assert len(edges) == 1
    assert edges == ["O_K"]


def test_multiple_edges():
    edges = get_edges_near_energy(640, width=100)
    expected_edges = [
        "Mn_L3",
        "Ra_N4",
        "I_M4",
        "Cd_M2",
        "Mn_L2",
        "V_L1",
        "I_M5",
        "Cd_M3",
        "In_M3",
        "Xe_M5",
        "Ac_N4",
        "Ra_N5",
        "Fr_N4",
        "Ag_M2",
        "F_K",
        "Xe_M4",
    ]
    assert len(edges) == 16
    # Test that all expected edges are present (order-independent)
    assert set(edges) == set(expected_edges)

    # Verify ordering is by distance from energy (closest first) for unique energies
    # Get info to check energies
    info = get_info_from_edges(edges)
    energies = [d["onset_energy (eV)"] for d in info]
    distances = [abs(e - 640) for e in energies]

    # Check that distances are generally non-decreasing (allowing for ties)
    for i in range(len(distances) - 1):
        # Allow small tolerance for floating point comparisons
        assert distances[i] <= distances[i + 1] + 1e-10


def test_multiple_edges_ascending():
    edges = get_edges_near_energy(640, width=100, order="ascending")
    expected_edges = [
        "Ag_M2",
        "Ra_N5",
        "Fr_N4",
        "Cd_M3",
        "I_M5",
        "V_L1",
        "I_M4",
        "Ra_N4",
        "Mn_L3",
        "Cd_M2",
        "Mn_L2",
        "In_M3",
        "Xe_M5",
        "Ac_N4",
        "F_K",
        "Xe_M4",
    ]
    assert len(edges) == 16
    # Test that all expected edges are present (order-independent)
    assert set(edges) == set(expected_edges)

    # Verify ordering is by onset energy in ascending order
    info = get_info_from_edges(edges)
    energies = [d["onset_energy (eV)"] for d in info]

    # Check that energies are in ascending order (allowing for ties)
    for i in range(len(energies) - 1):
        assert energies[i] <= energies[i + 1]


def test_multiple_edges_descending():
    edges = get_edges_near_energy(640, width=100, order="descending")
    expected_edges = [
        "F_K",
        "Xe_M4",
        "Ac_N4",
        "Xe_M5",
        "In_M3",
        "Cd_M2",
        "Mn_L2",
        "Mn_L3",
        "Ra_N4",
        "I_M4",
        "V_L1",
        "I_M5",
        "Cd_M3",
        "Ra_N5",
        "Fr_N4",
        "Ag_M2",
    ]
    assert len(edges) == 16
    # Test that all expected edges are present (order-independent)
    assert set(edges) == set(expected_edges)

    # Verify ordering is by onset energy in descending order
    info = get_info_from_edges(edges)
    energies = [d["onset_energy (eV)"] for d in info]

    # Check that energies are in descending order (allowing for ties)
    for i in range(len(energies) - 1):
        assert energies[i] >= energies[i + 1]


def test_negative_energy_width():
    with pytest.raises(Exception):
        get_edges_near_energy(849, width=-5)


def test_wrong_ordering():
    with pytest.raises(ValueError):
        get_edges_near_energy(532, order="random")


def test_info_one_edge():
    info = get_info_from_edges("O_K")
    assert len(info) == 1


def test_info_multiple_edges():
    info = get_info_from_edges(["O_K", "N_K", "Cr_L3"])
    assert len(info) == 3


def test_info_wrong_edge_format():
    with pytest.raises(ValueError):
        get_info_from_edges(["O_K", "NK"])
