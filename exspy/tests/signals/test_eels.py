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

import importlib

import numpy as np
import pytest
from pathlib import Path

import hyperspy.api as hs
from hyperspy.decorators import lazifyTestClass

import exspy


MYPATH = Path(__file__).resolve().parent


@lazifyTestClass
class Test_Estimate_Elastic_Scattering_Threshold:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.zeros((3, 2, 1024)))
        energy_axis = s.axes_manager.signal_axes[0]
        energy_axis.scale = 0.02
        energy_axis.offset = -5

        gauss = hs.model.components1D.Gaussian()
        gauss.centre.value = 0
        gauss.A.value = 5000
        gauss.sigma.value = 0.5
        gauss2 = hs.model.components1D.Gaussian()
        gauss2.sigma.value = 0.5
        # Inflexion point 1.5
        gauss2.A.value = 5000
        gauss2.centre.value = 5
        s.data[:] = gauss.function(energy_axis.axis) + gauss2.function(energy_axis.axis)
        self.signal = s

    def test_min_in_window_with_smoothing(self):
        s = self.signal
        thr = s.estimate_elastic_scattering_threshold(
            window=5,
            window_length=5,
            tol=0.00001,
        )
        np.testing.assert_allclose(thr.data, 2.5, atol=10e-3)
        assert thr.metadata.Signal.signal_type == ""
        assert thr.axes_manager.signal_dimension == 0

    def test_min_in_window_without_smoothing_single_spectrum(self):
        s = self.signal.inav[0, 0]
        thr = s.estimate_elastic_scattering_threshold(
            window=5,
            window_length=0,
            tol=0.001,
        )
        np.testing.assert_allclose(thr.data, 2.49, atol=10e-3)

    def test_min_in_window_without_smoothing(self):
        s = self.signal
        thr = s.estimate_elastic_scattering_threshold(
            window=5,
            window_length=0,
            tol=0.001,
        )
        np.testing.assert_allclose(thr.data, 2.49, atol=10e-3)

    def test_min_not_in_window(self):
        # If I use a much lower window, this is the value that has to be
        # returned as threshold.
        s = self.signal
        data = s.estimate_elastic_scattering_threshold(
            window=1.5,
            tol=0.001,
        ).data
        assert np.all(np.isnan(data))

    def test_estimate_elastic_scattering_intensity(self):
        s = self.signal
        threshold = s.estimate_elastic_scattering_threshold(window=4.0)
        # Threshold is nd signal
        t = s.estimate_elastic_scattering_intensity(threshold=threshold)
        assert t.metadata.Signal.signal_type == ""
        assert t.axes_manager.signal_dimension == 0
        np.testing.assert_array_almost_equal(t.data, 249999.985133)
        # Threshold is signal, 1 spectrum
        s0 = s.inav[0]
        t0 = s0.estimate_elastic_scattering_threshold(window=4.0)
        t = s0.estimate_elastic_scattering_intensity(threshold=t0)
        np.testing.assert_array_almost_equal(t.data, 249999.985133)
        # Threshold is value
        t = s.estimate_elastic_scattering_intensity(threshold=2.5)
        np.testing.assert_array_almost_equal(t.data, 249999.985133)


@lazifyTestClass
class TestEstimateZLPCentre:
    def setup_method(self, method):
        s = exspy.signals.EELSSpectrum(np.diag(np.arange(1, 11)))
        s.axes_manager[-1].scale = 0.1
        s.axes_manager[-1].offset = 100
        self.signal = s

    def test_estimate_zero_loss_peak_centre(self):
        s = self.signal
        zlpc = s.estimate_zero_loss_peak_centre()
        np.testing.assert_allclose(zlpc.data, np.arange(100, 101, 0.1))
        assert zlpc.metadata.Signal.signal_type == ""
        assert zlpc.axes_manager.signal_dimension == 0


@lazifyTestClass
class TestAlignZLP:
    def setup_method(self, method):
        s = exspy.signals.EELSSpectrum(np.zeros((10, 100)))
        self.scale = 0.1
        self.offset = -2
        eaxis = s.axes_manager.signal_axes[0]
        eaxis.scale = self.scale
        eaxis.offset = self.offset
        self.izlp = eaxis.value2index(0)
        self.bg = 2
        self.ishifts = np.array([0, 4, 2, -2, 5, -2, -5, -9, -9, -8])
        self.new_offset = self.offset - self.ishifts.min() * self.scale
        s.data[np.arange(10), self.ishifts + self.izlp] = 10
        s.data += self.bg
        s.axes_manager[-1].offset += 100
        self.signal = s

    def test_align_zero_loss_peak_calibrate_true(self):
        s = self.signal
        s.align_zero_loss_peak(calibrate=True, print_stats=False)
        zlpc = s.estimate_zero_loss_peak_centre()
        np.testing.assert_allclose(zlpc.data.mean(), 0)
        np.testing.assert_allclose(zlpc.data.std(), 0)

    def test_align_zero_loss_peak_calibrate_true_with_mask(self):
        s = self.signal
        mask = s._get_navigation_signal(dtype="bool").T
        mask.data[[3, 5]] = (True, True)
        s.align_zero_loss_peak(calibrate=True, print_stats=False, mask=mask)
        zlpc = s.estimate_zero_loss_peak_centre(mask=mask)
        np.testing.assert_allclose(np.nanmean(zlpc.data), 0, atol=np.finfo(float).eps)
        np.testing.assert_allclose(np.nanstd(zlpc.data), 0, atol=np.finfo(float).eps)

    def test_align_zero_loss_peak_calibrate_false(self):
        s = self.signal
        s.align_zero_loss_peak(calibrate=False, print_stats=False)
        zlpc = s.estimate_zero_loss_peak_centre()
        np.testing.assert_allclose(zlpc.data.std(), 0, atol=10e-3)

    def test_also_aligns(self):
        s = self.signal
        s2 = s.deepcopy()
        s.align_zero_loss_peak(calibrate=True, print_stats=False, also_align=[s2])
        zlpc = s2.estimate_zero_loss_peak_centre()
        assert zlpc.data.mean() == 0
        assert zlpc.data.std() == 0

    def test_align_zero_loss_peak_with_spike_signal_range(self):
        s = self.signal
        spike = np.zeros((10, 100))
        spike_amplitude = 20
        spike[:, 75] = spike_amplitude
        s.data += spike
        s.align_zero_loss_peak(
            print_stats=False, subpixel=False, signal_range=(98.0, 102.0)
        )
        zlp_max = s.isig[-0.5:0.5].max(-1).data
        # Max value in the original spectrum is 12, but due to the aligning
        # the peak is split between two different channels. So 8 is the
        # maximum value for the aligned spectrum
        np.testing.assert_allclose(zlp_max, 8)

    def test_align_zero_loss_peak_crop_false(self):
        s = self.signal
        original_size = s.axes_manager.signal_axes[0].size
        s.align_zero_loss_peak(crop=False, print_stats=False)
        assert original_size == s.axes_manager.signal_axes[0].size

    @pytest.mark.parametrize("signal_range", ((-2.0, 2.0), (0, 40), "roi"))
    def test_align_zero_loss_peak_start_end_float(self, signal_range):
        s = self.signal
        if signal_range == "roi":
            signal_range = hs.roi.SpanROI(-3, 3)
        s.axes_manager[-1].offset = -2
        s.align_zero_loss_peak(subpixel=True, signal_range=signal_range)
        zlpc = s.estimate_zero_loss_peak_centre()
        # Check if start and end arguments work
        assert zlpc.data.mean() == 0
        assert zlpc.data.std() == 0


@lazifyTestClass
class TestSpikesRemovalToolZLP:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.zeros((2, 3, 64)))
        energy_axis = s.axes_manager.signal_axes[0]
        energy_axis.scale = 0.2
        energy_axis.offset = -5

        gauss = hs.model.components1D.Gaussian()
        gauss.centre.value = 0
        gauss.A.value = 5000
        gauss.sigma.value = 0.5
        s.data = s.data + gauss.function(energy_axis.axis)
        s.add_gaussian_noise(1, random_state=1)
        self.signal = s

    def _add_spikes(self):
        s = self.signal
        s.data[1, 0, 1] += 200
        s.data[0, 2, 29] += 500
        s.data[1, 2, 14] += 1000

    def test_get_zero_loss_peak_mask(self):
        mask = self.signal.get_zero_loss_peak_mask()
        expected_mask = np.zeros(self.signal.axes_manager.signal_size, dtype=bool)
        expected_mask[13:38] = True
        np.testing.assert_allclose(mask, expected_mask)

    def test_get_zero_loss_peak_mask_signal_mask(self):
        signal_mask = np.zeros(self.signal.axes_manager.signal_size, dtype=bool)
        signal_mask[40:50] = True
        mask = self.signal.get_zero_loss_peak_mask(signal_mask=signal_mask)
        expected_mask = np.zeros(self.signal.axes_manager.signal_size, dtype=bool)
        expected_mask[13:38] = True
        np.testing.assert_allclose(mask, np.logical_or(expected_mask, signal_mask))

    def test_spikes_diagnosis(self):
        if self.signal._lazy:
            pytest.skip("Spikes diagnosis is not supported for lazy signal")
        self._add_spikes()
        self.signal.spikes_diagnosis(zero_loss_peak_mask_width=5.0)

        zlp_mask = self.signal.get_zero_loss_peak_mask()
        hist_data = self.signal._spikes_diagnosis(signal_mask=zlp_mask, bins=25)
        expected_data = np.zeros(25)
        expected_data[0] = 232
        expected_data[12] = 1
        expected_data[-1] = 1
        np.testing.assert_allclose(hist_data.data, expected_data)

        hist_data2 = self.signal._spikes_diagnosis(bins=25)
        expected_data2 = np.array([286, 10, 13, 0, 0, 1, 12, 0])
        np.testing.assert_allclose(hist_data2.data[:8], expected_data2)

        # mask all to check that it raises an error when there is no data
        signal_mask = self.signal.inav[0, 1].data.astype(bool)
        with pytest.raises(ValueError):
            self.signal.spikes_diagnosis(signal_mask=signal_mask)


def test_spikes_removal_tool_no_zlp():
    s = exspy.data.EELS_MnFe()
    with pytest.raises(ValueError):
        # Zero not in energy range
        s.spikes_removal_tool(zero_loss_peak_mask_width=5.0)


def test_spikes_diagnosis_constant_derivative():
    s = hs.signals.Signal1D(np.arange(20).reshape(2, 10))
    with pytest.warns():
        s._spikes_diagnosis(use_gui=False)

    hs.preferences.GUIs.enable_traitsui_gui = False
    with pytest.warns():
        s._spikes_diagnosis(use_gui=True)

    hyperspy_gui_traitsui_spec = importlib.util.find_spec("hyperspy_gui_traitsui")

    if hyperspy_gui_traitsui_spec is None:
        hs.preferences.GUIs.enable_traitsui_gui = True
        s._spikes_diagnosis(use_gui=True)


@lazifyTestClass
class TestPowerLawExtrapolation:
    def setup_method(self, method):
        s = exspy.signals.EELSSpectrum(0.1 * np.arange(50, 250, 0.5) ** -3.0)
        s.axes_manager[-1].is_binned = False
        s.axes_manager[-1].offset = 50
        s.axes_manager[-1].scale = 0.5
        self.s = s

    def test_unbinned(self):
        sc = self.s.isig[:300]
        s = sc.power_law_extrapolation(extrapolation_size=100)
        np.testing.assert_allclose(s.data, self.s.data, atol=10e-3)

    def test_binned(self):
        self.s.data *= self.s.axes_manager[-1].scale
        self.s.axes_manager[-1].is_binned = True
        sc = self.s.isig[:300]
        s = sc.power_law_extrapolation(extrapolation_size=100)
        np.testing.assert_allclose(s.data, self.s.data, atol=10e-3)


@lazifyTestClass
class TestFourierRatioDeconvolution:
    @pytest.mark.parametrize(("extrapolate_lowloss"), [True, False])
    def test_running(self, extrapolate_lowloss):
        s = exspy.signals.EELSSpectrum(np.arange(200))
        gaussian = hs.model.components1D.Gaussian()
        gaussian.A.value = 50
        gaussian.sigma.value = 10
        gaussian.centre.value = 20
        s_ll = exspy.signals.EELSSpectrum(gaussian.function(np.arange(0, 200, 1)))
        s_ll.axes_manager[0].offset = -50
        s.fourier_ratio_deconvolution(s_ll, extrapolate_lowloss=extrapolate_lowloss)


@lazifyTestClass
class TestRebin:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.ones((4, 2, 1024)))
        self.signal = s

    def test_rebin_without_dwell_time(self):
        s = self.signal
        s.rebin(scale=(2, 2, 1))

    def test_rebin_dwell_time(self):
        s = self.signal
        s.metadata.add_node("Acquisition_instrument.TEM.Detector.EELS")
        s_mdEELS = s.metadata.Acquisition_instrument.TEM.Detector.EELS
        s_mdEELS.dwell_time = 0.1
        s_mdEELS.exposure = 0.5
        s2 = s.rebin(scale=(2, 2, 8))
        s2_mdEELS = s2.metadata.Acquisition_instrument.TEM.Detector.EELS
        assert s2_mdEELS.dwell_time == (0.1 * 2 * 2)
        assert s2_mdEELS.exposure == (0.5 * 2 * 2)

        def test_rebin_exposure(self):
            s = self.signal
            s.metadata.exposure = 10.2
            s2 = s.rebin(scale=(2, 2, 8))
            assert s2.metadata.exposure == (10.2 * 2 * 2)

    def test_offset_after_rebin(self):
        s = self.signal
        s.axes_manager[0].offset = 1
        s.axes_manager[1].offset = 2
        s.axes_manager[2].offset = 3
        s2 = s.rebin(scale=(2, 2, 1))
        assert s2.axes_manager[0].offset == 1.5
        assert s2.axes_manager[1].offset == 2.5
        assert s2.axes_manager[2].offset == s.axes_manager[2].offset


@lazifyTestClass
class Test_Estimate_Thickness:
    def setup_method(self, method):
        # Create an empty spectrum
        self.s = hs.load(
            MYPATH.joinpath("data/EELS_LL_linescan_simulated_thickness_variation.hspy")
        )
        self.zlp = hs.load(
            MYPATH.joinpath("data/EELS_ZLP_linescan_simulated_thickness_variation.hspy")
        )

    def test_relative_thickness(self):
        t = self.s.estimate_thickness(zlp=self.zlp)
        np.testing.assert_allclose(t.data, np.arange(0.3, 2, 0.1), atol=4e-3)
        assert t.metadata.Signal.quantity == "$\\frac{t}{\\lambda}$"

    def test_thickness_mfp(self):
        t = self.s.estimate_thickness(zlp=self.zlp, mean_free_path=120)
        np.testing.assert_allclose(t.data, 120 * np.arange(0.3, 2, 0.1), rtol=3e-3)
        assert t.metadata.Signal.quantity == "thickness (nm)"

    def test_thickness_density(self):
        t = self.s.estimate_thickness(zlp=self.zlp, density=3.6)
        np.testing.assert_allclose(t.data, 142 * np.arange(0.3, 2, 0.1), rtol=3e-3)
        assert t.metadata.Signal.quantity == "thickness (nm)"

    def test_thickness_density_and_mfp(self):
        t = self.s.estimate_thickness(zlp=self.zlp, density=3.6, mean_free_path=120)
        np.testing.assert_allclose(t.data, 127.5 * np.arange(0.3, 2, 0.1), rtol=3e-3)
        assert t.metadata.Signal.quantity == "thickness (nm)"

    def test_threshold(self):
        t = self.s.estimate_thickness(threshold=4.5, density=3.6, mean_free_path=120)
        np.testing.assert_allclose(t.data, 127.5 * np.arange(0.3, 2, 0.1), rtol=3e-3)
        assert t.metadata.Signal.quantity == "thickness (nm)"

    def test_threshold_nd(self):
        threshold = self.s._get_navigation_signal()
        threshold.data[:] = 4.5
        t = self.s.estimate_thickness(
            threshold=threshold, density=3.6, mean_free_path=120
        )
        np.testing.assert_allclose(t.data, 127.5 * np.arange(0.3, 2, 0.1), rtol=3e-3)
        assert t.metadata.Signal.quantity == "thickness (nm)"

    def test_no_zlp_or_threshold(self):
        with pytest.raises(ValueError):
            self.s.estimate_thickness()

    def test_no_metadata(self):
        del self.s.metadata.Acquisition_instrument
        with pytest.raises(RuntimeError):
            self.s.estimate_thickness(zlp=self.zlp, density=3.6)


class TestPrintEdgesNearEnergy:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.ones((4, 2, 1024)))
        self.signal = s

    def test_at_532eV(self, capsys):
        s = self.signal
        s.print_edges_near_energy(532)
        captured = capsys.readouterr()

        # Parse the captured output to extract edge information
        lines = captured.out.strip().split("\n")
        # Skip the header lines (first 3 lines) and footer line (last line)
        data_lines = lines[3:-1]

        captured_edges = []
        captured_data = {}
        for line in data_lines:
            # Parse table row: | edge | energy | relevance | description |
            parts = [
                part.strip() for part in line.split("|")[1:-1]
            ]  # Remove empty first/last parts
            edge = parts[0]
            energy = float(parts[1])
            relevance = parts[2]
            description = parts[3]
            captured_edges.append(edge)
            captured_data[edge] = {
                "energy": energy,
                "relevance": relevance,
                "description": description,
            }

        # Test that all expected edges are present
        expected_edges = {"O_K", "Pd_M3", "At_N5", "Sb_M5", "Sb_M4"}
        assert set(captured_edges) == expected_edges
        assert len(captured_edges) == 5

        # Test specific edge properties
        assert captured_data["O_K"]["energy"] == 532.0
        assert captured_data["O_K"]["relevance"] == "Major"
        assert captured_data["O_K"]["description"] == "Abrupt onset"

        assert captured_data["Pd_M3"]["energy"] == 531.0
        assert captured_data["Pd_M3"]["relevance"] == "Minor"
        assert captured_data["Pd_M3"]["description"] == ""

        assert captured_data["At_N5"]["energy"] == 533.0
        assert captured_data["At_N5"]["relevance"] == "Minor"
        assert captured_data["At_N5"]["description"] == ""

        assert captured_data["Sb_M5"]["energy"] == 528.0
        assert captured_data["Sb_M5"]["relevance"] == "Major"
        assert captured_data["Sb_M5"]["description"] == "Delayed maximum"

        assert captured_data["Sb_M4"]["energy"] == 537.0
        assert captured_data["Sb_M4"]["relevance"] == "Major"
        assert captured_data["Sb_M4"]["description"] == "Delayed maximum"

        # Verify ordering is by distance from 532 eV (closest first)
        # O_K (532.0) should be first (distance = 0)
        assert captured_edges[0] == "O_K"

        # Pd_M3 (531.0) and At_N5 (533.0) both have distance = 1.0
        # Their relative order is not deterministic, so just check they're next
        assert captured_edges[1] in ["Pd_M3", "At_N5"]
        assert captured_edges[2] in ["Pd_M3", "At_N5"]
        assert captured_edges[1] != captured_edges[2]  # They should be different

    def test_sequence_edges(self, capsys):
        s = self.signal
        s.print_edges_near_energy(123, edges=["Mn_L2", "O_K", "Fe_L2"])
        captured = capsys.readouterr()
        expected_out = (
            "+-------+-------------------+-----------+-----------------------------+\n"
            "|  edge | onset energy (eV) | relevance |         description         |\n"
            "+-------+-------------------+-----------+-----------------------------+\n"
            "| Mn_L2 |       651.0       |   Major   | Sharp peak. Delayed maximum |\n"
            "|  O_K  |       532.0       |   Major   |         Abrupt onset        |\n"
            "| Fe_L2 |       721.0       |   Major   | Sharp peak. Delayed maximum |\n"
            "+-------+-------------------+-----------+-----------------------------+\n"
        )
        assert captured.out == expected_out

    def test_no_energy_and_edges(self):
        s = self.signal
        with pytest.raises(ValueError):
            s.print_edges_near_energy()


class Test_Edges_At_Energy:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.ones((4, 2, 1024)))
        self.signal = s

    def test_at_532eV(self, capsys):
        s = self.signal
        s.edges_at_energy(532, width=20, only_major=True, order="ascending")
        captured = capsys.readouterr()

        expected_out = (
            "+-------+-------------------+-----------+-----------------+\n"
            "|  edge | onset energy (eV) | relevance |   description   |\n"
            "+-------+-------------------+-----------+-----------------+\n"
            "| Sb_M5 |       528.0       |   Major   | Delayed maximum |\n"
            "|  O_K  |       532.0       |   Major   |   Abrupt onset  |\n"
            "| Sb_M4 |       537.0       |   Major   | Delayed maximum |\n"
            "+-------+-------------------+-----------+-----------------+\n"
        )
        assert captured.out == expected_out


class Test_Get_Complementary_Edges:
    def setup_method(self, method):
        # Create an empty spectrum
        s = exspy.signals.EELSSpectrum(np.ones((4, 2, 1024)))
        self.signal = s

    def test_Fe_O(self):
        s = self.signal
        complementary = s._get_complementary_edges(["Fe_L2", "O_K"])

        assert complementary == ["Fe_L1", "Fe_L3", "Fe_M2", "Fe_M3"]

    def test_Fe_O_only_major(self):
        s = self.signal
        complementary = s._get_complementary_edges(["Fe_L2", "O_K"], only_major=True)

        assert complementary == ["Fe_L3", "Fe_M2", "Fe_M3"]


class Test_Plot_EELS:
    def setup_method(self, method):
        s = exspy.data.EELS_MnFe()
        self.signal = s

    def test_plot_no_markers(self):
        s = self.signal
        s.add_elements(("Mn", "Cr"))
        s.plot()

        assert len(s._edge_markers["names"]) == 0

    def test_plot_edges_True(self):
        s = self.signal
        s.add_elements(("Mn", "Cr"))
        s.plot(plot_edges=True)

        print(s._edge_markers["names"])

        assert len(s._edge_markers["names"]) == 8
        assert set(s._edge_markers["names"]) == {
            "Cr_L2",
            "Cr_L3",
            "Cr_L1",
            "Fe_L2",
            "Fe_L3",
            "Mn_L2",
            "Mn_L3",
            "Mn_L1",
        }

    def test_plot_edges_True_without_elements(self):
        s = self.signal
        del s.metadata.Sample.elements
        s.metadata
        with pytest.raises(ValueError):
            s.plot(plot_edges=True)

    def test_plot_edges_from_element_family_specific(self):
        s = self.signal
        s.plot(plot_edges=["Mn", "Ti_L", "Cr_L3"], only_edges=("Major"))

        print(s._edge_markers["names"])

        assert len(s._edge_markers["names"]) == 7
        assert set(s._edge_markers["names"]) == {
            "Fe_L2",
            "Fe_L3",
            "Mn_L2",
            "Mn_L3",
            "Ti_L2",
            "Ti_L3",
            "Cr_L3",
        }

    def test_unsupported_edge_family(self):
        s = self.signal
        with pytest.raises(AttributeError):
            s.plot(plot_edges=["Cr_P"])

    def test_unsupported_edge(self):
        s = self.signal
        with pytest.raises(AttributeError):
            s.plot(plot_edges=["Xe_P4"])

    def test_unsupported_element(self):
        s = self.signal
        with pytest.raises(ValueError):
            s.plot(plot_edges=["ABC_L1"])

    def test_remove_edge_labels(self):
        s = self.signal
        del s.metadata.Sample.elements
        s.plot(plot_edges=["Cr_L", "Fe_L2"])
        s._remove_edge_labels(["Cr_L1", "Fe_L2"])

        assert len(s._edge_markers["names"]) == 2
        assert set(s._edge_markers["names"]) == set(["Cr_L2", "Cr_L3"])

    def test_plot_edges_without_markers_provided(self):
        s = self.signal
        s.plot()
        s._plot_edge_labels({"Fe_L2": 721.0, "O_K": 532.0})

        assert len(s._edge_markers["names"]) == 2
        assert set(s._edge_markers["names"]) == set(["Fe_L2", "O_K"])


@lazifyTestClass
class TestVacuumMask:
    def setup_method(self, method):
        s = exspy.signals.EELSSpectrum(np.array([np.linspace(0.001, 0.5, 20)] * 100).T)
        s.add_poissonian_noise(random_state=1)
        s.axes_manager[-1].scale = 0.25
        s.axes_manager[-1].units = "eV"
        s.inav[:10] += 20
        self.signal = s

    def test_vacuum_mask_opening(self):
        s = self.signal
        mask = s.vacuum_mask(opening=True)
        assert not mask.data[0]
        assert not mask.data[9]
        assert mask.data[10]
        assert mask.data[-1]

    def test_vacuum_mask_threshold(self):
        s = self.signal
        mask = s.vacuum_mask(threshold=20)
        assert mask.data[0]
        assert not mask.data[1]
        assert not mask.data[2]
        assert not mask.data[9]
        assert mask.data[10]
        assert mask.data[-1]

    def test_vacuum_mask_navigation_dimension_0(self):
        s = self.signal
        s2 = s.sum()
        with pytest.raises(RuntimeError):
            s2.vacuum_mask()
