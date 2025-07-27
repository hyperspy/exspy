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
import pytest

import hyperspy.api as hs
from hyperspy.components1d import Gaussian
from hyperspy.decorators import lazifyTestClass

import exspy
from exspy._defaults_parser import preferences
from exspy._misc.eds import utils as utils_eds
from exspy.signals import EDSTEMSpectrum


@lazifyTestClass
class Test_metadata:
    def setup_method(self, method):
        # Create an empty spectrum
        s = EDSTEMSpectrum(np.ones((4, 2, 1024)))
        s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time = 3.1
        s.metadata.Acquisition_instrument.TEM.beam_energy = 15.0
        self.signal = s

    def test_sum_minimum_missing(self):
        s = EDSTEMSpectrum(np.ones((4, 2, 1024)))
        s.sum()

    def test_sum_live_time1(self):
        s = self.signal
        old_metadata = s.metadata.deepcopy()
        sSum = s.sum(0)
        assert (
            sSum.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time
            == s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time * 2
        )
        # Check that metadata is unchanged
        print(old_metadata, s.metadata)  # Capture for comparison on error
        assert old_metadata.as_dictionary() == s.metadata.as_dictionary(), (
            "Source metadata changed"
        )

    def test_sum_live_time2(self):
        s = self.signal
        old_metadata = s.metadata.deepcopy()
        sSum = s.sum((0, 1))
        assert (
            sSum.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time
            == s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time * 2 * 4
        )
        # Check that metadata is unchanged
        print(old_metadata, s.metadata)  # Capture for comparison on error
        assert old_metadata.as_dictionary() == s.metadata.as_dictionary(), (
            "Source metadata changed"
        )

    def test_sum_live_time_out_arg(self):
        s = self.signal
        sSum = s.sum(0)
        s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time = 4.2
        s_resum = s.sum(0)
        r = s.sum(0, out=sSum)
        assert r is None
        assert (
            s_resum.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time
            == s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time * 2
        )
        np.testing.assert_allclose(s_resum.data, sSum.data)

    def test_rebin_live_time(self):
        s = self.signal
        old_metadata = s.metadata.deepcopy()
        dim = s.axes_manager.shape
        s = s.rebin(new_shape=[dim[0] / 2, dim[1] / 2, dim[2]])
        assert (
            s.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time == 3.1 * 2 * 2
        )
        # Check that metadata is unchanged
        print(old_metadata, self.signal.metadata)  # Captured on error
        assert old_metadata.as_dictionary() == self.signal.metadata.as_dictionary(), (
            "Source metadata changed"
        )

    def test_offset_after_rebin(self):
        s = self.signal
        s.axes_manager[0].offset = 1
        s.axes_manager[1].offset = 2
        s.axes_manager[2].offset = 3
        s2 = s.rebin(scale=(2, 2, 1))
        assert s2.axes_manager[0].offset == 1.5
        assert s2.axes_manager[1].offset == 2.5
        assert s2.axes_manager[2].offset == s.axes_manager[2].offset

    def test_add_elements(self):
        s = self.signal
        s.add_elements(["Al", "Ni"])
        assert s.metadata.Sample.elements == ["Al", "Ni"]
        s.add_elements(["Al", "Ni"])
        assert s.metadata.Sample.elements == ["Al", "Ni"]
        s.add_elements(
            [
                "Fe",
            ]
        )
        assert s.metadata.Sample.elements == ["Al", "Fe", "Ni"]
        s.set_elements(["Al", "Ni"])
        assert s.metadata.Sample.elements == ["Al", "Ni"]

    def test_default_param(self):
        s = self.signal
        mp = s.metadata
        assert (
            mp.Acquisition_instrument.TEM.Detector.EDS.energy_resolution_MnKa
            == preferences.EDS.eds_mn_ka
        )

    def test_TEM_to_SEM(self):
        s = self.signal.inav[0, 0]
        signal_type = "EDS_SEM"
        mp = s.metadata.Acquisition_instrument.TEM.Detector.EDS
        mp.energy_resolution_MnKa = 125.3
        sSEM = s.deepcopy()
        sSEM.set_signal_type(signal_type)
        mpSEM = sSEM.metadata.Acquisition_instrument.SEM.Detector.EDS
        results = [mp.energy_resolution_MnKa, signal_type]
        resultsSEM = [mpSEM.energy_resolution_MnKa, sSEM.metadata.Signal.signal_type]
        assert results == resultsSEM

    def test_get_calibration_from(self):
        s = self.signal
        scalib = EDSTEMSpectrum(np.ones(1024))
        energy_axis = scalib.axes_manager.signal_axes[0]
        energy_axis.scale = 0.01
        energy_axis.offset = -0.10
        s.get_calibration_from(scalib)
        assert s.axes_manager.signal_axes[0].scale == energy_axis.scale

    def test_are_microscope_parameters_missing(self):
        assert not self.signal._are_microscope_parameters_missing()

        del self.signal.metadata.Acquisition_instrument.TEM.beam_energy
        del self.signal.metadata.Acquisition_instrument.TEM.Detector.EDS.live_time
        assert self.signal._are_microscope_parameters_missing()


@lazifyTestClass
class Test_quantification:
    def setup_method(self, method):
        s = EDSTEMSpectrum(np.ones([2, 2, 1024]))
        energy_axis = s.axes_manager.signal_axes[0]
        energy_axis.scale = 1e-2
        energy_axis.units = "keV"
        energy_axis.name = "Energy"
        s.set_microscope_parameters(
            beam_energy=200,
            live_time=2.5,
            tilt_stage=0.0,
            azimuth_angle=0,
            elevation_angle=35,
            energy_resolution_MnKa=130,
            beam_current=0.05,
        )
        elements = ["Al", "Zn"]
        xray_lines = ["Al_Ka", "Zn_Ka"]
        intensities = [300, 500]
        for i, xray_line in enumerate(xray_lines):
            gauss = Gaussian()
            line_energy, FWHM = s._get_line_energy(xray_line, FWHM_MnKa="auto")
            gauss.centre.value = line_energy
            gauss.A.value = intensities[i]
            gauss.sigma.value = FWHM
            s.data[:] += gauss.function(energy_axis.axis)

        s.set_elements(elements)
        s.add_lines(xray_lines)
        s.axes_manager[0].scale = 0.5
        s.axes_manager[1].scale = 0.5
        s.axes_manager[0].units = "nm"
        s.axes_manager[1].units = "nm"
        self.signal = s

    def test_metadata(self):
        TEM_md = self.signal.metadata.Acquisition_instrument.TEM
        np.testing.assert_approx_equal(TEM_md.beam_energy, 200)
        np.testing.assert_approx_equal(TEM_md.beam_current, 0.05)
        np.testing.assert_approx_equal(TEM_md.Stage.tilt_alpha, 0.0)
        np.testing.assert_approx_equal(TEM_md.Detector.EDS.live_time, 2.5)
        np.testing.assert_approx_equal(TEM_md.Detector.EDS.elevation_angle, 35)
        np.testing.assert_approx_equal(TEM_md.Detector.EDS.energy_resolution_MnKa, 130)

        self.signal.set_microscope_parameters(real_time=3.1)
        self.signal.set_microscope_parameters(probe_area=1.2)
        np.testing.assert_approx_equal(TEM_md.probe_area, 1.2)
        np.testing.assert_approx_equal(TEM_md.Detector.EDS.real_time, 3.1)

    def test_quant_one_intensity_error(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        intensities = s.get_lines_intensity()[:1]
        assert len(intensities) == 1
        with pytest.raises(ValueError):
            _ = s.quantification(intensities, method, kfactors)

        intensities = s.get_lines_intensity()[0]
        with pytest.raises(ValueError):
            _ = s.quantification(intensities, method, kfactors)

    def test_quant_lorimer(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        composition_units = "weight"
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, kfactors, composition_units)
        s2 = s.rebin(new_shape=(1, 1, 1024)).squeeze()
        s2.quantification(
            intensities, method, kfactors, composition_units, plot_result=True
        )
        np.testing.assert_allclose(res[0].data, np.ones((2, 2)) * 22.70779, atol=1e-3)

        # Test plot_results
        s2 = s.inav[0, 0]
        s2.quantification(
            intensities, method, kfactors, composition_units, plot_result=True
        )
        np.testing.assert_allclose(res[0].data, 22.70779)

    def test_quant_lorimer_mask(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        composition_units = "weight"
        intensities = s.get_lines_intensity()
        mask = np.array([[1, 1], [0, 0]])
        res = s.quantification(
            intensities, method, kfactors, composition_units, navigation_mask=mask
        )
        np.testing.assert_allclose(
            res[0].data, np.array([[0, 0], [22.70779, 22.70779]]), atol=1e-3
        )

    def test_quant_lorimer_warning(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        composition_units = "weight"
        intensities = s.get_lines_intensity()
        with pytest.raises(ValueError, match="Thickness is required for absorption"):
            _ = s.quantification(
                intensities,
                method,
                kfactors,
                composition_units,
                absorption_correction=True,
                thickness=None,
            )

    def test_quant_lorimer_ac(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        composition_units = "weight"
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, kfactors, composition_units)
        np.testing.assert_allclose(res[0].data, np.ones((2, 2)) * 22.70779, atol=1e-3)
        res2 = s.quantification(
            intensities,
            method,
            kfactors,
            composition_units,
            absorption_correction=True,
            thickness=1.0,
        )
        res3 = s.quantification(
            intensities,
            method,
            kfactors,
            composition_units,
            absorption_correction=True,
            thickness=300.0,
        )
        res4 = s.quantification(
            intensities,
            method,
            kfactors,
            composition_units,
            absorption_correction=True,
            thickness=0.0001,
        )
        list.reverse(intensities)
        list.reverse(kfactors)
        res5 = s.quantification(
            intensities,
            method,
            kfactors,
            composition_units,
            absorption_correction=True,
            thickness=300.0,
        )
        np.testing.assert_allclose(res5[0][0].data, res3[0][1].data, atol=1e-5)
        np.testing.assert_allclose(
            res2[0][0].data, np.ones((2, 2)) * 22.743013, atol=1e-3
        )
        np.testing.assert_allclose(
            res3[0][0].data, np.ones((2, 2)) * 31.816908, atol=1e-3
        )
        np.testing.assert_allclose(res[0].data, res4[0][0].data, atol=1e-5)

    def test_quant_zeta(self):
        s = self.signal
        method = "zeta"
        composition_units = "weight"
        factors = [20, 50]
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, factors, composition_units)
        np.testing.assert_allclose(
            res[1].data, np.ones((2, 2)) * 2.7125736e-03, atol=1e-3
        )
        np.testing.assert_allclose(
            res[0][1].data, np.ones((2, 2)) * 80.962287987, atol=1e-3
        )
        res2 = s.quantification(
            intensities,
            method,
            factors,
            composition_units,
            absorption_correction=True,
            thickness=1.0,
        )
        res3 = s.quantification(
            intensities,
            method,
            factors,
            composition_units,
            absorption_correction=True,
            thickness=100.0,
        )
        assert res2 == res3
        np.testing.assert_allclose(
            res2[0][1].data, np.ones((2, 2)) * 65.5867, atol=1e-3
        )

    def test_quant_cross_section_units(self):
        s = self.signal.deepcopy()
        s2 = self.signal.deepcopy()
        s.axes_manager[0].units = "µm"
        s.axes_manager[1].units = "µm"
        s.axes_manager[0].scale = 0.5 / 1000
        s.axes_manager[1].scale = 0.5 / 1000

        method = "cross_section"
        factors = [3, 5]
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, factors)
        res2 = s2.quantification(intensities, method, factors)
        np.testing.assert_allclose(res[0][0].data, res2[0][0].data)
        # Check that the quantification doesn't change the units of the signal
        assert s.axes_manager[0].units == "µm"
        assert s.axes_manager[1].units == "µm"

    @pytest.mark.parametrize("axes", (None, "nav_axes", [0, 1], ["x", "y"]))
    def test_get_probe_area(self, axes):
        s = self.signal
        s.axes_manager[0].name = "x"
        s.axes_manager[1].name = "y"
        s.axes_manager[0].units = "µm"
        s.axes_manager[1].units = "µm"
        s.axes_manager[0].scale = 0.5 / 1000
        s.axes_manager[1].scale = 0.5 / 1000
        if axes == "nav_axes":
            axes = s.axes_manager.navigation_axes
        np.testing.assert_allclose(s.get_probe_area(axes), 0.25, atol=1e-3)

    @pytest.mark.parametrize("axes", (None, "nav_axes", [0], ["x"]))
    def test_get_probe_area_line_scan(self, axes):
        s = self.signal.inav[0]
        s.axes_manager[0].name = "x"
        s.axes_manager[0].units = "µm"
        s.axes_manager[0].scale = 0.5 / 1000
        if axes == "nav_axes":
            axes = s.axes_manager.navigation_axes
        np.testing.assert_allclose(s.get_probe_area(axes), 0.25, atol=1e-3)

    @pytest.mark.parametrize("axes", (None, "nav_axes", [0], ["x"]))
    def test_get_probe_area_line_scan_other_nav_axes(self, axes):
        s = self.signal
        s.axes_manager[0].name = "x"
        s.axes_manager[1].name = "time"
        s.axes_manager[0].units = "µm"
        s.axes_manager[1].units = "s"
        s.axes_manager[0].scale = 0.5 / 1000
        s.axes_manager[1].scale = 10
        if axes == "nav_axes" or axes is None:
            axes = s.axes_manager.navigation_axes
            with pytest.raises(ValueError):
                s.get_probe_area(axes)
        else:
            np.testing.assert_allclose(s.get_probe_area(axes), 0.25, atol=1e-3)

    def test_zeta_vs_cross_section(self):
        s = self.signal
        factors = [3, 5]
        method = "zeta"
        intensities = s.get_lines_intensity()
        zfactors = utils_eds.cross_section_to_zeta([3, 5], ["Al", "Zn"])
        factors2 = utils_eds.zeta_to_cross_section(zfactors, ["Al", "Zn"])
        np.testing.assert_allclose(factors, factors2, atol=1e-3)

        res = s.quantification(
            intensities,
            method,
            factors=utils_eds.cross_section_to_zeta([22.402, 21.7132], ["Al", "Zn"]),
        )
        res2 = s.quantification(
            intensities, method="cross_section", factors=[22.402, 21.7132]
        )
        np.testing.assert_allclose(res[0][0].data, res2[0][0].data, atol=1e-3)
        np.testing.assert_allclose(res[0][0].data, np.ones((2, 2)) * 36.2969, atol=1e-3)

    def test_quant_cross_section(self):
        s = self.signal
        method = "cross_section"
        factors = [3, 5]
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, factors)
        np.testing.assert_allclose(
            res[1][0].data, np.ones((2, 2)) * 21517.1647, atol=1e-3
        )
        np.testing.assert_allclose(
            res[1][1].data, np.ones((2, 2)) * 21961.6166, atol=1e-3
        )
        np.testing.assert_allclose(res[0][0].data, np.ones((2, 2)) * 49.4889, atol=1e-3)

    def test_method_error(self):
        s = self.signal
        method = "random_method"
        factors = [3, 5]
        intensities = s.get_lines_intensity()
        with pytest.raises(
            ValueError, match="Please specify method for quantification"
        ):
            _ = s.quantification(intensities, method, factors)

    def test_quant_cross_section_ac(self):
        s = self.signal
        method = "cross_section"
        zfactors = [20, 50]
        factors = utils_eds.zeta_to_cross_section(zfactors, ["Al", "Zn"])
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, factors, absorption_correction=True)
        res2 = s.quantification(
            intensities, method="zeta", factors=zfactors, absorption_correction=True
        )
        np.testing.assert_allclose(
            res[0][1].data, np.ones((2, 2)) * 44.02534, atol=1e-3
        )
        np.testing.assert_allclose(res2[0][0].data, res[0][0].data, atol=1e-3)

    def test_quant_zeros(self):
        intens = np.array(
            [
                [0.5, 0.5, 0.5],
                [0.0, 0.5, 0.5],
                [0.5, 0.0, 0.5],
                [0.5, 0.5, 0.0],
                [0.5, 0.0, 0.0],
            ]
        ).T

        # Specify intensities_sum_threshold not to set output values to zero
        quant = utils_eds.quantification_cliff_lorimer(
            intens, [1, 1, 3], intensities_sum_threshold=0.1
        ).T
        np.testing.assert_allclose(
            quant,
            np.array(
                [
                    [0.2, 0.2, 0.6],
                    [0.0, 0.25, 0.75],
                    [0.25, 0.0, 0.75],
                    [0.5, 0.5, 0.0],
                    [1.0, 0.0, 0.0],
                ]
            ),
        )

        # with default value of intensities_sum_threshold
        quant = utils_eds.quantification_cliff_lorimer(intens, [1, 1, 3]).T
        np.testing.assert_allclose(quant, np.zeros_like(quant))

    def test_edx_cross_section_to_zeta(self):
        cs = [3, 6]
        elements = ["Pt", "Ni"]
        res = utils_eds.cross_section_to_zeta(cs, elements)
        np.testing.assert_allclose(res, [1079.815272, 162.4378035], atol=1e-3)

    def test_zeta_to_edx_cross_section(self):
        factors = [1079.815272, 162.4378035]
        elements = ["Pt", "Ni"]
        res = utils_eds.zeta_to_cross_section(factors, elements)
        np.testing.assert_allclose(res, [3, 6], atol=1e-3)

    def test_quant_element_order(self):
        s = self.signal
        s.set_elements([])
        s.set_lines([])
        lines = ["Zn_Ka", "Al_Ka"]
        kfactors = [2.0009344042484134, 1]
        intensities = s.get_lines_intensity(xray_lines=lines)
        res = s.quantification(
            intensities, method="CL", factors=kfactors, composition_units="weight"
        )
        assert res[0].metadata.Sample.xray_lines[0] == "Zn_Ka"
        assert res[1].metadata.Sample.xray_lines[0] == "Al_Ka"
        np.testing.assert_allclose(res[1].data, np.ones((2, 2)) * 22.70779, atol=1e-3)

    def test_CL_get_mass_thickness(self):
        s = self.signal
        method = "CL"
        kfactors = [1, 2.0009344042484134]
        composition_units = "weight"
        intensities = s.get_lines_intensity()
        res = s.quantification(intensities, method, kfactors, composition_units)

        mass_thickness = s.CL_get_mass_thickness(res, 100.0)[0, 0]
        np.testing.assert_allclose(mass_thickness, 6.1317741e-4)

        thickness = np.array([[100.0, 90.0], [85, 80.0]])
        mass_thickness2 = s.CL_get_mass_thickness(res, thickness)
        np.testing.assert_allclose(mass_thickness2, mass_thickness * thickness / 100)


@lazifyTestClass
class Test_vacuum_mask:
    def setup_method(self, method):
        s = EDSTEMSpectrum(np.array([np.linspace(0.001, 0.5, 20)] * 100).T)
        s.add_poissonian_noise()
        self.signal = s

    def test_vacuum_mask(self):
        s = self.signal
        assert s.vacuum_mask().data[0]
        assert not s.vacuum_mask().data[-1]

    def test_vacuum_mask_navigation_dimension_0(self):
        s = self.signal
        s2 = s.sum()
        with pytest.raises(RuntimeError):
            s2.vacuum_mask()


@pytest.mark.parametrize("normalise_poissonian_noise", [True, False])
def test_decomposition(normalise_poissonian_noise):
    s = EDSTEMSpectrum(np.ones(shape=(32, 32, 1024)))
    s.add_poissonian_noise()
    # default uses `vacuum_mask`
    s.decomposition(normalise_poissonian_noise)

    # test with numpy array mask
    mask = s.vacuum_mask().data
    s.decomposition(normalise_poissonian_noise, navigation_mask=mask)


@lazifyTestClass
class Test_simple_model:
    def setup_method(self, method):
        s = utils_eds.xray_lines_model(elements=["Al", "Zn"], weight_percents=[50, 50])
        self.signal = s

    def test_intensity(self):
        s = self.signal
        np.testing.assert_allclose(
            [i.data[0] for i in s.get_lines_intensity(integration_window_factor=5.0)],
            [0.5, 0.5],
            atol=1e-1,
        )

    def test_intensity_dtype_uint(self):
        s = self.signal
        s.data *= 1e5
        s.change_dtype("uint")
        bw = s.estimate_background_windows()
        np.testing.assert_allclose(
            [i.data[0] for i in s.get_lines_intensity(background_windows=bw)],
            [5e4, 5e4],
            rtol=0.03,
        )

    def test_outside_range_background_windows(self):
        s = self.signal
        bw = s.estimate_background_windows()
        with pytest.raises(ValueError):
            s.isig[2.0:].plot(True, background_windows=bw)


def test_plot_windows():
    s = exspy.data.EDS_TEM_FePt_nanoparticles()

    rng = np.random.default_rng()

    [s * v * 10 for v in rng.random((10))]

    s = hs.stack([s * v * 10 for v in rng.random((10))])
    s = hs.stack([s * v * 10 for v in rng.random((5))])

    bw = s.estimate_background_windows(line_width=[5.0, 2.0])
    iw = s.estimate_integration_windows(windows_width=3)

    s.plot(True, background_windows=bw, integration_windows=iw)
    s.axes_manager.indices = (1, 2)


def test_with_signals_examples():
    sig = exspy.data.EDS_TEM_FePt_nanoparticles()
    for s in (sig, sig.as_lazy()):
        np.testing.assert_allclose(
            np.array([res.data[0] for res in s.get_lines_intensity()]),
            np.array([3710, 15872]),
        )


class Test_eds_markers:
    def setup_method(self, method):
        s = utils_eds.xray_lines_model(elements=["Al", "Zn"], weight_percents=[50, 50])
        self.signal = s

    def test_plot_auto_add(self):
        s = self.signal
        s.plot(xray_lines=True)
        # Should contain 6 lines
        assert sorted(
            s._xray_markers["names"]
            == ["Al_Ka", "Al_Kb", "Zn_Ka", "Zn_Kb", "Zn_La", "Zn_Lb1"]
        )

    def test_manual_add_line(self):
        s = self.signal
        s.plot()
        s.add_xray_lines_markers(["Zn_La"])
        assert list(s._xray_markers["names"]) == ["Zn_La"]
        assert len(s._xray_markers["names"]) == 1

    def test_manual_add_line_error(self):
        s = self.signal
        with pytest.raises(RuntimeError):
            s.add_xray_lines_markers(["Zn_La"])

    def test_manual_remove_element(self):
        s = self.signal
        s.plot()
        s.add_xray_lines_markers(["Zn_Ka", "Zn_Kb", "Zn_La"])
        s.remove_xray_lines_markers(["Zn_Kb"])
        assert sorted(s._xray_markers["names"]) == ["Zn_Ka", "Zn_La"]
        s.remove_xray_lines_markers(["Zn_Ka"], render_figure=False)
        assert sorted(s._xray_markers["names"]) == ["Zn_La"]
        s.remove_xray_lines_markers(["Zn_La"], render_figure=True)
        assert sorted(s._xray_markers["names"]) == []
        assert len(s._xray_markers["texts"].get_current_kwargs()["offsets"]) == 0
        assert len(s._xray_markers["texts"].get_current_kwargs()["texts"]) == 0
        assert len(s._xray_markers["lines"].get_current_kwargs()["segments"]) == 0
