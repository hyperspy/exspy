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
Utilities for X-ray line data retrieval using XrayDB as primary source
with fallback to Chantler2005 database.
"""

import warnings
from exspy._misc.eds.utils import _get_element_and_line, _get_energy_xray_line

import xraydb


def _xraydb_line_mapping(line):
    """
    Map line names from exspy format to xraydb format.

    Parameters
    ----------
    line : str
        X-ray line in exspy format (e.g., 'Ka', 'Kb', 'La', etc.)

    Returns
    -------
    str
        X-ray line in xraydb format (e.g., 'Ka1', 'Kb1', 'La1', etc.)
        None if mapping not available
    """
    # XrayDB uses specific line names like Ka1, Ka2, etc.
    # Map the main lines to their primary counterparts
    line_map = {
        "Ka": "Ka1",
        "Kb": "Kb1",
        "La": "La1",
        "Lb": "Lb1",
        "Lb1": "Lb1",
        "Lb2": "Lb2",
        "Lb3": "Lb3",
        "Lb4": "Lb4",
        "Lg1": "Lg1",
        "Lg2": "Lg2",
        "Lg3": "Lg3",
        "Ll": "Ll",
        "Ln": "Ln",
        "Ma": "Ma1",
        "Mb": "Mb",
        "Mg": "Mg",
        "Mz": "Mz",
        # Add specific lines that might not need mapping
        "Ka1": "Ka1",
        "Ka2": "Ka2",
        "Kb1": "Kb1",
        "Kb2": "Kb2",
        "Kb3": "Kb3",
        "Kb5": "Kb5",
        "La1": "La1",
        "La2": "La2",
        "Ma1": "Ma1",
        "Ma2": "Ma2",
        # Handle some special line notations
        "M2N4": "M2N4",
        "M3O4": "M3O4",
        "M3O5": "M3O5",
    }
    return line_map.get(line, None)


def get_xray_line_energy_xraydb(element, line):
    """
    Get X-ray line energy from XrayDB.

    Parameters
    ----------
    element : str
        Element symbol (e.g., 'Fe', 'Cu', etc.)
    line : str
        X-ray line designation (e.g., 'Ka', 'Kb', etc.)

    Returns
    -------
    float or None
        Energy in keV, None if not found
    """
    try:
        # Map line to XrayDB format
        xraydb_line = _xraydb_line_mapping(line)
        if xraydb_line is None:
            return None

        # Get energy from XrayDB (returns in eV, need to convert to keV)
        energy_ev = xraydb.xray_line(element, xraydb_line).energy
        return energy_ev / 1000.0  # Convert eV to keV

    except (AttributeError, ValueError, KeyError):
        # XrayDB might not have this line or element
        return None


def get_xray_line_energy_with_fallback(xray_line, source="xraydb"):
    """
    Get X-ray line energy with source preference and fallback.

    Parameters
    ----------
    xray_line : str
        X-ray line in format 'Element_Line' (e.g., 'Fe_Ka', 'Cu_Lb1')
    source : {'xraydb', 'Chantler2005'}, default 'xraydb'
        Primary source for X-ray line data:
        - 'xraydb': Use XrayDB as primary source, fallback to Chantler2005
        - 'Chantler2005': Use Chantler2005 database only

    Returns
    -------
    float
        Energy in keV

    Raises
    ------
    ValueError
        If X-ray line not found in any source
    """
    element, line = _get_element_and_line(xray_line)

    if source == "xraydb":
        # Try XrayDB first
        energy = get_xray_line_energy_xraydb(element, line)
        if energy is not None:
            return energy
        else:
            # Fallback to Chantler2005 database
            warnings.warn(
                f"X-ray line {xray_line} not found in XrayDB, "
                f"falling back to Chantler2005 database.",
                UserWarning,
            )
            return _get_energy_xray_line(xray_line)
    else:
        # Use Chantler2005 database directly
        return _get_energy_xray_line(xray_line)


def validate_xray_line_source(source):
    """
    Validate X-ray line source parameter.

    Parameters
    ----------
    source : str
        The source to validate ('xraydb' or 'Chantler2005')

    Raises
    ------
    ValueError
        If source is not recognized
    """
    valid_sources = ["xraydb", "Chantler2005"]
    if source not in valid_sources:
        raise ValueError(
            f"Invalid X-ray line source '{source}'. Valid options are: {valid_sources}"
        )
