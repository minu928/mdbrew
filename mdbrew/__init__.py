__author__ = "Minwoo Kim"
__email__ = "minu928@snu.ac.kr"

try:
    from mdbrew._version import version as __version__
except:
    __version__ = "none"

from . import io
from . import core
from . import utils
from . import errors
from . import analysis


__all__ = [
    "io",
    "core",
    "utils",
    "errors",
    "analysis",
]
