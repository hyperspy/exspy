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


import math


def effective_angle(E0, E, alpha, beta):
    """Calculates the effective collection angle

    Parameters
    ----------
    E0 : float
        electron beam energy in keV
    E : float
        energy loss in eV
    alpha : float
        convergence angle in mrad
    beta : float
        collection angle in mrad

    Returns
    -------
    effective_angle : float
        The effective collection angle in mrad.

    Notes
    -----
    Code translated to Python from Egerton (second edition) page 420

    """
    E0 *= 1e3  # keV to eV
    if alpha == 0:
        return beta
    E0 *= 10.0**-3  # In KeV
    E = float(E)
    alpha = float(alpha)
    beta = float(beta)
    TGT = E0 * (1.0 + E0 / 1022.0) / (1.0 + E0 / 511.0)
    thetaE = E / TGT
    A2 = alpha * alpha * 1e-6
    B2 = beta * beta * 1e-6
    T2 = thetaE * thetaE * 1e-6
    eta1 = math.sqrt((A2 + B2 + T2) ** 2 - 4.0 * A2 * B2) - A2 - B2 - T2
    eta2 = (
        2.0
        * B2
        * math.log(
            0.5 / T2 * (math.sqrt((A2 + T2 - B2) ** 2 + 4.0 * B2 * T2) + A2 + T2 - B2)
        )
    )
    eta3 = (
        2.0
        * A2
        * math.log(
            0.5 / T2 * (math.sqrt((B2 + T2 - A2) ** 2 + 4.0 * A2 * T2) + B2 + T2 - A2)
        )
    )
    #    ETA=(eta1+eta2+eta3)/A2/math.log(4./T2)
    F1 = (eta1 + eta2 + eta3) / 2 / A2 / math.log(1.0 + B2 / T2)
    F2 = F1
    if (alpha / beta) > 1:
        F2 = F1 * A2 / B2
    BSTAR = thetaE * math.sqrt(math.exp(F2 * math.log(1.0 + B2 / T2)) - 1.0)
    return BSTAR  # In mrad
