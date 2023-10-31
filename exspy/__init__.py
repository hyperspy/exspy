from pathlib import Path

from . import components
from . import data
from . import models
from . import signals
from .misc import material
from ._defaults_parser import preferences


if Path(__file__).parent.parent.name == "site-packages":  # pragma: no cover
    # Tested in the "build" workflow on GitHub CI
    from importlib.metadata import version

    __version__ = version("rosettasciio")
else:
    # Editable install
    from setuptools_scm import get_version

    __version__ = get_version(Path(__file__).parent.parent)


__all__ = [
    "__version__",
    "components",
    "data",
    "preferences",
    "material",
    "models",
    "signals",
]


def __dir__():
    return sorted(__all__)
