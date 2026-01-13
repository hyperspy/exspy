# -*- coding: utf-8 -*-
# Copyright 2007-2026 The eXSpy developers
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

from exspy._misc.eds.utils import (
    get_xray_lines,
    get_xray_lines_near_energy,
    print_lines,
    print_lines_near_energy,
    take_off_angle,
)


def test_xray_lines_near_energy():
    E = 1.36
    lines = get_xray_lines_near_energy(E)
    assert lines == [
        "Pm_M2N4",
        "Ho_Ma",
        "Eu_Mg",
        "Se_La",
        "Br_Ln",
        "W_Mz",
        "As_Lb3",
        "Kr_Ll",
        "Ho_Mb",
        "Ta_Mz",
        "Dy_Mb",
        "As_Lb1",
        "Gd_Mg",
        "Er_Ma",
        "Sm_M2N4",
        "Mg_Kb",
        "Se_Lb1",
        "Ge_Lb3",
        "Br_Ll",
        "Sm_Mg",
        "Dy_Ma",
        "Nd_M2N4",
        "As_La",
        "Re_Mz",
        "Hf_Mz",
        "Kr_Ln",
        "Er_Mb",
        "Tb_Mb",
    ]
    lines = get_xray_lines_near_energy(E, 0.02)
    assert lines == ["Pm_M2N4"]
    E = 5.4
    lines = get_xray_lines_near_energy(E)
    assert lines == [
        "Cr_Ka",
        "La_Lb2",
        "V_Kb",
        "Pm_La",
        "Pm_Ln",
        "Ce_Lb3",
        "Gd_Ll",
        "Pr_Lb1",
        "Xe_Lg3",
        "Pr_Lb4",
    ]
    lines = get_xray_lines_near_energy(E, only_lines=("a", "b"))
    assert lines == ["Cr_Ka", "V_Kb", "Pm_La", "Pr_Lb1"]
    lines = get_xray_lines_near_energy(E, only_lines=("a"))
    assert lines == ["Cr_Ka", "Pm_La"]


def test_takeoff_angle():
    np.testing.assert_allclose(40.0, take_off_angle(30.0, 0.0, 10.0))
    np.testing.assert_allclose(40.0, take_off_angle(0.0, 90.0, 10.0, beta_tilt=30.0))
    np.testing.assert_allclose(
        73.15788376370121, take_off_angle(45.0, 45.0, 45.0, 45.0)
    )


def test_get_xray_lines():
    lines = get_xray_lines(elements=["Fe"], weight_threshold=0.5)
    assert lines.as_dictionary() == {
        "Fe": {
            "Ka": {"energy (keV)": 6.4039, "weight": 1.0},
            "La": {"energy (keV)": 0.7045, "weight": 1.0},
        }
    }

    lines = get_xray_lines(elements=["Fe", "Pt"], weight_threshold=0.5)
    assert lines.as_dictionary() == {
        "Fe": {
            "Ka": {"energy (keV)": 6.4039, "weight": 1.0},
            "La": {"energy (keV)": 0.7045, "weight": 1.0},
        },
        "Pt": {
            "Ka": {"energy (keV)": 66.8311, "weight": 1.0},
            "La": {"energy (keV)": 9.4421, "weight": 1.0},
            "Ma": {"energy (keV)": 2.0505, "weight": 1.0},
            "Mb": {"energy (keV)": 2.1276, "weight": 0.59443},
        },
    }


def test_print_lines_near_energy(capsys):
    # Just test that it runs without error
    print_lines_near_energy(energy=6.4)
    captured = capsys.readouterr()
    assert (
        captured.out
        == """+---------+------+--------------+--------+------------+
| Element | Line | Energy (keV) | Weight | Intensity  |
+---------+------+--------------+--------+------------+
|    Sm   | Lb3  |     6.32     |  0.13  | #          |
|    Pm   | Lb2  |     6.34     |  0.20  | #          |
|    Fe   |  Ka  |     6.40     |  1.00  | ########## |
|    Eu   | Lb1  |     6.46     |  0.44  | ####       |
|    Mn   |  Kb  |     6.49     |  0.13  | #          |
|    Dy   |  La  |     6.50     |  1.00  | ########## |
+---------+------+--------------+--------+------------+
"""
    )


def test_print_lines(capsys):
    print_lines(elements=["Fe", "Pt"])
    captured = capsys.readouterr()
    assert (
        captured.out
        == """+---------+------+--------------+--------+------------+
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
"""
    )
