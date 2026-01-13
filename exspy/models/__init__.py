# -*- coding: utf-8 -*-
# Copyright 2007-2026 The eXSpy developers
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
Module containing eXSpy models used in model fitting.

EDSModel
    Base model for X-ray dispersive electron spectroscopy
EDSSEMModel
    Model for X-ray dispersive electron spectroscopy acquired in a scanning electron microscope
EDSTEMModel
    Model for X-ray dispersive electron spectroscopy acquired in a transmission electron microscope
EELSModel
    Model for electron energy-loss spectroscopy
"""

import lazy_loader

__getattr__, __dir__, __all__ = lazy_loader.attach_stub(__name__, __file__)
