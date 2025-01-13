import numpy as np
from mdbrew.utils.check import is_diagonal_matrix


def convert_to_box_matrix(box, *, dtype=None, dim: int = 3):
    box = np.asarray(box).astype(dtype=dtype)
    if not box.size:
        return box
    ndim = box.ndim
    shape = box.shape
    if ndim == 0:
        return np.eye(dim) * box
    elif ndim == 1 and shape[0] == dim:
        return np.diag(box)
    elif ndim == 2 and shape == (dim, dim):
        return box
    else:
        raise ValueError(f"We can not diagonalize the box shape. {shape}")


def convert_to_box_vec(box, tol: float = 1e-10):
    box = np.asarray(box)
    if box.ndim == 2:
        if box.shape[1] != 3:
            raise ValueError("Box shape must be (nframe, 3)")
        return box

    if box.ndim == 3:
        if box.shape[1:] != (3, 3):
            raise ValueError("Box shape must be (nframe, 3, 3)")

        if not is_diagonal_matrix(box, tol):
            raise ValueError("All boxes must be diagonal matrices")

        return box.diagonal(axis1=1, axis2=2)

    raise ValueError("Box must be 2D or 3D array")


def calculate_volume(box, *, dtype=None) -> None:
    a, b, c = convert_to_box_matrix(box=box, dtype=dtype)
    return np.cross(a, b) @ c


def apply_pbc(vec, box):
    box = np.asarray(box, dtype=None)
    vec = np.asarray(vec, dtype=None)
    half_box = box * 0.5
    return np.mod(vec + half_box, box) - half_box


def wrap(coord, box):
    box = np.asarray(box, dtype=None)
    coord = np.asarray(coord, dtype=None)
    return np.mod(coord, box)


def calculate_distance(vec):
    return np.sqrt(np.sum(np.square(vec), axis=-1))
