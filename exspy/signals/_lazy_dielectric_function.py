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

from hyperspy.signals import LazyComplexSignal1D
from hyperspy.docstrings.signal import LAZYSIGNAL_DOC

from exspy.signals import DielectricFunction


class LazyDielectricFunction(DielectricFunction, LazyComplexSignal1D):
    """Lazy signal class for dielectric functions."""

    __doc__ += LAZYSIGNAL_DOC.replace("__BASECLASS__", "DielectricFunction")
