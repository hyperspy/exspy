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
        Signal1D
            1D signal with the depth axis.
        """
        if mass is None:
            nav_signal = self.get_tic()
        else:
            roi = self.isig[mass - window : mass + window]
            nav_signal = roi.sum(axis=roi.axes_manager.signal_axes[0])

        # Collapse all navigation axes except axis 0 (depth / outermost).
        # Sum from the innermost navigation axis outward; each sum reduces
        # the navigation dimension by one, so we always collapse axis index 1
        # until only the depth axis (index 0) remains.
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


class LazyFIBSIMSSpectrum(FIBSIMSSpectrum, LazySignal1D):
    """Lazy version of FIBSIMSSpectrum."""

    __doc__ += LAZYSIGNAL_DOC.replace("__BASECLASS__", "FIBSIMSSpectrum")
