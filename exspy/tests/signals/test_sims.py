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
    pathlib.Path(__file__).parents[4]
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

try:
    from rsciio.tofwerk._api import _count_active_channels  # noqa: F401
    from rsciio.tofwerk import compute_peak_data_from_eventlist  # noqa: F401

    _TOFWERK_REINTEGRATE_AVAILABLE = True
except ImportError:
    _TOFWERK_REINTEGRATE_AVAILABLE = False

skip_no_reintegrate = pytest.mark.skipif(
    not _TOFWERK_REINTEGRATE_AVAILABLE,
    reason="rsciio.tofwerk event-list API not available (needs rosettasciio#491)",
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
    for key, val in extra.items():  # pragma: no cover
        s.metadata.set_item(key, val)
    return s


# ---------------------------------------------------------------------------
# TestSignalDispatch
# ---------------------------------------------------------------------------


@skip_no_files
@pytest.mark.filterwarnings("ignore:Loading old file version")
class TestSignalDispatch:  # pragma: no cover
    def test_opened_file_dispatches_fib_sims(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), file_format="Tofwerk")
        types = [type(s).__name__ for s in sigs]
        assert "FIBSIMSSpectrum" in types, f"Expected FIBSIMSSpectrum, got {types}"
        fib = next(s for s in sigs if isinstance(s, FIBSIMSSpectrum))
        assert fib.axes_manager.signal_dimension == 1

    def test_lazy_opened_file(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), file_format="Tofwerk", lazy=True)
        fib_lazy = [s for s in sigs if isinstance(s, LazyFIBSIMSSpectrum)]
        assert len(fib_lazy) >= 1, "Expected at least one LazyFIBSIMSSpectrum"

    def test_sum_spectrum_is_signal1d(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), file_format="Tofwerk")
        # First signal is the sum spectrum (1D)
        sum_sig = sigs[0]
        assert sum_sig.axes_manager.signal_dimension == 1

    def test_get_tic_returns_signal2d(self):
        import hyperspy.api as hs

        sigs = hs.load(str(OPENED_FILE), file_format="Tofwerk", signal="all")
        peak_data = next(s for s in sigs if s.axes_manager.navigation_dimension == 3)
        tic = peak_data.get_tic()
        assert tic.axes_manager.signal_dimension == 2
        assert tic.axes_manager.navigation_dimension == 1


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
        # y and x are promoted to signal axes: Signal2D (depth | y, x)
        assert tic.axes_manager.signal_dimension == 2
        assert tic.axes_manager.navigation_dimension == 1

    def test_normalize_tic_sums_to_one(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        # Make all spectra positive so normalisation is well-defined
        s.data = np.abs(s.data) + 1.0
        norm = s.normalize_tic()
        total = norm.data.sum(axis=-1)
        np.testing.assert_allclose(total, np.ones_like(total), rtol=1e-5)

    def test_normalize_tic_with_peaks(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        s.data = np.abs(s.data) + 1.0
        # Use values read from the axis to guarantee consistency
        ax_vals = s.axes_manager.signal_axes[0].axis
        norm = s.normalize_tic(peaks=[float(ax_vals[0]), float(ax_vals[3])])
        assert norm.data.shape == s.data.shape

    def test_normalize_tic_saturation_warning(self):
        s = _make_fib_sims_with_metadata()
        s.data = np.abs(s.data) + 1.0
        with pytest.warns(UserWarning, match="Saturation-based exclusion"):
            s.normalize_tic(exclude_saturated=True)

    def test_normalize_tic_inplace(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        s.data = np.abs(s.data) + 1.0
        orig_id = id(s)
        result = s.normalize_tic(inplace=True)
        assert result is s
        assert id(result) == orig_id

    def test_normalize_tic_zero_pixel_is_nan(self):
        s = _make_fib_sims(shape=(2, 3, 8))
        s.data = np.abs(s.data) + 1.0
        s.data[0, 0, :] = 0.0  # zero spectrum → TIC = 0
        with pytest.warns(RuntimeWarning, match="invalid value encountered in divide"):
            norm = s.normalize_tic()
        assert np.all(np.isnan(norm.data[0, 0, :]))

    def test_normalize_to_peak(self):
        s = _make_fib_sims(shape=(2, 10))
        s.data = np.ones((2, 10), dtype=float)
        masses = np.linspace(1.0, 100.0, 10)
        s.axes_manager.signal_axes[0].axis = masses
        norm = s.normalize_to_peak(1.0, window=1.0)
        assert norm.data.shape == s.data.shape

    def test_normalize_to_peak_inplace(self):
        s = _make_fib_sims(shape=(2, 10))
        s.data = np.abs(s.data) + 1.0
        masses = np.linspace(1.0, 100.0, 10)
        s.axes_manager.signal_axes[0].axis = masses
        result = s.normalize_to_peak(50.0, window=5.0, inplace=True)
        assert result is s

    def test_get_depth_profile_shape(self):
        profile = self.s.get_depth_profile()
        assert profile.data.ndim == 1
        assert profile.data.shape[0] == 3

    def test_get_depth_profile_with_mass(self):
        masses = np.linspace(1.0, 100.0, 10)
        self.s.axes_manager.signal_axes[0].axis = masses
        profile = self.s.get_depth_profile(mass=50.0, window=5.0)
        assert profile.data.ndim == 1
        assert profile.data.shape[0] == 3

    def test_integrate_peak_shape(self):
        masses = np.linspace(1.0, 100.0, 10)
        self.s.axes_manager.signal_axes[0].axis = masses
        result = self.s.integrate_peak(50.0, window=5.0)
        assert result.data.shape == (3, 4, 5)

    def test_get_mass_spectrum_no_indices(self):
        # navigation_indices=None: sum over all nav axes → 1D result
        result = self.s.get_mass_spectrum()
        assert result.axes_manager.navigation_dimension == 0
        assert result.data.shape == (10,)

    def test_get_mass_spectrum_with_indices(self):
        # navigation_indices specified: index then sum → 1D result
        result = self.s.get_mass_spectrum(navigation_indices=(0, 0, 0))
        assert result.axes_manager.navigation_dimension == 0
        assert result.data.shape == (10,)

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

    def test_to_count_rate_inplace(self):
        s = _make_fib_sims_with_metadata()
        orig_data_id = id(s.data)
        result = s.to_count_rate(inplace=True)
        assert result is s
        assert id(result.data) != orig_data_id  # data was replaced

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


# ---------------------------------------------------------------------------
# TestReintegratePeaks
# ---------------------------------------------------------------------------


class TestReintegratePeaks:
    """Tests for FIBSIMSSpectrum.reintegrate_peaks()."""

    NWRITES = 3
    NSEGS = 8
    NX = 8
    NPEAKS = 5
    NSAMPLES = 256

    _PEAK_TABLE = [
        {
            "label": f"nominal_{i}",
            "mass": float(i + 1),
            "lower_integration_limit": float(i) + 0.5,
            "upper_integration_limit": float(i) + 1.5,
        }
        for i in range(NPEAKS)
    ]

    def _make_fib_sims_signal(self):
        """Synthetic FIBSIMSSpectrum with peak_table in metadata."""
        rng = np.random.default_rng(42)
        data = rng.uniform(
            0, 10, (self.NWRITES, self.NSEGS, self.NX, self.NPEAKS)
        ).astype(np.float32)
        s = FIBSIMSSpectrum(data)
        masses = np.array([p["mass"] for p in self._PEAK_TABLE])
        s.axes_manager.signal_axes[0].axis = masses
        s.metadata.set_item("Signal.peak_table", self._PEAK_TABLE)
        return s

    def _make_event_list_signal(self):
        """Synthetic EventList signal with required calibration metadata."""
        from hyperspy.signals import BaseSignal

        mass_axis = np.linspace(0.0, 20.0, self.NSAMPLES)
        rng = np.random.default_rng(7)
        el = np.empty((self.NWRITES, self.NSEGS, self.NX), dtype=object)
        for w in range(self.NWRITES):
            for s in range(self.NSEGS):
                for x in range(self.NX):
                    n = int(rng.poisson(5))
                    # indices in [0, NSAMPLES) map to mass_axis values [0, 20] Da
                    el[w, s, x] = rng.integers(0, self.NSAMPLES, n, dtype=np.uint16)

        sig = BaseSignal(el)
        sig.original_metadata.add_dictionary(
            {
                "MassAxis": mass_axis.tolist(),
                "FullSpectra": {"SampleInterval": 1.0, "ClockPeriod": 1.0},
                "NbrWaveforms": 1,
                "Configuration File Contents": "Ch1Record=1\nCh2Record=0\n",
            }
        )
        return sig

    # -- error cases --------------------------------------------------------

    def test_no_peak_table_raises(self):
        s = _make_fib_sims()
        el_sig = self._make_event_list_signal()
        with pytest.raises(AttributeError, match="peak_table"):
            s.reintegrate_peaks(el_sig)

    def test_missing_mass_axis_raises(self):
        """event_list_signal without MassAxis in original_metadata raises AttributeError."""
        from hyperspy.signals import BaseSignal

        s = _make_fib_sims()
        s.metadata.set_item("Signal.peak_table", self._PEAK_TABLE)
        el_sig = BaseSignal(np.zeros((2, 3, 4), dtype=object))
        # No MassAxis in original_metadata
        with pytest.raises(AttributeError, match="MassAxis"):
            s.reintegrate_peaks(el_sig)

    # -- success cases ------------------------------------------------------

    @skip_no_reintegrate
    def test_returns_fib_sims_spectrum(self):
        s = self._make_fib_sims_signal()
        el_sig = self._make_event_list_signal()
        result = s.reintegrate_peaks(el_sig)
        assert isinstance(result, FIBSIMSSpectrum)

    @skip_no_reintegrate
    def test_output_shape(self):
        s = self._make_fib_sims_signal()
        el_sig = self._make_event_list_signal()
        result = s.reintegrate_peaks(el_sig)
        assert result.data.shape == (self.NWRITES, self.NSEGS, self.NX, self.NPEAKS)

    @skip_no_reintegrate
    def test_mz_axis_matches_peak_table(self):
        s = self._make_fib_sims_signal()
        el_sig = self._make_event_list_signal()
        result = s.reintegrate_peaks(el_sig)
        expected_masses = np.array(sorted(p["mass"] for p in self._PEAK_TABLE))
        np.testing.assert_array_almost_equal(
            result.axes_manager.signal_axes[0].axis, expected_masses
        )

    @skip_no_reintegrate
    def test_explicit_peak_table_override(self):
        """Passing a subset peak_table reduces the m/z dimension."""
        s = self._make_fib_sims_signal()
        el_sig = self._make_event_list_signal()
        subset = self._PEAK_TABLE[:3]
        result = s.reintegrate_peaks(el_sig, peak_table=subset)
        assert result.data.shape[-1] == 3

    @skip_no_reintegrate
    def test_result_peak_table_is_mass_sorted(self):
        s = self._make_fib_sims_signal()
        el_sig = self._make_event_list_signal()
        shuffled = self._PEAK_TABLE[::-1]
        result = s.reintegrate_peaks(el_sig, peak_table=shuffled)
        result_masses = [r["mass"] for r in result.metadata.Signal.peak_table]
        assert result_masses == sorted(result_masses)
