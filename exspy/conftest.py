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

import importlib
from time import sleep

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
import pooch

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


def _download_and_cache_GOS():
    """Download GOS files for testing purposes."""
    print("Start download of GOS files")
    pooch.retrieve(
        url="https://zenodo.org/records/6599071/files/Segger_Guzzinati_Kohl_1.0.0.gos",
        known_hash="md5:d65d5c23142532fde0a80e160ab51574",
        downloader=pooch.HTTPDownloader(chunk_size=8192),
        progressbar=False,
    )
    print("sleeping 30s to throttle zenodo requests")
    sleep(30)
    pooch.retrieve(
        url="https://zenodo.org/records/7645765/files/Segger_Guzzinati_Kohl_1.5.0.gosh",
        known_hash="md5:7fee8891c147a4f769668403b54c529b",
        downloader=pooch.HTTPDownloader(chunk_size=8192),
        progressbar=False,
    )
    print("sleeping 30s to throttle zenodo requests")
    sleep(30)
    pooch.retrieve(
        url="https://zenodo.org/records/12800856/files/Dirac_GOS_compact.gosh",
        known_hash="md5:01a855d3750d2c063955248358dbee8d",
        downloader=pooch.HTTPDownloader(chunk_size=8192),
        progressbar=False,
    )
    print("finished download of GOS files")


pytest_mpl_spec = importlib.util.find_spec("pytest_mpl")


if pytest_mpl_spec is None:
    # Register dummy marker to allow running the test suite without pytest-mpl
    def pytest_configure(config):
        config.addinivalue_line(
            "markers",
            "mpl_image_compare: dummy marker registration to allow running "
            "without the pytest-mpl plugin.",
        )
        _download_and_cache_GOS()


else:

    def pytest_configure(config):
        _download_and_cache_GOS()
        print("finish")
