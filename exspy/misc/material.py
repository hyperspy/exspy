# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy.material import (
    atomic_to_weight,
    density_of_mixture,
    mass_absorption_coefficient,
    mass_absorption_mixture,
    weight_to_atomic,
)


__all__ = [
    "atomic_to_weight",
    "density_of_mixture",
    "mass_absorption_coefficient",
    "mass_absorption_mixture",
    "weight_to_atomic",
]


def __dir__():
    return sorted(__all__)


warnings.warn(
    "This module is deprecated, use `exspy.material` instead. "
    "It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)
