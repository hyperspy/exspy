import warnings

from hyperspy.exceptions import VisibleDeprecationWarning

from exspy._misc.eds.utils import (
    cross_section_to_zeta,
    electron_range,
    get_xray_lines_near_energy,
    take_off_angle,
    xray_range,
    zeta_to_cross_section,
)


warnings.warn(
    "This module is deprecated, use `exspy.utils.eds` instead. "
    "It will be removed in exspy 1.0.",
    VisibleDeprecationWarning,
)

__all__ = [
    "cross_section_to_zeta",
    "electron_range",
    "get_xray_lines_near_energy",
    "take_off_angle",
    "xray_range",
    "zeta_to_cross_section",
]


def __dir__():
    return sorted(__all__)
