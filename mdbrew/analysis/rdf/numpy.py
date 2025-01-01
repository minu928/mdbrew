from tqdm import tqdm

import numpy as np

from mdbrew.utils.space import convert_to_box_vec
from mdbrew.errors import NotEqualFrameError
from mdbrew.analysis.rdf.base import BaseRDF


class NumpyRDF(BaseRDF):
    def __init__(self, a, b, box, *, nbins=100, ranges=(0, 6)):
        super().__init__(a, b, box, nbins=nbins, ranges=ranges)

    def _check_args(self, a, b, box):
        if not (len(a) == len(b) == len(box)):
            raise NotEqualFrameError("Lengths of a, b, and box must be equal")
        a = np.asarray(a)
        b = np.asarray(b)
        box = convert_to_box_vec(box=np.asarray(box))
        return a, b, box

    def run(self, start: int = 0, stop: int | None = None, step: int = 1, verbose: bool = True) -> "NumpyRDF":
        frames = zip(self.a[start:stop:step], self.b[start:stop:step], self.box[start:stop:step])
        if verbose:
            frames = tqdm(frames, **self.TQDM_OPTIONS)
        return self._compute_rdf(frames)
