import numpy as np
from numpy.typing import NDArray

from .core import convert_to_box_matrix


def apply_pbc(vec: NDArray, box: NDArray):
    half_box = box * 0.5
    return np.mod(vec + half_box, box) - half_box


def wrap(coord: NDArray, box: NDArray):
    return np.mod(coord, box)


def _stack_box_matrices(box: NDArray, nframes: int) -> NDArray:
    """Normalize a box specification to per-frame matrices of shape (nframes, 3, 3).

    A 3D array is treated as one box matrix per frame (e.g. NPT cells from
    ``extract(states, "box")``). Anything else is treated as a single constant
    box and broadcast across all frames.
    """
    box = np.asarray(box, dtype=float)
    if box.ndim == 3:
        if box.shape != (nframes, 3, 3):
            raise ValueError(f"Per-frame box must have shape ({nframes}, 3, 3), got {box.shape}.")
        return box
    return np.broadcast_to(convert_to_box_matrix(box), (nframes, 3, 3))


def unwrap(coords: NDArray, box: NDArray) -> NDArray:
    """Unwrap a trajectory across periodic boundaries.

    Reconstructs continuous particle trajectories from wrapped coordinates using
    the minimum-image displacement scheme — the default method of OVITO's
    "Unwrap trajectories" modifier. For each pair of consecutive frames the
    per-particle displacement is mapped into the cell's minimum image (in
    fractional coordinates) and the true displacements are accumulated, so a
    particle that crosses a boundary is shifted by a whole cell vector instead of
    jumping. Particle order must be consistent across frames, and displacements
    between frames are assumed to be smaller than half the cell.

    Parameters
    ----------
    coords : NDArray
        Wrapped positions of shape ``(nframes, natoms, 3)``.
    box : NDArray
        Either a single constant cell (``(3, 3)`` matrix, ``(3,)`` lengths, or a
        scalar) applied to every frame, or per-frame cells of shape
        ``(nframes, 3, 3)`` for a variable cell. Cell vectors are the matrix rows.

    Returns
    -------
    NDArray
        Unwrapped positions of shape ``(nframes, natoms, 3)``.
    """
    coords = np.asarray(coords, dtype=float)
    if coords.ndim != 3 or coords.shape[-1] != 3:
        raise ValueError(f"coords must have shape (nframes, natoms, 3), got {coords.shape}.")

    nframes = coords.shape[0]
    if nframes < 2:
        return coords.copy()

    box_mats = _stack_box_matrices(box, nframes)
    box_next = box_mats[1:]  # cell of the later frame of each consecutive pair
    box_inv_next = np.linalg.inv(box_next)

    deltas = np.diff(coords, axis=0)  # (nframes - 1, natoms, 3)
    deltas_frac = np.einsum("kni,kij->knj", deltas, box_inv_next)
    deltas_frac -= np.round(deltas_frac)  # minimum image in fractional space
    deltas_min = np.einsum("knj,kjl->knl", deltas_frac, box_next)

    unwrapped = np.empty_like(coords)
    unwrapped[0] = coords[0]
    unwrapped[1:] = coords[0] + np.cumsum(deltas_min, axis=0)
    return unwrapped
