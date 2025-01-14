from typing import Callable

import numpy as np
from numpy.typing import ArrayLike

from mdbrew.space import convert_to_box_matrix
from mdbrew.type import MDState, MDStateAttr


ATTR_TRANSFORMERS: dict[MDStateAttr, Callable[[any], any]] = {
    "energy": float,
    "coord": lambda x: np.asarray(x).reshape(-1, 3),
    "force": lambda x: np.asarray(x).reshape(-1, 3),
    "stress": lambda x: np.asarray(x).reshape(3, 3),
    "virial": lambda x: np.asarray(x).reshape(3, 3),
    "velocity": lambda x: np.asarray(x).reshape(-1, 3),
    "box": lambda x: convert_to_box_matrix(x),
    "atom": lambda x: x,
    "atomid": lambda x: x,
    "residue": lambda x: x,
    "residueid": lambda x: x,
    "charge": lambda x: x,
}


def load(**states: dict[MDStateAttr, ArrayLike]) -> list[MDState]:
    first_val = next(iter(states.values()))
    nframe = len(first_val)

    if not all(len(val) == nframe for val in states.values()):
        raise ValueError("All input arrays must have the same number of frames.")

    transformers = {key: ATTR_TRANSFORMERS[key] for key in states}
    return [MDState(**{key: transformers[key](val[i]) for key, val in states.items()}) for i in range(nframe)]
