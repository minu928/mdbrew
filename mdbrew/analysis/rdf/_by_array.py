from typing import Iterable
from numpy import asarray
from numpy.typing import NDArray, ArrayLike

from mdbrew.space import convert_to_box_vec
from ._base import BaseRDF


class ArrayRDF(BaseRDF):
    def __init__(
        self,
        x1: ArrayLike,
        x2: ArrayLike,
        box: ArrayLike,
        *,
        nbins: int = 250,
        range: tuple[float, float] = (0.0, 6.0),
    ):
        super().__init__(x1, x2, box, nbins=nbins, range=range)

    def _update_x(self, x: ArrayLike) -> NDArray:
        return asarray(x)

    def _update_box(self, box: ArrayLike) -> NDArray:
        return convert_to_box_vec(box=box)

    def _update_atomnumb(self, x: NDArray) -> int:
        return x.shape[1]

    def _update_iteration(self, start: int = 0, stop: int | None = None, step: int = 1) -> Iterable:
        return zip(self._x1[start:stop:step], self._x2[start:stop:step], self._box[start:stop:step])
