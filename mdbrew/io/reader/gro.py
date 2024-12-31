import numpy as np
from typing import TextIO
from mdbrew.dataclass import MDState
from mdbrew.io.reader.base import BaseReader


PROPERTY_SLICES = {
    "residueid": slice(0, 5),
    "residue": slice(5, 10),
    "atom": slice(10, 15),
    "atomid": slice(15, 20),
    "coord": slice(20, 44),  # x,y,z (20-28, 28-36, 36-44)
    "velocity": slice(44, 68),  # vx,vy,vz (44-52, 52-60, 60-68)
}


class GROReader(BaseReader):
    fmt = "gro"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self._has_velocity = None

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError

        natoms = int(file.readline().strip())
        lines = [file.readline() for _ in range(natoms)]

        if self._has_velocity is None:
            self._has_velocity = bool(lines[0][PROPERTY_SLICES["velocity"]].strip())

        data = {}
        for prop, _slice in PROPERTY_SLICES.items():
            if prop == "velocity" and not self._has_velocity:
                data[prop] = None
                continue
            data[prop] = np.array([line[_slice].split() for line in lines])

        box = np.diag([float(x) for x in file.readline().split()])
        return MDState(**data, box=box)
