from typing import Tuple, Iterable
from abc import abstractmethod, ABCMeta

import numpy as np
from numpy.typing import NDArray

from mdbrew.utils.space import apply_pbc, calculate_distance


class BaseRDF(metaclass=ABCMeta):
    TQDM_OPTIONS = dict(unit=" frame")

    def __init__(
        self,
        a: Iterable,
        b: Iterable,
        box: Iterable,
        *,
        nbins: int = 100,
        ranges: tuple[float, float] = (0, 6),
    ):
        self.a, self.b, self.box = self._check_args(a=a, b=b, box=box)
        self.nbins = nbins
        self.range = ranges

        self._rdf: NDArray | None = None
        self._cn: NDArray | None = None
        self._radii = np.linspace(*ranges, num=nbins + 1)[:-1]
        self._radii_square = np.square(self.radii[1:])

    @property
    def radii(self) -> NDArray:
        return self._radii

    @property
    def rdf(self) -> NDArray:
        if self._rdf is None:
            raise ValueError("RDF not computed. Call run() first.")
        return self._rdf

    @property
    def cn(self) -> NDArray:
        if self._cn is None:
            raise ValueError("CN not computed. Call run() first.")
        return self._cn

    @abstractmethod
    def _check_args(self, a, b, box):
        return a, b, box

    @abstractmethod
    def run(self, start: int = 0, stop: int | None = None, step: int = 1, verbose: bool = True) -> "BaseRDF":
        return self

    def _compute_rdf(self, frames) -> "BaseRDF":
        nframes = 0
        histogram = np.zeros(self.nbins, dtype=np.float64)
        rdf = np.zeros(self.nbins, dtype=np.float64)

        for a_frame, b_frame, box_frame in frames:
            hist, vol = self._process_single_frame(a_frame, b_frame, box_frame)
            nframes += 1
            histogram[1:] += hist[1:]
            rdf[1:] += hist[1:] / self._radii_square * vol

        self._finalize_rdf(rdf, histogram, nframes)
        return self

    def _process_single_frame(self, a_frame: NDArray, b_frame: NDArray, box_frame: NDArray) -> Tuple[NDArray, float]:
        distance = calculate_distance(apply_pbc(a_frame[:, None, :] - b_frame[None, :, :], box=box_frame))
        histogram = np.histogram(distance, bins=self.nbins, range=self.range)[0]
        volume = np.prod(box_frame)
        return histogram, volume

    def _finalize_rdf(self, rdf: NDArray, histogram: NDArray, nframes: int) -> None:
        dr = (self.range[1] - self.range[0]) / (self.nbins + 1)
        factor = 4.0 * np.pi * dr * nframes * self.a.shape[1] * self.b.shape[1]

        self._rdf = rdf / factor
        self._cn = np.cumsum(histogram / (nframes * self.a.shape[1]))
