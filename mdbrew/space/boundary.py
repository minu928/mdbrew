import numpy as np
from numpy.typing import NDArray


def apply_pbc(vec: NDArray, box: NDArray):
    half_box = box * 0.5
    return np.mod(vec + half_box, box) - half_box


def wrap(coord: NDArray, box: NDArray):
    return np.mod(coord, box)
