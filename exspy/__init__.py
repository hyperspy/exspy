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
Attributes
----------
__version__ : str
    The version of the eXSpy package.
preferences :
    The global preferences for eXSpy, where the default settings are stored.

Examples
--------

To set a preference value, for example setting the EDS detector elevation
angle to 15 degrees:

>>> exspy.preferences.EDS.eds_detector_elevation = 15.0

To open the preferences dialog. Requires GUI widgets, to enable them see the hyperspy
documentation for :external+hyperspy:ref:`configuring HyperSpy <configuring-hyperspy-label>`.

>>> exspy.preferences.gui()

"""

import lazy_loader

__getattr__, __dir__, __all__ = lazy_loader.attach_stub(__name__, __file__)
