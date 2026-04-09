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

from pathlib import Path
import warnings

import hyperspy.api as hs

__all__ = [
    "EDS_SEM_TM002",
    "EDS_TEM_FePt_nanoparticles",
]


def _resolve_dir():
    """Returns the absolute path to this file's directory."""
    return Path(__file__).resolve().parent


def EDS_SEM_TM002():
    """
    Load an EDS-SEM spectrum of a EDS-TM002 standard supplied by the
    Bundesanstalt für Materialforschung und -prüfung (BAM).
    The sample consists of an approximately 6 µm thick layer containing
    the elements C, Al, Mn, Cu and Zr on a silicon substrate.

    Notes
    -----
    - Sample: EDS-TM002 provided by BAM (www.webshop.bam.de)
    - SEM Microscope: Nvision40 Carl Zeiss
    - EDS Detector: X-max 80 from Oxford Instrument
    """
    file_path = _resolve_dir().joinpath("EDS_SEM_TM002.hspy")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        # load "read-only" to ensure data access regardless of install location
        return hs.load(file_path, mode="r", file_format="hspy")


def EDS_TEM_FePt_nanoparticles():
    """
    Load an EDS-TEM spectrum of FePt bimetallic nanoparticles.

    Notes
    -----
    - TEM Microscope: Tecnai Osiris 200 kV D658 AnalyticalTwin
    - EDS Detector: Super-X 4 detectors Brucker
    """
    file_path = _resolve_dir().joinpath("EDS_TEM_FePt_nanoparticles.hspy")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        return hs.load(file_path, mode="r", file_format="hspy")
