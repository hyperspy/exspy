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

__all__ = ["GOSH_SOURCES"]


DFT_GOSH = {
    "DOI": "10.5281/zenodo.7645765",
    "URL": "https://zenodo.org/records/7645765/files/Segger_Guzzinati_Kohl_1.5.0.gosh",
    "KNOWN_HASH": "md5:7fee8891c147a4f769668403b54c529b",
}
DIRAC_GOSH = {
    "DOI": "10.5281/zenodo.12800856",
    "URL": "https://zenodo.org/records/12800856/files/Dirac_GOS_compact.gosh",
    "KNOWN_HASH": "md5:01a855d3750d2c063955248358dbee8d",
}
GOSH_SOURCES = {"dft": DFT_GOSH, "dirac": DIRAC_GOSH}
