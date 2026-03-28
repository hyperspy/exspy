"""Utility functions for EDS and EELS analysis."""

from . import eds
from . import eels

__all__ = [
    "eds",
    "eels",
]


def __dir__():
    return sorted(__all__)
