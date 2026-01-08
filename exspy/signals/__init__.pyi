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

from ._dielectric_function import DielectricFunction
from ._eds import EDSSpectrum
from ._eds_sem import EDSSEMSpectrum
from ._eds_tem import EDSTEMSpectrum
from ._eels import EELSSpectrum
from ._lazy_dielectric_function import LazyDielectricFunction
from ._lazy_eds import LazyEDSSpectrum
from ._lazy_eds_sem import LazyEDSSEMSpectrum
from ._lazy_eds_tem import LazyEDSTEMSpectrum
from ._lazy_eels import LazyEELSSpectrum

__all__ = [
    "DielectricFunction",
    "LazyDielectricFunction",
    "EDSSpectrum",
    "LazyEDSSpectrum",
    "EDSTEMSpectrum",
    "LazyEDSTEMSpectrum",
    "EELSSpectrum",
    "LazyEELSSpectrum",
    "EDSSEMSpectrum",
    "LazyEDSSEMSpectrum",
]

def __dir__():
    return sorted(__all__)
