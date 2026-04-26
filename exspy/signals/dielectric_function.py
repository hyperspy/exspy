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

# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

# ruff: noqa: F822

__all__ = ["DielectricFunction", "LazyDielectricFunction"]


def __dir__():
    return sorted(__all__)


def __getattr__(name):
    warnings.warn(
        "This module has been privatised, use `exspy.signals` instead. "
        "It will be removed in exspy 1.0.",
        VisibleDeprecationWarning,
    )

    if name == "DielectricFunction":
        from ._dielectric_function import DielectricFunction

        return DielectricFunction
    elif name == "LazyDielectricFunction":
        from ._lazy_dielectric_function import LazyDielectricFunction

        return LazyDielectricFunction
    else:
        raise AttributeError(f"module {__name__} has no attribute {name}")
