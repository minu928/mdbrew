from numpy import asarray
from numpy.typing import NDArray

from mdbrew.utils.space import convert_to_box_vec


from ._base import BaseRDF


class NumpyRDF(BaseRDF):
    def _update_x(self, x) -> NDArray:
        return asarray(x)

    def _update_box(self, box):
        return convert_to_box_vec(box=box)

    def _update_atomnumb(self, x: NDArray):
        return x.shape[1]

    def _update_iteration(self, start=0, stop=None, step=1):
        return (self._x1[start:stop:step], self._x2[start:stop:step], self._box[start:stop:step])
