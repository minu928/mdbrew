import numpy as np
from numpy.typing import NDArray


def is_diagonal_matrix(matrix: NDArray, tol: float = 1e-10) -> bool:
    off_diag_mask = ~np.eye(3, dtype=bool)
    return not np.any(np.abs(matrix[:, off_diag_mask]) > tol)
