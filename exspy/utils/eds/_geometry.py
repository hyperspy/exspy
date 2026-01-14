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

import numpy as np


def take_off_angle(tilt_stage, azimuth_angle, elevation_angle, beta_tilt=0.0):
    """Calculate the take-off-angle (TOA).

    TOA is the angle with which the X-rays leave the surface towards
    the detector.

    Parameters
    ----------
    tilt_stage : float
        The alpha-tilt of the stage in degrees. The sample is facing the detector
        when positively tilted.
    azimuth_angle : float
        The azimuth of the detector in degrees. 0 is perpendicular to the alpha
        tilt axis.
    elevation_angle : float
        The elevation of the detector in degrees.
    beta_tilt : float
        The beta-tilt of the stage in degrees. The sample is facing positive 90
        in the azimuthal direction when positively tilted.

    Returns
    -------
    take_off_angle : float
        The take off angle in degrees.

    Examples
    --------
    >>> exspy.utils.eds.take_off_angle(tilt_stage=10., beta_tilt=0.
    >>>                          azimuth_angle=45., elevation_angle=22.)
    28.865971201155283
    """

    if tilt_stage is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Stage.tilt_alpha` is not set."
        )

    if azimuth_angle is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Detector.EDS.azimuth_angle` is not set."
        )

    if elevation_angle is None:
        raise ValueError(
            "Unable to calculate take-off angle. The metadata property "
            "`Detector.EDS.elevation_angle` is not set."
        )

    alpha = math.radians(tilt_stage)
    beta = -math.radians(beta_tilt)
    phi = math.radians(azimuth_angle)
    theta = -math.radians(elevation_angle)

    return 90 - math.degrees(
        np.arccos(
            math.sin(alpha) * math.cos(beta) * math.cos(phi) * math.cos(theta)
            - math.sin(beta) * math.sin(phi) * math.cos(theta)
            - math.cos(alpha) * math.cos(beta) * math.sin(theta)
        )
    )
