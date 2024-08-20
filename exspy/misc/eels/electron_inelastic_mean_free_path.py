# Deprecated and to be removed in exspy 1.0

import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy.utils.eels import (
    iMFP_angular_correction,
    iMFP_Iakoubovskii,
    iMFP_TPP2M,
)

__all__ = [
    "iMFP_angular_correction",
    "iMFP_Iakoubovskii",
    "iMFP_TPP2M",
]


warnings.warn(
    "This module is deprecated, use `exspy.utils.eels` instead. "
    "It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)
