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


"""This module provides tools to interact with The EELS Database."""

import io
import logging
import os
import warnings

import requests
from hyperspy.decorators import deprecated_argument
from hyperspy.defaults_parser import preferences
from hyperspy.docstrings.signal import SHOW_PROGRESSBAR_ARG
from hyperspy.exceptions import VisibleDeprecationWarning
from hyperspy.external.progressbar import progressbar
from hyperspy.io import dict2signal
from rsciio.hspy import file_reader

from exspy._version import __version__

_logger = logging.getLogger(__name__)

API_URL = os.environ.get("EELSDB_API_URL", "https://api.eelsdb.eu/v2/spectra")

_ORDER_KEYS = {
    "spectrumMin": "min_energy_ev",
    "spectrumMax": "max_energy_ev",
    "spectrumFormula": "formula",
    "spectrumUpload": "published_at",
    "beamenergy": "beam_energy_kv",
    "resolution": "resolution_ev",
}


@deprecated_argument("min_energy_compare", since="0.4", removal="1.0")
@deprecated_argument("max_energy_compare", since="0.4", removal="1.0")
@deprecated_argument("resolution_compare", since="0.4", removal="1.0")
def eelsdb(
    spectrum_type=None,
    title=None,
    author=None,
    element=None,
    formula=None,
    edge=None,
    min_energy=None,
    max_energy=None,
    resolution=None,
    min_energy_compare="gt",
    max_energy_compare="lt",
    resolution_compare="lt",
    max_n=-1,
    monochromated=None,
    order=None,
    order_direction="ASC",
    verify_certificate=True,
    show_progressbar=None,
    phase=None,
):
    r"""Download spectra from the `EELS database <https://eelsdb.eu/>`_.

    Parameters
    ----------
    spectrum_type: {'coreloss', 'lowloss', 'zeroloss', 'xrayabs'}, optional
    title: string
        Search spectra titles and descriptions for a text string.
    author: string, optional
        Search authors for a text string.
    element: string or list of strings, optional
        Filter for the presence of one or more element. Each string must
        correspond with a valid element symbol.
    formula: string
        Chemical formula of the sample.
    edge: string, optional
        Filter for spectra with an edge, matched whole: for example 'K' or
        'L2,3' for any element, or 'Fe_L2,3' for one element.
    min_energy, max_energy: float, optional
        Spectra that start at or above `min_energy` and end at or below
        `max_energy`, in eV.
    resolution: float, optional
        Spectra with this energy resolution or better, in eV.
    min_energy_compare, max_energy_compare, resolution_compare: str, optional
        Deprecated. Only the defaults, "gt", "lt" and "lt", are supported.
    monochromated: bool or None (default)
    max_n: int, default -1
        Maximum number of spectra to return. -1 to return all.
    order: string
        Key to sort results by. Valid keys are:

        * "spectrumMin",
        * "spectrumMax",
        * "spectrumFormula",
        * "spectrumUpload",
        * "beamenergy",
        * "resolution"

        Other keys are ignored with a warning.
    order_direction : {"ASC", "DESC"}
        Sorting `order` direction.
    verify_certificate: bool
        If True, verify the eelsdb website certificate and raise an error
        if it is invalid. If False, continue querying the database if the certificate
        is invalid. (This is a potential security risk.)
    %s
    phase: {'solid', 'liquid', 'gas'} or list of strings, optional
        Phase of the specimen.

    Returns
    -------
    spectra: list
        A list containing all the spectra matching the given criteria if
        any.

    Notes
    -----
    Set the ``EELSDB_API_URL`` environment variable to query another
    instance of the database, for example a development server.

    """
    if order is not None and order not in _ORDER_KEYS:
        warnings.warn(
            f"The EELS database cannot sort by `{order}`, so this argument is "
            f"ignored. Valid keys are: {', '.join(_ORDER_KEYS)}."
        )
    if order_direction not in ("ASC", "DESC"):
        raise ValueError('`order_direction` must be "ASC" or "DESC".')
    for label, value, supported in (
        ("min_energy_compare", min_energy_compare, "gt"),
        ("max_energy_compare", max_energy_compare, "lt"),
        ("resolution_compare", resolution_compare, "lt"),
    ):
        if value != supported:
            raise ValueError(f'`{label}` only supports "{supported}".')
    if isinstance(resolution, str):
        warnings.warn(
            "Passing `resolution` as a string is deprecated and will be removed "
            "in exSpy 1.0. Pass a number in eV instead.",
            VisibleDeprecationWarning,
        )
        resolution = float(resolution.replace("eV", ""))

    params = {
        "type": spectrum_type,
        "q": title,
        "author": author,
        "element": element,
        "formula": formula,
        "edge": edge,
        "phase": phase,
        "min_energy_ev": min_energy,
        "max_energy_ev": max_energy,
        "max_resolution_ev": resolution,
        "per_page": max_n if 0 < max_n < 500 else 500,
    }
    if monochromated is not None:
        params["monochromated"] = "true" if monochromated else "false"
    if order in _ORDER_KEYS:
        params["sort"] = _ORDER_KEYS[order]
        params["order"] = order_direction.lower()

    if show_progressbar is None:
        show_progressbar = preferences.General.show_progressbar

    session = requests.Session()
    session.verify = verify_certificate
    session.headers["User-Agent"] = (
        f"exSpy/{__version__} (+https://github.com/hyperspy/exspy)"
    )
    records = []
    url = API_URL
    while url and (max_n < 0 or len(records) < max_n):
        response = session.get(url, params=params)
        if response.status_code == 400:
            raise ValueError(response.json()["error"]["message"])
        response.raise_for_status()
        page = response.json()
        records += page["results"]
        url, params = page["next"], None
    if max_n >= 0:
        records = records[:max_n]

    spectra = []
    for record in progressbar(records, disable=not show_progressbar):
        try:
            response = session.get(record["downloads"]["hspy"])
            response.raise_for_status()
            s = dict2signal(file_reader(io.BytesIO(response.content))[0])
        except Exception:
            _logger.exception(
                "Failed to load the spectrum.\n"
                f"Title: {record['title']} id: {record['id']}.\n"
                "Please report this error to https://eelsdb.eu/contact/ \n"
            )
            continue
        s.original_metadata.set_item("json", record)
        if record["technique"] == "xas":
            s.set_signal_type("XAS")
        if s.metadata.Signal.signal_type == "EELS" and record["elements"]:
            try:
                s.add_elements(record["elements"])
            except ValueError:
                _logger.warning(
                    f"Invalid elements {record['elements']} in spectrum "
                    f"{record['id']}, please report this to "
                    "https://eelsdb.eu/contact/"
                )
        s.metadata.set_item("General.author", record["author"]["name"])
        s.metadata.set_item("Sample.description", record["description"])
        s.metadata.set_item("Sample.chemical_formula", record["formula"])
        if record["acquisition"]:
            s.metadata.set_item(
                "Acquisition_instrument.TEM.microscope",
                record["acquisition"]["microscope"],
            )
        spectra.append(s)

    if not spectra:
        _logger.info(
            "The EELS database does not contain any spectra matching your query"
            ". If you have some, why not submitting them "
            "https://eelsdb.eu/submit-data/ ?\n"
        )

    return spectra


eelsdb.__doc__ %= SHOW_PROGRESSBAR_ARG
