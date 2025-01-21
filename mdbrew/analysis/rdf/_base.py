from abc import abstractmethod, ABCMeta
from typing import Iterator

import numpy as np
from numpy.typing import NDArray
from tqdm import tqdm

from mdbrew.space import apply_pbc, calculate_distance


class BaseRDF(metaclass=ABCMeta):
    def __init__(
        self,
        x1,
        x2,
        box: NDArray | None = None,
        *,
        nbins: int = 250,
        range: tuple[float, float] = (0.0, 6.0),
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

        self._is_run = False

    def __repr__(self):
        return f"RDF(nx1={self._nx1}, nx2={self._nx2}, is_run={self._is_run})"

    @property
    def radii(self) -> NDArray[np.float_]:
        if not self._is_run:
            raise RuntimeError("RDF not calculated. Call run() first.")
        return self._radii

    @property
    def rdf(self) -> NDArray[np.float_]:
        if not self._is_run:
            raise RuntimeError("RDF not calculated. Call run() first.")
        return self._rdf

    @property
    def cn(self) -> NDArray[np.float_]:
        if not self._is_run:
            raise RuntimeError("RDF not calculated. Call run() first.")
        return self._cn

    def run(self, start: int = 0, stop: int | None = None, step: int = 1, *, verbose: bool = False):
        if len(self._x1) != len(self._x2):
            raise ValueError("x1 and x2's frames are must be same.")
        stop = stop or len(self._x1)
        iteration = self._update_iteration(start=start, stop=stop, step=step)
        _max_nframe = (stop - start) // step
        if verbose:
            iteration = tqdm(iteration, desc="Calculating RDF", unit="frame", total=_max_nframe)

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

        if _max_nframe != nframe:
            raise ValueError(
                f"Something is wrong. number of iteration should be {_max_nframe} but in your data {nframe}"
            )

        factor = self._factor_base * nframe * self._nx1 * self._nx2 * self._radii_square
        _rdf[1:] /= factor[1:]
        _cn = np.cumsum(_hist / (nframe * self._nx1))

        self._rdf = _rdf
        self._cn = _cn

        self._is_run = True
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
