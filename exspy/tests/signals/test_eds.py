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

import numpy as np

from exspy.signals import EDSSpectrum
from exspy._signal_tools import EDSRange


def test_print_lines_near_energy(capsys):
    s = EDSSpectrum(np.ones(1024))
    s.print_lines_near_energy(energy=6.4)
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
    s = EDSSpectrum(np.ones(1024))
    s.set_elements(["Fe", "Pt"])
    s.print_lines()
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


def test_print_lines_no_elements():
    s = EDSSpectrum(np.ones(1024))
    with pytest.raises(ValueError):
        s.print_lines()


def test_lines_at_energy_non_interactive():
    s = EDSSpectrum(np.ones(1024))
    out = s.lines_at_energy(energy=6.4, width=0.2)
    expected_out = s.print_lines_near_energy(energy=6.4, width=0.2)

    assert out == expected_out


def test_lines_at_energy_interactive():
    s = EDSSpectrum(np.ones(1024))
    s.axes_manager[0].units = "keV"
    s.add_elements(["Pt"])
    er = EDSRange(s)
    assert er.width == 0.2  # default width
    assert er.only_lines == "all"  # default only_lines
    assert er.weight_threshold == 0.1  # default weight_threshold
    assert (
        er.selected_elements == set()
    )  # at initialisation, selected_elements is empty

    # Set the line at a given position
    er.position = 6.4

    # check `get_lines_information`
    out_keys = er.get_lines_information().as_dictionary().keys()
    assert list(out_keys) == ["Dy", "Eu", "Fe", "Mn", "Pm", "Sm"]

    er.width = 0.01
    lines_info = er.get_lines_information()
    # check that the intensity is included
    assert lines_info["Fe"]["Ka"]["intensity"] == "##########"
    lines_info_keys = list(lines_info.as_dictionary().keys())
    assert lines_info_keys == ["Fe"]

    # check that the markers have been updated
    er.update_markers()
    # no selected elements, so no markers should be present
    assert len(er.selected_elements) == 0
    assert len(s._xray_markers["lines"]) == 0

    # select Fe and check that the markers are updated
    er.selected_elements.add("Fe")
    assert er.selected_elements == {"Fe"}
    er.update_markers()
    assert len(s._xray_markers["names"]) == 6

    # check closing the tool
    er.close()
    assert er.on is False
    assert er._line is None

    # should do nothing since the plot is closed
    # but it should not raise an error
    s._plot.close()
    er.update_markers()


def test_lines_at_energy_interactive_units_error():
    s = EDSSpectrum(np.ones(1024))
    s.add_elements(["Pt"])
    with pytest.raises(RuntimeError):
        # units must be keV
        EDSRange(s)


def test_lines_at_energy_interactive_plot_without_markers():
    s = EDSSpectrum(np.ones(1024))
    s.axes_manager[0].units = "keV"
    s.add_elements(["Pt"])
    # plot without markers
    s.plot(False)
    er = EDSRange(s)
    er.get_lines_information()
    er.update_markers()
