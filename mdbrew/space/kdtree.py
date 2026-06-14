"""A periodic k-d tree for neighbor queries under periodic boundary conditions.

The tree mirrors the semantics of ``scipy.spatial.cKDTree(boxsize=...)`` but is
implemented with numpy only, matching the package's orthorhombic minimum-image
convention (see :func:`mdbrew.space.apply_pbc`). Distances between a query point
and tree nodes are measured with the *minimum image* of the box, so neighbors
are found across periodic boundaries without replicating atoms.
"""

import heapq

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .core import convert_to_box_matrix


def _as_boxsize(boxsize: ArrayLike, dim: int = 3) -> NDArray:
    """Normalize a box specification to per-axis lengths of shape ``(dim,)``."""
    box = np.asarray(boxsize, dtype=float)
    if box.ndim == 0:
        return np.full(dim, float(box))
    if box.ndim == 1:
        if box.shape[0] != dim:
            raise ValueError(f"boxsize must have {dim} entries, got {box.shape[0]}.")
        return box
    matrix = convert_to_box_matrix(box, dim=dim)
    off_diagonal = matrix - np.diag(np.diag(matrix))
    if np.abs(off_diagonal).max() > 1e-8 * max(1.0, np.abs(matrix).max()):
        raise ValueError("PeriodicKDTree supports only orthorhombic (diagonal) boxes.")
    lengths = np.diag(matrix).astype(float)
    if np.any(lengths <= 0.0):
        raise ValueError("All box lengths must be positive.")
    return lengths


class _Node:
    __slots__ = ("lo", "hi", "dim", "split", "left", "right", "idx")

    def __init__(self):
        self.dim = -1  # leaf by default
        self.idx = None
        self.left = None
        self.right = None


class PeriodicKDTree:
    """k-d tree with periodic (minimum-image) distance queries.

    Parameters
    ----------
    data : ArrayLike
        Point coordinates of shape ``(npoints, dim)``. Points are wrapped into
        the primary cell ``[0, L)`` internally; returned indices refer to the
        original ``data`` order.
    boxsize : ArrayLike
        Orthorhombic cell as a scalar, per-axis lengths ``(dim,)``, or a diagonal
        ``(dim, dim)`` matrix.
    leafsize : int, optional
        Points per leaf where the search switches to a vectorized brute force.
    """

    def __init__(self, data: ArrayLike, boxsize: ArrayLike, *, leafsize: int = 16):
        data = np.ascontiguousarray(data, dtype=float)
        if data.ndim != 2:
            raise ValueError(f"data must have shape (npoints, dim), got {data.shape}.")
        self.dim = data.shape[1]
        self.boxsize = _as_boxsize(boxsize, dim=self.dim)
        self.leafsize = max(1, int(leafsize))
        self.data = np.mod(data, self.boxsize)  # wrap into the primary cell
        self.n = self.data.shape[0]
        self.root = self._build(np.arange(self.n)) if self.n else None

    def __repr__(self) -> str:
        return f"PeriodicKDTree(n={self.n}, dim={self.dim}, boxsize={self.boxsize.tolist()})"

    # -- build ---------------------------------------------------------------
    def _build(self, idx: NDArray) -> _Node:
        pts = self.data[idx]
        node = _Node()
        node.lo = pts.min(axis=0)
        node.hi = pts.max(axis=0)
        if idx.shape[0] <= self.leafsize:
            node.idx = idx
            return node
        dim = int(np.argmax(node.hi - node.lo))
        order = np.argsort(pts[:, dim], kind="quicksort")
        idx = idx[order]
        mid = idx.shape[0] // 2
        node.dim = dim
        node.split = float(self.data[idx[mid], dim])
        node.left = self._build(idx[:mid])
        node.right = self._build(idx[mid:])
        return node

    # -- periodic distance helpers ------------------------------------------
    def _bbox_mindist2(self, q: NDArray, lo: NDArray, hi: NDArray) -> float:
        """Squared minimum-image distance from point ``q`` to the box [lo, hi]."""
        L = self.boxsize
        dlo = np.abs(q - lo)
        dlo = np.minimum(dlo, L - dlo)
        dhi = np.abs(q - hi)
        dhi = np.minimum(dhi, L - dhi)
        d = np.where((q >= lo) & (q <= hi), 0.0, np.minimum(dlo, dhi))
        return float(d @ d)

    def _pdist2(self, q: NDArray, pts: NDArray) -> NDArray:
        """Squared minimum-image distances from ``q`` to each point in ``pts``."""
        delta = pts - q
        delta -= self.boxsize * np.round(delta / self.boxsize)
        return np.einsum("ij,ij->i", delta, delta)

    # -- radius search -------------------------------------------------------
    def _radius(self, node: _Node, q: NDArray, r2: float, out: list) -> None:
        if node is None or self._bbox_mindist2(q, node.lo, node.hi) > r2:
            return
        if node.idx is not None:
            d2 = self._pdist2(q, self.data[node.idx])
            hit = node.idx[d2 <= r2]
            if hit.size:
                out.append(hit)
            return
        self._radius(node.left, q, r2, out)
        self._radius(node.right, q, r2, out)

    def query_ball_point(self, x: ArrayLike, r: float):
        """Return indices of all points within radius ``r`` of each query point.

        For a single point (1D ``x``) returns a sorted index array; for multiple
        points (2D ``x``) returns a list of such arrays.
        """
        x = np.asarray(x, dtype=float)
        single = x.ndim == 1
        queries = np.mod(np.atleast_2d(x), self.boxsize)  # wrap into the primary cell
        r2 = float(r) * float(r)
        results = []
        for q in queries:
            out: list = []
            self._radius(self.root, q, r2, out)
            hits = np.concatenate(out) if out else np.empty(0, dtype=int)
            results.append(np.sort(hits))
        return results[0] if single else results

    def _radius_dist(self, node: _Node, q: NDArray, r2: float, out: list) -> None:
        if node is None or self._bbox_mindist2(q, node.lo, node.hi) > r2:
            return
        if node.idx is not None:
            d2 = self._pdist2(q, self.data[node.idx])
            hit = d2[d2 <= r2]
            if hit.size:
                out.append(hit)
            return
        self._radius_dist(node.left, q, r2, out)
        self._radius_dist(node.right, q, r2, out)

    def query_ball_distances(self, x: ArrayLike, r: float) -> NDArray:
        """Flat array of every minimum-image distance ``<= r`` from the query
        points ``x`` to the tree points. Each unordered neighbor contributes once
        per query point (self-distances of 0 are included when ``x`` is the tree's
        own data). Tailored for histogram-based analyses such as the RDF.
        """
        queries = np.mod(np.atleast_2d(np.asarray(x, dtype=float)), self.boxsize)
        r2 = float(r) * float(r)
        chunks = []
        for q in queries:
            out: list = []
            self._radius_dist(self.root, q, r2, out)
            if out:
                chunks.append(np.concatenate(out))
        return np.sqrt(np.concatenate(chunks)) if chunks else np.empty(0, dtype=float)

    def sorted_neighbor_distances(self, x: ArrayLike, r: float, k: int) -> NDArray:
        """Per query point, the ``k`` smallest minimum-image neighbor distances
        within radius ``r``, sorted ascending and padded to width ``k`` with
        ``inf``. Returns shape ``(nqueries, k)``.

        Useful for per-neighbor-shell analyses: column ``i`` holds the distance
        to each query point's ``i``-th nearest neighbor (``inf`` where fewer than
        ``k`` neighbors lie within ``r``).
        """
        queries = np.mod(np.atleast_2d(np.asarray(x, dtype=float)), self.boxsize)
        out = np.full((queries.shape[0], int(k)), np.inf)
        r2 = float(r) * float(r)
        for i, q in enumerate(queries):
            chunks: list = []
            self._radius_dist(self.root, q, r2, chunks)
            if chunks:
                d = np.sqrt(np.concatenate(chunks))
                d.sort()
                m = min(int(k), d.size)
                out[i, :m] = d[:m]
        return out

    # -- k nearest neighbors -------------------------------------------------
    def _knn(self, node: _Node, q: NDArray, k: int, heap: list) -> None:
        if node is None:
            return
        if len(heap) == k and self._bbox_mindist2(q, node.lo, node.hi) > -heap[0][0]:
            return
        if node.idx is not None:
            d2 = self._pdist2(q, self.data[node.idx])
            for dist2, point in zip(d2, node.idx):
                if len(heap) < k:
                    heapq.heappush(heap, (-float(dist2), int(point)))
                elif dist2 < -heap[0][0]:
                    heapq.heapreplace(heap, (-float(dist2), int(point)))
            return
        near, far = (node.left, node.right) if q[node.dim] < node.split else (node.right, node.left)
        self._knn(near, q, k, heap)
        self._knn(far, q, k, heap)

    def query(self, x: ArrayLike, k: int = 1):
        """Return the ``k`` nearest neighbors of each query point.

        Returns ``(distances, indices)``. Shapes are ``(k,)`` for a single 1D
        query and ``(nqueries, k)`` for a 2D batch. Missing neighbors (when
        ``k > npoints``) are reported as ``inf`` distance and index ``-1``.
        """
        x = np.asarray(x, dtype=float)
        single = x.ndim == 1
        queries = np.mod(np.atleast_2d(x), self.boxsize)  # wrap into the primary cell
        k = int(k)
        dists = np.full((queries.shape[0], k), np.inf)
        idxs = np.full((queries.shape[0], k), -1, dtype=int)
        for i, q in enumerate(queries):
            heap: list = []
            self._knn(self.root, q, k, heap)
            ordered = sorted(((-nd2, pt) for nd2, pt in heap))  # ascending distance
            for j, (dist2, point) in enumerate(ordered):
                dists[i, j] = np.sqrt(dist2)
                idxs[i, j] = point
        if single:
            return dists[0], idxs[0]
        return dists, idxs

    # -- neighbor pairs ------------------------------------------------------
    def query_pairs(self, r: float) -> NDArray:
        """Return all unique index pairs ``(i, j)`` with ``i < j`` within ``r``.

        Shape ``(npairs, 2)`` — convenient for building neighbor lists.
        """
        neighbors = self.query_ball_point(self.data, r)
        pairs = [(i, int(j)) for i, js in enumerate(neighbors) for j in js if j > i]
        return np.array(pairs, dtype=int).reshape(-1, 2)
