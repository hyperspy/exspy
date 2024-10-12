# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy._misc.elements import elements_db

# atomap still using elements
elements = elements_db


__all__ = ["elements_db", "elements"]


def __dir__():
    return sorted(__all__)


warnings.warn(
    "This module is deprecated, use `exspy.material` instead. "
    "It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)
