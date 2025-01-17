import numpy as np
from numpy.typing import NDArray
import numba as nb

from .core import convert_to_box_matrix


def calculate_volume(box, *, dtype=None) -> None:
    a, b, c = convert_to_box_matrix(box=box, dtype=dtype)
    return np.cross(a, b) @ c


@nb.njit
def calculate_distance(vec: NDArray):
    return np.sqrt(np.sum(np.square(vec), axis=-1))


def calculate_virial(box, stress, *, dtype=None):
    box = np.asarray(box, dtype=dtype)
    stress = np.asarray(stress, dtype=dtype)
    return stress * calculate_volume(box=box, dtype=dtype)


@nb.njit
def calculate_angle(vec1: NDArray, vec2: NDArray, rad2deg: bool = False):
    dot_product = np.sum(vec1 * vec2, axis=-1)
    norm_v1 = calculate_distance(vec1)
    norm_v2 = calculate_distance(vec2)
    angle = np.arccos(dot_product / (norm_v1 * norm_v2))
    if rad2deg:
        angle = np.rad2deg(angle)
    return angle
