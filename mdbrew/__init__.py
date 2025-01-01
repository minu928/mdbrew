__author__ = "Minwoo Kim"
__email__ = "minu928@snu.ac.kr"

try:
    from mdbrew._version import version as __version__
except:
    __version__ = "none"

from . import io
from ._core import state, array
from . import utils
from . import errors
from . import analysis


__all__ = [
    "io",
    "state",
    "array",
    "utils",
    "errors",
    "analysis",
]
