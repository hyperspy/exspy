# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy.utils.eels import (
    effective_angle,
    get_edges_near_energy,
    get_info_from_edges,
)


__all__ = [
    "effective_angle",
    "get_edges_near_energy",
    "get_info_from_edges",
]


def __dir__():
    return sorted(__all__)


warnings.warn(
    "This module is deprecated, use `exspy.utils.eels` instead. "
    "It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)
