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

import math
import logging

import numpy as np

import hyperspy.api as hs
from hyperspy.misc.array_tools import rebin
from exspy._misc import elements as elements_module

_logger = logging.getLogger(__name__)


def _estimate_gain(
    ns, cs, weighted=False, higher_than=None, plot_results=False, binning=0, pol_order=1
):
    if binning > 0:
        factor = 2**binning
        remainder = np.mod(ns.shape[1], factor)
        if remainder != 0:
            ns = ns[:, remainder:]
            cs = cs[:, remainder:]
        new_shape = (ns.shape[0], ns.shape[1] / factor)
        ns = rebin(ns, new_shape)
        cs = rebin(cs, new_shape)

    noise = ns - cs
    variance = np.var(noise, 0)
    average = np.mean(cs, 0).squeeze()

    # Select only the values higher_than for the calculation
    if higher_than is not None:
        sorting_index_array = np.argsort(average)
        average_sorted = average[sorting_index_array]
        average_higher_than = average_sorted > higher_than
        variance_sorted = variance.squeeze()[sorting_index_array]
        variance2fit = variance_sorted[average_higher_than]
        average2fit = average_sorted[average_higher_than]
    else:
        variance2fit = variance
        average2fit = average

    fit = np.polynomial.Polynomial.fit(average2fit, variance2fit, pol_order)
    if weighted is True:
        s = hs.signals.Signal1D(variance2fit)
        s.axes_manager.signal_axes[0].axis = average2fit
        m = s.create_model()
        line = hs.model.components1D.Polynomial()
        line.a.value = fit[1]
        line.b.value = fit[0]
        m.append(line)
        m.fit(weights=True)
        fit[0] = line.b.value
        fit[1] = line.a.value

    if plot_results is True:
        import matplotlib.pyplot as plt

        plt.figure()
        plt.scatter(average.squeeze(), variance.squeeze())
        plt.xlabel("Counts")
        plt.ylabel("Variance")
        plt.plot(average2fit, np.polyval(fit, average2fit), color="red")
    results = {"fit": fit, "variance": variance.squeeze(), "counts": average.squeeze()}

    return results


def _estimate_correlation_factor(g0, gk, k):
    a = math.sqrt(g0 / gk)
    e = k * (a - 1) / (a - k)
    c = (1 - e) ** 2
    return c


def estimate_variance_parameters(
    noisy_signal,
    clean_signal,
    mask=None,
    pol_order=1,
    higher_than=None,
    return_results=False,
    plot_results=True,
    weighted=False,
    store_results="ask",
):
    """Find the scale and offset of the Poissonian noise

    By comparing an SI with its denoised version (i.e. by PCA),
    this plots an estimation of the variance as a function of the number of counts
    and fits a polynomial to the result.

    Parameters
    ----------
    noisy_SI, clean_SI : hyperspy.api.signals.Signal1D
    mask : numpy.ndarray
        To define the channels that will be used in the calculation.
    pol_order : int
        The order of the polynomial.
    higher_than: float
        To restrict the fit to counts over the given value.
    return_results : bool
        Whether to return the results or not.
    plot_results : bool
        Whether to plot the results or not.
    store_results: {True, False, "ask"}, default "ask"
        If True, it stores the result in the signal metadata

    Returns
    -------
    dict
        Dictionary with the result of a linear fit to estimate the offset
        and scale factor

    """
    with noisy_signal.unfolded(), clean_signal.unfolded():
        # The rest of the code assumes that the first data axis
        # is the navigation axis. We transpose the data if that is not the
        # case.
        ns = (
            noisy_signal.data.copy()
            if noisy_signal.axes_manager[0].index_in_array == 0
            else noisy_signal.data.T.copy()
        )
        cs = (
            clean_signal.data.copy()
            if clean_signal.axes_manager[0].index_in_array == 0
            else clean_signal.data.T.copy()
        )

        if mask is not None:
            _slice = [
                slice(None),
            ] * len(ns.shape)
            _slice[noisy_signal.axes_manager.signal_axes[0].index_in_array] = ~mask
            ns = ns[_slice]
            cs = cs[_slice]

        results0 = _estimate_gain(
            ns,
            cs,
            weighted=weighted,
            higher_than=higher_than,
            plot_results=plot_results,
            binning=0,
            pol_order=pol_order,
        )

        results2 = _estimate_gain(
            ns,
            cs,
            weighted=weighted,
            higher_than=higher_than,
            plot_results=False,
            binning=2,
            pol_order=pol_order,
        )

        c = _estimate_correlation_factor(results0["fit"][0], results2["fit"][0], 4)

        message = (
            "Gain factor: %.2f\n" % results0["fit"][0]
            + "Gain offset: %.2f\n" % results0["fit"][1]
            + "Correlation factor: %.2f\n" % c
        )
        if store_results == "ask":
            is_ok = ""
            while is_ok not in ("Yes", "No"):
                is_ok = input(message + "Would you like to store the results (Yes/No)?")
            is_ok = is_ok == "Yes"
        else:
            is_ok = store_results
            _logger.info(message)
        if is_ok:
            noisy_signal.metadata.set_item(
                "Signal.Noise_properties.Variance_linear_model.gain_factor",
                results0["fit"][0],
            )
            noisy_signal.metadata.set_item(
                "Signal.Noise_properties.Variance_linear_model.gain_offset",
                results0["fit"][1],
            )
            noisy_signal.metadata.set_item(
                "Signal.Noise_properties.Variance_linear_model.correlation_factor", c
            )
            noisy_signal.metadata.set_item(
                "Signal.Noise_properties.Variance_linear_model."
                + "parameters_estimation_method",
                "eXSpy",
            )

    if return_results is True:
        return results0


def power_law_perc_area(E1, E2, r):
    a = E1
    b = E2
    return (
        100
        * (
            (a**r * r - a**r)
            * (a / (a**r * r - a**r) - (b + a) / ((b + a) ** r * r - (b + a) ** r))
        )
        / a
    )


def rel_std_of_fraction(a, std_a, b, std_b, corr_factor=1):
    rel_a = std_a / a
    rel_b = std_b / b
    return np.sqrt(rel_a**2 + rel_b**2 - 2 * rel_a * rel_b * corr_factor)


def ratio(edge_A, edge_B):
    a = edge_A.intensity.value
    std_a = edge_A.intensity.std
    b = edge_B.intensity.value
    std_b = edge_B.intensity.std
    ratio = a / b
    ratio_std = ratio * rel_std_of_fraction(a, std_a, b, std_b)
    _logger.info(
        "Ratio %s/%s %1.3f +- %1.3f ", edge_A.name, edge_B.name, a / b, 1.96 * ratio_std
    )
    return ratio, ratio_std


def get_edges_near_energy(energy, width=10, only_major=False, order="closest"):
    """Find edges near a given energy that are within the given energy
    window.

    Parameters
    ----------
    energy : float
        Energy to search, in eV
    width : float
        Width of window, in eV, around energy in which to find nearby
        energies, i.e. a value of 10 eV (the default) means to
        search +/- 5 eV. The default is 10.
    only_major : bool
        Whether to show only the major edges. The default is False.
    order : str
        Sort the edges, if 'closest', return in the order of energy difference,
        if 'ascending', return in ascending order, similarly for 'descending'

    Returns
    -------
    edges : list
        All edges that are within the given energy window, sorted by
        energy difference to the given energy.

    See Also
    --------
    exspy.utils.eels.get_info_from_edges
    """

    if width < 0:
        raise ValueError("Provided width needs to be >= 0.")
    if order not in ("closest", "ascending", "descending"):
        raise ValueError("order needs to be 'closest', 'ascending' or 'descending'")

    Emin, Emax = energy - width / 2, energy + width / 2

    # find all subshells that have its energy within range
    valid_edges = []
    for element, element_info in elements_module.elements.items():
        try:
            for shell, shell_info in element_info["Atomic_properties"][
                "Binding_energies"
            ].items():
                if only_major:
                    if shell_info["relevance"] != "Major":
                        continue
                if shell[-1] != "a" and Emin <= shell_info["onset_energy (eV)"] <= Emax:
                    subshell = "{}_{}".format(element, shell)
                    Ediff = abs(shell_info["onset_energy (eV)"] - energy)
                    valid_edges.append(
                        (subshell, shell_info["onset_energy (eV)"], Ediff)
                    )
        except KeyError:
            continue

    # Sort according to 'order' and return only the edges
    if order == "closest":
        edges = [edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[2])]
    elif order == "ascending":
        edges = [edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[1])]
    elif order == "descending":
        edges = [
            edge for edge, _, _ in sorted(valid_edges, key=lambda x: x[1], reverse=True)
        ]

    return edges


def get_info_from_edges(edges):
    """Return the information of a sequence of edges as a list of dictionaries

    Parameters
    ----------
    edges : str or iterable
        the sequence of edges, each entry in the format of 'element_subshell'.

    Returns
    -------
    info : list
        A list of dictionaries with information corresponding to the provided
        edges.

    See Also
    --------
    exspy.utils.eels.get_edges_near_energy
    """

    edges = np.atleast_1d(edges)
    info = []
    for edge in edges:
        element, subshell = edge.split("_")
        d = elements_module.elements[element]["Atomic_properties"]["Binding_energies"][
            subshell
        ]
        info.append(d)

    return info
