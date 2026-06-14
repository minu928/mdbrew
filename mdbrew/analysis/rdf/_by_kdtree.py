import numpy as np
from numpy.typing import NDArray

from mdbrew.space import PeriodicKDTree
from ._by_array import ArrayRDF


class KDTreeRDF(ArrayRDF):
    """RDF accelerated with a periodic k-d tree.

    Produces the same result as :class:`ArrayRDF` but, instead of forming the
    full ``(n1, n2)`` distance matrix each frame, it queries only the pairs
    within the histogram's maximum radius (``range[1]``) using a periodic k-d
    tree. This replaces the ``O(n1 * n2)`` work (and memory) with roughly
    ``O(n1 * k)`` for ``k`` neighbors within the cutoff — a large win whenever
    the cutoff is much smaller than the box, as is typical for an RDF.

    The interface matches :class:`ArrayRDF` exactly; only the per-frame distance
    computation differs.
    """

    def _frame_histogram(self, x1_i: NDArray, x2_i: NDArray, box: NDArray) -> NDArray:
        tree = PeriodicKDTree(x2_i, box)
        distances = tree.query_ball_distances(x1_i, self._range[1])
        hist_i, _ = np.histogram(distances, bins=self._nbins, range=self._range)
        return hist_i
