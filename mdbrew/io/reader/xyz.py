from typing import TextIO

from mdbrew.type import MDState

from .base import BaseReader


class XYZReader(BaseReader):
    fmt = "xyz"

    def _make_mdstate(self, file: TextIO) -> MDState:
        line = file.readline().strip()
        if not line:
            raise EOFError
        next(file)
        natoms = int(line)
        atom_list = []
        coord_list = []
        for _ in range(natoms):
            atom, x, y, z = file.readline().split()
            atom_list.append([atom])
            coord_list.append([float(x), float(y), float(z)])
        return MDState(atom=atom_list, coord=coord_list, atomid=range(1, natoms + 1))

    def _get_frame_offset(self, file: TextIO) -> int:
        frame_offset = file.tell()
        line = file.readline()
        if not line:
            raise EOFError
        natoms = int(line.strip())
        file.readline()  # skip property line
        [file.readline() for _ in range(natoms)]
        return frame_offset
