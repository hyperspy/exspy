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

import numpy as np
from hyperspy.signals import LazySignal1D
from hyperspy.docstrings.signal import LAZYSIGNAL_DOC

from .sims import SIMSSpectrum, LazySIMSSpectrum  # noqa: F401

_logger = logging.getLogger(__name__)


class FIBSIMSSpectrum(SIMSSpectrum):
    """Signal class for FIB-ToF-SIMS spectra (3D depth-profiling).

    This class handles 4-dimensional datasets produced by the Tofwerk
    HDF5 reader in rosettasciio, where the navigation axes are
    depth (slices), y and x, and the signal axis is m/z (Da).
    """

    _signal_type = "FIB-SIMS"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def plot(self, *args, **kwargs):
        kwargs.setdefault("norm", "log")
        super().plot(*args, **kwargs)

    def get_tic(self):
        """Return the Total Ion Count map as a Signal2D.

        Sums all mass channels and promotes the spatial navigation axes
        (y, x) to signal axes so the result is a 2D image per depth slice.

        Returns
        -------
        Signal2D
            Shape ``(depth | y, x)`` for a standard 4D FIB-SIMS input.
        """
        result = super().get_tic()  # BaseSignal with all-navigation axes
        if result.axes_manager.navigation_dimension >= 2:
            result = result.transpose(signal_axes=2)
        base_title = self.metadata.General.title
        result.metadata.General.title = (
            f"{base_title} TIC" if base_title else "TIC"
        )
        return result

    def get_depth_profile(self, mass=None, window=0.5):
        """Return a 1D depth profile.

        Parameters
        ----------
        mass : float or None, optional
            Centre of the mass window in Da. If None, the Total Ion
            Count (sum over all masses) is used.
        window : float, optional
            Half-width of the integration window in Da (default 0.5).

        Returns
        -------
        BaseSignal
            1D signal with the depth axis.
        """
        if mass is None:
            # Use the parent class get_tic() which returns a navigation-aligned
            # BaseSignal (depth, y, x | 0D) suitable for collapsing below.
            nav_signal = super().get_tic()
        else:
            roi = self.isig[mass - window : mass + window]
            nav_signal = roi.sum(axis=roi.axes_manager.signal_axes[0])

        # Collapse all navigation axes except axis 0 (depth / outermost).
        result = nav_signal
        while result.axes_manager.navigation_dimension > 1:
            result = result.sum(result.axes_manager.navigation_axes[0])
        return result

    def integrate_peak(self, mass, window=0.5):
        """Integrate a mass window and return the full navigation map.

        Parameters
        ----------
        mass : float
            Centre of the peak in Da.
        window : float, optional
            Half-width of the integration window in Da (default 0.5).

        Returns
        -------
        BaseSignal
            Navigation-space signal (depth × y × x for a 4D input).
        """
        roi = self.isig[mass - window : mass + window]
        return roi.sum(axis=roi.axes_manager.signal_axes[0])

    def compute_integration_borders(self, resolution=3000):
        """Compute integration borders for each peak.

        Uses the TOF-Tracer algorithm (MasslistFunctions.jl:7–42):
        for each adjacent peak pair the border is placed at
        ``min(midpoint, m_i + m_i / resolution)``.

        Parameters
        ----------
        resolution : float, optional
            Mass resolving power (m/Δm) used to constrain the upper
            border of each peak (default 3000).

        Returns
        -------
        dict
            Mapping ``mass_Da -> (low_Da, high_Da)`` for each peak on
            the signal axis.
        """
        masses = self.axes_manager.signal_axes[0].axis
        n = len(masses)
        borders = {}

        for i, m in enumerate(masses):
            if i == 0:
                low = m - (masses[1] - m) / 2 if n > 1 else m - 0.5
            else:
                candidate = min(
                    (masses[i - 1] + m) / 2,
                    masses[i - 1] + masses[i - 1] / resolution,
                )
                low = candidate

            if i == n - 1:
                high = m + (m - masses[i - 1]) / 2 if n > 1 else m + 0.5
            else:
                candidate = min(
                    (m + masses[i + 1]) / 2,
                    m + m / resolution,
                )
                high = candidate

            borders[float(m)] = (float(low), float(high))

        return borders


    def reintegrate_peaks(self, event_list_signal, peak_table=None):
        """Reintegrate the 4D peak data cube from a loaded EventList signal.

        Re-derives the ``(depth, y, x, m/z)`` peak-integrated array from the
        raw TDC timestamps using the integration windows in
        ``metadata.Signal.peak_table`` (or a user-supplied override).

        The ``event_list_signal`` must be loaded from the same acquisition
        using ``rsciio.tofwerk.file_reader(signal="event_list")``.  All
        calibration parameters (mass axis, clock ratio, normalisation) are
        read from its ``original_metadata``.

        Parameters
        ----------
        event_list_signal : hyperspy.signals.BaseSignal
            The EventList signal loaded from the same Tofwerk ``.h5`` file
            via ``file_reader(signal="event_list")``.  Its ``original_metadata``
            must contain ``MassAxis`` and ``FullSpectra`` timing attributes.
        peak_table : list of dict, optional
            Integration windows to use.  Each dict must have keys:

            * ``"label"`` (str)
            * ``"mass"`` (float, Da)
            * ``"lower_integration_limit"`` (float, Da)
            * ``"upper_integration_limit"`` (float, Da)

            If not provided, ``self.metadata.Signal.peak_table`` is used.

        Returns
        -------
        FIBSIMSSpectrum
            New signal with reintegrated data and updated m/z axis.

        Raises
        ------
        AttributeError
            If ``peak_table`` is None and ``metadata.Signal.peak_table`` is
            not set.
        AttributeError
            If ``event_list_signal.original_metadata`` does not contain the
            required timing attributes (``MassAxis``, ``FullSpectra``).
        """
        if peak_table is None:
            try:
                peak_table = list(self.metadata.Signal.peak_table)
            except AttributeError:
                raise AttributeError(
                    "No peak_table found in metadata.Signal.peak_table. "
                    "Load the signal from a Tofwerk file or supply peak_table explicitly."
                )

        # Extract calibration parameters from the EventList signal's metadata.
        omd = event_list_signal.original_metadata
        try:
            mass_axis = np.asarray(omd.MassAxis, dtype=np.float64)
        except AttributeError:
            raise AttributeError(
                "event_list_signal.original_metadata.MassAxis is not set. "
                "Load the EventList signal via rsciio.tofwerk.file_reader(signal='event_list')."
            )
        nbr_samples = len(mass_axis)

        try:
            fs = omd.FullSpectra
            sample_interval = float(fs["SampleInterval"])
            clock_period = float(fs["ClockPeriod"])
        except (AttributeError, KeyError):
            sample_interval = 1.0
            clock_period = 1.0
        clock_ratio = int(round(sample_interval / clock_period)) if clock_period else 1

        nbr_waveforms_raw = omd.as_dictionary().get("NbrWaveforms", 1)
        if isinstance(nbr_waveforms_raw, list):
            nbr_waveforms_raw = nbr_waveforms_raw[0]
        nbr_waveforms = int(nbr_waveforms_raw)
        ini = omd.as_dictionary().get("Configuration File Contents", "")
        from rsciio.tofwerk._api import _count_active_channels
        n_active = _count_active_channels(ini)
        normalization = nbr_waveforms * n_active

        # Sort peak_table by mass for a monotonically increasing m/z axis.
        masses = np.array([p["mass"] for p in peak_table])
        sort_idx = np.argsort(masses)
        sorted_peak_table = [peak_table[i] for i in sort_idx]
        sorted_masses = masses[sort_idx]

        from rsciio.tofwerk import compute_peak_data_from_eventlist

        # Get the raw event data (numpy object array or dask array).
        el = event_list_signal.data
        if hasattr(el, "compute"):
            try:
                from dask.diagnostics import ProgressBar
                with ProgressBar(dt=0.5):
                    el = el.compute()
            except ImportError:
                el = el.compute()

        peak_data = compute_peak_data_from_eventlist(
            el, mass_axis, nbr_samples, clock_ratio, normalization, sorted_peak_table
        )

        # Rebuild axes: reuse the navigation axes from this signal, replace m/z.
        new_axes = []
        for ax in self.axes_manager._axes[:-1]:  # depth, y, x
            if not ax.is_uniform:
                new_axes.append(
                    {
                        "name": ax.name,
                        "axis": ax.axis.copy(),
                        "units": ax.units,
                        "navigate": True,
                    }
                )
            else:
                new_axes.append(
                    {
                        "name": ax.name,
                        "offset": ax.offset,
                        "scale": ax.scale,
                        "units": ax.units,
                        "size": ax.size,
                        "navigate": True,
                    }
                )
        new_axes.append(
            {
                "name": "m/z",
                "axis": sorted_masses,
                "units": "Da",
                "navigate": False,
                "is_binned": True,
            }
        )

        result_cls = self.__class__ if hasattr(peak_data, "compute") else FIBSIMSSpectrum
        result = result_cls(peak_data, axes=new_axes)
        result.metadata.add_dictionary(self.metadata.as_dictionary())
        result.metadata.Signal.peak_table = sorted_peak_table
        result.original_metadata.add_dictionary(self.original_metadata.as_dictionary())
        return result


class LazyFIBSIMSSpectrum(FIBSIMSSpectrum, LazySignal1D):
    """Lazy version of FIBSIMSSpectrum."""

    __doc__ += LAZYSIGNAL_DOC.replace("__BASECLASS__", "FIBSIMSSpectrum")
