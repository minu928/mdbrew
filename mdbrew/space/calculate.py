import numpy as np

from .convert import convert_to_box_matrix


def calculate_volume(box, *, dtype=None) -> None:
    a, b, c = convert_to_box_matrix(box=box, dtype=dtype)
    return np.cross(a, b) @ c


def calculate_distance(vec):
    return np.sqrt(np.sum(np.square(vec), axis=-1))


def calculate_virial(box, stress, *, dtype=None):
    box = np.asarray(box, dtype=dtype)
    stress = np.asarray(stress, dtype=dtype)
    return stress * calculate_volume(box=box, dtype=dtype)


def calculate_angle(vec1, vec2, *, rad2deg: bool = False, dtype=None):
    vec1 = np.asarray(vec1)
    vec2 = np.asarray(vec2)
    dot_product = np.sum(vec1 * vec2, axis=-1)
    norm_v1 = np.linalg.norm(vec1, axis=-1)
    norm_v2 = np.linalg.norm(vec2, axis=-1)
    angle = np.arccos(dot_product / (norm_v1 * norm_v2), dtype=dtype)
    if rad2deg:
        angle = np.rad2deg(angle)
    return angle
