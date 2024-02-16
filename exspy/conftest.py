# -*- coding: utf-8 -*-
# Copyright 2007-2024 The eXSpy developers
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

import importlib

try:
    # Set traits toolkit to work in a headless system
    # Capture error when toolkit is already previously set which typically
    # occurs when building the doc locally
    from traits.etsconfig.api import ETSConfig

    ETSConfig.toolkit = "null"
except ValueError:
    # in case ETSConfig.toolkit was already set previously.
    pass

# pytest-mpl 0.7 already import pyplot, so setting the matplotlib backend to
# 'agg' as early as we can is useless for testing.
import matplotlib.pyplot as plt

import pytest
import numpy as np
import hyperspy.api as hs

# Use matplotlib fixture to clean up figure, setup backend, etc.
from matplotlib.testing.conftest import mpl_test_settings  # noqa: F401


@pytest.fixture(autouse=True)
def add_np(doctest_namespace):
    doctest_namespace["np"] = np
    doctest_namespace["plt"] = plt
    doctest_namespace["hs"] = hs


@pytest.fixture
def pdb_cmdopt(request):
    return request.config.getoption("--pdb")


def setup_module(mod, pdb_cmdopt):
    if pdb_cmdopt:
        import dask

        dask.set_options(get=dask.local.get_sync)


pytest_mpl_spec = importlib.util.find_spec("pytest_mpl")


if pytest_mpl_spec is None:
    # Register dummy marker to allow running the test suite without pytest-mpl
    def pytest_configure(config):
        config.addinivalue_line(
            "markers",
            "mpl_image_compare: dummy marker registration to allow running "
            "without the pytest-mpl plugin.",
        )
