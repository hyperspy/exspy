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

import importlib
import logging

_logger = logging.getLogger(__name__)


def parse_component_module(module):
    """Check if numexpr is installed, if not fall back to numpy"""
    if module == "numexpr":
        numexpr_spec = importlib.util.find_spec("numexpr")
        if numexpr_spec is None:
            module = "numpy"
            _logger.warning(
                "Numexpr is not installed, falling back to numpy, "
                "which is slower to calculate model."
            )

    return module
