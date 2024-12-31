__author__ = "Minwoo Kim"
__email__ = "minu928@snu.ac.kr"

try:
    from mdbrew._version import version as __version__
except:
    __version__ = "none"


from . import dataclass
from . import utils
from . import typing
from . import mdpy
from . import errors
from . import analysis

__all__ = ["utils", "typing", "dataclass", "mdpy", "errors", "analysis", "io"]
