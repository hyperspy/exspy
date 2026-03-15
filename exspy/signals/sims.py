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

import logging
import warnings

import numpy as np

from hyperspy.signals import Signal1D, LazySignal1D
from hyperspy.docstrings.signal import LAZYSIGNAL_DOC

_logger = logging.getLogger(__name__)


class SIMSSpectrum(Signal1D):
    """Signal class for Secondary Ion Mass Spectrometry (SIMS) spectra."""

    _signal_type = "SIMS"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.axes_manager.signal_axes:  # pragma: no branch
            self.axes_manager.signal_axes[0].is_binned = True

    def get_tic(self):
        """Return Total Ion Count across all mass channels.

        Returns
        -------
        BaseSignal
            Navigation-space signal with shape equal to the navigation
            dimensions (e.g. depth × y × x for a 4D input).
        """
        return self.sum(axis=self.axes_manager.signal_axes[0])

    def normalize_tic(self, peaks=None, exclude_saturated=True, inplace=False):
        """Normalise every spectrum by its Total Ion Count (TIC).

        Parameters
        ----------
        peaks : list of float, optional
            m/z values to use for TIC calculation. If None, all mass
            channels are summed.
        exclude_saturated : bool, optional
            If True and FIB_SIMS metadata is present, a warning is
            logged that saturation exclusion is not yet implemented.
        inplace : bool, optional
            If True, modify the signal in place. If False (default),
            return a new signal.

        Returns
        -------
        SIMSSpectrum
            Normalised signal.
        """
        if peaks is None:
            # Sum over signal axis directly so that the result is always a
            # navigation-aligned BaseSignal, regardless of how get_tic() may
            # be overridden in subclasses for visualisation purposes.
            tic = self.sum(axis=self.axes_manager.signal_axes[0])
        else:
            ax = self.axes_manager.signal_axes[0]
            indices = [int(np.argmin(np.abs(ax.axis - m))) for m in peaks]
            tic = None
            for idx in indices:
                channel = self.isig[idx]
                tic = channel if tic is None else tic + channel

        if exclude_saturated and "Acquisition_instrument.FIB_SIMS" in self.metadata:
            warnings.warn(
                "Saturation-based exclusion is not yet implemented. "
                "Proceeding without saturation masking. This will be "
                "addressed in a future release.",
                UserWarning,
                stacklevel=2,
            )

        result = self / tic
        result.data[np.isinf(result.data)] = np.nan
        result.metadata.Signal.TIC = tic.data.copy()

        if inplace:
            self.data = result.data
            self.metadata.Signal.TIC = result.metadata.Signal.TIC
            return self
        return result._deepcopy_with_new_data(result.data)

    def normalize_to_peak(self, mass, window=0.5, inplace=False):
        """Normalise every spectrum by the intensity of a reference peak.

        Parameters
        ----------
        mass : float
            Centre of the reference peak in m/z (Da).
        window : float, optional
            Half-width of the integration window in Da (default 0.5).
        inplace : bool, optional
            If True, modify the signal in place.

        Returns
        -------
        SIMSSpectrum
            Normalised signal.
        """
        roi = self.isig[mass - window : mass + window]
        ref = roi.sum(axis=roi.axes_manager.signal_axes[0])

        result = self / ref
        result.data[np.isinf(result.data)] = np.nan
        result.metadata.Signal.reference_mass_Da = mass

        if inplace:
            self.data = result.data
            self.metadata.Signal.reference_mass_Da = mass
            return self
        return result._deepcopy_with_new_data(result.data)

    def to_count_rate(self, inplace=False):
        """Convert raw counts to count rate (counts / second).

        Requires the following metadata keys under
        ``Acquisition_instrument.FIB_SIMS``:

        * ``ToF.sample_interval_s``
        * ``ToF.single_ion_signal``
        * ``ToF.tof_period_samples``
        * ``n_depth_slices``
        * ``n_segments``

        Parameters
        ----------
        inplace : bool, optional
            If True, modify the signal in place.

        Returns
        -------
        SIMSSpectrum
            Signal in count-rate units.

        Raises
        ------
        AttributeError
            If any required metadata key is missing.
        """
        try:
            fib_md = self.metadata.Acquisition_instrument.FIB_SIMS
            tof = fib_md.ToF
            sample_interval_s = tof.sample_interval_s
            single_ion_signal = tof.single_ion_signal
            tof_period_samples = tof.tof_period_samples
            n_depth_slices = fib_md.n_depth_slices
            n_segments = fib_md.n_segments
        except AttributeError as exc:
            raise AttributeError(
                "Missing required metadata for count-rate conversion. "
                "Expected keys under Acquisition_instrument.FIB_SIMS: "
                "ToF.sample_interval_s, ToF.single_ion_signal, "
                "ToF.tof_period_samples, n_depth_slices, n_segments. "
                f"Original error: {exc}"
            ) from exc

        # Integration time per pixel per acquisition cycle
        inttime = tof_period_samples * n_segments * n_depth_slices * 1e-9
        result = self * (sample_interval_s / single_ion_signal / inttime)

        if inplace:
            self.data = result.data
            return self
        return result._deepcopy_with_new_data(result.data)

    def get_mass_spectrum(self, navigation_indices=None):
        """Return a 1D mass spectrum by summing over navigation axes.

        Parameters
        ----------
        navigation_indices : tuple or None, optional
            If given, index the navigation space before summing. Each
            element corresponds to one navigation axis (in HyperSpy
            order, i.e. outermost first).

        Returns
        -------
        Signal1D
            1D mass spectrum.
        """
        if navigation_indices is None:
            s = self
            while s.axes_manager.navigation_dimension > 0:
                s = s.sum(s.axes_manager.navigation_axes[-1])
            return s
        else:
            slices = tuple(slice(i, i + 1) for i in navigation_indices)
            s = self.inav[slices]
            while s.axes_manager.navigation_dimension > 0:
                s = s.sum(s.axes_manager.navigation_axes[-1])
            return s

    def label_peaks(self, peak_table=None, min_intensity=0.0):
        """Label peaks on the mass spectrum.

        .. note::
           Not yet implemented. Will annotate the signal plot with
           chemical formulae from ``peak_table`` for peaks above
           ``min_intensity``.

        Parameters
        ----------
        peak_table : dict or None, optional
            Mapping of m/z values to chemical labels. If None, uses the
            peak information stored in ``original_metadata``.
        min_intensity : float, optional
            Minimum peak intensity threshold for labelling.

        Raises
        ------
        NotImplementedError
            Always raised until this feature is implemented.
        """
        raise NotImplementedError("label_peaks not yet implemented")


class LazySIMSSpectrum(SIMSSpectrum, LazySignal1D):
    """Lazy version of SIMSSpectrum."""

    __doc__ += LAZYSIGNAL_DOC.replace("__BASECLASS__", "SIMSSpectrum")
