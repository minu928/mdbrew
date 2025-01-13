import numpy as np


def apply_pbc(vec, box):
    box = np.asarray(box, dtype=None)
    vec = np.asarray(vec, dtype=None)
    half_box = box * 0.5
    return np.mod(vec + half_box, box) - half_box


def wrap(coord, box):
    box = np.asarray(box, dtype=None)
    coord = np.asarray(coord, dtype=None)
    return np.mod(coord, box)
