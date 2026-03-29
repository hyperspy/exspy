# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy.material import elements


__all__ = ["elements"]


def __dir__():
    return sorted(__all__)


warnings.warn(
    "This module is deprecated, use `from exspy.material import "
    "elements` instead. It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)
