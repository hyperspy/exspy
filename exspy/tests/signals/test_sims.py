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

"""Tests for SIMSSpectrum and FIBSIMSSpectrum signal classes."""

import pathlib

import numpy as np
import pytest

from exspy.signals.fib_sims import FIBSIMSSpectrum, LazyFIBSIMSSpectrum

# ---------------------------------------------------------------------------
# Paths to rosettasciio test fixtures (optional dependency)
# ---------------------------------------------------------------------------
_RSCIIO_DATA = (
    pathlib.Path(__file__).parent.parent.parent.parent.parent
    / "rosettasciio"
    / "rsciio"
    / "tests"
    / "data"
    / "tofwerk"
)
OPENED_FILE = _RSCIIO_DATA / "fib_sims_opened.h5"
RAW_FILE = _RSCIIO_DATA / "fib_sims_raw.h5"

_FILES_AVAILABLE = OPENED_FILE.exists() and RAW_FILE.exists()
skip_no_files = pytest.mark.skipif(
    not _FILES_AVAILABLE,
    reason="Tofwerk test fixtures not found",
)


# ---------------------------------------------------------------------------
# Helper: build a synthetic FIBSIMSSpectrum with known values
# ---------------------------------------------------------------------------


def _make_fib_sims(shape=(3, 4, 5, 10), nav_axes=3):
    """Return a FIBSIMSSpectrum with a ramp along the signal axis."""
    rng = np.random.default_rng(0)
    data = rng.uniform(1, 100, shape).astype(np.float32)
    s = FIBSIMSSpectrum(data)
    masses = np.linspace(1.0, 100.0, shape[-1])
    s.axes_manager.signal_axes[0].axis = masses
    return s


def _make_fib_sims_with_metadata(**extra):
    """Return a FIBSIMSSpectrum with minimal ToF metadata."""
    s = _make_fib_sims()
    s.metadata.set_item("Acquisition_instrument.FIB_SIMS.ToF.sample_interval_s", 1e-9)
    s.metadata.set_item("Acquisition_instrument.FIB_SIMS.ToF.single_ion_signal", 100.0)
    s.metadata.set_item(
        "Acquisition_instrument.FIB_SIMS.ToF.tof_period_samples", 128000
    )
    s.metadata.set_item("Acquisition_instrument.FIB_SIMS.n_depth_slices", 3)
    s.metadata.set_item("Acquisition_instrument.FIB_SIMS.n_segments", 1)
    for key, val in extra.items():
        s.metadata.set_item(key, val)
    return s


# ---------------------------------------------------------------------------
# TestSignalDispatch
# ---------------------------------------------------------------------------


@skip_no_files
class TestSignalDispatch:
    def test_opened_file_dispatches_fib_sims(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), reader="Tofwerk")
        types = [type(s).__name__ for s in sigs]
        assert "FIBSIMSSpectrum" in types, f"Expected FIBSIMSSpectrum, got {types}"
        fib = next(s for s in sigs if isinstance(s, FIBSIMSSpectrum))
        assert fib.axes_manager.signal_dimension == 1

    def test_lazy_opened_file(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), reader="Tofwerk", lazy=True)
        fib_lazy = [s for s in sigs if isinstance(s, LazyFIBSIMSSpectrum)]
        assert len(fib_lazy) >= 1, "Expected at least one LazyFIBSIMSSpectrum"

    def test_sum_spectrum_is_signal1d(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), reader="Tofwerk")
        # First signal is the sum spectrum (1D)
        sum_sig = sigs[0]
        assert sum_sig.axes_manager.signal_dimension == 1

    def test_tic_map_is_2d(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), reader="Tofwerk")
        tic = sigs[1]
        assert tic.data.ndim >= 2


# ---------------------------------------------------------------------------
# TestSIMSSpectrumMethods
# ---------------------------------------------------------------------------


class TestSIMSSpectrumMethods:
    def setup_method(self):
        self.s = _make_fib_sims(shape=(3, 4, 5, 10))

    def test_signal_type(self):
        assert self.s.metadata.Signal.signal_type == "FIB-SIMS"

    def test_is_binned(self):
        assert self.s.axes_manager.signal_axes[0].is_binned

    def test_get_tic_shape(self):
        tic = self.s.get_tic()
        assert tic.data.shape == (3, 4, 5)

    def test_normalize_tic_sums_to_one(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        # Make all spectra positive so normalisation is well-defined
        s.data = np.abs(s.data) + 1.0
        norm = s.normalize_tic()
        total = norm.data.sum(axis=-1)
        np.testing.assert_allclose(total, np.ones_like(total), rtol=1e-5)

    def test_normalize_tic_zero_pixel_is_nan(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        s.data = np.abs(s.data) + 1.0
        s.data[0, 0, :] = 0.0  # zero spectrum → TIC = 0
        norm = s.normalize_tic()
        assert np.all(np.isnan(norm.data[0, 0, :]))

    def test_normalize_to_peak(self):
        s = _make_fib_sims(shape=(2, 10))
        s.data = np.ones((2, 10), dtype=float)
        # mass axis: 1..100 in 10 steps
        masses = np.linspace(1.0, 100.0, 10)
        s.axes_manager.signal_axes[0].axis = masses
        # Peak at first mass (1.0 Da), window 1.0 Da
        norm = s.normalize_to_peak(1.0, window=1.0)
        # Reference = sum over [0.0, 2.0] → captures first bin only (1 count)
        # All spectra are 1.0 everywhere, so reference = 1.0 → no change
        assert norm.data.shape == s.data.shape

    def test_get_depth_profile_shape(self):
        profile = self.s.get_depth_profile()
        assert profile.data.ndim == 1
        assert profile.data.shape[0] == 3

    def test_integrate_peak_shape(self):
        masses = np.linspace(1.0, 100.0, 10)
        self.s.axes_manager.signal_axes[0].axis = masses
        result = self.s.integrate_peak(50.0, window=5.0)
        assert result.data.shape == (3, 4, 5)

    def test_label_peaks_raises(self):
        with pytest.raises(NotImplementedError):
            self.s.label_peaks()


# ---------------------------------------------------------------------------
# TestCountRate
# ---------------------------------------------------------------------------


class TestCountRate:
    def test_to_count_rate_returns_fib_sims(self):
        s = _make_fib_sims_with_metadata()
        result = s.to_count_rate()
        assert isinstance(result, FIBSIMSSpectrum)

    def test_to_count_rate_scales_data(self):
        s = _make_fib_sims_with_metadata()
        orig_sum = s.data.sum()
        result = s.to_count_rate()
        # Result should differ from original (scaled)
        assert not np.allclose(result.data, s.data)
        assert result.data.sum() != orig_sum

    def test_to_count_rate_missing_metadata_raises(self):
        s = _make_fib_sims()
        with pytest.raises(AttributeError, match="Missing required metadata"):
            s.to_count_rate()


# ---------------------------------------------------------------------------
# TestComputeIntegrationBorders
# ---------------------------------------------------------------------------


class TestComputeIntegrationBorders:
    def test_five_peak_borders(self):
        s = FIBSIMSSpectrum(np.ones((5,)))
        masses = np.array([10.0, 20.0, 30.0, 40.0, 50.0])
        s.axes_manager.signal_axes[0].axis = masses
        borders = s.compute_integration_borders(resolution=3000)
        assert len(borders) == 5

        # First peak: low border comes from midpoint with previous (none → uses
        # spacing to the right); high border ≤ midpoint(10, 20) = 15
        low_0, high_0 = borders[10.0]
        assert low_0 < 10.0
        assert high_0 <= 15.0 + 1e-9  # ≤ midpoint

        # Last peak: high border uses spacing to the left
        low_last, high_last = borders[50.0]
        assert high_last > 50.0
        assert low_last >= 40.0 + 1e-9

    def test_borders_do_not_overlap(self):
        s = FIBSIMSSpectrum(np.ones((5,)))
        masses = np.array([14.0, 16.0, 28.0, 32.0, 56.0])
        s.axes_manager.signal_axes[0].axis = masses
        borders = s.compute_integration_borders()
        sorted_masses = sorted(borders.keys())
        for i in range(len(sorted_masses) - 1):
            _, hi = borders[sorted_masses[i]]
            lo, _ = borders[sorted_masses[i + 1]]
            assert hi <= lo + 1e-9, (
                f"Overlap between {sorted_masses[i]} and {sorted_masses[i + 1]}: "
                f"hi={hi}, lo={lo}"
            )

    def test_resolution_constrains_high_border(self):
        s = FIBSIMSSpectrum(np.ones((3,)))
        masses = np.array([100.0, 200.0, 400.0])
        s.axes_manager.signal_axes[0].axis = masses
        borders = s.compute_integration_borders(resolution=100)
        # high border of 100 Da: min(midpoint=150, 100 + 100/100=101) → 101
        _, high_100 = borders[100.0]
        assert high_100 == pytest.approx(101.0, rel=1e-6)
