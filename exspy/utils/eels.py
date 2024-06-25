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


from exspy._misc.eels.effective_angle import effective_angle
from exspy._misc.eels.electron_inelastic_mean_free_path import (
    iMFP_angular_correction,
    iMFP_Iakoubovskii,
    iMFP_TPP2M,
)
from exspy._misc.eels.tools import (
    get_edges_near_energy,
    get_info_from_edges,
)


__all__ = [
    "effective_angle",
    "get_edges_near_energy",
    "get_info_from_edges",
    "iMFP_angular_correction",
    "iMFP_Iakoubovskii",
    "iMFP_TPP2M",
]


def __dir__():
    return sorted(__all__)
