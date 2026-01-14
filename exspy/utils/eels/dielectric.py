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

import numbers
import logging

import numpy as np
import scipy

from hyperspy.signals import BaseSignal

_logger = logging.getLogger(__name__)


def eels_constant_dielectric(s, zlp, t):
    r"""Calculate the constant of proportionality (k) in the relationship
    between the EELS signal and the dielectric function.
    dielectric function from a single scattering distribution (SSD) using
    the Kramers-Kronig relations.

        .. math::

            S(E)=\frac{I_{0}t}{\pi a_{0}m_{0}v^{2}}\ln\left[1+\left(\frac{\beta}
            {\theta_{E}}\right)^{2}\right]\Im(\frac{-1}{\epsilon(E)})=
            k\Im(\frac{-1}{\epsilon(E)})


    Parameters
    ----------
    zlp: {number, BaseSignal}
        If the ZLP is the same for all spectra, the intengral of the ZLP
        can be provided as a number. Otherwise, if the ZLP intensity is not
        the same for all spectra, it can be provided as i) a Signal
        of the same dimensions as the current signal containing the ZLP
        spectra for each location ii) a Signal of signal dimension 0
        and navigation_dimension equal to the current signal containing the
        integrated ZLP intensity.
    t: {None, number, BaseSignal}
        The sample thickness in nm. If the thickness is the same for all
        spectra it can be given by a number. Otherwise, it can be provided
        as a Signal with signal dimension 0 and navigation_dimension equal
        to the current signal.

    Returns
    -------
    k: Signal instance

    """

    # Constants and units
    me = scipy.constants.value("electron mass energy equivalent in MeV") * 1e3  # keV

    # Mapped parameters
    try:
        e0 = s.metadata.Acquisition_instrument.TEM.beam_energy
    except BaseException:
        raise AttributeError(
            "Please define the beam energy."
            "You can do this e.g. by using the "
            "set_microscope_parameters method"
        )
    try:
        beta = s.metadata.Acquisition_instrument.TEM.Detector.EELS.collection_angle
    except BaseException:
        raise AttributeError(
            "Please define the collection semi-angle."
            "You can do this e.g. by using the "
            "set_microscope_parameters method"
        )

    axis = s.axes_manager.signal_axes[0]
    eaxis = axis.axis.copy()
    if eaxis[0] == 0:
        # Avoid singularity at E=0
        eaxis[0] = 1e-10

    if isinstance(zlp, BaseSignal):
        if zlp.axes_manager.navigation_dimension == s.axes_manager.navigation_dimension:
            if zlp.axes_manager.signal_dimension == 0:
                i0 = zlp.data
            else:
                i0 = zlp.integrate1D(axis.index_in_axes_manager).data
        else:
            raise ValueError(
                "The ZLP signal dimensions are not "
                "compatible with the dimensions of the "
                "low-loss signal"
            )
        # The following prevents errors if the signal is a single spectrum
        if len(i0) != 1:
            i0 = i0.reshape(np.insert(i0.shape, axis.index_in_array, 1))
    elif isinstance(zlp, numbers.Number):
        i0 = zlp
    else:
        raise ValueError(
            "The zero-loss peak input is not valid, it must be\
                         in the BaseSignal class or a Number."
        )

    if isinstance(t, BaseSignal):
        if (
            t.axes_manager.navigation_dimension == s.axes_manager.navigation_dimension
        ) and (t.axes_manager.signal_dimension == 0):
            t = t.data
            t = t.reshape(np.insert(t.shape, axis.index_in_array, 1))
        else:
            raise ValueError(
                "The thickness signal dimensions are not "
                "compatible with the dimensions of the "
                "low-loss signal"
            )

    # Kinetic definitions
    ke = e0 * (1 + e0 / 2.0 / me) / (1 + e0 / me) ** 2
    tgt = e0 * (2 * me + e0) / (me + e0)
    k = s.__class__(
        data=(t * i0 / (332.5 * ke)) * np.log(1 + (beta * tgt / eaxis) ** 2)
    )
    k.metadata.General.title = "EELS proportionality constant K"
    return k
