from typing import Iterable

import numpy as np
from numpy.typing import NDArray

from mdbrew._core import MDState


def is_diagonal_matrix(matrix: NDArray, tol: float = 1e-10) -> bool:
    off_diag_mask = ~np.eye(3, dtype=bool)
    return not np.any(np.abs(matrix[:, off_diag_mask]) > tol)


def check_mdstates(mdstates: list[MDState]):
    if not isinstance(mdstates, Iterable):
        raise TypeError("mdstates must be iterable")
    if not mdstates:
        raise ValueError("mdstates is empty")
