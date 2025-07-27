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

"""Common docstring snippets for model."""

DOSE_DOC = """beam_current : float or "auto"
            Probe current in nA.
            If "auto", the value is extracted from the metadata.
            Only for ``"zeta"`` and ``"cross_section"`` method.
        live_time : float or "auto"
            Acquisition time in s, compensated for the dead time of the detector.
            If "auto", the value is extracted from the metadata.
            Only for ``"zeta"`` and ``"cross_section"`` method.
        probe_area : float or "auto"
            The illumination area of the electron beam in nm².
            If ``"auto"`` the value is extracted from the scale axes_manager,
            assuming that the probe is oversampling such that the illumination
            area can be approximated to the pixel area of the spectrum image.
            Only for the ``"cross_section"`` method."""

INTENSITIES_THRESHOLD_DOC = """intensities_threshold : float, optional
        Threshold value used to set individual intensity values to zero when they
        fall below this threshold. This helps filter out noise and very low
        intensity peaks. If <= 0, no individual intensity thresholding is applied.
        Default is 1.0."""


INTENSITIES_SUM_THRESHOLD_DOC = """intensities_sum_threshold : int, float or None, optional
        Threshold value used to set output values to zero in areas with very low
        X-ray intensities, such as vacuum areas. If the sum of the
        intensities falls below this threshold, the output is set to zero.
        If None, the length of the intensities list is used as the threshold.
        Default is None."""
