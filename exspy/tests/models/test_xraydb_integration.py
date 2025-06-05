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

"""Test suite for XrayDB integration in exspy."""

import pytest
from hyperspy.decorators import lazifyTestClass

import exspy
from exspy._misc.eds import utils as utils_eds
from exspy._misc.eds.xraydb_utils import (
    get_xray_line_energy_with_fallback,
    validate_xray_line_source,
)

# Skip all tests if xraydb is not available
pytest.importorskip("xraydb")


class TestXrayDBIntegration:
    """Test XrayDB integration functionality."""

    def test_parameter_validation(self):
        """Test that parameter validation works correctly."""
        # Valid parameters should pass
        validate_xray_line_source("xraydb")
        validate_xray_line_source("internal")

        # Invalid parameters should raise ValueError
        with pytest.raises(ValueError):
            validate_xray_line_source("invalid")

    def test_energy_retrieval_with_fallback(self):
        """Test X-ray line energy retrieval with fallback mechanism."""
        test_lines = ["Al_Ka", "Fe_Ka", "Cu_Ka"]

        for xray_line in test_lines:
            # Both sources should return valid energies
            internal_energy = get_xray_line_energy_with_fallback(
                xray_line, source="internal"
            )
            xraydb_energy = get_xray_line_energy_with_fallback(
                xray_line, source="xraydb"
            )

            assert internal_energy > 0, (
                f"Internal energy for {xray_line} should be positive"
            )
            assert xraydb_energy > 0, (
                f"XrayDB energy for {xray_line} should be positive"
            )

            # Energies should be close but may differ slightly
            diff_ev = abs(xraydb_energy - internal_energy) * 1000
            assert diff_ev < 10, (
                f"Energy difference for {xray_line} too large: {diff_ev} eV"
            )

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_model_creation_with_sources(self, source):
        """Test model creation with different X-ray line sources."""
        s_sem = exspy.data.EDS_SEM_TM002()
        s_tem = exspy.data.EDS_TEM_FePt_nanoparticles()

        # Should be able to create models with both sources
        m_sem = s_sem.create_model(xray_line_source=source, auto_add_lines=False)
        m_tem = s_tem.create_model(xray_line_source=source, auto_add_lines=False)

        assert len(m_sem) > 0, "SEM model should have background component"
        assert len(m_tem) > 0, "TEM model should have background component"

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_family_lines_addition(self, source):
        """Test adding family lines with different sources."""
        s = exspy.data.EDS_SEM_TM002()
        m = s.create_model(xray_line_source=source, auto_add_lines=False)

        # Add specific lines
        m.add_family_lines(["Al_Ka", "Cu_Ka"])

        # Check that lines were added
        assert "Al_Ka" in [comp.name for comp in m]
        assert "Cu_Ka" in [comp.name for comp in m]

        # Check that energies are reasonable
        al_ka_energy = m["Al_Ka"].centre.value
        cu_ka_energy = m["Cu_Ka"].centre.value

        assert 1.4 < al_ka_energy < 1.5, (
            f"Al_Ka energy should be ~1.49 keV, got {al_ka_energy}"
        )
        assert 8.0 < cu_ka_energy < 8.1, (
            f"Cu_Ka energy should be ~8.05 keV, got {cu_ka_energy}"
        )

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_auto_add_lines(self, source):
        """Test automatic line addition from metadata."""
        s = exspy.data.EDS_SEM_TM002()

        # Create model with auto_add_lines=True
        m = s.create_model(xray_line_source=source, auto_add_lines=True)

        # Should have added lines for elements in metadata
        component_names = [comp.name for comp in m]

        # Check that some expected lines are present based on metadata elements
        assert any("Al_Ka" in name for name in component_names), (
            "Al_Ka line should be added"
        )
        assert any("Cu_Ka" in name for name in component_names), (
            "Cu_Ka line should be added"
        )
        assert any("Mn_Ka" in name for name in component_names), (
            "Mn_Ka line should be added"
        )


class TestDatabaseSourcesCalibration:
    """Test X-ray line energy calibration with different database sources."""

    def test_calibration_with_both_sources(self):
        """Test energy calibration with both database sources."""
        # Create a test spectrum
        s = utils_eds.xray_lines_model(
            elements=["Fe"],
            beam_energy=200,
            weight_percents=[100],
            energy_axis={
                "units": "keV",
                "size": 400,
                "scale": 0.01,
                "name": "E",
                "offset": 5.0,
            },
        )

        for source in ["internal", "xraydb"]:
            # Create model with specific database source
            m = s.create_model(xray_line_source=source)
            m.fit()

            # Get reference energy
            reference_energy, _ = s._get_line_energy(
                "Fe_Ka", FWHM_MnKa="auto", xray_line_source=source
            )

            # Deliberately set wrong energy
            m["Fe_Ka"].centre.value = 6.39
            assert m["Fe_Ka"].centre.value == 6.39, (
                "Energy should be set to wrong value"
            )

            # Calibrate energy
            m.calibrate_xray_lines(calibrate="energy", xray_lines=["Fe_Ka"])
            calibrated_energy = m["Fe_Ka"].centre.value

            # Check that calibration worked
            assert abs(calibrated_energy - reference_energy) < 1e-6, (
                f"Calibrated energy should match reference for {source} source"
            )
            assert not m["Fe_Ka"].centre.free, (
                f"Line should be fixed after calibration with {source}"
            )

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_calibration_accuracy(self, source):
        """Test that calibration restores correct energy values."""
        s = utils_eds.xray_lines_model(
            elements=["Al", "Fe"],
            beam_energy=200,
            weight_percents=[50, 50],
            energy_axis={
                "units": "keV",
                "size": 800,
                "scale": 0.01,
                "name": "E",
                "offset": 1.0,
            },
        )

        m = s.create_model(xray_line_source=source)
        m.fit()

        # Store reference energies
        al_ref, _ = s._get_line_energy(
            "Al_Ka", FWHM_MnKa="auto", xray_line_source=source
        )
        fe_ref, _ = s._get_line_energy(
            "Fe_Ka", FWHM_MnKa="auto", xray_line_source=source
        )

        # Introduce errors
        m["Al_Ka"].centre.value = 1.4  # Wrong value
        m["Fe_Ka"].centre.value = 6.0  # Wrong value

        # Calibrate
        m.calibrate_xray_lines(calibrate="energy", xray_lines=["Al_Ka", "Fe_Ka"])

        # Check accuracy
        assert abs(m["Al_Ka"].centre.value - al_ref) < 1e-6, "Al_Ka calibration failed"
        assert abs(m["Fe_Ka"].centre.value - fe_ref) < 1e-6, "Fe_Ka calibration failed"


@lazifyTestClass
class TestXrayDBWithLazySignals:
    """Test XrayDB integration with lazy signals."""

    def setup_method(self, method):
        self.s_sem = exspy.data.EDS_SEM_TM002()
        self.s_tem = exspy.data.EDS_TEM_FePt_nanoparticles()

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_lazy_model_creation(self, source):
        """Test that lazy signals work with XrayDB integration."""
        # Create models with both sources
        m_sem = self.s_sem.create_model(xray_line_source=source, auto_add_lines=False)
        m_tem = self.s_tem.create_model(xray_line_source=source, auto_add_lines=False)

        # Should work regardless of lazy or not
        assert len(m_sem) >= 1, "SEM model should have at least background"
        assert len(m_tem) >= 1, "TEM model should have at least background"

    @pytest.mark.parametrize("source", ["internal", "xraydb"])
    def test_lazy_family_lines(self, source):
        """Test adding family lines to lazy signals."""
        m = self.s_sem.create_model(xray_line_source=source, auto_add_lines=False)

        # Add lines
        m.add_family_lines(["Al_Ka"])

        # Should work with lazy signals
        assert "Al_Ka" in [comp.name for comp in m]
        assert hasattr(m["Al_Ka"], "centre")
