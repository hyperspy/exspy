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
