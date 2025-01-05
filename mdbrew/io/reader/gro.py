from typing import TextIO

from numpy import empty, diag

from mdbrew.core import MDState

from .base import BaseReader


class GROReader(BaseReader):
    fmt = "gro"

    def __init__(self, filepath, **kwargs):
        super().__init__(filepath, **kwargs)
        self._has_velocity = None

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError

        natoms = int(file.readline().strip())

        line = file.readline()
        if self._has_velocity is None:
            self._has_velocity = bool(line[slice(44, 68)].strip())

        data = {
            "residueid": empty(natoms, dtype=int),
            "residue": empty(natoms, dtype="<U5"),
            "atom": empty(natoms, dtype="<U5"),
            "atomid": empty(natoms, dtype=int),
            "coord": empty((natoms, 3), dtype=float),
            "velocity": empty((natoms, 3), dtype=float) if self._has_velocity else None,
        }

        for i in range(natoms):
            if i > 0:
                line = file.readline()
            data["residueid"][i] = int(line[0:5])
            data["residue"][i] = line[5:10].strip()
            data["atom"][i] = line[10:15].strip()
            data["atomid"][i] = int(line[15:20])
            data["coord"][i] = [float(line[20 + j * 8 : 20 + (j + 1) * 8].strip()) for j in range(3)]

            if self._has_velocity:
                data["velocity"][i] = [float(line[44 + j * 8 : 44 + (j + 1) * 8].strip()) for j in range(3)]

        box = diag([float(x) for x in file.readline().split()])
        return MDState(**data, box=box)

    def _get_frame_offset(self, file: TextIO):
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        natoms = int(file.readline().strip())
        [file.readline() for _ in range(natoms)]  # line: data
        file.readline()  # line: box
        return frame_offset

    def _get_frame_offset(self, file: TextIO):
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        natoms = int(file.readline().strip())
        [file.readline() for _ in range(natoms)]  # line: data
        file.readline()  # line: box
        return frame_offset
