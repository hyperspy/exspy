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

"""
Modules containing the eXSpy signals and their lazy counterparts.

EELSSpectrum
    For electron energy-loss data with ``signal_dimension`` equal one, i.e.
    spectral data of ``n`` dimensions. The signal is binned by default.
EDSTEMSpectrum
    For electron energy-dispersive X-ray data acquired in a transmission
    electron microscopy with ``signal_dimension`` equal one, i.e.
    spectral data of ``n`` dimensions. The signal is binned by default.
EDSSEMSpectrum
    For electron energy-dispersive X-ray data acquired in a scanning
    electron microscope with ``signal_dimension`` equal one, i.e.
    spectral data of ``n`` dimensions. The signal is binned by default.
DielectricFunction
    For dielectric function data with ``signal_dimension`` equal one. The signal
    is unbinned by default.
"""

import lazy_loader

__getattr__, __dir__, __all__ = lazy_loader.attach_stub(__name__, __file__)
