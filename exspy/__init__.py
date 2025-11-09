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

import importlib
from importlib.metadata import version
from pathlib import Path


__version__ = version("exspy")

# For development version, `setuptools_scm` will be used at build time
# to get the dev version, in case of missing vcs information (git archive,
# shallow repository), the fallback version defined in pyproject.toml will
# be used

# If we have an editable installed from a git repository try to use
# `setuptools_scm` to find a more accurate version:
# `importlib.metadata` will provide the version at installation
# time and for editable version this may be different

# we only do that if we have enough git history, e.g. not shallow checkout
_root = Path(__file__).resolve().parents[1]
if (_root / ".git").exists() and not (_root / ".git/shallow").exists():
    try:
        # setuptools_scm may not be installed
        from setuptools_scm import get_version

        __version__ = get_version(_root)
    except ImportError:  # pragma: no cover
        # setuptools_scm not installed, we keep the existing __version__
        pass


# ruff: noqa: F822

__all__ = [
    "__version__",
    "components",
    "data",
    "preferences",
    "material",
    "models",
    "signals",
    "utils",
]


# mapping following the pattern: from value import key
_import_mapping = {
    "preferences": "._defaults_parser",
}


def __dir__():
    return sorted(__all__)


def __getattr__(name):
    if name in __all__:
        if name in _import_mapping.keys():
            import_path = "exspy" + _import_mapping.get(name)
            return getattr(importlib.import_module(import_path), name)
        else:
            return importlib.import_module("." + name, "exspy")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
