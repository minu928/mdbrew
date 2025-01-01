from numpy import ndarray, asarray
from numpy.typing import ArrayLike


class MDArray(ndarray):
    _default_type = float

    def __new__(cls, obj: ArrayLike, dtype=None):
        dtype = cls._default_type if dtype is None else dtype
        if isinstance(obj, ndarray) and obj.dtype == dtype:
            return obj.view(cls)
        return asarray(obj).astype(dtype=dtype).view(cls)
