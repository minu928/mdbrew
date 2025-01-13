from typing import TextIO

from mdbrew.type import MDState
from mdbrew.space import convert_to_box_matrix

from .base import BaseReader


calculate_box_length = lambda lb, ub: float(ub) - float(lb)


class LMPSReader(BaseReader):
    fmt = "lmps"

    def _make_mdstate(self, file: TextIO) -> MDState:
        if not file.readline().strip():
            raise EOFError
        next(file)
        natoms = int(file.readline().split()[0])
        next(file)
        next(file)
        box = convert_to_box_matrix([calculate_box_length(*file.readline().split()[0:2]) for _ in range(3)])
        next(file)
        next(file)
        next(file)
        next(file)
        data = dict(atomid=[], atom=[], coord=[])
        for _ in range(natoms):
            atomid, atom, x, y, z = file.readline().split()
            data["atomid"].append(atomid)
            data["atom"].append(atom)
            data["coord"].append([x, y, z])
        return MDState(**data, box=box)

    def _get_frame_offset(self, file: TextIO) -> int:
        frame_offset = file.tell()
        if not file.readline().strip():
            raise EOFError
        file.readline()
        natoms = int(file.readline().split()[0])
        file.readline()
        file.readline()
        [file.readline() for _ in range(3)]
        file.readline()
        file.readline()
        file.readline()
        file.readline()
        [file.readline() for _ in range(natoms)]
        return frame_offset
