from abc import abstractmethod, ABCMeta
from typing import Iterator, Optional

import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from mdbrew.utils.space import convert_to_box_vec, apply_pbc, calculate_distance


class BaseRDF(metaclass=ABCMeta):
    def __init__(
        self, x1, x2, box: Optional[NDArray] = None, *, nbins: int = 250, range: tuple[float, float] = (0, 6)
    ):
        self._x1 = self._update_x(x1)
        self._x2 = self._update_x(x2)
        self._nx1 = self._update_atomnumb(x1)
        self._nx2 = self._update_atomnumb(x2)
        self._box = self._update_box(box=box)

        self._rdf = None
        self._hist = None
        self._radii = np.linspace(*range, num=nbins)
        self._radii_square = self._radii * self._radii

        self._nbins = nbins
        self._range = range
        self._dr = (range[1] - range[0]) / (nbins + 1)
        self._factor_base = 4.0 * np.pi * self._dr

    def __repr__(self):
        return "RDF"

    @property
    def radii(self) -> NDArray[np.float_]:
        return self._radii

    @property
    def rdf(self) -> NDArray[np.float_]:
        return self._rdf

    @property
    def cn(self) -> NDArray[np.float_]:
        return self._cn

    def run(self, start: int = 0, stop: int | None = None, step: int = 1, *, verbose: bool = False):
        iteration = self._update_iteration(start=start, stop=stop, step=step)
        if verbose:
            iteration = tqdm(iteration, desc="Calculating RDF")

        _hist = np.zeros(self._nbins, dtype=np.int64)
        _rdf = np.zeros(self._nbins, dtype=np.float64)

        nframe = 0
        for x1_i, x2_i, box in iteration:
            diff = x1_i[:, None, :] - x2_i[None, :, :]
            pbc_diff = apply_pbc(diff, box=box)
            distance = calculate_distance(vec=pbc_diff)

            hist_i, _ = np.histogram(distance, bins=self._nbins, range=self._range)
            _hist[1:] += hist_i[1:]
            _rdf[1:] += hist_i[1:] * np.prod(box)
            nframe += 1

        factor = self._factor_base * nframe * self._nx1 * self._nx2 * self._radii_square
        _rdf[1:] /= factor[1:]
        _cn = np.cumsum(_hist / (nframe * self._nx1))

        self._rdf = _rdf
        self._cn = _cn
        return self

    @abstractmethod
    def _update_x(self, x):
        pass

    @abstractmethod
    def _update_atomnumb(self, x) -> int:
        pass

    @abstractmethod
    def _update_box(self, box):
        pass

    @abstractmethod
    def _update_iteration(self, start: int = 0, stop: int | None = None, step: int = 1) -> Iterator:
        pass
