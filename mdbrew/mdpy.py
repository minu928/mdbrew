import numpy
from numpy.typing import NDArray
from mdbrew.utils.space import calculate_volume
from mdbrew.typing import npf64, Virial
from mdbrew.errors import AttributeIsNoneError
from mdbrew.dataclass import MDState, MDStateList, MDStateAttr, NPDType


def stack(mdstatelist: MDStateList, what: MDStateAttr) -> NDArray:
    return numpy.stack([getattr(mdstate, what) for mdstate in mdstatelist])


def calculate_virial(mdstate: MDState, *, dtype: NPDType = npf64) -> Virial:
    if mdstate.virial is not None:
        return mdstate.virial
    for require in ("stress", "box"):
        if mdstate.stress is None:
            raise AttributeIsNoneError(require)
    return calculate_volume(box=mdstate.box, dtype=dtype) * mdstate.stress
