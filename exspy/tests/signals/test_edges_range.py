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
from copy import deepcopy

import numpy as np

import exspy
from exspy._signal_tools import EdgesRange


class Owner:
    """for use in Test_EdgesRange"""

    def __init__(self, edge):
        self.description = edge


class Test_EdgesRange:
    def setup_method(self, method):
        s = exspy.data.EELS_MnFe()
        er = EdgesRange(s)
        self.signal = s
        self.er = er

    def test_init(self):
        edges_all = np.array(
            [
                "Ag_M2",
                "Ra_N5",
                "Fr_N4",
                "Cr_L2",
                "Cd_M3",
                "Te_M4",
                "I_M5",
                "Fr_N5",
                "Cr_L3",
                "Te_M5",
                "V_L1",
                "Ag_M3",
                "I_M4",
                "Rn_N4",
                "Ti_L1",
                "Ra_N4",
                "Mn_L3",
                "Pd_M2",
                "Cd_M2",
                "Mn_L2",
                "Tc_M1",
                "Sb_M4",
                "In_M3",
                "At_N5",
                "O_K",
                "Pd_M3",
                "Sb_M5",
                "Xe_M5",
                "Ac_N4",
                "Rh_M2",
                "V_L2",
                "F_K",
                "Xe_M4",
                "V_L3",
                "Cr_L1",
                "Sc_L1",
                "In_M2",
                "Rh_M3",
                "Sn_M4",
                "Pa_N5",
                "Fe_L3",
                "Sn_M3",
                "Sn_M5",
                "Ru_M2",
                "Fe_L2",
                "Cs_M5",
                "Ti_L2",
                "Ru_M3",
                "Cs_M4",
                "At_N3",
                "Pa_N4",
                "Ti_L3",
                "In_M4",
                "Pu_N6",
                "Tc_M2",
                "Sn_M2",
                "In_M5",
                "Ca_L1",
                "Sb_M3",
                "Pu_N7",
                "Rn_N3",
                "Mn_L1",
                "Np_N5",
                "Tc_M3",
                "Co_L3",
                "Ba_M5",
                "Np_N6",
                "Cd_M4",
                "Mo_M2",
                "Sc_L2",
                "Co_L2",
                "Cd_M5",
                "Np_N7",
                "Ba_M4",
                "Sc_L3",
                "N_K",
            ]
        )
        energy_all = np.array(
            [
                602.0,
                603.0,
                603.0,
                584.0,
                616.0,
                582.0,
                620.0,
                577.0,
                575.0,
                572.0,
                628.0,
                571.0,
                631.0,
                567.0,
                564.0,
                636.0,
                640.0,
                559.0,
                651.0,
                651.0,
                544.0,
                537.0,
                664.0,
                533.0,
                532.0,
                531.0,
                528.0,
                672.0,
                675.0,
                521.0,
                521.0,
                685.0,
                685.0,
                513.0,
                695.0,
                500.0,
                702.0,
                496.0,
                494.0,
                708.0,
                708.0,
                714.0,
                485.0,
                483.0,
                721.0,
                726.0,
                462.0,
                461.0,
                740.0,
                740.0,
                743.0,
                456.0,
                451.0,
                446.0,
                445.0,
                756.0,
                443.0,
                438.0,
                766.0,
                432.0,
                768.0,
                769.0,
                770.0,
                425.0,
                779.0,
                781.0,
                415.0,
                411.0,
                410.0,
                407.0,
                794.0,
                404.0,
                404.0,
                796.0,
                402.0,
                401.0,
            ]
        )
        relevance_all = np.array(
            [
                "Minor",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Major",
                "Major",
                "Major",
                "Minor",
                "Minor",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Major",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Major",
                "Minor",
                "Minor",
                "Minor",
                "Minor",
                "Major",
                "Major",
                "Major",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Major",
                "Major",
                "Major",
                "Major",
                "Major",
            ]
        )
        description_all = np.array(
            [
                "Delayed maximum",
                "",
                "",
                "Sharp peak. Delayed maximum",
                "Delayed maximum",
                "Delayed maximum",
                "Delayed maximum",
                "",
                "Sharp peak. Delayed maximum",
                "Delayed maximum",
                "Abrupt onset",
                "Delayed maximum",
                "Delayed maximum",
                "",
                "Abrupt onset",
                "",
                "Sharp peak. Delayed maximum",
                "",
                "",
                "Sharp peak. Delayed maximum",
                "Abrupt onset",
                "Delayed maximum",
                "Delayed maximum",
                "",
                "Abrupt onset",
                "",
                "Delayed maximum",
                "Delayed maximum",
                "",
                "Sharp peak",
                "Sharp peak. Delayed maximum",
                "Abrupt onset",
                "Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Abrupt onset",
                "Abrupt onset",
                "",
                "Sharp peak",
                "Delayed maximum",
                "",
                "Sharp peak. Delayed maximum",
                "Delayed maximum",
                "Delayed maximum",
                "Sharp peak",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Sharp peak",
                "Sharp peak. Delayed maximum",
                "",
                "",
                "Sharp peak. Delayed maximum",
                "Delayed maximum",
                "",
                "Sharp peak. Delayed maximum",
                "",
                "Delayed maximum",
                "Abrupt onset",
                "Delayed maximum",
                "",
                "",
                "Abrupt onset",
                "",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "",
                "Delayed maximum",
                "Sharp peak",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Delayed maximum",
                "",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Abrupt onset",
            ]
        )

        # Test that all expected edges are present (order-independent)
        assert set(self.er.edge_all) == set(edges_all)
        assert len(self.er.edge_all) == len(edges_all)

        # Test that all expected energies are present (order-independent)
        assert set(self.er.energy_all) == set(energy_all)
        assert len(self.er.energy_all) == len(energy_all)

        # Test that all expected relevances are present (order-independent)
        assert set(self.er.relevance_all) == set(relevance_all)
        assert len(self.er.relevance_all) == len(relevance_all)

        # Test that all expected descriptions are present (order-independent)
        assert set(self.er.description_all) == set(description_all)
        assert len(self.er.description_all) == len(description_all)

        # Test that arrays have consistent lengths
        assert len(self.er.edge_all) == len(self.er.energy_all)
        assert len(self.er.edge_all) == len(self.er.relevance_all)
        assert len(self.er.edge_all) == len(self.er.description_all)

        # Test that corresponding entries match (for a few key edges)
        edge_to_energy = dict(zip(edges_all, energy_all))
        edge_to_relevance = dict(zip(edges_all, relevance_all))
        edge_to_description = dict(zip(edges_all, description_all))

        actual_edge_to_energy = dict(zip(self.er.edge_all, self.er.energy_all))
        actual_edge_to_relevance = dict(zip(self.er.edge_all, self.er.relevance_all))
        actual_edge_to_description = dict(
            zip(self.er.edge_all, self.er.description_all)
        )

        # Check a few specific mappings to ensure data integrity
        test_edges = ["O_K", "Fe_L3", "Mn_L3", "V_L2", "Cr_L3"]
        for edge in test_edges:
            if edge in edge_to_energy:  # Only test if edge exists in expected data
                assert actual_edge_to_energy[edge] == edge_to_energy[edge]
                assert actual_edge_to_relevance[edge] == edge_to_relevance[edge]
                assert actual_edge_to_description[edge] == edge_to_description[edge]

    def test_selected_span_selector(self):
        # self.er.span_selector.extents = (500, 550)
        self.er.ss_left_value = 500
        self.er.ss_right_value = 550

        edges, energy, relevance, description = self.er.update_table()
        assert set(edges) == set(
            (
                "Tc_M1",
                "Sb_M4",
                "At_N5",
                "O_K",
                "Pd_M3",
                "Sb_M5",
                "Rh_M2",
                "V_L2",
                "V_L3",
                "Sc_L1",
            )
        )
        assert set(energy) == set(
            (544.0, 537.0, 533.0, 532.0, 531.0, 528.0, 521.0, 521.0, 513.0, 500.0)
        )
        assert set(relevance) == set(
            (
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Minor",
                "Major",
                "Major",
                "Minor",
            )
        )
        assert set(description) == set(
            (
                "Abrupt onset",
                "Delayed maximum",
                "",
                "Abrupt onset",
                "",
                "Delayed maximum",
                "Sharp peak",
                "Sharp peak. Delayed maximum",
                "Sharp peak. Delayed maximum",
                "Abrupt onset",
            )
        )

    def test_none_span_selector(self):
        self.er.span_selector = None

        edges, energy, relevance, description = self.er.update_table()

        assert len(edges) == 0
        assert len(energy) == 0
        assert len(relevance) == 0
        assert len(description) == 0

    def test_complementary_edge(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        assert er.active_edges == ["V_L2"]
        assert er.active_complementary_edges == ["V_L1", "V_L3"]

    def test_off_complementary_edge(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.complementary = False
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        assert er.active_edges == ["V_L2"]
        assert len(er.active_complementary_edges) == 0

    def test_keep_valid_edge(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        er.ss_right_value = 650
        er.ss_left_value = 600
        _ = er.update_table()

        assert er.active_edges == ["V_L1"]
        assert er.active_complementary_edges == ["V_L2", "V_L3"]

    def test_remove_out_of_range_edge(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        er.ss_right_value = 750
        er.ss_left_value = 700
        _ = er.update_table()

        assert len(er.active_edges) == 0
        assert len(er.active_complementary_edges) == 0

    def test_select_edge_by_button(self):
        self.er.ss_left_value = 500
        self.er.ss_right_value = 550
        _ = self.er.update_table()

        on_V_L2 = {"owner": Owner("V_L2"), "new": True}
        self.er.update_active_edge(on_V_L2)

        assert self.er.active_edges == ["V_L2"]
        assert self.er.active_complementary_edges == ["V_L1", "V_L3"]

        off_V_L2 = {"owner": Owner("V_L2"), "new": False}
        self.er.update_active_edge(off_V_L2)

        assert len(self.er.active_edges) == 0
        assert len(self.er.active_complementary_edges) == 0

    def test_remove_all_edge_markers(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        er._clear_markers()

        assert len(er.active_edges) == 0
        assert len(er.active_complementary_edges) == 0

    def test_on_figure_changed(self):
        self.signal.plot(plot_edges=["V_L2"])
        er = EdgesRange(self.signal)
        er.ss_right_value = 550
        er.ss_left_value = 500
        _ = er.update_table()

        segments = deepcopy(self.signal._edge_markers["lines"].get_current_kwargs())
        scaled = self.signal._edge_markers["lines"]._scale_kwarg(segments, "segments")
        self.signal._plot.pointer.indices = (9,)
        assert self.signal.axes_manager.navigation_axes[0].index == 9
        segments2 = deepcopy(self.signal._edge_markers["lines"].get_current_kwargs())
        scaled2 = self.signal._edge_markers["lines"]._scale_kwarg(segments2, "segments")
        assert not np.array_equal(scaled["segments"], scaled2["segments"])
